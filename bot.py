import os
import time
import requests
import pandas as pd
import feedparser
from datetime import datetime
from threading import Thread

import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

# ==========================
# 🔐 CONFIG
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telepot.Bot(BOT_TOKEN)

# ==========================
# 🌍 MARKET SESSION
# ==========================
def get_utc_hour():
    return datetime.utcnow().hour

def get_market_session():
    h = get_utc_hour()

    if 22 <= h or h < 7:
        return "SYDNEY", 0.8
    elif 0 <= h < 9:
        return "TOKYO", 1.0
    elif 8 <= h < 17:
        return "LONDON", 1.3
    elif 13 <= h < 22:
        return "NEW YORK", 1.5
    return "QUIET", 0.6

# ==========================
# 📊 PRICE DATA
# ==========================
def get_price(symbol):
    try:
        return float(requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=5
        ).json()["price"])
    except:
        return None

def klines(symbol):
    try:
        data = requests.get(
            f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
        ).json()

        close = [float(x[4]) for x in data]
        high = [float(x[2]) for x in data]
        low = [float(x[3]) for x in data]

        return close, high, low
    except:
        return [], [], []

# ==========================
# 📈 INDICATORS
# ==========================
def ema(data, period):
    return pd.Series(data).ewm(span=period).mean().iloc[-1]

def rsi(data):
    s = pd.Series(data)
    d = s.diff()

    gain = d.clip(lower=0).rolling(14).mean()
    loss = (-d.clip(upper=0)).rolling(14).mean()

    rs = gain.iloc[-1] / (loss.iloc[-1] + 1e-9)
    return 100 - (100 / (1 + rs))

def atr(high, low, close):
    tr = []
    for i in range(1, len(close)):
        tr.append(max(
            high[i] - low[i],
            abs(high[i] - close[i-1]),
            abs(low[i] - close[i-1])
        ))

    return pd.Series(tr).rolling(14).mean().iloc[-1]

# ==========================
# 🧠 NEWS
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0

        for e in feed.entries[:10]:
            t = e.title.lower()

            if "bull" in t or "pump" in t:
                score += 1
            if "bear" in t or "dump" in t:
                score -= 1

        return score
    except:
        return 0

# ==========================
# 🧠 AI ENGINE (CORE)
# ==========================
def ai_engine(symbol):

    close, high, low = klines(symbol)
    price = get_price(symbol)

    if not price or len(close) < 60:
        return None

    ema20 = ema(close, 20)
    ema50 = ema(close, 50)
    r = rsi(close)
    a = atr(high, low, close)

    trend = 1 if ema20 > ema50 else -1

    momentum = 0
    if r < 30:
        momentum = 1
    elif r > 70:
        momentum = -1

    score = (trend * 2) + (momentum * 3)

    session, power = get_market_session()
    news_score = news_engine()

    final_score = (score * power) + (news_score * 2)

    if abs(final_score) < 6:
        return None

    if final_score > 0:
        direction = "🟢 BUY"
        sl = price - a * 1.5
        tp1 = price + a * 1.5
        tp2 = price + a * 2.5
    else:
        direction = "🔴 SELL"
        sl = price + a * 1.5
        tp1 = price - a * 1.5
        tp2 = price - a * 2.5

    confidence = min(100, abs(final_score) * 6)

    return {
        "symbol": symbol,
        "price": price,
        "direction": direction,
        "score": final_score,
        "confidence": confidence,
        "session": session,
        "power": power,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2
    }

# ==========================
# 📱 PANEL
# ==========================
def send_panel():

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 BTC", callback_data="BTCUSDT"),
            InlineKeyboardButton(text="⚡ ETH", callback_data="ETHUSDT")
        ],
        [
            InlineKeyboardButton(text="🏆 RANK", callback_data="RANK"),
            InlineKeyboardButton(text="🧠 STATUS", callback_data="STATUS")
        ]
    ])

    bot.sendMessage(CHAT_ID,
        "🚀 ULTRA V10 PANEL\n\n📊 ONLINE\n🧠 AI ACTIVE\n📡 LIVE RUNNING",
        reply_markup=keyboard
    )

# ==========================
# 📩 CALLBACK
# ==========================
def on_callback(msg):

    qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

    if data == "STATUS":
        bot.sendMessage(chat_id, "🧠 BOT IS RUNNING")

    elif data == "RANK":
        bot.sendMessage(chat_id, "🏆 RANK SYSTEM READY")

    else:
        result = ai_engine(data)

        if not result:
            bot.sendMessage(chat_id, f"{data}\n⚪ NO SIGNAL")
            return

        bot.sendMessage(chat_id,
            f"""
📊 {result['symbol']}
💰 {result['price']}

🎯 {result['direction']}
🔥 Score: {round(result['score'],2)}
📊 Conf: {round(result['confidence'],2)}%

🌍 Session: {result['session']}
⚡ Power: {result['power']}

🛑 SL: {result['sl']}
🎯 TP1: {result['tp1']}
🎯 TP2: {result['tp2']}
"""
        )

# ==========================
# 📩 CHAT
# ==========================
def on_chat(msg):

    chat_id = msg['chat']['id']
    text = msg.get('text','')

    if text == "/start":
        send_panel()

# ==========================
# 🔥 HANDLER
# ==========================
def handle(msg):

    if 'data' in msg:
        on_callback(msg)
    elif 'text' in msg:
        on_chat(msg)

# ==========================
# 🔄 LIVE LOOP
# ==========================
def live_loop():

    watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

    while True:

        for coin in watchlist:

            result = ai_engine(coin)

            if result and result['confidence'] > 85:

                bot.sendMessage(CHAT_ID,
                    f"""
🔥 SIGNAL

📊 {coin}
🎯 {result['direction']}
🔥 {round(result['confidence'],2)}%
🌍 {result['session']}
"""
                )

            time.sleep(2)

        time.sleep(30)

# ==========================
# 🚀 START SYSTEM
# ==========================
def start_system():

    print("🚀 ULTRA V10 FULL SYSTEM RUNNING")

    send_panel()

    MessageLoop(bot, handle).run_as_thread()

    Thread(target=live_loop).start()

    while True:
        time.sleep(10)


if __name__ == "__main__":
    start_system()
