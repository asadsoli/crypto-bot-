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
# 🌐 WEB SERVER
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "👑 ULTRA AI BOT RUNNING"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


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

sent_signals = {}
last_event_hour = None
bot_enabled = True


# ==========================
# ⏱ TIME
# ==========================
def now():
    return datetime.now(timezone.utc)


# ==========================
# 🌍 MARKET SESSION
# ==========================
def market_data():
    h = now().hour
    if 0 <= h < 6:
        return "ASIA", 1.0, 0.8
    elif 6 <= h < 12:
        return "LONDON", 1.3, 1.2
    elif 12 <= h < 20:
        return "NEW YORK", 1.5, 1.5
    return "QUIET", 0.7, 0.6


# ==========================
# 🌍 EVENTS
# ==========================
def market_events():
    h = now().hour
    mapping = {
        1: "🔔 Tokyo Open",
        10: "🔔 London Open",
        15: "🔔 New York Open",
        19: "🔕 London Close",
    }
    return [mapping[h]] if h in mapping else []


# ==========================
# 🌐 SESSION
# ==========================
session = requests.Session()


# ==========================
# 📊 BINANCE
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
                        params={"symbol": symbol, "interval": "5m", "limit": 100},
                        timeout=5)
        d = r.json()
        c = [float(x[4]) for x in d]
        h = [float(x[2]) for x in d]
        l = [float(x[3]) for x in d]
        v = [float(x[5]) for x in d]
        return c, h, l, v
    except:
        return [], [], [], []


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
    out = pd.Series(tr).rolling(14).mean().iloc[-1]
    return out if not pd.isna(out) else None


# ==========================
# 📰 NEWS
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0

        bull = ["bull","pump","rise","surge","breakout"]
        bear = ["bear","dump","drop","crash","fall"]

        for e in feed.entries[:10]:
            t = e.title.lower()
            if any(w in t for w in bull):
                score += 1
            if any(w in t for w in bear):
                score -= 1

        if score >= 3:
            return "BULLISH", 1.3
        elif score <= -3:
            return "BEARISH", 0.7
        return "NEUTRAL", 1.0
    except:
        return "NO_NEWS", 1.0


# ==========================
# 🧠 ANALYSIS
# ==========================
def analyse(symbol):
    try:
        c, h, l, v = klines(symbol)
        p = price(symbol)

        if not p or len(c) < 60:
            return None

        ema20 = ema(c, 20)
        ema50 = ema(c, 50)
        r = rsi(c)
        a = atr(h, l, c)

        if not a:
            return None

        trend = 1 if ema20 > ema50 else -1
        momentum = 1 if r < 40 else (-1 if r > 60 else 0)

        session_name, mp, w = market_data()
        news, nw = news_engine()

        score = (trend*2 + momentum*3) * mp * w * nw

        # 🔥 improved classification
        if abs(score) < 1.5:
            state = "⚪ QUIET"
        elif abs(score) < 3:
            state = "🟡 WEAK"
        elif abs(score) < 5:
            state = "🟢 BUY" if score > 0 else "🔴 SELL"
        else:
            state = "🔥 STRONG BUY" if score > 0 else "💥 STRONG SELL"

        direction = "BUY" if score > 0 else "SELL"

        sl = p - a if score > 0 else p + a
        tp1 = p + a if score > 0 else p - a
        tp2 = p + a*2 if score > 0 else p - a*2
        tp3 = p + a*3 if score > 0 else p - a*3

        return symbol, p, state, direction, score, sl, tp1, tp2, tp3, session_name, news

    except:
        return None


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

            sym, pr, state, dr, sc, sl, t1, t2, t3, sess, news = info

            if "STRONG" not in state:
                continue

            key = f"{sym}_{state}"
            if key in sent_signals and time.time() - sent_signals[key] < 600:
                continue

            sent_signals[key] = time.time()

            bot.sendMessage(ADMIN_CHAT_ID, f"""
🚀 {sym}
💰 {round(pr,2)}

🔥 {state}
🌍 {sess}
📰 {news}

🛑 SL {round(sl,2)}
🎯 TP1 {round(t1,2)}
🎯 TP2 {round(t2,2)}
🎯 TP3 {round(t3,2)}
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
            for e in market_events():
                bot.sendMessage(ADMIN_CHAT_ID, f"🌍 {e}")
            last_event_hour = h
        time.sleep(60)


# ==========================
# 💚 HEARTBEAT
# ==========================
def heartbeat():
    while True:
        print("💚 ALIVE", datetime.now())
        time.sleep(30)


# ==========================
# 📩 TELEGRAM
# ==========================
def handle(msg):
    global bot_enabled

    try:
        flavor = telepot.flavor(msg)

        if flavor == 'callback_query':
            _, chat_id, data = telepot.glance(msg, flavor='callback_query')

            if data == "TOGGLE":
                bot_enabled = not bot_enabled
                bot.sendMessage(chat_id, f"BOT {'ON 🟢' if bot_enabled else 'OFF 🔴'}")
                return

            p = price(data)
            info = analyse(data)

            if not info:
                bot.sendMessage(chat_id, f"{data} 💰 {p}")
                return

            sym, pr, state, dr, sc, sl, t1, t2, t3, sess, news = info

            bot.sendMessage(chat_id, f"""
📊 {sym}
💰 {round(pr,2)}
🔥 {state}
🌍 {sess}
📰 {news}
""")

        elif 'text' in msg:
            chat_id = msg['chat']['id']

            if msg['text'] == "/start":
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT"),
                     InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
                    [InlineKeyboardButton(text="BNB", callback_data="BNBUSDT"),
                     InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")],
                    [InlineKeyboardButton(text="TOGGLE BOT", callback_data="TOGGLE")]
                ])

                bot.sendMessage(chat_id, "👑 CONTROL PANEL", reply_markup=kb)

    except Exception as e:
        print("ERROR", e)


# ==========================
# 🚀 START
# ==========================
if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    MessageLoop(bot, handle).run_as_thread()
    Thread(target=signal_loop, daemon=True).start()
    Thread(target=event_loop, daemon=True).start()
    Thread(target=heartbeat, daemon=True).start()

    while True:
        time.sleep(10)
