import os
import time
import requests
import pandas as pd
import feedparser
from datetime import datetime, timezone
from threading import Thread

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from flask import Flask

# ==========================
# 🌐 FLASK KEEP ALIVE
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "👑 ULTRA V10 RUNNING"

def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ==========================
# 🔑 TELEGRAM
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")


# ==========================
# 📊 STATE
# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

bot_enabled = True
sent_signals = {}
last_event_hour = None


# ==========================
# ⏱ TIME
# ==========================
def now():
    return datetime.now(timezone.utc)


# ==========================
# 🌍 MARKET SESSION
# ==========================
def market_session():
    h = now().hour
    if 0 <= h < 6:
        return "ASIA", 1.0
    elif 6 <= h < 12:
        return "LONDON", 1.3
    elif 12 <= h < 20:
        return "NEW YORK", 1.5
    return "QUIET", 0.7


# ==========================
# 🌍 EVENTS
# ==========================
def market_events():
    h = now().hour
    events = []

    if h == 1: events.append("🔔 Tokyo Open")
    if h == 10: events.append("🔔 London Open")
    if h == 15: events.append("🔔 New York Open")
    if h == 19: events.append("🔕 London Close")

    return events


# ==========================
# 🌐 REQUEST
# ==========================
session = requests.Session()


# ==========================
# 📊 BINANCE DATA
# ==========================
def price(symbol):
    try:
        r = session.get("https://api.binance.com/api/v3/ticker/price",
                        params={"symbol": symbol}, timeout=5)
        return float(r.json()["price"])
    except:
        return None


def klines(symbol):
    try:
        r = session.get("https://api.binance.com/api/v3/klines",
                        params={"symbol": symbol, "interval": "5m", "limit": 100})
        d = r.json()

        c = [float(x[4]) for x in d]
        h = [float(x[2]) for x in d]
        l = [float(x[3]) for x in d]

        return c, h, l
    except:
        return [], [], []


# ==========================
# 📊 INDICATORS
# ==========================
def ema(data, p):
    return pd.Series(data).ewm(span=p).mean().iloc[-1]


def rsi(data):
    s = pd.Series(data)
    d = s.diff()
    g = d.clip(lower=0).rolling(14).mean()
    l = (-d.clip(upper=0)).rolling(14).mean()
    rs = g.iloc[-1] / (l.iloc[-1] + 1e-9)
    return 100 - (100 / (1 + rs))


def atr(h, l, c):
    tr = []
    for i in range(1, len(c)):
        tr.append(max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])))
    return pd.Series(tr).rolling(14).mean().iloc[-1]


# ==========================
# 🧠 SMART MONEY (LIGHT)
# ==========================
def liquidity(h, l):
    if len(h) < 20:
        return 0

    high_zone = max(h[-20:])
    low_zone = min(l[-20:])

    return high_zone, low_zone


def bos(h):
    return h[-1] > max(h[-10:-1])


def choch(h, l):
    return h[-1] < max(h[-10:-1]) and l[-1] > min(l[-10:-1])


# ==========================
# 📰 NEWS
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0

        for e in feed.entries[:10]:
            t = e.title.lower()

            if any(w in t for w in ["bull", "pump", "rise", "surge"]):
                score += 1

            if any(w in t for w in ["bear", "dump", "crash", "drop"]):
                score -= 1

        if score >= 3:
            return 1.2
        elif score <= -3:
            return 0.8
        return 1.0

    except:
        return 1.0


# ==========================
# ⚡ ANTI CHOP FILTER
# ==========================
def anti_chop(score, atr_val):
    if atr_val is None:
        return True
    if atr_val < 0.2 and abs(score) < 5:
        return True
    return False


