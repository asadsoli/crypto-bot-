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
# 🌐 FLASK (RENDER FIXED)
# ==========================
app = Flask(__name__)

@app.route("/")
def home():
    return "👑 ULTRA V10 BOT RUNNING"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ==========================
# 🔑 BOT CONFIG
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

bot = telepot.Bot(TOKEN)

# 🔥 remove webhook (important)
try:
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true",
        timeout=10
    )
except:
    pass


# ==========================
# 📊 STATE
# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

bot_enabled = True
last_signal = {}
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

    if h == 1:
        events.append("🔔 Tokyo Open")
    if h == 10:
        events.append("🔔 London Active")
    if h == 15:
        events.append("🔔 New York Open")
    if h == 19:
        events.append("🔕 London Close")

    return events


# ==========================
# 📈 PRICE
# ==========================
session = requests.Session()

def price(symbol):
    try:
        r = session.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=5
        )
        return float(r.json()["price"])
    except:
        return None


def klines(symbol):
    try:
        r = session.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": symbol, "interval": "5m", "limit": 100},
            timeout=5
        )

        data = r.json()
        closes = [float(x[4]) for x in data]
        highs = [float(x[2]) for x in data]
        lows = [float(x[3]) for x in data]

        return closes, highs, lows
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
        tr.append(
            max(
                h[i] - l[i],
                abs(h[i] - c[i - 1]),
                abs(l[i] - c[i - 1])
            )
        )

    return pd.Series(tr).rolling(14).mean().iloc[-1]


# ==========================
# 📰 NEWS ENGINE
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
            return "BULLISH", 1.3
        if score <= -3:
            return "BEARISH", 0.7

        return "NEUTRAL", 1.0

    except:
        return "NO_NEWS", 1.0


# ==========================
# 🧠 ANALYSIS CORE
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

    if not a:
        return None

    trend = 1 if ema20 > ema50 else -1

    momentum = 0
    if r < 35:
        momentum = 1
    elif r > 65:
        momentum = -1

    score = (trend * 2) + (momentum * 3)

    sess, mp = market_session()
    news, nw = news_engine()

    score *= mp * nw

    if abs(score) < 5:
        return None

    if score > 0:
        direction = "🟢 BUY"
        sl = p - a
        tp1 = p + a
        tp2 = p + a * 2
        tp3 = p + a * 3
    else:
        direction = "🔴 SELL"
        sl = p + a
        tp1 = p - a
        tp2 = p - a * 2
        tp3 = p - a * 3

    conf = min(100, abs(score) * 7)

    return symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, news


# ==========================
# 📩 TELEGRAM UI
# ==========================
def on_chat(msg):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    if text == "/start":

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT")],
            [InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
            [InlineKeyboardButton(text="BNB", callback_data="BNBUSDT")],
            [InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")],
            [InlineKeyboardButton(text="PAXG", callback_data="PAXGUSDT")],
            [InlineKeyboardButton(text="🟢 BOT ON/OFF", callback_data="TOGGLE")]
        ])

        bot.sendMessage(chat_id, "👑 ULTRA V10 CONTROL PANEL", reply_markup=kb)


# ==========================
# 🔘 CALLBACK
# ==========================
def on_callback(msg):
    global bot_enabled

    qid, chat_id, data = telepot.glance(msg, flavor="callback_query")

    if data == "TOGGLE":
        bot_enabled = not bot_enabled
        bot.sendMessage(chat_id, f"BOT {'🟢 ON' if bot_enabled else '🔴 OFF'}")
        return

    p = price(data)

    if not p:
        bot.sendMessage(chat_id, "❌ no price")
        return

    info = analyse(data)

    if not info:
        bot.sendMessage(chat_id, f"{data}\n💰 {p}\n⚪ NO SIGNAL")
        return

    sym, p, direction, score, conf, sl, tp1, tp2, tp3, sess, news = info

    bot.sendMessage(chat_id, f"""
📊 {sym}
💰 {round(p,2)}

🎯 {direction}
🔥 Score: {round(score,2)}
📊 Conf: {round(conf,2)}%

💼 Session: {sess}
📰 News: {news}

🛑 SL {round(sl,2)}
🎯 TP1 {round(tp1,2)}
🎯 TP2 {round(tp2,2)}
🎯 TP3 {round(tp3,2)}
""")


# ==========================
# 🔥 MAIN LOOP
# ==========================
def signal_loop():
    global bot_enabled, last_event_hour

    while True:
        try:

            if not bot_enabled:
                time.sleep(5)
                continue

            h = now().hour

            if h != last_event_hour:
                last_event_hour = h
                for e in market_events():
                    bot.sendMessage(ADMIN_CHAT_ID, e)

            for s in watchlist:

                info = analyse(s)
                if not info:
                    continue

                sym, p, direction, score, conf, sl, tp1, tp2, tp3, sess, news = info

                if conf < 50:
                    continue

                key = f"{sym}_{direction}"

                if key in last_signal:
                    continue

                last_signal[key] = time.time()

                bot.sendMessage(ADMIN_CHAT_ID, f"""
🚀 SIGNAL

📊 {sym}
💰 {round(p,2)}

🎯 {direction}
🔥 Score {round(score,2)}
📊 Conf {round(conf,2)}%

💼 {sess}
📰 {news}

🛑 SL {round(sl,2)}
🎯 TP1 {round(tp1,2)}
🎯 TP2 {round(tp2,2)}
🎯 TP3 {round(tp3,2)}
""")

            time.sleep(30)

        except Exception as e:
            print("LOOP ERROR:", e)
            time.sleep(3)


# ==========================
# 🌐 START SYSTEM
# ==========================
def start_bot():
    MessageLoop(bot, {
        "chat": on_chat,
        "callback_query": on_callback
    }).run_as_thread()


if __name__ == "__main__":

    print("🔥 ULTRA V10 STARTING...")

    Thread(target=run_web, daemon=True).start()
    Thread(target=start_bot, daemon=True).start()
    Thread(target=signal_loop, daemon=True).start()

    while True:
        time.sleep(10)
