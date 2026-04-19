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
    return "BOT IS RUNNING - AI GOLDEN EDITION"

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
# 📊 DATA FETCHING (Multi-Timeframe)
# ==========================
def get_klines(symbol, interval='5m', limit=100):
    try:
        url = f"https://binance.com{symbol}&interval={interval}&limit={limit}"
        d = requests.get(url, timeout=5).json()
        df = pd.DataFrame(d, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
        return df.astype(float)
    except:
        return pd.DataFrame()

def price(symbol):
    try:
        return float(requests.get(f"https://binance.com{symbol}").json()["price"])
    except: return None

# ==========================
# 📉 INDICATORS ENGINE
# ==========================
def ema(df, p): return df['close'].ewm(span=p).mean().iloc[-1]

def rsi(df, p=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=p).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=p).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs.iloc[-1]))

def adx(df, p=14):
    df = df.copy()
    df['up'] = df['high'].diff()
    df['down'] = -df['low'].diff()
    df['+dm'] = df['up'].where((df['up'] > df['down']) & (df['up'] > 0), 0)
    df['-dm'] = df['down'].where((df['down'] > df['up']) & (df['down'] > 0), 0)
    tr = pd.concat([df['high'] - df['low'], abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))], axis=1).max(axis=1)
    atr_v = tr.rolling(p).mean()
    plus_di = 100 * (df['+dm'].rolling(p).mean() / (atr_v + 1e-9))
    minus_di = 100 * (df['-dm'].rolling(p).mean() / (atr_v + 1e-9))
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
    return dx.rolling(p).mean().iloc[-1]

def bollinger(df, p=20):
    ma = df['close'].rolling(p).mean()
    std = df['close'].rolling(p).std()
    return ma.iloc[-1], (ma + 2*std).iloc[-1], (ma - 2*std).iloc[-1]

# ==========================
# 🧠 ANALYSIS LOGIC
# ==========================
def analyse(symbol):
    df5m = get_klines(symbol, '5m')
    df1h = get_klines(symbol, '1h')
    p_now = price(symbol)
    
    if df5m.empty or df1h.empty or not p_now: return None

    # 1. فحص الاتجاه العام (1H)
    ema20_1h = ema(df1h, 20)
    ema50_1h = ema(df1h, 50)
    trend_1h = 1 if ema20_1h > ema50_1h else -1

    # 2. مؤشرات الفريم الصغير (5m)
    ema20_5m = ema(df5m, 20)
    ema50_5m = ema(df5m, 50)
    r = rsi(df5m)
    strength = adx(df5m)
    ma_b, upper_b, lower_b = bollinger(df5m)
    
    # 3. أحجام التداول والسيولة
    avg_vol = df5m['volume'].iloc[-20:-1].mean()
    curr_vol = df5m['volume'].iloc[-1]
    vol_factor = 1.3 if curr_vol > avg_vol * 1.5 else 1.0

    # 4. حساب النقاط الذكي (Scoring)
    score = 0
    if ema20_5m > ema50_5m: score += 2
    else: score -= 2
    
    if r < 35: score += 3
    elif r > 65: score -= 3
    
    # فلتر ADX (قوة الاتجاه)
    if strength > 25: score *= 1.2 
    else: score *= 0.5 # تقليل الثقة إذا كان السوق جانبياً

    # فحص توافق الفريمات
    if (score > 0 and trend_1h == 1) or (score < 0 and trend_1h == -1):
        score *= 1.5
    else:
        score *= 0.7 # إضعاف الإشارة إذا كانت عكس اتجاه الساعة

    # 5. تحليل الأخبار وجلسات التداول
    h_utc = datetime.now(timezone.utc).hour
    sess_w = 1.5 if 12 <= h_utc < 20 else (1.3 if 6 <= h_utc < 12 else 0.8)
    
    final_score = score * sess_w * vol_factor
    if abs(final_score) < 8: return None # رفع حد الصرامة للإشارات الذهبية

    # اتجاه الإشارة
    direction = "🟢 BUY" if final_score > 0 else "🔴 SELL"
    
    # حماية Bollinger
    if direction == "🟢 BUY" and p_now > upper_b * 0.99: return None # تشبع شراء
    if direction == "🔴 SELL" and p_now < lower_b * 1.01: return None # تشبع بيع

    conf = min(99.9, abs(final_score) * 5)
    
    # حساب الأهداف بناءً على التقلب
    tr = pd.concat([df5m['high'] - df5m['low']], axis=1).max(axis=1).rolling(14).mean().iloc[-1]
    sl = p_now - (tr * 2) if final_score > 0 else p_now + (tr * 2)
    tp = p_now + (tr * 3) if final_score > 0 else p_now - (tr * 3)

    return symbol, p_now, direction, final_score, conf, sl, tp, strength, trend_1h

# ==========================
# 📩 HANDLERS & BOT RUN
# ==========================
def handle(msg):
    if 'data' in msg:
        qid, chat_id, data = telepot.glance(msg, flavor='callback_query')
        res = analyse(data)
        if not res:
            bot.sendMessage(chat_id, f"📊 {data}\n💰 {price(data)}\n⚪ السوق حالياً لا يوفر إشارة ذهبية آمنة.")
        else:
            sym, pr, dr, sc, cf, sl, tp, adx_v, tr_1h = res
            trend_txt = "صاعد 📈" if tr_1h == 1 else "هابط 📉"
            bot.sendMessage(chat_id, f"🏆 **إشارة ذهبية: {sym}**\n\n🎯 الاتجاه: {dr}\n💰 السعر: {round(pr,4)}\n🛡️ الثقة: {round(cf,1)}%\n🔥 القوة (ADX): {round(adx_v,1)}\n🌍 اتجاه الساعة: {trend_txt}\n\n🛑 SL: {round(sl,4)}\n✅ TP: {round(tp,4)}")

    elif 'text' in msg:
        chat_id = msg['chat']['id']
        if msg.get('text') == "/start":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT"), InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
                [InlineKeyboardButton(text="SOL", callback_data="SOLUSDT"), InlineKeyboardButton(text="PAXG", callback_data="PAXGUSDT")]
            ])
            bot.sendMessage(chat_id, "🚀 **AI Sniper v3**\nنظام التحليل المتعدد للفريمات والسيولة جاهز:", reply_markup=kb)

if __name__ == "__main__":
    Thread(target=run_web).start()
    if ADMIN_CHAT_ID: bot.sendMessage(ADMIN_CHAT_ID, "🟢 AI GOLDEN SYSTEM STARTING...")
    MessageLoop(bot, handle).run_as_thread()
    while True: time.sleep(10)
    
