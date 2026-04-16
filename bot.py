import telepot
import requests
import time
import pandas as pd
import feedparser
from datetime import datetime, timezone
import os

from flask import Flask
from threading import Thread

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================
# 🔥 KEEP ALIVE
# ==========================
app = Flask('')

@app.route('/')
def home():
    return "BOT IS RUNNING"

def run_web():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run_web).start()

# ==========================
# 🔐 بيانات
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
except:
    pass

# ==========================
# 🧠 حالة
# ==========================
last_signal = {}
last_session = None
last_event_hour = None

# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

# ==========================
# ⏱️ الوقت
# ==========================
def now():
    return datetime.now(timezone.utc)

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

# ==========================
# 🌍 قوة السوق (PRO)
# ==========================
def market_power():
    sess = market_session()

    if sess == "NEW YORK":
        return 1.5
    elif sess == "LONDON":
        return 1.3
    elif sess == "ASIA":
        return 1.0
    return 0.7

# ==========================
# 🌍 أحداث الأسواق
# ==========================
def market_events():
    h = now().hour
    events = []

    if h == 23:
        events.append("🔔 افتتاح سوق سيدني")
    if h == 8:
        events.append("🔕 إغلاق سوق سيدني")

    if h == 1:
        events.append("🔔 افتتاح سوق طوكيو")
    if h == 10:
        events.append("🔕 إغلاق سوق طوكيو")

    if h == 10:
        events.append("🔔 افتتاح سوق لندن")
    if h == 19:
        events.append("🔕 إغلاق سوق لندن")

    if h == 15:
        events.append("🔔 افتتاح سوق نيويورك")
    if h == 0:
        events.append("🔕 إغلاق سوق نيويورك")

    return events

# ==========================
# 📡 API
# ==========================
def price(symbol):
    try:
        return float(requests.get(
            f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        ).json()["price"])
    except:
        return None

def klines(symbol):
    try:
        data = requests.get(
            f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        ).json()

        return (
            [float(x[4]) for x in data],
            [float(x[2]) for x in data],
            [float(x[3]) for x in data],
        )
    except:
        return [], [], []

# ==========================
# 📊 مؤشرات
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

def atr(high, low, close):
    tr = []
    for i in range(1, len(close)):
        tr.append(max(
            high[i]-low[i],
            abs(high[i]-close[i-1]),
            abs(low[i]-close[i-1])
        ))
    return pd.Series(tr).rolling(14).mean().iloc[-1]

# ==========================
# 📊 تحليل (بدون تغيير منطقي)
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

    score = 0
    score += 2 if ema20 > ema50 else -2
    score += 2 if r < 30 else -2 if r > 70 else 0

    sess, w = session()
    mp = market_power()

    score *= w
    score *= mp

    if abs(score) < 4:
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

    conf = min(100, abs(score) * 15)

    return symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, mp

# ==========================
# 🎛 لوحة
# ==========================
def on_chat(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text','')

    if text == "/start":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT")],
            [InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
            [InlineKeyboardButton(text="BNB", callback_data="BNBUSDT")],
            [InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")],
            [InlineKeyboardButton(text="PAXG", callback_data="PAXGUSDT")],
            [InlineKeyboardButton(text="STATUS", callback_data="STATUS")]
        ])

        bot.sendMessage(chat_id, "👑 لوحة البوت", reply_markup=keyboard)

def on_callback(msg):
    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    if data == "STATUS":
        bot.sendMessage(chat_id, "🟢 البوت يعمل")
        return

# ==========================
MessageLoop(bot, {
    'chat': on_chat,
    'callback_query': on_callback
}).run_as_thread()

# ==========================
# 🚀 تشغيل
# ==========================
def run():
    bot.sendMessage(ADMIN_CHAT_ID, "👑 BOT STARTED PRO VERSION")

    while True:
        try:

            events = market_events()
            for e in events:
                bot.sendMessage(ADMIN_CHAT_ID, e)

            for s in watchlist:

                r = analyse(s)
                if not r:
                    continue

                symbol,p,direction,score,conf,sl,tp1,tp2,tp3,sess,mp = r

                if conf < 50:
                    continue

                if last_signal.get(s) == direction:
                    continue

                msg = f"""
👑 روبوت برو

📊 {symbol}
💰 {p}

🎯 {direction}
🔥 {score}
🧠 {conf}%

💼 الجلسة: {sess}
🌍 قوة السوق: {round(mp,2)}

🛑 SL {sl}
🎯 TP1 {tp1}
🎯 TP2 {tp2}
🎯 TP3 {tp3}
"""

                bot.sendMessage(ADMIN_CHAT_ID, msg)

                last_signal[s] = direction

                time.sleep(2)

        except Exception as e:
            print(e)

        time.sleep(60)

Thread(target=run).start()
