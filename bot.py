import os
import telepot
from flask import request

from core.time_engine import TimeEngine
from core.market_state import MarketStateEngine
from core.news_engine import NewsEngine
from core.risk_manager import RiskManager

# 🧠 Engines Initialization
time_engine = TimeEngine()
market = MarketStateEngine()
news_engine = NewsEngine()
risk_manager = RiskManager()

# 🔑 Telegram Token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telepot.Bot(TOKEN)


def telegram_webhook():
    data = request.get_json()

    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # 📌 /start command
        if text == "/start":

            # 🕒 Time Engine
            current_time = time_engine.get_current_time()
            session = time_engine.get_session()

            # 📰 News Engine
            news = news_engine.analyze_news()

            # 🧠 Market State
            state = market.get_market_state(
                news_risk=news["risk"]
            )

            # 🛡 Risk Manager (🔥 الإضافة الجديدة)
            risk = risk_manager.evaluate(
                market_state=state,
                news=news,
                volatility=0  # مؤقتًا (لاحقًا نربطه بالسوق الحقيقي)
            )

            # 📤 Response
            bot.sendMessage(
                chat_id,
                f"""🤖 ULTRA V10 CORE ACTIVE ✔

🕒 الوقت: {current_time}
🌍 الجلسة: {session}

📰 NEWS ENGINE:
⚠️ Risk: {news['risk']}
📊 Impact Score: {news['impact_score']}

📊 MARKET STATE:
⚡ الحالة: {state['state']}
🧠 السبب: {state['reason']}

🛡 RISK MANAGER:
⚡ القرار: {risk['decision']}
📊 SCORE: {risk['score']}
🧠 السبب: {risk['reason']}
"""
            )

    return "OK"
