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
# 🌐 Flask App (FIXED - بدون تكرار)
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT IS RUNNING"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


# ==========================
# 🚀 TELEGRAM SETUP
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

# 🔴 إزالة webhook
try:
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true"
    )
    print("🟢 Webhook deleted")
except Exception as e:
    print("Webhook error:", e)


# ==========================
# 📊 STATE
# ==========================
last_signal = {}
last_event_hour = None

watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

# FIX: كان خطأ عندك session_state
last_session_state = {
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
# 🌍 SESSIONS
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
# 🔔 EVENTS
# ==========================
def market_events():
    h = now().hour
    events = []

    if h == 23: events.append("🔔 افتتاح سيدني")
    if h == 8: events.append("🔕 إغلاق سيدني")
    if h == 1: events.append("🔔 افتتاح طوكيو")
    if h == 10: events.append("🔕 إغلاق طوكيو")
    if h == 10: events.append("🔔 افتتاح لندن")
    if h == 19: events.append("🔕 إغلاق لندن")
    if h == 15: events.append("🔔 افتتاح نيويورك")
    if h == 0: events.append("🔕 إغلاق نيويورك")

    return events


# ==========================
# 📈 PRICE
# ==========================
def price(symbol):
    try:
        return float(requests.get(
            f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        ).json()["price"])
    except:
        return None


# ==========================
# 📊 INDICATORS
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
# 🧠 NEWS
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/", request_timeout=5)
        score = 0

        for e in feed.entries[:10]:
            t = e.title.lower()

            if any(w in t for w in ["rise", "bull", "pump", "gain", "surge"]):
                score += 1

            if any(w in t for w in ["fall", "crash", "drop", "bear", "dump"]):
                score -= 1

        if score >= 3:
            return "BULLISH", 1.2
        elif score <= -3:
            return "BEARISH", 0.7
        return "NEUTRAL", 1.0

    except:
        return "NO_NEWS", 1.0


# ==========================
# 📊 ANALYSIS
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

    if score > 0:
        direction = "🟢 BUY"
        sl = p - a * 1.5
        tp1 = p + a * 1.5
        tp2 = p + a * 2.5
        tp3 = p + a * 4
    else:
        direction = "🔴 SELL"
        sl = p + a * 1.5
        tp1 = p - a * 1.5
        tp2 = p - a * 2.5
        tp3 = p - a * 4

    conf = min(100, abs(score) * 6)

    return symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, mp


# ==========================
# 📩 CHAT (لوحة الأزرار)
# ==========================
def on_chat(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 BTC", callback_data="BTCUSDT")],
            [InlineKeyboardButton(text="📊 ETH", callback_data="ETHUSDT")],
            [InlineKeyboardButton(text="📊 BNB", callback_data="BNBUSDT")],
            [InlineKeyboardButton(text="📊 SOL", callback_data="SOLUSDT")],
            [InlineKeyboardButton(text="🟡 PAXG", callback_data="PAXGUSDT")],
            [InlineKeyboardButton(text="⚡ حالة السوق", callback_data="MARKET")],
            [InlineKeyboardButton(text="👑 حالة البوت", callback_data="STATUS")]
        ])

        bot.sendMessage(chat_id, "👑 لوحة التحكم الاحترافية", reply_markup=keyboard)


# ==========================
# 🔥 CALLBACK (FIXED)
# ==========================
def on_callback(msg):
    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    p = price(data)

    if not p:
        bot.sendMessage(chat_id, "❌ لا يمكن جلب السعر")
        return

    info = analyse(data)

    if not info:
        bot.sendMessage(chat_id,
            f"📊 {data}\n💰 {round(p,2)}\n⚪ لا توجد إشارة قوية")
        return

    symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, mp = info

    bot.sendMessage(chat_id,
        f"""📊 {symbol}
💰 {round(p,2)}
🎯 {direction}
🔥 Score {round(score,2)}
📊 Conf {round(conf,2)}%
💼 Session {sess}
🌍 Power {mp}
"""
    )


# ==========================
# 🔁 HANDLE (FIXED)
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
# 🔥 LOOP (FIXED)
# ==========================
def run():
    bot.sendMessage(ADMIN_CHAT_ID, "👑 AI LEVEL 2 STARTED")

    while True:
        try:
            time.sleep(5)
        except Exception as e:
            print("RUN ERROR:", e)


# ==========================
# 🚀 START
# ==========================
def start_bot():
    MessageLoop(bot, {
        'chat': on_chat,
        'callback_query': on_callback
    }).run_as_thread()


def bot_supervisor():
    print("🟢 BOT SUPERVISOR STARTED")
    MessageLoop(bot, handle).run_as_thread()
    while True:
        time.sleep(10)


if __name__ == "__main__":
    print("🟢 MAIN STARTED")
    Thread(target=run_web).start()
    Thread(target=start_bot).start()
