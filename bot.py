import os
import time
import requests
import pandas as pd
import feedparser
from datetime import datetime
from threading import Thread

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from flask import Flask

# ==========================
# 🌐 FLASK (RENDER FIX)
# ==========================
app = Flask(__name__)

@app.route("/")
def home():
    return "ULTRA V10 RUNNING 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ==========================
# 🔐 BOT CONFIG
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telepot.Bot(BOT_TOKEN)

# ==========================
# 🧠 CORE WATCHLIST
# ==========================
CORE_WATCHLIST = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "PAXGUSDT"]

# ==========================
# 🌍 MARKET SESSION
# ==========================
def get_hour():
    return datetime.utcnow().hour

def get_session():
    h = get_hour()

    if 0 <= h < 7:
        return "ASIA", 0.8
    elif 7 <= h < 12:
        return "LONDON", 1.2
    elif 12 <= h < 22:
        return "NEW YORK", 1.5
    return "QUIET", 0.6

# ==========================
# 📊 PRICE
# ==========================
def price(symbol):
    try:
        return float(requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol}
        ).json()["price"])
    except:
        return None

# ==========================
# 📈 AI ENGINE (SIMPLE CORE)
# ==========================
def ai_engine(symbol):

    p = price(symbol)
    if not p:
        return None

    # fake scoring (placeholder AI logic)
    score = (hash(symbol) % 10) - 5

    session, power = get_session()

    final_score = score * power

    if abs(final_score) < 3:
        return None

    direction = "🟢 BUY" if final_score > 0 else "🔴 SELL"

    confidence = min(100, abs(final_score) * 10)

    return {
        "symbol": symbol,
        "price": p,
        "score": final_score,
        "direction": direction,
        "confidence": confidence,
        "session": session,
        "power": power
    }

# ==========================
# 🔥 SMART SCANNER
# ==========================
def scan_best():

    results = []

    for coin in CORE_WATCHLIST:

        data = ai_engine(coin)

        if data:
            results.append(data)

    results = sorted(results, key=lambda x: x["confidence"], reverse=True)

    return results[:2]

# ==========================
# 📊 MARKET OPEN / CLOSE
# ==========================
last_state = {}

def market_events():

    h = get_hour()
    events = []

    markets = {
        "LONDON": 7,
        "NEW YORK": 12,
        "ASIA": 0
    }

    for m, hour in markets.items():

        if h == hour and last_state.get(m) != "OPEN":
            bot.sendMessage(CHAT_ID, f"🔔 افتتاح {m}")
            last_state[m] = "OPEN"

        if h == (hour + 8) % 24 and last_state.get(m) != "CLOSED":
            bot.sendMessage(CHAT_ID, f"🔕 إغلاق {m}")
            last_state[m] = "CLOSED"

# ==========================
# 📱 PANEL
# ==========================
def send_panel():

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("📊 BTC", callback_data="BTCUSDT"),
            InlineKeyboardButton("⚡ ETH", callback_data="ETHUSDT")
        ],
        [
            InlineKeyboardButton("🏆 RANK", callback_data="RANK"),
            InlineKeyboardButton("🧠 STATUS", callback_data="STATUS")
        ]
    ])

    bot.sendMessage(CHAT_ID,
        "🚀 ULTRA V10 PANEL\n🧠 ACTIVE\n📡 LIVE",
        reply_markup=keyboard
    )

# ==========================
# 📩 CALLBACK
# ==========================
def on_callback(msg):

    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    if data == "STATUS":
        bot.sendMessage(chat_id, "🧠 BOT RUNNING OK")

    elif data == "RANK":
        bot.sendMessage(chat_id, "🏆 SYSTEM RANKING ACTIVE")

    else:
        result = ai_engine(data)

        if not result:
            bot.sendMessage(chat_id, f"{data}\n⚪ NO SIGNAL")
            return

        bot.sendMessage(chat_id,
            f"""
📊 {result['symbol']}
💰 {result['price']}
🎯 {result['direction']}
🔥 {result['confidence']}%

🌍 {result['session']}
⚡ {result['power']}
"""
        )

# ==========================
# 📩 CHAT
# ==========================
def on_chat(msg):

    text = msg.get("text", "")

    if text == "/start":
        send_panel()

# ==========================
# 🔥 HANDLER
# ==========================
def handle(msg):

    if 'data' in msg:
        on_callback(msg)
    else:
        on_chat(msg)

# ==========================
# 🔄 LIVE LOOP
# ==========================
def live_loop():

    while True:

        market_events()

        best = scan_best()

        for s in best:

            if s["confidence"] > 70:

                bot.sendMessage(CHAT_ID,
                    f"""
🔥 BEST SIGNAL

📊 {s['symbol']}
🎯 {s['direction']}
🔥 {s['confidence']}%
🌍 {s['session']}
"""
                )

        time.sleep(30)

# ==========================
# 🚀 START SYSTEM
# ==========================
def start_system():

    print("🚀 ULTRA V10 RUNNING")

    send_panel()

    MessageLoop(bot, handle).run_as_thread()

    Thread(target=run_web).start()
    Thread(target=live_loop).start()

    while True:
        time.sleep(10)


if __name__ == "__main__":
    start_system()
