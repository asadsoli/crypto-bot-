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
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
except:
    pass

# ==========================
last_signal = {}
last_signal_info = "لا يوجد"
last_event_hour = None

watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

# ==========================
def now():
    return datetime.now(timezone.utc)

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
    return {"NEW YORK":1.5,"LONDON":1.3,"ASIA":1.0}.get(sess,0.7)

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
def price(symbol):
    try:
        return float(requests.get(
            f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        ).json()["price"])
    except:
        return None

def klines(symbol):
    try:
        d = requests.get(
            f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        ).json()
        return [float(x[4]) for x in d],[float(x[2]) for x in d],[float(x[3]) for x in d]
    except:
        return [],[],[]

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
def market_event_bias():
    h = now().hour

    bias = 1.0

    if h in [10, 15, 16, 17]:
        bias = 1.2

    if h in [0, 8, 19]:
        bias = 0.8

    return bias

# ==========================
def ai_regime(score, atr_val):
    if atr_val is None:
        return "UNKNOWN"
    if atr_val > 1:
        return "VOLATILE"
    if abs(score) > 8:
        return "TRENDING"
    return "RANGING"

def ai_quality(score, conf):
    if conf >= 80 and abs(score) > 10:
        return "👑 FANNAN AI"
    if conf >= 65:
        return "⭐⭐⭐ STRONG"
    if conf >= 50:
        return "⭐⭐ MID"
    return "⭐ WEAK"

def fake_filter(score, regime):
    if regime == "RANGING" and abs(score) < 6:
        return True
    if regime == "VOLATILE" and abs(score) < 5:
        return True
    return False

# ==========================
def analyse(symbol):

    c,h,l = klines(symbol)
    p = price(symbol)

    if not p or len(c)<60:
        return None

    ema20=ema(c,20)
    ema50=ema(c,50)
    r=rsi(c)
    a=atr(h,l,c)

    score=0
    score+=2 if ema20>ema50 else -2
    score+=2 if r<30 else -2 if r>70 else 0

    sess,w=session()
    mp=market_power()
    me=market_event_bias()
    news, nw = news_engine()

    score*=w
    score*=mp
    score*=me
    score*=nw

    regime = ai_regime(score,a)

    if fake_filter(score,regime):
        return None

    if abs(score)<2:
        return None

    if score>0:
        direction="🟢 BUY"
        sl=p-a*1.5
        tp1=p+a*1.5
        tp2=p+a*2.5
        tp3=p+a*4
    else:
        direction="🔴 SELL"
        sl=p+a*1.5
        tp1=p-a*1.5
        tp2=p-a*2.5
        tp3=p-a*4

    conf=min(100,abs(score)*15)

    return symbol,p,direction,score,conf,sl,tp1,tp2,tp3,sess,mp

# ==========================
def on_chat(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text','')

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
def on_callback(msg):
    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    if data == "STATUS":
        bot.sendMessage(chat_id,
            f"👑 حالة البوت\n🟢 يعمل بشكل طبيعي\n📊 آخر إشارة: {last_signal_info}"
        )
        return

    if data == "MARKET":
        sess, _ = session()
        mp = market_power()

        bot.sendMessage(chat_id,
            f"🌍 السوق الآن\n💼 الجلسة: {sess}\n⚡ قوة السوق: {round(mp,2)}"
        )
        return

    info = analyse(data)

    if not info:
        bot.sendMessage(chat_id, "❌ لا توجد إشارة حالياً")
        return

    symbol,p,direction,score,conf,sl,tp1,tp2,tp3,sess,mp = info

    bot.sendMessage(chat_id,
        f"""👑 تحليل مباشر

📊 {symbol}
💰 السعر: {round(p,2)}

🎯 الاتجاه: {direction}
🔥 القوة: {round(score,2)}
🧠 الثقة: {round(conf,2)}%

💼 الجلسة: {sess}
🌍 قوة السوق: {round(mp,2)}

🛑 SL: {round(sl,2)}
🎯 TP1: {round(tp1,2)}
🎯 TP2: {round(tp2,2)}
🎯 TP3: {round(tp3,2)}
"""
    )

# ==========================
def handle(msg):
    try:
        # 🔥 callback (زر)
        if 'data' in msg:
            on_callback(msg)
            return

        # 🔥 رسالة عادية
        if 'text' in msg:
            on_chat(msg)
            return

    except Exception as e:
        print("HANDLE ERROR:", e)

# ==========================
def run():

    global last_event_hour

    bot.sendMessage(ADMIN_CHAT_ID,"👑 AI LEVEL 2 STARTED")

    while True:
        try:

            h=now().hour
            if h!=last_event_hour:
                last_event_hour=h
                for e in market_events():
                    bot.sendMessage(ADMIN_CHAT_ID,e)

            for s in watchlist:

                r=analyse(s)
                if not r:
                    continue

                symbol,p,direction,score,conf,sl,tp1,tp2,tp3,sess,mp = r

                if conf<40:
                    continue

                if last_signal.get(s)==direction:
                    continue

                msg=f"""
👑 AI LEVEL 2 BOT

📊 {symbol}
💰 {p}

🎯 {direction}
🔥 Score {score}
🧠 Conf {conf}%

💼 Session {sess}
🌍 Power {mp}

🛑 SL {sl}
🎯 TP1 {tp1}
🎯 TP2 {tp2}
🎯 TP3 {tp3}
"""

                bot.sendMessage(ADMIN_CHAT_ID,msg)

                last_signal[s]=direction
                time.sleep(2)

        except Exception as e:
            print("RUN ERROR:", e)
            time.sleep(3)

Thread(target=run).start()

# ==========================
def bot_supervisor():
    while True:
        try:
            print("🟢 STARTING BOT LOOP")

            MessageLoop(bot, handle).run_as_thread()

            while True:
                time.sleep(60)

        except Exception as e:
            print("🔴 BOT CRASH:", e)
            time.sleep(5)

Thread(target=bot_supervisor).start()
