import telepot
import requests
import time
import pandas as pd
import feedparser
from datetime import datetime, timezone
import os
from flask import Flask
from threading import Thread

# ==========================
# 🔥 KEEP ALIVE (RENDER FIX)
# ==========================
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
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
last_signal = {}

# ==========================
def analyse(symbol):

    c, h, l = klines(symbol)
    p = price(symbol)

    if not p or len(c) < 60:
        return None

    ema20 = ema(c, 20)
    ema50 = ema(c, 50)
    r = rsi(c)
    a = atr(h, l, c)

    buy_liq, sell_liq = liquidity(h, l)

    score = 0
    score += 2 if ema20 > ema50 else -2
    score += 2 if r < 30 else -2 if r > 70 else 0
    score += 1 if buy_liq and p > buy_liq else -1 if sell_liq and p < sell_liq else 0

    score += fvg(h, l)
    score += order_block(c)

    c15, _, _ = klines_tf(symbol, "15m")
    if len(c15) > 50:
        score += 2 if ema(c15, 20) > ema(c15, 50) else -2

    c1h, _, _ = klines_tf(symbol, "1h")
    if len(c1h) > 50:
        score += 2 if ema(c1h, 20) > ema(c1h, 50) else -2

    res, sup = support_resistance(h, l)
    if res and p > res:
        score += 2
    elif sup and p < sup:
        score -= 2

    sess, w = session()
    score *= w

    news, nw = news_engine()
    score *= nw

    # 🔥 فلتر القوة
    if abs(score) < 4:
        return None

    # الاتجاه
    if score > 0:
        direction = "🟢 شراء"
        sl = p - a * 1.5
        tp1 = p + a * 1.5
        tp2 = p + a * 2.5
        tp3 = p + a * 4
    else:
        direction = "🔴 بيع"
        sl = p + a * 1.5
        tp1 = p - a * 1.5
        tp2 = p - a * 2.5
        tp3 = p - a * 4

    conf = min(100, abs(score) * 15)

    return symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, news

# ==========================
def run():
    bot.sendMessage(ADMIN_CHAT_ID, "👑 تم تشغيل البوت على السيرفر بنجاح")

    while True:
        try:
            for s in watchlist:

                r = analyse(s)
                if not r:
                    continue

                symbol, p, direction, score, conf, sl, tp1, tp2, tp3, sess, news = r

                # 🔥 فلتر الثقة
                if conf < 50:
                    continue

                # منع التكرار
                if last_signal.get(s) == direction:
                    continue

                # 📩 رسالة عربية احترافية
                msg = f"""
👑 روبوت الإشارات الذكي

📊 الزوج: {symbol}
💰 سعر الدخول: {round(p, 2)}

🎯 الاتجاه: {direction}
🔥 قوة الإشارة: {round(score, 2)}
🧠 نسبة الثقة: {round(conf, 2)}%

💼 الجلسة: {sess}
📰 الأخبار: {news}

🛑 وقف الخسارة: {round(sl, 2)}
🎯 الهدف الأول: {round(tp1, 2)}
🎯 الهدف الثاني: {round(tp2, 2)}
🎯 الهدف الثالث: {round(tp3, 2)}
"""

                bot.sendMessage(ADMIN_CHAT_ID, msg)

                last_signal[s] = direction
                time.sleep(2)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

        time.sleep(60)

# ==========================
keep_alive()

import threading
t = threading.Thread(target=run)
t.start()
