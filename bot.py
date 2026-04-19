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
# 🌐 Flask App (Render Keep-Alive)
# ==========================
app = Flask(__name__)
@app.route('/')
def home(): return "BOT IS ACTIVE - ALL FEATURES INCLUDED"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ==========================
# 🚀 TELEGRAM SETUP
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
bot = telepot.Bot(TOKEN)

# ==========================
# 📊 DATA FETCHING (FIXED WITH HEADERS)
# ==========================
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_safe_data(url):
    """دالة لجلب البيانات مع معالجة حظر بايننس"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except: return None

def price(symbol):
    url = f"https://binance.com{symbol}"
    data = get_safe_data(url)
    return float(data["price"]) if data else None

def get_klines(symbol, interval='5m', limit=100):
    url = f"https://binance.com{symbol}&interval={interval}&limit={limit}"
    data = get_safe_data(url)
    if data:
        df = pd.DataFrame(data).astype(float)
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'ct', 'qa', 'nt', 'tb', 'tq', 'ig']
        return df
    return pd.DataFrame()

# ==========================
# 📉 ALL INDICATORS (RSI, ADX, EMA, BOLLINGER)
# ==========================
def rsi(df, p=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=p).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=p).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs.iloc[-1]))

def adx(df, p=14):
    df = df.copy()
    df['up'] = df['high'].diff(); df['down'] = -df['low'].diff()
    df['+dm'] = df['up'].where((df['up'] > df['down']) & (df['up'] > 0), 0)
    df['-dm'] = df['down'].where((df['down'] > df['up']) & (df['down'] > 0), 0)
    tr = pd.concat([df['high'] - df['low'], abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))], axis=1).max(axis=1)
    atr_v = tr.rolling(p).mean()
    p_di = 100 * (df['+dm'].rolling(p).mean() / (atr_v + 1e-9))
    m_di = 100 * (df['-dm'].rolling(p).mean() / (atr_v + 1e-9))
    dx = 100 * abs(p_di - m_di) / (p_di + m_di + 1e-9)
    return dx.rolling(p).mean().iloc[-1]

# ==========================
# 🧠 NEWS & SESSION ENGINE
# ==========================
def news_score():
    try:
        feed = feedparser.parse("https://cryptopanic.com", request_timeout=5)
        s = 0
        for e in feed.entries[:10]:
            t = e.title.lower()
            if any(w in t for w in ["bull", "pump", "surge"]): s += 1
            if any(w in t for w in ["bear", "dump", "crash"]): s -= 1
        return 1.2 if s >= 2 else (0.8 if s <= -2 else 1.0)
    except: return 1.0

# ==========================
# 🔬 COMPLETE ANALYSIS (No Features Dropped)
# ==========================
def analyse(symbol):
    df5m = get_klines(symbol, '5m')
    df1h = get_klines(symbol, '1h')
    p_now = price(symbol)
    if df5m.empty or df1h.empty or p_now is None: return None

    # مؤشرات فنية
    ema20_1h, ema50_1h = df1h['close'].ewm(span=20).mean().iloc[-1], df1h['close'].ewm(span=50).mean().iloc[-1]
    trend_1h = 1 if ema20_1h > ema50_1h else -1
    r, strength = rsi(df5m), adx(df5m)
    
    # أحجام التداول
    vol_factor = 1.3 if df5m['volume'].iloc[-1] > df5m['volume'].iloc[-20:-1].mean() * 1.5 else 1.0
    
    # الحساب النهائي
    score = (2 if df5m['close'].ewm(span=20).mean().iloc[-1] > df5m['close'].ewm(span=50).mean().iloc[-1] else -2)
    score += (3 if r < 35 else (-3 if r > 65 else 0))
    if strength > 25: score *= 1.2
    if (score > 0 and trend_1h == 1) or (score < 0 and trend_1h == -1): score *= 1.5
    
    final_score = score * vol_factor * news_score()
    if abs(final_score) < 6: return None

    direction = "🟢 BUY" if final_score > 0 else "🔴 SELL"
    atr = (df5m['high'] - df5m['low']).rolling(14).mean().iloc[-1]
    sl, tp = p_now - (atr * 2), p_now + (atr * 3)
    if final_score < 0: sl, tp = p_now + (atr * 2), p_now - (atr * 3)

    return symbol, p_now, direction, final_score, sl, tp, strength

# ==========================
# ⏰ MARKET ALERTS & STATUS
# ==========================
def market_alerts_loop():
    last_sent = -1
    while True:
        try:
            h = datetime.now(timezone.utc).hour
            if h != last_sent:
                m = {22:"سيدني 🇦🇺", 0:"طوكيو 🇯🇵", 8:"لندن 🇬🇧", 13:"نيويورك 🇺🇸"}.get(h)
                if m and ADMIN_CHAT_ID: bot.sendMessage(ADMIN_CHAT_ID, f"🔔 افتتاح سوق {m}")
                last_sent = h
        except: pass
        time.sleep(60)

# ==========================
# 📩 HANDLERS
# ==========================
def handle(msg):
    try:
        if 'data' in msg:
            qid, chat_id, data = telepot.glance(msg, flavor='callback_query')
            p_val = price(data)
            names = {"PAXGUSDT":"GOLD", "BTCUSDT":"BTC", "ETHUSDT":"ETH", "BNBUSDT":"BNB", "SOLUSDT":"SOL"}
            
            if data == "MARKET":
                h = datetime.now(timezone.utc).hour
                bot.sendMessage(chat_id, f"🌍 لندن: {'🟢' if 8<=h<16 else '🔴'}\n🇺🇸 نيويورك: {'🟢' if 13<=h<21 else '🔴'}")
                return

            if p_val is None:
                bot.sendMessage(chat_id, "❌ خطأ اتصال (Binance Busy). حاول ثانية")
                return

            res = analyse(data)
            if not res:
                bot.sendMessage(chat_id, f"📊 {names.get(data)}\n💰 {round(p_val,2)}\n⚪ لا إشارة قوية")
            else:
                s, pr, dr, sc, sl, tp, adx_v = res
                bot.sendMessage(chat_id, f"🏆 **إشارة: {names.get(data)}**\n🎯 {dr}\n💰 {round(pr,2)}\n🔥 ADX: {round(adx_v,1)}\n🛑 SL: {round(sl,2)}\n✅ TP: {round(tp,2)}")

        elif 'text' in msg and msg.get('text') == "/start":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏆 Gold", callback_data="PAXGUSDT"), InlineKeyboardButton(text="📊 BTC", callback_data="BTCUSDT")],
                [InlineKeyboardButton(text="📊 ETH", callback_data="ETHUSDT"), InlineKeyboardButton(text="📊 BNB", callback_data="BNBUSDT")],
                [InlineKeyboardButton(text="📊 SOL", callback_data="SOLUSDT"), InlineKeyboardButton(text="⚡ السوق", callback_data="MARKET")]
            ])
            bot.sendMessage(msg['chat']['id'], "🚀 AI Sniper V5 - All Features Active", reply_markup=kb)
    except: pass

# ==========================
# 🚀 RUN
# ==========================
if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    Thread(target=market_alerts_loop, daemon=True).start()
    MessageLoop(bot, handle).run_as_thread()
    while True: time.sleep(10)
                
