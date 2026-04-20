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
# 🌐 FLASK KEEP ALIVE
# ==========================
app = Flask(__name__)

@app.route('/')
def home():
    return "👑 ULTRA AI BOT RUNNING"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


# ==========================
# 🔑 TELEGRAM
# ==========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = telepot.Bot(TOKEN)

# delete webhook
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
except:
    pass


# ==========================
# 📊 STATE
# ==========================
watchlist = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PAXGUSDT"]
last_signal = {}

# ==========================
# ⏱ TIME
# ==========================
def now():
    return datetime.now(timezone.utc)


# ==========================
# 🌍 MARKET SESSIONS
# ==========================
def market_data():
    h = now().hour
    if 0 <= h < 6:
        return "ASIA", 1.0, 0.8
    elif 6 <= h < 12:
        return "LONDON", 1.3, 1.2
    elif 12 <= h < 20:
        return "NEW YORK", 1.5, 1.5
    return "QUIET", 0.7, 0.6


# ==========================
# 📈 EVENTS
# ==========================
def market_events():
    h = now().hour

    mapping = {
        1: "🔔 Tokyo Open",
        10: "🔔 London Open",
        15: "🔔 New York Open",
        19: "🔕 London Close",
    }

    return [mapping[h]] if h in mapping else []


# ==========================
# 🌐 SESSION (IMPORTANT FIX)
# ==========================
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


# ==========================
# 📊 BINANCE API
# ==========================
def price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price"
        r = session.get(url, params={"symbol": symbol}, timeout=5)
        return float(r.json()["price"])
    except:
        return None


