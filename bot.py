# ==========================
# 🧠 ULTRA V10 - PHASE 1 CORE FUSION ENGINE
# ==========================

import requests
import pandas as pd
import feedparser

# ==========================
# 🌐 FLASK WEB LAYER
# ==========================
from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "ULTRA V10 RUNNING 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# ==========================
# 🧠 AI CORE ANALYSIS
# ==========================
def ai_core(trend, momentum):
    score = 0

    score += trend * 2
    score += momentum * 3

    return score


# ==========================
# 📰 NEWS ENGINE (FED + MACRO)
# ==========================
FED_KEYWORDS = ["powell", "fomc", "cpi", "interest", "inflation"]

def news_engine():
    try:
        feed = feedparser.parse("https://cryptopanic.com/news/rss/")
        score = 0
        fed = False

        for e in feed.entries[:10]:
            t = e.title.lower()

            if "bull" in t:
                score += 1
            if "bear" in t:
                score -= 1

            if any(k in t for k in FED_KEYWORDS):
                score -= 3
                fed = True

        return score, fed

    except:
        return 0, False


# ==========================
# 🛡 RISK MANAGER
# ==========================
def risk_manager(confidence, fed_flag, volatility=1.0):

    if fed_flag:
        return False

    if confidence < 55:
        return False

    if volatility < 0.5:
        return False

    return True


# ==========================
# 🔮 PRE-MOVE ENGINE
# ==========================
def pre_move_signal():
    # بسيط الآن، لاحقاً يصير متقدم
    return 1


# ==========================
# ⚖ FUSION ENGINE (FINAL BRAIN)
# ==========================
def fusion_engine(symbol, trend, momentum, session_power=1.0, volatility=1.0):

    # 🧠 AI
    ai_score = ai_core(trend, momentum)

    # 📰 News
    news_score, fed_flag = news_engine()

    # 🔮 Pre-move
    pre = pre_move_signal()

    # 📊 FINAL SCORE
    final_score = (
        ai_score +
        news_score * 2 +
        pre * 5
    ) * session_power

    confidence = min(100, max(0, 50 + final_score))

    # 🛡 RISK FILTER
    if not risk_manager(confidence, fed_flag, volatility):
        return {
            "symbol": symbol,
            "decision": "NO TRADE ⚪",
            "confidence": confidence,
            "reason": "RISK FILTER / NEWS BLOCK"
        }

    # 🎯 DECISION ENGINE
    if final_score > 15:
        decision = "STRONG BUY 📈"
    elif final_score > 5:
        decision = "BUY 🟢"
    elif final_score < -15:
        decision = "STRONG SELL 📉"
    elif final_score < -5:
        decision = "SELL 🔴"
    else:
        decision = "NO TRADE ⚪"

    return {
        "symbol": symbol,
        "decision": decision,
        "confidence": round(confidence, 2),
        "score": round(final_score, 2),
        "fed_risk": fed_flag
    }
    
# ==========================
# 🧠 ULTRA V10 - PHASE 2 MARKET CONTEXT LAYER
# ==========================

from datetime import datetime
import pytz

# ==========================
# 🕒 SYRIA SESSION ENGINE
# ==========================
SYRIA_TZ = pytz.timezone("Asia/Damascus")

def get_syria_session():
    hour = datetime.now(SYRIA_TZ).hour

    if 3 <= hour < 10:
        return "ASIA", 0.8
    elif 10 <= hour < 16:
        return "LONDON", 1.2
    elif 16 <= hour < 22:
        return "NEWYORK", 1.5
    else:
        return "LATE NIGHT", 0.6


# ==========================
# 🌍 MARKET REGIME FILTER
# ==========================
def market_regime(volatility, news_score):
    if volatility > 1.5 and news_score > 2:
        return "HIGH VOLATILITY 🔥", 1.3

    if volatility < 0.5:
        return "LOW VOLATILITY ⚠", 0.7

    return "NORMAL 🟡", 1.0


# ==========================
# 📉 NOISE FILTER (REDUCES BAD SIGNALS)
# ==========================
def noise_filter(score, session_power):

    adjusted = score * session_power

    # فلترة الإشارات الضعيفة
    if abs(adjusted) < 5:
        return False

    return True


# ==========================
# 🔄 LEARNING BIAS (from Phase 5 later)
# ==========================
def learning_bias(base_score, winrate=0.5):

    if winrate > 0.7:
        return base_score * 1.2
    elif winrate < 0.4:
        return base_score * 0.8

    return base_score