# ==========================
# 🧠 ANALYSIS ENGINE
# ==========================
def analyse(symbol):

    c, h, l = klines(symbol)
    p = price(symbol)

    if not p or len(c) < 60:
        return None

    ema20 = ema(c, 20)
    ema50 = ema(c, 50)
    r = rsi(c)
    a = atr(h, l, c)

    trend = 1 if ema20 > ema50 else -1

    momentum = 0
    if r < 30:
        momentum = 1
    elif r > 70:
        momentum = -1

    score = (trend * 2) + (momentum * 3)

    sess, mp = market_session()
    news_factor = news_engine()

    score = score * mp * news_factor

    # 💧 liquidity
    liq_high, liq_low = liquidity(h, l)

    if anti_chop(score, a):
        return None

    # 🧠 Smart Money confirmation
    bos_signal = bos(h)
    choch_signal = choch(h, l)

    if not (bos_signal or choch_signal):
        score *= 0.8

    # 🔥 signal filter
    if abs(score) < 6:
        return None

    direction = "🟢 BUY" if score > 0 else "🔴 SELL"

    if score > 0:
        sl = p - a
        tp1 = p + a
        tp2 = p + a * 2
        tp3 = p + a * 3
    else:
        sl = p + a
        tp1 = p - a
        tp2 = p - a * 2
        tp3 = p - a * 3

    conf = min(100, abs(score) * 7)

    return symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess


# ==========================
# 📩 TELEGRAM UI
# ==========================
def on_chat(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT")],
            [InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
            [InlineKeyboardButton(text="BNB", callback_data="BNBUSDT")],
            [InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")],
            [InlineKeyboardButton(text="PAXG", callback_data="PAXGUSDT")],
            [InlineKeyboardButton(text="BOT ON/OFF", callback_data="TOGGLE")]
        ])

        bot.sendMessage(chat_id, "👑 ULTRA V10 CONTROL PANEL", reply_markup=kb)


# ==========================
# 📊 CALLBACK
# ==========================
def on_callback(msg):
    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    global bot_enabled

    if data == "TOGGLE":
        bot_enabled = not bot_enabled
        bot.sendMessage(chat_id, f"BOT {'🟢 ON' if bot_enabled else '🔴 OFF'}")
        return

    p = price(data)
    info = analyse(data)

    if not info:
        bot.sendMessage(chat_id, f"📊 {data}\n💰 {p}\n⚪ No strong signal")
        return

    sym, pr, dr, sc, cf, sl, tp1, tp2, tp3, sess = info

    bot.sendMessage(chat_id, f"""
📊 {sym}

💰 {round(pr,2)}
🎯 {dr}

🔥 Score: {round(sc,2)}
📊 Conf: {round(cf,2)}%

🌍 Session: {sess}

🛑 SL: {round(sl,2)}
🎯 TP1: {round(tp1,2)}
🎯 TP2: {round(tp2,2)}
🎯 TP3: {round(tp3,2)}
""")


# ==========================
# 🚀 SIGNAL LOOP
# ==========================
def signal_loop():
    global bot_enabled

    while True:

        if not bot_enabled:
            time.sleep(5)
            continue

        for s in watchlist:

            info = analyse(s)
            if not info:
                continue

            sym, pr, dr, sc, cf, sl, tp1, tp2, tp3, sess = info

            key = f"{sym}_{dr}"

            if key in sent_signals and time.time() - sent_signals[key] < 600:
                continue

            sent_signals[key] = time.time()

            if cf < 70:
                continue

            bot.sendMessage(ADMIN_CHAT_ID, f"""
🔥 ULTRA V10 SIGNAL

📊 {sym}
💰 {round(pr,2)}
🎯 {dr}

🔥 Score {round(sc,2)}
📊 Conf {round(cf,2)}%

🌍 {sess}

🛑 SL {round(sl,2)}
🎯 TP1 {round(tp1,2)}
🎯 TP2 {round(tp2,2)}
🎯 TP3 {round(tp3,2)}
""")

        time.sleep(30)


# ==========================
# 🌍 EVENTS LOOP
# ==========================
def event_loop():
    global last_event_hour

    while True:
        h = now().hour

        if h != last_event_hour:
            last_event_hour = h
            for e in market_events():
                bot.sendMessage(ADMIN_CHAT_ID, f"🌍 {e}")

        time.sleep(60)


# ==========================
# 💚 HEARTBEAT
# ==========================
def heartbeat():
    while True:
        print("💚 ULTRA V10 ALIVE", datetime.now())
        time.sleep(30)


# ==========================
# 🚀 START SYSTEM
# ==========================
if __name__ == "__main__":

    Thread(target=run_web, daemon=True).start()
    MessageLoop(bot, handle).run_as_thread()
    Thread(target=signal_loop, daemon=True).start()
    Thread(target=event_loop, daemon=True).start()
    Thread(target=heartbeat, daemon=True).start()

    while True:
        time.sleep(10)
