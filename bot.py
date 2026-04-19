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
# 🌐 FLASK SERVER
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT IS RUNNING - OK"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ==========================
# 🤖 TELEGRAM SETUP
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

# حذف webhook
try:
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true"
    )
    print("🟢 Webhook cleared")
except Exception as e:
    print("Webhook error:", e)


# ==========================
# 🧠 SYSTEM STATE (SELF HEALING)
# ==========================
BOT_RUNNING = True
last_ping = time.time()
start_time = time.time()

last_signal = {}
last_event_hour = None

watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

session_state = {
    "ASIA": None,
    "LONDON": None,
    "NEW_YORK": None
}


# ==========================
# ⏱ TIME
# ==========================
def now():
    return datetime.now(timezone.utc)


# ==========================
# 🌍 MARKET SESSION
# ==========================
def session():
    h = now().hour
    if 0 <= h < 6:
        return "ASIA", 0.8
    elif 6 <= h < 12:
        return "LONDON", 1.2
    elif 12 <= h < 18:
        return "NEW YORK", 1.5
    return "QUIET", 0.6


def market_session():
    h = now().hour
    if 0 <= h < 6:
        return "ASIA"
    elif 6 <= h < 12:
        return "LONDON"
    elif 12 <= h < 20:
        return "NEW YORK"
    return "QUIET"


def market_power():
    sess = market_session()
    return {"NEW YORK": 1.5, "LONDON": 1.3, "ASIA": 1.0}.get(sess, 0.7)


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
# 📈 INDICATORS
# ==========================
def klines(symbol):
    try:
        d = requests.get(
            f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        ).json()
        return [float(x[4]) for x in d], [float(x[2]) for x in d], [float(x[3]) for x in d]
    except:
        return [], [], []


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
        tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
    return pd.Series(tr).rolling(14).mean().iloc[-1]


# ==========================
# 🧠 NEWS ENGINE
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0

        for e in feed.entries[:10]:
            t = e.title.lower()

            if any(w in t for w in ["rise", "bull", "pump"]):
                score += 1

            if any(w in t for w in ["fall", "crash", "dump"]):
                score -= 1

        if score >= 3:
            return "BULLISH", 1.2
        elif score <= -3:
            return "BEARISH", 0.7
        return "NEUTRAL", 1.0

    except:
        return "NO_NEWS", 1.0


# ==========================
# 📊 ANALYSIS ENGINE
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

    sess, w = session()
    mp = market_power()
    news, nw = news_engine()

    score = score * w * mp * nw

    if abs(score) < 6:
        return None

    direction = "🟢 BUY" if score > 0 else "🔴 SELL"

    sl = p - a * 1.5
    tp1 = p + a * 1.5 if score > 0 else p - a * 1.5
    tp2 = p + a * 2.5 if score > 0 else p - a * 2.5
    tp3 = p + a * 4 if score > 0 else p - a * 4

    conf = min(100, abs(score) * 6)

    return symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, mp


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
            [InlineKeyboardButton(text="📊 BNB", callback_data="BNBUSDT")],
            [InlineKeyboardButton(text="📊 SOL", callback_data="SOLUSDT")],
            [InlineKeyboardButton(text="🟡 PAXG", callback_data="PAXGUSDT")],

            [InlineKeyboardButton(text="⚡ MARKET", callback_data="MARKET")],
            [InlineKeyboardButton(text="🟢 BOT STATUS", callback_data="STATUS")],
            [InlineKeyboardButton(text="🔄 RESTART BOT", callback_data="RESTART")]
        ])

        bot.sendMessage(chat_id, "👑 LIVE AI CONTROL PANEL", reply_markup=keyboard)


# ==========================
# 🔥 CALLBACK HANDLER
# ==========================
def on_callback(msg):
    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    if data == "STATUS":
        uptime = int(time.time() - start_time)
        bot.sendMessage(chat_id,
            f"""🟢 BOT STATUS

⏱ Uptime: {uptime}s
🔥 Running: {BOT_RUNNING}
📡 Last Ping: {int(time.time() - last_ping)}s ago
""")
        return

    if data == "RESTART":
        bot.sendMessage(chat_id, "🔄 Restarting system...")
        Thread(target=start_bot).start()
        Thread(target=run).start()
        return

    if data == "MARKET":
        bot.sendMessage(chat_id, "📊 Market is active")
        return

    p = price(data)
    info = analyse(data)

    if not info:
        bot.sendMessage(chat_id, f"📊 {data}\n💰 {p}\n⚪ No signal")
        return

    symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, mp = info

    bot.sendMessage(chat_id,
        f"""📊 {symbol}
💰 {p}
🎯 {direction}
🔥 Score {score}
📊 Conf {conf}%

💼 Session {sess}
🌍 Power {mp}
"""
    )


# ==========================
# 🔁 HANDLE
# ==========================
def handle(msg):
    try:
        if 'data' in msg:
            on_callback(msg)
        elif 'text' in msg:
            on_chat(msg)
    except Exception as e:
        print("HANDLE ERROR:", e)


# ==========================
# ⚡ AI ENGINE
# ==========================
def run():
    global last_event_hour

    bot.sendMessage(ADMIN_CHAT_ID, "👑 AI LEVEL 2 STARTED")

    while True:
        try:
            time.sleep(5)
        except Exception as e:
            print("RUN ERROR:", e)


# ==========================
# 🟢 BOT START
# ==========================
def start_bot():
    print("🟢 BOT STARTED")

    MessageLoop(bot, {
        'chat': on_chat,
        'callback_query': on_callback
    }).run_as_thread()


# ==========================
# 🛡 AUTO HEAL WATCHDOG
# ==========================
def watchdog():
    global last_ping

    while True:
        time.sleep(10)

        if time.time() - last_ping > 60:
            print("🔴 BOT DEAD → RESTARTING")

            Thread(target=start_bot).start()
            Thread(target=run).start()

            last_ping = time.time()


# ==========================
# 🚀 START ALL SYSTEMS
# ==========================
if __name__ == "__main__":
    print("🟢 MAIN STARTED")

    Thread(target=run_web).start()
    Thread(target=start_bot).start()
    Thread(target=run).start()
    Thread(target=watchdog).start()
