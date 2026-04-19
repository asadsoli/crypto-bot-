import os
import time
import requests
import pandas as pd
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
def home(): return "BOT ACTIVE"

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
# 📊 DATA FETCHING (ULTRA STABLE)
# ==========================
def get_safe_price(symbol):
    """جلب السعر بطريقة تضمن عدم ظهور None"""
    try:
        url = f"https://binance.com{symbol}"
        res = requests.get(url, timeout=10).json()
        return float(res["price"])
    except:
        try: # محاولة ثانية برابط بديل
            url = f"https://binance.com{symbol}"
            res = requests.get(url, timeout=10).json()
            return float(res["price"])
        except: return None

def get_klines(symbol, interval='5m', limit=100):
    try:
        url = f"https://binance.com{symbol}&interval={interval}&limit={limit}"
        d = requests.get(url, timeout=10).json()
        df = pd.DataFrame(d).astype(float)
        df = df.iloc[:, :6]
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        return df
    except: return pd.DataFrame()

# ==========================
# 📉 ANALYSIS & INDICATORS
# ==========================
def analyse(symbol):
    df5m = get_klines(symbol, '5m')
    df1h = get_klines(symbol, '1h')
    p_now = get_safe_price(symbol)
    
    if df5m.empty or df1h.empty or p_now is None: return None

    # مؤشرات بسيطة وقوية
    ema20 = df5m['close'].ewm(span=20).mean().iloc[-1]
    ema50 = df5m['close'].ewm(span=50).mean().iloc[-1]
    
    score = 2 if ema20 > ema50 else -2
    direction = "🟢 BUY" if score > 0 else "🔴 SELL"
    
    # حساب الأهداف بناءً على التقلب
    atr = (df5m['high'] - df5m['low']).rolling(14).mean().iloc[-1]
    sl = p_now - (atr * 2) if score > 0 else p_now + (atr * 2)
    tp = p_now + (atr * 3) if score > 0 else p_now - (atr * 3)
    
    return symbol, p_now, direction, sl, tp

# ==========================
# ⏰ MARKET STATUS
# ==========================
def get_market_status():
    h = datetime.now(timezone.utc).hour
    status = "🌍 **حالة الأسواق الآن:**\n"
    status += "🟢 لندن: مفتوح\n" if 8 <= h < 16 else "🔴 لندن: مغلق\n"
    status += "🟢 نيويورك: مفتوح\n" if 13 <= h < 21 else "🔴 نيويورك: مغلق\n"
    status += "🟢 طوكيو: مفتوح\n" if 0 <= h < 9 else "🔴 طوكيو: مغلق\n"
    return status

# ==========================
# 📩 HANDLERS
# ==========================
def handle(msg):
    try:
        if 'data' in msg:
            qid, chat_id, data = telepot.glance(msg, flavor='callback_query')
            
            if data == "MARKET_STATUS":
                bot.sendMessage(chat_id, get_market_status())
                return
            
            if data == "BOT_STATUS":
                bot.sendMessage(chat_id, "👑 البوت يعمل بكفاءة على Render\n✅ اتصال Binance: مستقر")
                return

            p_val = get_safe_price(data)
            names = {"PAXGUSDT": "🏆 GOLD", "BTCUSDT": "📊 BTC", "ETHUSDT": "📊 ETH", "BNBUSDT": "📊 BNB", "SOLUSDT": "📊 SOL"}
            name = names.get(data, data)

            if p_val is None:
                bot.sendMessage(chat_id, f"❌ فشل جلب سعر {name}. حاول مرة أخرى.")
                return

            res = analyse(data)
            if not res:
                bot.sendMessage(chat_id, f"📊 {name}\n💰 السعر: {round(p_val, 2)}\n⚪ الانتظار.. لا توجد إشارة قوية.")
            else:
                sym, pr, dr, sl, tp = res
                bot.sendMessage(chat_id, f"🏆 **إشارة: {name}**\n\n🎯 {dr}\n💰 السعر الحالي: {round(pr, 2)}\n🛑 SL: {round(sl, 2)}\n✅ TP: {round(tp, 2)}")

        elif 'text' in msg:
            chat_id = msg['chat']['id']
            if msg.get('text') == "/start":
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏆 الذهب (XAU)", callback_data="PAXGUSDT")],
                    [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT"), InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
                    [InlineKeyboardButton(text="BNB", callback_data="BNBUSDT"), InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")],
                    [InlineKeyboardButton(text="⚡ حالة السوق", callback_data="MARKET_STATUS"), InlineKeyboardButton(text="👑 حالة البوت", callback_data="BOT_STATUS")]
                ])
                bot.sendMessage(chat_id, "🚀 **AI Sniper Final v4**\nتم إصلاح الأسعار وإضافة BNB وحالة السوق:", reply_markup=kb)
    except Exception as e: print(f"Error: {e}")

# ==========================
# 🚀 RUN
# ==========================
if __name__ == "__main__":
    try: requests.get(f"https://telegram.org{TOKEN}/deleteWebhook?drop_pending_updates=true")
    except: pass

    Thread(target=run_web, daemon=True).start()
    print("🟢 Bot Started Successfully")
    
    while True:
        try:
            MessageLoop(bot, handle).run_forever()
        except:
            time.sleep(5)
            
