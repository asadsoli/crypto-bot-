import os
import time
import requests
import pandas as pd
import feedparser
from datetime import datetime, timezone

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from flask import Flask
from threading import Thread

# ==========================
# 🌐 WEB SERVER (Render)
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT IS RUNNING - STABLE MODE"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ==========================
# 🤖 BOT SETUP
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

# remove webhook
try:
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true"
    )
except:
    pass


# ==========================
# 🧠 SYSTEM STATE (NO LOOP BUGS)
# ==========================
start_time = time.time()
last_ping = time.time()
ai_started = False

last_signal = {}

watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]


# ==========================
# ⏱ TIME
# ==========================
def now():
    return datetime.now(timezone.utc)


# ==========================
# 📊 PRICE
# ==========================
def price(symbol):
    try:
        return float(requests.get(
            f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        ).json()["price"])
    except:
        return None


# ==========================
# 📈 KLINES
# ==========================
def klines(symbol):
    try:
        d = requests.get(
            f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        ).json()
        return [float(x[4]) for x in d]
    except:
        return []


# ==========================
# 📊 SIMPLE ANALYSIS (STABLE)
# ==========================
def analyse(symbol):
    c = klines(symbol)
    p = price(symbol)

    if not p or len(c) < 50:
        return None

    ema20 = pd.Series(c).ewm(span=20).mean().iloc[-1]
    ema50 = pd.Series(c).ewm(span=50).mean().iloc[-1]

    trend = 1 if ema20 > ema50 else -1
    score = trend * 10

    if abs(score) < 6:
        return None

    direction = "🟢 BUY" if score > 0 else "🔴 SELL"

    return symbol, p, direction, score


# ==========================
# 📩 LIVE PANEL
# ==========================
def on_chat(msg):
    global last_ping
    last_ping = time.time()

    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 BTC", callback_data="BTCUSDT")],
            [InlineKeyboardButton(text="📊 ETH", callback_data="ETHUSDT")],
            [InlineKeyboardButton(text="⚡ STATUS", callback_data="STATUS")],
            [InlineKeyboardButton(text="🔄 RESTART", callback_data="RESTART")]
        ])

        bot.sendMessage(chat_id, "👑 LIVE CONTROL PANEL", reply_markup=keyboard)


# ==========================
# 🔥 CALLBACK
# ==========================
def on_callback(msg):
    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    if data == "STATUS":
        uptime = int(time.time() - start_time)

        bot.sendMessage(chat_id,
            f"""🟢 BOT STATUS

⏱ Uptime: {uptime}s
📡 Last Ping: {int(time.time() - last_ping)}s ago
🤖 AI Engine: ACTIVE
"""
        )
        return

    if data == "RESTART":
        bot.sendMessage(chat_id, "🔄 Manual restart done")
        Thread(target=start_bot).start()
        return

    p = price(data)
    info = analyse(data)

    if not info:
        bot.sendMessage(chat_id, f"📊 {data}\n💰 {p}\n⚪ No signal")
        return

    symbol, p, direction, score = info

    bot.sendMessage(chat_id,
        f"""📊 {symbol}
💰 {p}
🎯 {direction}
🔥 Score {score}
"""
    )


# ==========================
# 🔁 HANDLER (SINGLE ENTRY)
# ==========================
def handle(msg):
    try:
        if 'data' in msg:
            on_callback(msg)
        elif 'text' in msg:
            on_chat(msg)
    except Exception as e:
        print("ERROR:", e)


# ==========================
# ⚡ AI ENGINE (RUN ONCE ONLY)
# ==========================
def run():
    global ai_started

    if not ai_started:
        bot.sendMessage(ADMIN_CHAT_ID, "👑 AI LEVEL 2 STARTED")
        ai_started = True

    while True:
        try:
            time.sleep(10)

            # تحليل خفيف
            for s in watchlist:
                analyse(s)

        except Exception as e:
            print("RUN ERROR:", e)


# ==========================
# 🚀 BOT START (ONLY ONCE)
# ==========================
def start_bot():
    print("🟢 BOT STARTED")

    MessageLoop(bot, {
        'chat': on_chat,
        'callback_query': on_callback
    }).run_as_thread()


# ==========================
# 🚀 MAIN SYSTEM (ONE ENGINE ONLY)
# ==========================
if __name__ == "__main__":
    print("🟢 SYSTEM STARTED")

    Thread(target=run_web).start()
    Thread(target=start_bot).start()
    Thread(target=run).start()
