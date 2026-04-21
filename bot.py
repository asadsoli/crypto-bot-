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
    return "👑 ULTRA V10 BOT RUNNING"

@app.route('/healthz')
def healthz():
    return "OK", 200

def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()

# ==========================
# 🔑 TELEGRAM
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

# 🔥 حذف webhook (حل مشاكل النسخ القديمة)
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
except:
    pass

# ==========================
# 📊 STATE
# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

sent_signals = {}
last_event_hour = None
bot_enabled = True

session_state = {
    "ASIA": None,
    "LONDON": None,
    "NEW YORK": None
}

# ==========================
# ⏱ TIME
# ==========================
def now():
    return datetime.now(timezone.utc)

# ==========================
# 🌍 MARKET
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
# 📊 BINANCE
# ==========================
session = requests.Session()

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
    try:
        tr = []
        for i in range(1, len(c)):
            tr.append(max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])))
        return pd.Series(tr).rolling(14).mean().iloc[-1]
    except:
        return None

# ==========================
# 📰 NEWS
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0

        for e in feed.entries[:10]:
            t = e.title.lower()
            if "bull" in t or "rise" in t:
                score += 1
            if "bear" in t or "drop" in t:
                score -= 1

        if score >= 3:
            return "BULLISH", 1.3
        elif score <= -3:
            return "BEARISH", 0.7
        return "NEUTRAL", 1.0
    except:
        return "NO_NEWS", 1.0

# ==========================
# 🧠 ANALYSIS CORE (بدون حذف منطقك)
# ==========================
def analyse(symbol):
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

    score = (trend*2 + momentum*3)

    sess, w, mp = market_data()
    news, nw = news_engine()

    score = score * w * mp * nw

    if abs(score) < 6:
        return None

    direction = "🟢 BUY" if score > 0 else "🔴 SELL"

    sl = p - a if score > 0 else p + a
    tp1 = p + a if score > 0 else p - a
    tp2 = p + a*2 if score > 0 else p - a*2
    tp3 = p + a*3 if score > 0 else p - a*3

    conf = min(100, abs(score)*6)

    return symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, mp, news

# ==========================
# 📩 TELEGRAM UI
# ==========================
def on_chat(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text','')

    if text == "/start":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT")],
            [InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
            [InlineKeyboardButton(text="BNB", callback_data="BNBUSDT")],
            [InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")],
            [InlineKeyboardButton(text="PAXG", callback_data="PAXGUSDT")],
            [InlineKeyboardButton(text="ON/OFF BOT", callback_data="TOGGLE")]
        ])
        bot.sendMessage(chat_id, "👑 V10 CONTROL PANEL", reply_markup=kb)

# ==========================
# 🔥 CALLBACK FIXED (حل مشكلة handle)
# ==========================
def on_callback(msg):
    global bot_enabled

    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    if data == "TOGGLE":
        bot_enabled = not bot_enabled
        bot.sendMessage(chat_id, f"BOT {'🟢 ON' if bot_enabled else '🔴 OFF'}")
        return

    p = price(data)

    info = analyse(data)

    if not info:
        bot.sendMessage(chat_id, f"📊 {data}\n💰 {p}\n⚪ لا توجد إشارة")
        return

    sym, pr, direction, score, conf, sl, tp1, tp2, tp3, sess, mp, news = info

    bot.sendMessage(chat_id, f"""
📊 {sym}
💰 {round(pr,2)}

🎯 {direction}
🔥 Score {round(score,2)}
📊 Conf {round(conf,2)}%

💼 Session {sess}
🌍 Power {mp}
📰 {news}
""")

# ==========================
# 🔁 HANDLER (حل نهائي لمشكلة الكود القديم)
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
# 🚀 LOOPS
# ==========================
def signal_loop():
    global bot_enabled

    while True:
        if not bot_enabled:
            time.sleep(5)
            continue

        for s in watchlist:
            r = analyse(s)
            if not r:
                continue

            sym, pr, direction, score, conf, sl, tp1, tp2, tp3, sess, mp, news = r

            if "STRONG" in direction:
                bot.sendMessage(ADMIN_CHAT_ID, f"🚀 {sym} STRONG SIGNAL")

        time.sleep(30)

def event_loop():
    global last_event_hour
    while True:
        h = now().hour
        if h != last_event_hour:
            last_event_hour = h
            for e in market_events():
                bot.sendMessage(ADMIN_CHAT_ID, f"🌍 {e}")
        time.sleep(60)

def supervisor():
    MessageLoop(bot, handle).run_as_thread()
    while True:
        time.sleep(10)

# ==========================
# 🚀 START
# ==========================
if __name__ == "__main__":
    Thread(target=supervisor, daemon=True).start()
    Thread(target=signal_loop, daemon=True).start()
    Thread(target=event_loop, daemon=True).start()