def klines(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines"
        r = session.get(url, params={
            "symbol": symbol,
            "interval": "5m",
            "limit": 100
        }, timeout=5)

        d = r.json()

        c = [float(x[4]) for x in d]
        h = [float(x[2]) for x in d]
        l = [float(x[3]) for x in d]
        v = [float(x[5]) for x in d]

        return c, h, l, v
    except:
        return [], [], [], []


# ==========================
# 📊 INDICATORS
# ==========================
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
        tr.append(max(
            h[i] - l[i],
            abs(h[i] - c[i-1]),
            abs(l[i] - c[i-1])
        ))
    return pd.Series(tr).rolling(14).mean().iloc[-1]


# ==========================
# 💧 LIQUIDITY
# ==========================
def liquidity(h, l):
    if len(h) < 20:
        return None, None
    return max(h[-20:]), min(l[-20:])


# ==========================
# ⚡ VOLUME
# ==========================
def volume_factor(v):
    if len(v) < 20:
        return 1.0
    avg = sum(v[-20:-1]) / 19
    return 1.3 if v[-1] > avg * 1.5 else 1.0


# ==========================
# 📰 NEWS ENGINE
# ==========================
def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0

        for e in feed.entries[:10]:
            t = e.title.lower()
            if any(w in t for w in ["bull", "pump", "rise"]):
                score += 1
            if any(w in t for w in ["crash", "drop", "bear"]):
                score -= 1

        if score >= 3:
            return "BULLISH", 1.2
        elif score <= -3:
            return "BEARISH", 0.7
        return "NEUTRAL", 1.0
    except:
        return "NO_NEWS", 1.0


# ==========================
# 🧠 ANALYSIS ENGINE (FIXED)
# ==========================
def analyse(symbol):
    try:
        c, h, l, v = klines(symbol)
        p = price(symbol)

        if not p or len(c) < 60:
            return None

        ema20 = ema(c, 20)
        ema50 = ema(c, 50)
        r = rsi(c)
        a = atr(h, l, c)

        buy_liq, sell_liq = liquidity(h, l)

        trend = 1 if ema20 > ema50 else -1
        momentum = 1 if r < 35 else (-1 if r > 65 else 0)

        score = (trend * 2) + (momentum * 3)

        if buy_liq and p > buy_liq:
            score += 1
        if sell_liq and p < sell_liq:
            score -= 1

        session_name, mp, w = market_data()
        news, nw = news_engine()
        vf = volume_factor(v)

        final_score = score * mp * w * nw * vf

        if abs(final_score) < 4:
            return None

        if abs(final_score) >= 8:
            strength = "🔥 STRONG"
        elif abs(final_score) >= 6:
            strength = "🟢 GOOD"
        else:
            return None

        direction = "🟢 BUY" if final_score > 0 else "🔴 SELL"
        mult = 1.5 if final_score > 0 else -1.5

        sl = p - (a * mult)
        tp1 = p + (a * mult)
        tp2 = p + (a * mult * 1.6)
        tp3 = p + (a * mult * 2.6)

        conf = min(100, abs(final_score) * 6)

        return symbol, p, direction, strength, final_score, conf, sl, tp1, tp2, tp3, session_name, vf

    except Exception as e:
        print("ANALYSE ERROR:", e)
        return None


# ==========================
# 🚀 ENGINE LOOP (ANTI FREEZE)
# ==========================
def market_events():
    h = now().hour

    mapping = {
        1: "🔔 Tokyo Open",
        10: "🔔 London Open",
        15: "🔔 New York Open",
        19: "🔕 London Close",
    }

    return [mapping[h]] if h in mapping else []


last_event_hour = None

def event_loop():
    global last_event_hour

    while True:
        try:
            h = now().hour

            # يمنع التكرار (يرسل مرة واحدة فقط لكل ساعة)
            if h != last_event_hour:
                events = market_events()

                for e in events:
                    bot.sendMessage(
                        ADMIN_CHAT_ID,
                        f"""
🌍 MARKET EVENT

{e}
"""
                    )

                last_event_hour = h

        except Exception as e:
            print("EVENT ERROR:", e)

        time.sleep(60)


# ==========================
# 📩 TELEGRAM HANDLER (SAFE)
# ==========================
sent_signals = {}

def signal_loop():
    while True:
        try:
            for s in watchlist:
                info = analyse(s)
                if not info:
                    continue

                sym, pr, dr, strength, sc, cf, sl, t1, t2, t3, sess, vf = info

                key = f"{sym}_{dr}_{strength}"

                if key in sent_signals:
                    continue

                sent_signals[key] = time.time()

                msg = f"""
╔═══ 🔥 ULTRA SIGNAL ═══╗
📊 {sym}
💰 {round(pr,2)}

🎯 {dr} {strength}
🧠 {cf}%

🌍 {sess}
📈 Volume x{vf}

━━━━━━━━━━━━━━
🛑 SL: {round(sl,2)}
🎯 TP1: {round(t1,2)}
🎯 TP2: {round(t2,2)}
🎯 TP3: {round(t3,2)}
╚══════════════════════╝
"""

                bot.sendMessage(ADMIN_CHAT_ID, msg)

        except Exception as e:
            print("SIGNAL ERROR:", e)

        time.sleep(60)

        def handle(msg):
    try:
        flavor = telepot.flavor(msg)

        if flavor == 'callback_query':
            qid, chat_id, data = telepot.glance(msg, flavor='callback_query')

            if data == "MARKET":
                sess, mp, _ = market_data()
                ev = "\n".join(market_events()) or "No events"
                bot.sendMessage(chat_id, f"🌍 {sess}\nPower: {mp}\n{ev}")
                return

            info = analyse(data)

            if not info:
                p = price(data)
                bot.sendMessage(chat_id, f"""
📊 {data}
💰 {round(p,2) if p else "?"}

⚪ السوق هادئ
""")
                return

            sym, pr, dr, strength, sc, cf, sl, t1, t2, t3, sess, vf = info

            bot.sendMessage(chat_id, f"""
📊 {sym}
💰 {round(pr,2)}

🎯 {dr} {strength}
🔥 Score: {round(sc,2)}
🧠 {cf}%

🌍 {sess}
📈 Volume x{vf}

🛑 SL: {round(sl,2)}
🎯 TP1: {round(t1,2)}
🎯 TP2: {round(t2,2)}
🎯 TP3: {round(t3,2)}
""")

        elif 'text' in msg:
            chat_id = msg['chat']['id']

            if msg.get('text') == "/start":
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="BTC", callback_data="BTCUSDT"),
                     InlineKeyboardButton(text="ETH", callback_data="ETHUSDT")],
                    [InlineKeyboardButton(text="BNB", callback_data="BNBUSDT"),
                     InlineKeyboardButton(text="SOL", callback_data="SOLUSDT")],
                    [InlineKeyboardButton(text="PAXG", callback_data="PAXGUSDT")],
                    [InlineKeyboardButton(text="Market", callback_data="MARKET")]
                ])

                bot.sendMessage(chat_id, "👑 ULTRA AI CONTROL", reply_markup=keyboard)

    except Exception as e:
        print("HANDLER ERROR:", e)

# ==========================
# 💚 HEARTBEAT
# ==========================
def heartbeat():
    while True:
        print("💚 BOT ALIVE:", datetime.now())
        time.sleep(30)
        
# ==========================
# 🚀 START SYSTEM
# ==========================
if __name__ == "__main__":

    try:
        # 🌐 Web server (keep alive)
        Thread(target=run_web, daemon=True, name="web").start()

        # 📩 Telegram bot loop
        MessageLoop(bot, handle).run_as_thread()

        # 🧠 Engine (تحليل السوق)
        Thread(target=engine_loop, daemon=True, name="engine").start()

        # 🔥 Signal system
        Thread(target=signal_loop, daemon=True, name="signal").start()

        # 🌍 Market events
        Thread(target=event_loop, daemon=True, name="events").start()

        # 💚 Heartbeat
        Thread(target=heartbeat, daemon=True, name="heartbeat").start()

        # 🔔 رسالة بدء التشغيل
        try:
            bot.sendMessage(ADMIN_CHAT_ID, "👑 ULTRA AI BOT STARTED")
        except Exception as e:
            print("START MSG ERROR:", e)

        # 🔒 إبقاء البرنامج شغال
        while True:
            time.sleep(10)

    except Exception as e:
        print("FATAL START ERROR:", e)
        time.sleep(5)
