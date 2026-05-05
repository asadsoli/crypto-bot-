# ==========================
# 🧠 ULTRA V10 - FULL FINAL VERSION
# ==========================

import os
import time
import requests
import pandas as pd
import feedparser

from datetime import datetime, timezone
from threading import Thread
from flask import Flask

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================
# 🌐 FLASK (حل Render)
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "ULTRA V10 BOT IS RUNNING"

def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ==========================
# 🔐 ENV VARIABLES
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID") or os.getenv("ADMIN_CHAT_ID")

if CHAT_ID:
    CHAT_ID = int(CHAT_ID)
else:
    print("❌ لم يتم العثور على CHAT_ID")

bot = telepot.Bot(BOT_TOKEN)

# ==========================
# 🕒 TIME
# ==========================
def now():
    return datetime.now(timezone.utc)

# ==========================
# 🌍 SESSION
# ==========================
def get_session():
    h = now().hour

    if 0 <= h < 6:
        return "ASIA", 0.8
    elif 6 <= h < 12:
        return "LONDON", 1.2
    elif 12 <= h < 18:
        return "NEW YORK", 1.5
    return "QUIET", 0.6

# ==========================
# 📊 MARKET DATA
# ==========================
def get_price(symbol):
    try:
        return float(requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol}, timeout=5
        ).json()["price"])
    except:
        return None

def get_klines(symbol):
    try:
        d = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": symbol, "interval": "5m", "limit": 100}
        ).json()

        close = [float(x[4]) for x in d]
        high = [float(x[2]) for x in d]
        low = [float(x[3]) for x in d]

        return close, high, low
    except:
        return [], [], []

# ==========================
# 📐 INDICATORS
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
# 📰 NEWS
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0

        for e in feed.entries[:10]:
            t = e.title.lower()

            if "bull" in t: score += 1
            if "bear" in t: score -= 1

        return score
    except:
        return 0

# ==========================
# 🧠 AI ENGINE
# ==========================
def ai_engine(symbol):

    c, h, l = get_klines(symbol)
    p = get_price(symbol)

    if not p or len(c) < 50:
        return None

    ema20 = ema(c, 20)
    ema50 = ema(c, 50)
    r = rsi(c)
    a = atr(h, l, c)

    trend = 1 if ema20 > ema50 else -1
    momentum = 1 if r < 30 else (-1 if r > 70 else 0)

    score = (trend * 2) + (momentum * 3)
    score += news_engine()

    session, power = get_session()
    score *= power

    if abs(score) < 5:
        return None

    if score > 0:
        direction = "BUY 🟢"
        sl = p - a * 1.5
        tp1 = p + a * 1.5
        tp2 = p + a * 2.5
    else:
        direction = "SELL 🔴"
        sl = p + a * 1.5
        tp1 = p - a * 1.5
        tp2 = p - a * 2.5

    confidence = min(100, abs(score) * 6)

    return {
        "symbol": symbol,
        "price": round(p, 2),
        "direction": direction,
        "score": round(score, 2),
        "confidence": round(confidence, 2),
        "sl": round(sl, 2),
        "tp1": round(tp1, 2),
        "tp2": round(tp2, 2),
        "session": session,
        "power": power
    }

# ==========================
# 📱 PANEL
# ==========================
def send_panel():

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 BTC", callback_data="BTCUSDT"),
            InlineKeyboardButton(text="📊 ETH", callback_data="ETHUSDT")
        ],
        [
            InlineKeyboardButton(text="📊 BNB", callback_data="BNBUSDT"),
            InlineKeyboardButton(text="💰 PAXG", callback_data="PAXGUSDT")
        ],
        [
            InlineKeyboardButton(text="🧠 الحالة", callback_data="STATUS")
        ]
    ])

    bot.sendMessage(CHAT_ID,
        "🚀 ULTRA V10 PANEL\nاختر عملة:",
        reply_markup=keyboard
    )

# ==========================
# 📩 CALLBACK
# ==========================
def on_callback(msg):

    _, chat_id, data = telepot.glance(msg, flavor='callback_query')

    if data == "STATUS":
        bot.sendMessage(chat_id, "🧠 البوت يعمل")
        return

    result = ai_engine(data)

    if not result:
        bot.sendMessage(chat_id, f"{data}\n⚪ NO SIGNAL")
        return

    bot.sendMessage(chat_id,
f"""
📊 {result['symbol']}
💰 {result['price']}

🎯 {result['direction']}
🔥 {result['score']}
📊 {result['confidence']}%

🛑 SL: {result['sl']}
🎯 TP1: {result['tp1']}
🎯 TP2: {result['tp2']}

🌍 {result['session']}
"""
    )

# ==========================
# 📩 CHAT
# ==========================
def on_chat(msg):
    if msg.get('text') == "/start":
        send_panel()

# ==========================
# 🔥 HANDLER
# ==========================
def handle(msg):

    if 'data' in msg:
        on_callback(msg)
    elif 'text' in msg:
        on_chat(msg)

# ==========================
# 🔄 LIVE LOOP
# ==========================
last_signal = {}

def live_loop():

    watchlist = ["BTCUSDT","ETHUSDT","BNBUSDT","PAXGUSDT"]

    while True:

        for coin in watchlist:

            result = ai_engine(coin)
            if not result:
                continue

            if result['confidence'] < 80:
                continue

            if last_signal.get(coin) == result['direction']:
                continue

            bot.sendMessage(CHAT_ID,
                f"🔥 SIGNAL\n{coin}\n{result['direction']} {result['confidence']}%"
            )

            last_signal[coin] = result['direction']
            time.sleep(2)

        time.sleep(30)

# ==========================
# 🚀 START SYSTEM
# ==========================
def start_system():

    Thread(target=run_web).start()
    MessageLoop(bot, handle).run_as_thread()
    Thread(target=live_loop).start()

    time.sleep(2)
    send_panel()

    print("🚀 ULTRA V10 RUNNING")

# ==========================
if __name__ == "__main__":
    start_system()
