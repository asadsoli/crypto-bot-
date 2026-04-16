import telepot
import requests
import time
import pandas as pd
import feedparser
from datetime import datetime, timezone
import os

# ==========================
# 🔥 KEEP ALIVE (RENDER FIX)
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
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

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

# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
last_signal = {}

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

    if abs(score) < 2:
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
def run():
    bot.sendMessage(ADMIN_CHAT_ID, "👑 BOT LIVE ON RENDER")

    while True:
        try:
            for s in watchlist:

                r = analyse(s)
                if not r:
                    continue

                symbol,p,direction,score,conf,sl,tp1,tp2,tp3,sess,news = r

                if conf < 40:
                    continue

                if last_signal.get(s) == direction:
                    continue

                msg = f"""
👑 MASTER BOT FINAL

📊 {symbol}
💰 Entry: {round(p,2)}

🎯 {direction}
🔥 Score: {round(score,2)}
🧠 Confidence: {round(conf,2)}%

💼 Session: {sess}
📰 News: {news}

🛑 SL: {round(sl,2)}
🎯 TP1: {round(tp1,2)}
🎯 TP2: {round(tp2,2)}
🎯 TP3: {round(tp3,2)}
"""

                bot.sendMessage(ADMIN_CHAT_ID, msg)

                last_signal[s] = direction
                time.sleep(2)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(60)

# ==========================
keep_alive()
run()