# ==========================
# 🧠 PHASE 2 INTEGRATOR
# ==========================
def phase2_context(symbol, raw_score, volatility, news_score):

    session, session_power = get_syria_session()
    regime, regime_power = market_regime(volatility, news_score)

    # دمج القوة الزمنية والسوقية
    final_score = raw_score * session_power * regime_power

    # فلترة الضوضاء
    if not noise_filter(final_score, session_power):
        return {
            "symbol": symbol,
            "decision": "NO TRADE ⚪",
            "reason": "MARKET NOISE FILTER",
            "session": session,
            "regime": regime
        }

    return {
        "symbol": symbol,
        "session": session,
        "regime": regime,
        "adjusted_score": final_score
    }
    
# ==========================
# 🧠 ULTRA V10 - PHASE 3 SELF LEARNING ENGINE
# ==========================

import json
from datetime import datetime

learning_file = "learning.json"

# ==========================
# 📦 LOAD MEMORY
# ==========================
def load_memory():
    try:
        return json.load(open(learning_file))
    except:
        return {
            "BUY": {"wins": 0, "losses": 0},
            "SELL": {"wins": 0, "losses": 0},
            "daily": []
        }

memory = load_memory()

# ==========================
# 💾 SAVE MEMORY
# ==========================
def save_memory():
    json.dump(memory, open(learning_file, "w"))


# ==========================
# 💰 UPDATE TRADE RESULT
# ==========================
def update_trade(direction, result):
    """
    result: "WIN" or "LOSS"
    """

    if direction not in memory:
        memory[direction] = {"wins": 0, "losses": 0}

    if result == "WIN":
        memory[direction]["wins"] += 1
    else:
        memory[direction]["losses"] += 1

    save_memory()


# ==========================
# 📊 WINRATE CALCULATION
# ==========================
def get_winrate(direction):

    data = memory.get(direction, {"wins": 0, "losses": 0})
    total = data["wins"] + data["losses"]

    if total == 0:
        return 0.5  # neutral

    return data["wins"] / total


# ==========================
# 🧠 SELF ADAPTIVE WEIGHTING
# ==========================
def adaptive_weight(direction, base_score):

    winrate = get_winrate(direction)

    if winrate > 0.75:
        return base_score * 1.3  # قوي جدًا
    elif winrate < 0.4:
        return base_score * 0.7  # ضعيف → يقلل القوة

    return base_score


# ==========================
# 📊 DAILY PERFORMANCE LOG
# ==========================
def log_daily(symbol, decision, confidence):

    today = datetime.now().strftime("%Y-%m-%d")

    memory["daily"].append({
        "date": today,
        "symbol": symbol,
        "decision": decision,
        "confidence": confidence
    })

    save_memory()


# ==========================
# 🔄 SMART FILTER (LEARNING FILTER)
# ==========================
def learning_filter(direction, score):

    winrate = get_winrate(direction)

    # إذا النظام خسر كثير → يقلل الإشارات
    if winrate < 0.35:
        return False

    # إذا الأداء جيد → يسمح بالإشارة
    return True


# ==========================
# 🧠 PHASE 3 INTEGRATION
# ==========================
def phase3_learning(symbol, direction, score, confidence):

    # تعديل القوة حسب الأداء
    adjusted_score = adaptive_weight(direction, score)

    # فلترة التعلم
    if not learning_filter(direction, adjusted_score):
        return {
            "symbol": symbol,
            "decision": "NO TRADE ⚪",
            "reason": "LEARNING FILTER BLOCK",
            "winrate": get_winrate(direction)
        }

    # تسجيل الأداء اليومي
    log_daily(symbol, direction, confidence)

    return {
        "symbol": symbol,
        "direction": direction,
        "score": adjusted_score,
        "winrate": get_winrate(direction),
        "status": "LEARNING ACTIVE 🧠"
    }
    
# ==========================
# 📱 ULTRA V10 - PHASE 4 CONTROL PANEL INTEGRATION
# ==========================

watchlist = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XAUUSD"]

# ==========================
# ➕ ADD COIN (FROM PANEL)
# ==========================
def add_coin(symbol):

    if symbol not in watchlist:
        watchlist.append(symbol)
        return f"✅ تم إضافة {symbol}"
    
    return "⚠ العملة موجودة مسبقاً"


# ==========================
# ❌ REMOVE COIN
# ==========================
def remove_coin(symbol):

    if symbol in watchlist:
        watchlist.remove(symbol)
        return f"❌ تم حذف {symbol}"

    return "⚠ العملة غير موجودة"


