import telepot
import requests
import time
import pandas as pd
import feedparser
from datetime import datetime, timezone
import os

# ==========================
# 🔥 KEEP ALIVE
# ==========================
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "BOT IS RUNNING"

def run_web():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==========================
# 🔐 بيانات
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

# ==========================
# 🧠 حالة البوت
# ==========================
last_run_time = time.time()
last_signal_info = "لا يوجد"
last_session = None
last_signal = {}

# ==========================
# 📊 قائمة العملات (مع PAXG)
# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

# ==========================
# ⏱️ الوقت والجلسة
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
# 📡 API
# ==========================
def price(symbol):
    try:
        return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=10).json()["price"])
    except:
        return None

def klines(symbol):
    try:
        data = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100", timeout=10).json()
        closes = [float(x[4]) for x in data]
        highs = [float(x[2]) for x in data]
        lows = [float(x[3]) for x in data]
        return closes, highs, lows
    except:
        return [], [], []

def klines_tf(symbol, interval):
    try:
        data = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100", timeout=10).json()
        closes = [float(x[4]) for x in data]
        highs = [float(x[2]) for x in data]
        lows = [float(x[3]) for x in data]
        return closes, highs, lows
    except:
        return [], [], []

# ==========================
# 📐 مؤشرات
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
        tr.append(max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1])))
    return pd.Series(tr).rolling(14).mean().iloc[-1]

# ==========================
# 📊 أدوات التحليل
# ==========================
def liquidity(highs, lows):
    if len(highs) < 20:
        return None, None
    return max(highs[-20:]), min(lows[-20:])

def support_resistance(highs, lows):
    if len(highs) < 50:
        return None, None
    return max(highs[-50:]), min(lows[-50:])

def fvg(highs, lows):
    if len(highs) < 5:
        return 0
    gap_up = lows[-3] > highs[-1]
    gap_down = highs[-3] < lows[-1]
    return 2 if gap_up or gap_down else 0

def order_block(closes):
    if len(closes) < 3:
        return 0
    return 1 if abs(closes[-1] - closes[-2]) > abs(closes[-2] - closes[-3]) else 0

# ==========================
# 📰 الأخبار
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0
        for e in feed.entries[:10]:
            t = e.title.lower()
            if any(w in t for w in ["rise","bull","pump","gain"]):
                score += 1
            if any(w in t for w in ["fall","crash","drop","bear"]):
                score -= 1

        if score >= 3:
            return "BULLISH", 1.2
        elif score <= -3:
            return "BEARISH", 0.7
        return "NEUTRAL", 1.0
    except:
        return "NO_NEWS", 1.0

# ==========================
# 🧠 التحليل الأساسي (لم يتم تغييره)
# ==========================
def analyse(symbol):

    c,h,l = klines(symbol)
    p = price(symbol)

    if not p or len(c) < 60:
        return None

    ema20 = ema(c,20)
    ema50 = ema(c,50)
    r = rsi(c)
    a = atr(h,l,c)

    buy_liq, sell_liq = liquidity(h,l)

    score = 0
    score += 2 if ema20 > ema50 else -2
    score += 2 if r < 30 else -2 if r > 70 else 0
    score += 1 if buy_liq and p > buy_liq else -1 if sell_liq and p < sell_liq else 0

    score += fvg(h,l)
    score += order_block(c)

    c15,_,_ = klines_tf(symbol,"15m")
    if len(c15) > 50:
        score += 2 if ema(c15,20) > ema(c15,50) else -2

    c1h,_,_ = klines_tf(symbol,"1h")
    if len(c1h) > 50:
        score += 2 if ema(c1h,20) > ema(c1h,50) else -2

    res, sup = support_resistance(h,l)
    if res and p > res:
        score += 2
    elif sup and p < sup:
        score -= 2

    sess, w = session()
    score *= w

    news, nw = news_engine()
    score *= nw

    if abs(score) < 4:
        return None

    if score > 0:
        direction = "🟢 BUY"
        sl = p - a*1.5
        tp1 = p + a*1.5
        tp2 = p + a*2.5
        tp3 = p + a*4
    else:
        direction = "🔴 SELL"
        sl = p + a*1.5
        tp1 = p - a*1.5
        tp2 = p - a*2.5
        tp3 = p - a*4

    conf = min(100, abs(score)*15)

    return symbol,p,direction,score,conf,sl,tp1,tp2,tp3,sess,news

# ==========================
# 📊 فحص العملة
# ==========================
def coin_status(symbol):
    c,h,l = klines(symbol)
    p = price(symbol)

    if not p or len(c) < 50:
        return None

    ema20 = ema(c,20)
    ema50 = ema(c,50)
    r = rsi(c)
    a = atr(h,l,c)

    if a / p < 0.003:
        state = "هادئ 🟢"
    elif a / p < 0.01:
        state = "متوسط ⚡"
    else:
        state = "عنيف 🔥"

    trend = "صاعد 📈" if ema20 > ema50 else "هابط 📉"

    return symbol,p,trend,r,state

# ==========================
# 🚀 التشغيل
# ==========================
def run():
    global last_run_time, last_signal_info, last_session

    bot.sendMessage(ADMIN_CHAT_ID, "👑 تم تشغيل البوت على السيرفر بنجاح")

    while True:
        try:
            # جلسات السوق
            sess_now = market_session()
            if sess_now != last_session:
                last_session = sess_now
                bot.sendMessage(ADMIN_CHAT_ID, f"🌍 تغيير الجلسة: {sess_now}")

            for s in watchlist:

                last_run_time = time.time()

                r = analyse(s)
                if not r:
                    continue

                symbol,p,direction,score,conf,sl,tp1,tp2,tp3,sess,news = r

                if conf < 50:
                    continue

                if last_signal.get(s) == direction:
                    continue

                msg = f"""
👑 روبوت الإشارات الذكي

📊 الزوج: {symbol}
💰 سعر الدخول: {round(p, 2)}

🎯 الاتجاه: {direction}
🔥 قوة الإشارة: {round(score, 2)}
🧠 نسبة الثقة: {round(conf, 2)}%

💼 الجلسة: {sess}
📰 الأخبار: {news}

🛑 وقف الخسارة: {round(sl, 2)}
🎯 الهدف الأول: {round(tp1, 2)}
🎯 الهدف الثاني: {round(tp2, 2)}
🎯 الهدف الثالث: {round(tp3, 2)}
"""

                bot.sendMessage(ADMIN_CHAT_ID, msg)

                last_signal[s] = direction
                last_signal_info = f"{symbol} {direction}"

                time.sleep(2)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

        time.sleep(60)

# ==========================
# 🟢 تشغيل
# ==========================
keep_alive()

import threading
threading.Thread(target=run).start()
