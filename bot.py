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
# 🌐 Flask App
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT IS RUNNING WITH VOLUME AI"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ==========================
# 🚀 TELEGRAM SETUP
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
bot = telepot.Bot(TOKEN)

try:
    requests.get(f"https://telegram.org{TOKEN}/deleteWebhook?drop_pending_updates=true")
    print("🟢 Webhook deleted")
except Exception as e:
    print("Webhook error:", e)

# ==========================
# 📊 TECHNICAL ANALYSIS + VOLUME
# ==========================
def get_market_data():
    h = datetime.now(timezone.utc).hour
    if 0 <= h < 6: return "ASIA", 1.0, 0.8
    elif 6 <= h < 12: return "LONDON", 1.3, 1.2
    elif 12 <= h < 20: return "NEW YORK", 1.5, 1.5
    return "QUIET", 0.7, 0.6

def price(symbol):
    try:
        url = f"https://binance.com{symbol}"
        return float(requests.get(url, timeout=5).json()["price"])
    except: return None

def klines(symbol):
    try:
        url = f"https://binance.com{symbol}&interval=5m&limit=100"
        d = requests.get(url, timeout=5).json()
        c = [float(x[4]) for x in d] # Close
        h = [float(x[2]) for x in d] # High
        l = [float(x[3]) for x in d] # Low
        v = [float(x[5]) for x in d] # Volume (إضافة حجم التداول)
        return c, h, l, v
    except: return [], [], [], []

# --- إضافة تحليل أحجام التداول ---
def volume_analysis(v_data):
    if len(v_data) < 20: return 1.0
    current_v = v_data[-1]
    avg_v = sum(v_data[-20:-1]) / 19
    # إذا كان الحجم الحالي أكبر من المتوسط بـ 50%، فهذا يعني دخول سيولة قوية
    if current_v > avg_v * 1.5:
        return 1.3 # تقوية الإشارة بنسبة 30%
    return 1.0

def ema(data, p): return pd.Series(data).ewm(span=p).mean().iloc[-1]
def rsi(data):
    s = pd.Series(data)
    d = s.diff()
    g = d.clip(lower=0).rolling(14).mean()
    l = (-d.clip(upper=0)).rolling(14).mean()
    return 100 - (100 / (1 + (g.iloc[-1] / (l.iloc[-1] + 1e-9))))

def atr(h, l, c):
    tr = [max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])) for i in range(1, len(c))]
    return pd.Series(tr).rolling(14).mean().iloc[-1]

def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com", request_timeout=5)
        score = 0
        for e in feed.entries[:10]:
            t = e.title.lower()
            if any(w in t for w in ["rise", "bull", "pump", "gain", "surge"]): score += 1
            if any(w in t for w in ["fall", "crash", "drop", "bear", "dump"]): score -= 1
        return ("BULLISH", 1.2) if score >= 3 else (("BEARISH", 0.7) if score <= -3 else ("NEUTRAL", 1.0))
    except: return "NO_NEWS", 1.0

def analyse(symbol):
    c, h, l, v = klines(symbol)
    p = price(symbol)
    if not p or len(c) < 60: return None

    ema20, ema50 = ema(c, 20), ema(c, 50)
    r, a = rsi(c), atr(h, l, c)
    
    trend = 1 if ema20 > ema50 else -1
    momentum = 1 if r < 35 else (-1 if r > 65 else 0) # تحسين مستويات الـ RSI
    
    # دمج أحجام التداول في الحساب
    vol_factor = volume_analysis(v)
    
    score = (trend * 2) + (momentum * 3)
    sess_name, mp, w = get_market_data()
    news_label, nw = news_engine()
    
    # النتيجة النهائية مع كل العوامل
    final_score = score * w * mp * nw * vol_factor
    
    if abs(final_score) < 6: return None

    direction = "🟢 BUY" if final_score > 0 else "🔴 SELL"
    mult = 1.5 if final_score > 0 else -1.5
    sl = p - (a * mult)
    tp1, tp2 = p + (a * mult), p + (a * mult * 2)
    conf = min(100, abs(final_score) * 6)

    return symbol, p, direction, final_score, conf, sl, tp1, tp2, sess_name, vol_factor

# ==========================
# 📩 TELEGRAM HANDLERS
# ==========================
def handle(msg):
    if 'data' in msg:
        qid, chat_id, data = telepot.glance(msg, flavor='callback_query')
        
        if data in ["MARKET", "STATUS"]:
            bot.sendMessage(chat_id, "⚙️ يتم جلب البيانات المحدثة...")
            return

        info = analyse(data)
        if not info:
            bot.sendMessage(chat_id, f"📊 {data}\n💰 {price(data)}\n⚪ السيولة أو المؤشرات لا تدعم دخول صفقة الآن.")
        else:
            sym, pr, dr, sc, cf, sl, t1, t2, ss, vf = info
            vol_status = "🔥 سيولة عالية" if vf > 1.0 else "💎 سيولة عادية"
            bot.sendMessage(chat_id, f"📊 {sym}\n💰 {round(pr,2)}\n🎯 {dr}\n\n💡 القوة: {round(sc,2)}\n🛡️ الثقة: {round(cf,1)}%\n💼 الجلسة: {ss}\n📈 {vol_status}\n\n🛑 SL: {round(sl,2)}\n✅ TP1: {round(t1,2)}")

    elif 'text' in msg:
        chat_id = msg['chat']['id']
        if msg.get('text') == "/start":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 BTC", callback_data="BTCUSDT"), InlineKeyboardButton(text="📊 ETH", callback_data="ETHUSDT")],
                [InlineKeyboardButton(text="📊 SOL", callback_data="SOLUSDT"), InlineKeyboardButton(text="🟡 PAXG", callback_data="PAXGUSDT")],
                [InlineKeyboardButton(text="⚡ حالة السوق", callback_data="MARKET")]
            ])
            bot.sendMessage(chat_id, "🤖 AI Trader (Volume v2)\nاضغط على العملة لتحليلها الآن:", reply_markup=keyboard)

# ==========================
# 🚀 RUN
# ==========================
if __name__ == "__main__":
    Thread(target=run_web).start()
    if ADMIN_CHAT_ID: bot.sendMessage(ADMIN_CHAT_ID, "🟢 BOT UPDATED WITH VOLUME AI")
    MessageLoop(bot, handle).run_as_thread()
    while True: time.sleep(10)