# ==========================
# 📊 GET COIN ANALYSIS (CLICK BUTTON)
# ==========================
def coin_analysis(symbol, score, confidence):

    return {
        "symbol": symbol,
        "price": get_price(symbol),
        "decision": "ANALYZED",
        "score": score,
        "confidence": confidence,
        "scalp_ready": confidence > 70
    }


# ==========================
# ⚡ SCALP ENGINE (FAST TRADE)
# ==========================
def scalp_engine(symbol, score, confidence):

    if confidence < 65:
        return {
            "symbol": symbol,
            "decision": "NO SCALP ⚪",
            "reason": "LOW CONFIDENCE"
        }

    if score > 5:
        return {
            "symbol": symbol,
            "decision": "SCALP BUY ⚡📈",
            "tp": "0.5%",
            "sl": "0.3%"
        }

    elif score < -5:
        return {
            "symbol": symbol,
            "decision": "SCALP SELL ⚡📉",
            "tp": "0.5%",
            "sl": "0.3%"
        }

    return {
        "symbol": symbol,
        "decision": "NO TRADE ⚪"
    }


# ==========================
# 🏆 BEST COINS RANKING
# ==========================
def rank_coins():

    ranked = []

    for c in watchlist:

        price = get_price(c)
        score = 10  # placeholder (later from AI)
        confidence = 70  # placeholder

        ranked.append({
            "symbol": c,
            "score": score,
            "confidence": confidence
        })

    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    return ranked


# ==========================
# 📱 CONTROL PANEL ROUTER
# ==========================
def control_panel(action, symbol=None):

    if action == "add":
        return add_coin(symbol)

    if action == "remove":
        return remove_coin(symbol)

    if action == "scalp":
        return scalp_engine(symbol, 10, 75)

    if action == "analyze":
        return coin_analysis(symbol, 10, 75)

    if action == "rank":
        return rank_coins()

    return "⚠ أمر غير معروف"
    
# ==========================
# 🏦 ULTRA V10 - PHASE 5 FULL SYSTEM MERGE
# ==========================

import time
from threading import Thread

# ==========================
# 🧠 GLOBAL PIPELINE (FULL ENGINE)
# ==========================
def full_engine(symbol):

    # 🔥 المرحلة 1 (AI + News + Risk)
    raw = fusion_engine(symbol, trend=1, momentum=0)

    # 🌍 المرحلة 2 (Market Context)
    ctx = phase2_context(
        symbol,
        raw.get("score", 0),
        volatility=1.0,
        news_score=0
    )

    # 🧠 المرحلة 3 (Self Learning)
    learn = phase3_learning(
        symbol,
        raw.get("decision", "BUY"),
        raw.get("score", 0),
        raw.get("confidence", 50)
    )

    # 📊 دمج نهائي
    final = {
        "symbol": symbol,
        "decision": raw.get("decision"),
        "confidence": raw.get("confidence"),
        "session": ctx.get("session"),
        "regime": ctx.get("regime"),
        "learning": learn.get("status", "ACTIVE")
    }

    return final


# ==========================
# 📱 TELEGRAM INLINE PANEL (LOGIC)
# ==========================
def telegram_router(command, symbol=None):

    if command == "ANALYZE":
        return full_engine(symbol)

    if command == "SCALP":
        data = full_engine(symbol)
        return scalp_engine(symbol, data["confidence"], data["confidence"])

    if command == "RANK":
        return rank_coins()

    if command == "ADD":
        return add_coin(symbol)

    if command == "REMOVE":
        return remove_coin(symbol)

    return "⚠ أمر غير معروف"


# ==========================
# 🚀 SIGNAL LOOP (LIVE ENGINE)
# ==========================
def live_loop():

    while True:

        for coin in watchlist:

            result = full_engine(coin)

            # 📡 هنا يتم إرسال الإشارة (Telegram)
            print(f"""
🧠 {result['symbol']}
📊 {result['decision']}
🔥 CONF: {result['confidence']}
🌍 {result['session']} | {result['regime']}
🧠 {result['learning']}
""")

        time.sleep(30)


# ==========================
# 🔗 SYSTEM STARTUP
# ==========================
def start_system():
    Thread(target=run_web).start()
    Thread(target=live_loop).start()

    print("🚀 ULTRA V10 FULL SYSTEM RUNNING")

if __name__ == "__main__":
    start_system()
