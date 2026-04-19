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
# 🌐 Flask App (لإبقاء الريندر يعمل)
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
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = telepot.Bot(TOKEN)

# إزالة الـ Webhook لضمان عمل الـ Polling
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
    print("🟢 Webhook deleted")
except Exception as e:
    print("Webhook error:", e)

# ==========================
# 📊 STATE & WATCHLIST
# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]

# ==========================
# 🌍 MARKET LOGIC (SESSIONS & EVENTS)
# ==========================
def now():
    return datetime.now(timezone.utc)

def get_market_data():
    h = now().hour
    if 0 <= h < 6:
        return "ASIA", 1.0, 0.8
    elif 6 <= h < 12:
        return "LONDON", 1.3, 1.2
    elif 12 <= h < 20:
        return "NEW YORK", 1.5, 1.5
    return "QUIET", 0.7, 0.6

def market_events():
    h = now().hour
    events = []
    event_map = {
        23: "🔔 افتتاح سيدني", 8: "🔕 إغلاق سيدني",
        1: "🔔 افتتاح طوكيو", 10: "🔕 إغلاق طوكيو/لندن",
        19: "🔕 إغلاق لندن", 15: "🔔 افتتاح نيويورك", 0: "🔕 إغلاق نيويورك"
    }
    if h in event_map:
        events.append(event_map[h])
    return events

# ==========================
# 📈 TECHNICAL ANALYSIS
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
        return c, h, l
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

def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/", request_timeout=5)
        score = 0
        for e in feed.entries[:10]:  
            t = e.title.lower()  
            if any(w in t for w in ["rise", "bull", "pump", "gain", "surge"]): score += 1  
            if any(w in t for w in ["fall", "crash", "drop", "bear", "dump"]): score -= 1  
        
        if score >= 3: return "BULLISH", 1.2  
        elif score <= -3: return "BEARISH", 0.7  
        return "NEUTRAL", 1.0  
    except:  
        return "NO_NEWS", 1.0

def analyse(symbol):
    c, h, l = klines(symbol)
    p = price(symbol)
    if not p or len(c) < 60: return None  

    ema20, ema50 = ema(c, 20), ema(c, 50)
    r, a = rsi(c), atr(h, l, c)
    
    trend = 1 if ema20 > ema50 else -1
    momentum = 1 if r < 30 else (-1 if r > 70 else 0)
    
    score = (trend * 2) + (momentum * 3)
    sess_name, mp, w = get_market_data()
    news_label, nw = news_engine()
    
    score = score * w * mp * nw
    if abs(score) < 6: return None  

    direction = "🟢 BUY" if score > 0 else "🔴 SELL"
    mult = 1.5 if score > 0 else -1.5
    sl = p - (a * mult)
    tp1, tp2, tp3 = p + (a * mult), p + (a * mult * 1.6), p + (a * mult * 2.6)
    conf = min(100, abs(score) * 6)

    return symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess_name, mp

# ==========================
# 📩 TELEGRAM HANDLERS
# ==========================
def handle(msg):
    # التعامل مع الضغط على الأزرار
    if 'data' in msg:
        qid, chat_id, data = telepot.glance(msg, flavor='callback_query')
        
        if data == "MARKET":
            sess, mp, _ = get_market_data()
            ev = "\n".join(market_events()) or "لا توجد أحداث حالياً"
            bot.sendMessage(chat_id, f"🌍 حالة السوق:\nالفترة: {sess}\nالقوة: {mp}\nالأحداث:\n{ev}")
            return

        if data == "STATUS":
            bot.sendMessage(chat_id, "👑 البوت يعمل بكفاءة عالية")
            return

        p_current = price(data)
        if not p_current:
            bot.sendMessage(chat_id, "❌ فشل جلب البيانات")
            return

        info = analyse(data)
        if not info:
            bot.sendMessage(chat_id, f"📊 {data}\n💰 {round(p_current,2)}\n⚪ الانتظار.. لا توجد إشارة قوية")
        else:
            sym, pr, dr, sc, cf, sl, t1, t2, t3, ss, m_p = info
            bot.sendMessage(chat_id, f"📊 {sym}\n💰 {round(pr,2)}\n🎯 {dr}\n🔥 Score: {round(sc,2)}\n📊 Conf: {round(cf,2)}%\n💼 Session: {ss}\n🌍 Power: {m_p}")

    # التعامل مع الرسائل النصية
    elif 'text' in msg:
        chat_id = msg['chat']['id']
        text = msg.get('text', '')

        if text == "/start":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 BTC", callback_data="BTCUSDT"), InlineKeyboardButton(text="📊 ETH", callback_data="ETHUSDT")],
                [InlineKeyboardButton(text="📊 BNB", callback_data="BNBUSDT"), InlineKeyboardButton(text="📊 SOL", callback_data="SOLUSDT")],
                [InlineKeyboardButton(text="🟡 PAXG", callback_data="PAXGUSDT")],
                [InlineKeyboardButton(text="⚡ حالة السوق", callback_data="MARKET"), InlineKeyboardButton(text="👑 حالة البوت", callback_data="STATUS")]
            ])
            bot.sendMessage(chat_id, "👑 لوحة التحكم الاحترافية لـ AI Signals", reply_markup=keyboard)

# ==========================
# 🚀 MAIN START
# ==========================
if __name__ == "__main__":
    print("🟢 STARTING BOT SYSTEM...")
    
    # تشغيل Flask في خيط منفصل
    Thread(target=run_web).start()
    
    # تشغيل البوت
    try:
        if ADMIN_CHAT_ID:
            bot.sendMessage(ADMIN_CHAT_ID, "👑 AI LEVEL 2 STARTED ON RENDER")
        
        MessageLoop(bot, handle).run_as_thread()
        print("🟢 BOT IS LIVE")
        
        while True:
            time.sleep(10)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
    
