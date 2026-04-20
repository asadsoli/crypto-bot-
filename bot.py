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
# 🌐 FLASK (KEEP RENDER ALIVE)
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

# حذف webhook
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
except:
    pass

# ==========================
# 📊 STATE
# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]
last_signal = {}

# ==========================
# ⏱ TIME
# ==========================
def now():
    return datetime.now(timezone.utc)

# ==========================
# 🌍 SESSIONS + POWER
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
# 🔔 EVENTS
# ==========================
def market_events():
    h = now().hour
    events = []

    mapping = {
        23: "🔔 Sydney Open",
        1: "🔔 Tokyo Open",
        10: "🔔 London Open",
        15: "🔔 New York Open",
        8: "🔕 Sydney Close",
        10: "🔕 Tokyo Close",
        19: "🔕 London Close",
        0: "🔕 New York Close"
    }

    if h in mapping:
        events.append(mapping[h])

    return events

# ==========================
# 📈 BINANCE API (FIXED)
# ==========================
def price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        return float(requests.get(url, timeout=5).json()["price"])
    except:
        return None

def klines(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        d = requests.get(url, timeout=5).json()

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
        tr.append(max(
            h[i] - l[i],
            abs(h[i] - c[i-1]),
            abs(l[i] - c[i-1])
        ))
    return pd.Series(tr).rolling(14).mean().iloc[-1]

# ==========================
# 💧 LIQUIDITY
# ==========================
def liquidity(h, l):
    if len(h) < 20:
        return None, None
    return max(h[-20:]), min(l[-20:])

# ==========================
# ⚡ VOLUME AI
# ==========================
def volume_factor(v):
    if len(v) < 20:
        return 1.0
    avg = sum(v[-20:-1]) / 19
    return 1.3 if v[-1] > avg * 1.5 else 1.0

# ==========================
# 📰 NEWS ENGINE
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0

        for e in feed.entries[:10]:
            t = e.title.lower()
            if any(w in t for w in ["bull", "pump", "rise", "gain"]):
                score += 1
            if any(w in t for w in ["crash", "drop", "bear", "hack"]):
                score -= 1

        if score >= 3:
            return "BULLISH", 1.2
        elif score <= -3:
            return "BEARISH", 0.7
        return "NEUTRAL", 1.0
    except:
        return "NO_NEWS", 1.0

# ==========================
# 🧠 ANALYSIS CORE
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

    buy_liq, sell_liq = liquidity(h, l)

    trend = 1 if ema20 > ema50 else -1
    momentum = 1 if r < 35 else (-1 if r > 65 else 0)

    score = (trend * 2) + (momentum * 3)

    # liquidity boost
    if buy_liq and p > buy_liq:
        score += 1
    if sell_liq and p < sell_liq:
        score -= 1

    # factors
    session_name, mp, w = market_data()
    news, nw = news_engine()
    vf = volume_factor(v)

    final_score = score * mp * w * nw * vf

    if abs(final_score) < 6:
        return None

    direction = "🟢 BUY" if final_score > 0 else "🔴 SELL"

    mult = 1.5 if final_score > 0 else -1.5

    sl = p - (a * mult)
    tp1 = p + (a * mult)
    tp2 = p + (a * mult * 1.6)
    tp3 = p + (a * mult * 2.6)

    conf = min(100, abs(final_score) * 6)

    return symbol, p, direction, final_score, conf, sl, tp1, tp2, tp3, session_name, vf

# ==========================
# 📩 TELEGRAM UI
# ==========================
def handle(msg):

    try:
        if 'data' in msg:
            qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

            if data == "MARKET":
                sess, mp, _ = market_data()
                ev = "\n".join(market_events()) or "No events"
                bot.sendMessage(chat_id, f"🌍 {sess}\nPower: {mp}\n{ev}")
                return

            info = analyse(data)

            if not info:
                bot.sendMessage(chat_id, f"{data} ⚪ No signal")
                return

            sym, pr, dr, sc, cf, sl, t1, t2, t3, sess, vf = info

            bot.sendMessage(chat_id, f"""
📊 {sym}
💰 {round(pr,2)}

🎯 {dr}
🔥 Score: {round(sc,2)}
🧠 {cf}%

💼 {sess}
📈 Volume x{vf}

🛑 SL: {round(sl,2)}
🎯 TP1: {round(t1,2)}
🎯 TP2: {round(t2,2)}
🎯 TP3: {round(t3,2)}
""")

        elif 'text' in msg:
            chat_id = msg['chat']['id']

            if msg.get('text') == "/start":
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT"),
                     InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
                    [InlineKeyboardButton(text="BNB", callback_data="BNBUSDT"),
                     InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")],
                    [InlineKeyboardButton(text="PAXG", callback_data="PAXGUSDT")],
                    [InlineKeyboardButton(text="Market", callback_data="MARKET")]
                ])

                bot.sendMessage(chat_id, "👑 ULTRA AI CONTROL", reply_markup=keyboard)

    except Exception as e:
        print("ERROR:", e)

# ==========================
# 🚀 START
# ==========================
if __name__ == "__main__":

    Thread(target=run_web).start()

    MessageLoop(bot, handle).run_as_thread()

    bot.sendMessage(ADMIN_CHAT_ID, "👑 ULTRA AI BOT STARTED")

    while True:
        time.sleep(10)
