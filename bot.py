import os
import telepot
from flask import request

from core.time_engine import TimeEngine
from core.market_state import MarketStateEngine
from core.news_engine import NewsEngine

# 🧠 Engines
time_engine = TimeEngine()
market = MarketStateEngine()
news_engine = NewsEngine()

# 🔑 Token
TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telepot.Bot(TOKEN)


def telegram_webhook():
    data = request.get_json()

    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # 📌 /start command
        if text == "/start":

            current_time = time_engine.get_current_time()
            session = time_engine.get_session()

            # 📰 News Analysis (مبدئي فارغ الآن)
            news = news_engine.analyze_news()

            # 🧠 Market State Engine (مرتبط بالأخبار)
            state = market.get_market_state(
                news_risk=news["risk"]
            )

            bot.sendMessage(
                chat_id,
                f"""🤖 ULTRA V10 CORE ACTIVE ✔

🕒 الوقت: {current_time}
🌍 الجلسة: {session}

📰 NEWS STATUS:
⚠️ Risk: {news['risk']}
📊 Impact Score: {news['impact_score']}

📊 MARKET STATE:
⚡ الحالة: {state['state']}
🧠 السبب: {state['reason']}
"""
            )

    return "OK"
