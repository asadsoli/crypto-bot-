# ==========================
# 🔥 ULTRA V10 FINAL STABLE
# ==========================

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
# 🌐 WEB SERVER (RENDER FIX)
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "👑 ULTRA V10 RUNNING"

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
bot_enabled = True
last_signal = {}
last_event_hour = None

watchlist = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","PAXGUSDT"]

# ==========================
# ⏱ TIME
# ==========================
def now():
    return datetime.now(timezone.utc)

# ==========================
# 🌍 SESSION
# ==========================
def session():
    h = now().hour
    if 0 <= h < 6:
        return "ASIA", 1.0
    elif 6 <= h < 12:
        return "LONDON", 1.3
    elif 12 <= h < 20:
        return "NEW YORK", 1.5
    return "QUIET", 0.7

# ==========================
# 🔔 EVENTS
# ==========================
def market_events():
    h = now().hour
    events = {
        1: "🔔 Tokyo Open",
        10: "🔔 London Open",
        15: "🔔 New York Open",
        19: "🔕 London Close",
    }
    return [events[h]] if h in events else []

# ==========================
# 📊 DATA
# ==========================
def price(symbol):
    try:
        return float(requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol":symbol}, timeout=5).json()["price"])
    except:
        return None

def klines(symbol):
    try:
        d = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol":symbol,"interval":"5m","limit":100},
            timeout=5).json()

        c = [float(x[4]) for x in d]
        h = [float(x[2]) for x in d]
        l = [float(x[3]) for x in d]

        return c,h,l
    except:
        return [],[],[]

# ==========================
# 📊 INDICATORS
# ==========================
def ema(data,p):
    return pd.Series(data).ewm(span=p).mean().iloc[-1]

def rsi(data):
    s=pd.Series(data)
    d=s.diff()
    g=d.clip(lower=0).rolling(14).mean()
    l=(-d.clip(upper=0)).rolling(14).mean()
    rs=g.iloc[-1]/(l.iloc[-1]+1e-9)
    return 100-(100/(1+rs))

def atr(h,l,c):
    tr=[]
    for i in range(1,len(c)):
        tr.append(max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1])))
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
            if "bull" in t or "rise" in t: score+=1
            if "bear" in t or "drop" in t: score-=1

        if score >= 3:
            return "BULLISH",1.3
        elif score <= -3:
            return "BEARISH",0.7
        return "NEUTRAL",1.0
    except:
        return "NO_NEWS",1.0

# ==========================
# 🧠 ANALYSIS
# ==========================
def analyse(symbol):
    c,h,l = klines(symbol)
    p = price(symbol)

    if not p or len(c)<60:
        return None

    ema20 = ema(c,20)
    ema50 = ema(c,50)
    r = rsi(c)
    a = atr(h,l,c)

    trend = 1 if ema20>ema50 else -1
    momentum = 1 if r<40 else (-1 if r>60 else 0)

    sess, power = session()
    news, nw = news_engine()

    score = (trend*2 + momentum*3) * power * nw

    if abs(score)<2:
        state="⚪ QUIET"
    elif abs(score)<4:
        state="🟡 WEAK"
    elif abs(score)<6:
        state="🟢 BUY" if score>0 else "🔴 SELL"
    else:
        state="🔥 STRONG BUY" if score>0 else "💥 STRONG SELL"

    direction = "BUY" if score>0 else "SELL"

    sl = p-a if score>0 else p+a
    tp1 = p+a if score>0 else p-a
    tp2 = p+a*2 if score>0 else p-a*2
    tp3 = p+a*3 if score>0 else p-a*3

    return symbol,p,state,direction,score,sl,tp1,tp2,tp3,sess,news

# ==========================
# 🚀 SIGNAL LOOP
# ==========================
def signal_loop():
    global bot_enabled

    while True:
        if not bot_enabled:
            time.sleep(5)
            continue

        for s in watchlist:

            info = analyse(s)
            if not info:
                continue

            sym,pr,state,dr,sc,sl,t1,t2,t3,sess,news = info

            if "STRONG" not in state:
                continue

            key = f"{sym}_{state}"

            if key in last_signal and time.time()-last_signal[key]<600:
                continue

            last_signal[key]=time.time()

            bot.sendMessage(ADMIN_CHAT_ID,f"""
🚀 {sym}
💰 {round(pr,2)}

🔥 {state}
🌍 {sess}
📰 {news}

🛑 SL {round(sl,2)}
🎯 TP1 {round(t1,2)}
🎯 TP2 {round(t2,2)}
🎯 TP3 {round(t3,2)}
""")

        time.sleep(30)

# ==========================
# 📩 TELEGRAM
# ==========================
def handle(msg):
    global bot_enabled

    try:
        if 'data' in msg:
            _,chat_id,data = telepot.glance(msg,flavor='callback_query')

            if data=="TOGGLE":
                bot_enabled = not bot_enabled
                bot.sendMessage(chat_id,f"BOT {'ON 🟢' if bot_enabled else 'OFF 🔴'}")
                return

            p = price(data)
            info = analyse(data)

            if not info:
                bot.sendMessage(chat_id,f"{data} ⚪ {round(p,2) if p else '?'}")
                return

            sym,pr,state,dr,sc,sl,t1,t2,t3,sess,news = info

            bot.sendMessage(chat_id,f"""
📊 {sym}
💰 {round(pr,2)}

🔥 {state}
🌍 {sess}
📰 {news}
""")

        elif 'text' in msg:
            chat_id = msg['chat']['id']

            if msg['text']=="/start":
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="BTC",callback_data="BTCUSDT"),
                     InlineKeyboardButton(text="ETH",callback_data="ETHUSDT")],
                    [InlineKeyboardButton(text="BNB",callback_data="BNBUSDT"),
                     InlineKeyboardButton(text="SOL",callback_data="SOLUSDT")],
                    [InlineKeyboardButton(text="PAXG",callback_data="PAXGUSDT")],
                    [InlineKeyboardButton(text="ON/OFF BOT",callback_data="TOGGLE")]
                ])

                bot.sendMessage(chat_id,"👑 ULTRA V10 CONTROL",reply_markup=kb)

    except Exception as e:
        print("ERROR:",e)

# ==========================
# 💚 HEARTBEAT
# ==========================
def heartbeat():
    while True:
        print("💚 RUNNING")
        time.sleep(30)

# ==========================
# 🚀 START
# ==========================
if __name__=="__main__":
    Thread(target=run_web).start()
    MessageLoop(bot,handle).run_as_thread()
    Thread(target=signal_loop).start()
    Thread(target=heartbeat).start()

    while True:
        time.sleep(10)
