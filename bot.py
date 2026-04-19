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
# 🌐 Flask App & Anti-Sleep
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "BOT IS RUNNING - AI GOLDEN EDITION 24/7"

def run_web():
    try:
        port = int(os.environ.get("PORT", 10000))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Flask Error: {e}")

def ping_self():
    """دالة لزيارة رابط البوت تلقائياً لمنعه من النوم على ريندر المجاني"""
    time.sleep(30) # انتظر قليلاً حتى يبدأ السيرفر
    app_name = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if app_name:
        url = f"https://{app_name}://"
        while True:
            try:
                requests.get(url, timeout=10)
                print("🚀 Self-Ping: Keeping the bot awake...")
            except:
                print("⚠️ Self-Ping failed")
            time.sleep(600) # كل 10 دقائق

# ==========================
# 🚀 TELEGRAM SETUP
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
bot = telepot.Bot(TOKEN)

def clear_webhook():
    try:
        requests.get(f"https://telegram.org{TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=10)
        print("🟢 Webhook deleted")
    except:
        pass

# ==========================
# 📊 DATA FETCHING (Corrected Links)
# ==========================
def get_klines(symbol, interval='5m', limit=100):
    try:
        url = f"https://binance.com{symbol}&interval={interval}&limit={limit}"
        d = requests.get(url, timeout=10).json()
        df = pd.DataFrame(d, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
        return df.astype(float)
    except:
        return pd.DataFrame()

def price(symbol):
    try:
        url = f"https://binance.com{symbol}"
        return float(requests.get(url, timeout=10).json()["price"])
    except:
        return None

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
    df['up'] = df['high'].diff(); df['down'] = -df['low'].diff()
    df['+dm'] = df['up'].where((df['up'] > df['down']) & (df['up'] > 0), 0)
    df['-dm'] = df['down'].where((df['down'] > df['up']) & (df['down'] > 0), 0)
    tr = pd.concat([df['high'] - df['low'], abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))], axis=1).max(axis=1)
    atr_v = tr.rolling(p).mean()
    plus_di = 100 * (df['+dm'].rolling(p).mean() / (atr_v + 1e-9))
    minus_di = 100 * (df['-dm'].rolling(p).mean() / (atr_v + 1e-9))
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
    return dx.rolling(p).mean().iloc[-1]

def bollinger(df, p=20):
    ma = df['close'].rolling(p).mean(); std = df['close'].rolling(p).std()
    return ma.iloc[-1], (ma + 2*std).iloc[-1], (ma - 2*std).iloc[-1]

# ==========================
# 🧠 ANALYSIS LOGIC
# ==========================
def analyse(symbol):
    try:
        df5m = get_klines(symbol, '5m'); df1h = get_klines(symbol, '1h')
        p_now = price(symbol)
        if df5m.empty or df1h.empty or not p_now: return None

        ema20_1h, ema50_1h = ema(df1h, 20), ema(df1h, 50)
        trend_1h = 1 if ema20_1h > ema50_1h else -1
        ema20_5m, ema50_5m = ema(df5m, 20), ema(df5m, 50)
        r, strength = rsi(df5m), adx(df5m)
        ma_b, upper_b, lower_b = bollinger(df5m)
        
        avg_vol = df5m['volume'].iloc[-20:-1].mean()
        curr_vol = df5m['volume'].iloc[-1]
        vol_factor = 1.3 if curr_vol > avg_vol * 1.5 else 1.0

        score = 2 if ema20_5m > ema50_5m else -2
        if r < 35: score += 3
        elif r > 65: score -= 3
        
        if strength > 25: score *= 1.2 
        else: score *= 0.5

        if (score > 0 and trend_1h == 1) or (score < 0 and trend_1h == -1): score *= 1.5
        else: score *= 0.7

        h_utc = datetime.now(timezone.utc).hour
        sess_w = 1.5 if 12 <= h_utc < 20 else (1.3 if 6 <= h_utc < 12 else 0.8)
        final_score = score * sess_w * vol_factor
        
        if abs(final_score) < 8: return None

        direction = "🟢 BUY" if final_score > 0 else "🔴 SELL"
        if direction == "🟢 BUY" and p_now > upper_b * 0.99: return None
        if direction == "🔴 SELL" and p_now < lower_b * 1.01: return None

        tr = (df5m['high'] - df5m['low']).rolling(14).mean().iloc[-1]
        sl = p_now - (tr * 2) if final_score > 0 else p_now + (tr * 2)
        tp = p_now + (tr * 3) if final_score > 0 else p_now - (tr * 3)
        conf = min(99.9, abs(final_score) * 5)

        return symbol, p_now, direction, final_score, conf, sl, tp, strength, trend_1h
    except:
        return None

# ==========================
# 📩 HANDLERS
# ==========================
def handle(msg):
    try:
        if 'data' in msg:
            qid, chat_id, data = telepot.glance(msg, flavor='callback_query')
            res = analyse(data)
            p_val = price(data)
            name = "🏆 GOLD (الذهب)" if data == "PAXGUSDT" else data
            
            if not res:
                bot.sendMessage(chat_id, f"📊 {name}\n💰 {p_val}\n⚪ السوق حالياً لا يوفر إشارة ذهبية آمنة.")
            else:
                sym, pr, dr, sc, cf, sl, tp, adx_v, tr_1h = res
                trend_txt = "صاعد 📈" if tr_1h == 1 else "هابط 📉"
                bot.sendMessage(chat_id, f"🏆 **إشارة ذهبية: {name}**\n\n🎯 الاتجاه: {dr}\n💰 السعر: {round(pr,4)}\n🛡️ الثقة: {round(cf,1)}%\n🔥 القوة: {round(adx_v,1)}\n🌍 اتجاه الساعة: {trend_txt}\n\n🛑 SL: {round(sl,4)}\n✅ TP: {round(tp,4)}")

        elif 'text' in msg:
            chat_id = msg['chat']['id']
            if msg.get('text') == "/start":
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏆 الذهب (XAU)", callback_data="PAXGUSDT")],
                    [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT"), InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
                    [InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")]
                ])
                bot.sendMessage(chat_id, "🚀 **AI Sniper v3 GOLDEN**\nتم تفعيل نظام الحماية 24/7. اختر عملة للتحليل:", reply_markup=kb)
    except Exception as e:
        print(f"Handle Error: {e}")

# ==========================
# 🛡️ MAIN START ENGINE
# ==========================
def start_bot():
    clear_webhook()
    print("🟢 Bot System Starting...")
    MessageLoop(bot, handle).run_as_thread()
    while True:
        time.sleep(15)

if __name__ == "__main__":
    # 1. تشغيل Flask لـ Render
    Thread(target=run_web, daemon=True).start()
    
    # 2. تشغيل الـ Anti-Sleep
    Thread(target=ping_self, daemon=True).start()
    
    # 3. تشغيل البوت مع إعادة تشغيل تلقائية عند الانهيار
    while True:
        try:
            if ADMIN_CHAT_ID:
                bot.sendMessage(ADMIN_CHAT_ID, "🟢 AI System Online (Render Free)")
            start_bot()
        except Exception as e:
            print(f"Crash Detected: {e}. Restarting...")
            time.sleep(5)
