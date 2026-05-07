import os
import traceback
import telepot

from flask import request

from core.time_engine import TimeEngine
from core.market_state import MarketStateEngine
from core.news_engine import NewsEngine
from core.risk_manager import RiskManager
from core.signal_engine import SignalEngine

# 🧠 Engines Initialization
time_engine = TimeEngine()
market = MarketStateEngine()
news_engine = NewsEngine()
risk_manager = RiskManager()
signal_engine = SignalEngine()

# 🔑 Telegram Token
TOKEN = os.environ.get("TELEGRAM_TOKEN")

print("🔑 TOKEN LOADED:", TOKEN is not None)

bot = telepot.Bot(TOKEN)


# =========================
# 🤖 TELEGRAM LAYER (NEW ADDITION - SAFE)
# =========================
class TelegramLayer:

    def __init__(self, token, signal_engine):
        self.bot = telepot.Bot(token)
        self.signal_engine = signal_engine

    def send_message(self, chat_id, text):
        try:
            self.bot.sendMessage(chat_id, text)
        except Exception as e:
            print("❌ Telegram Send Error:", e)

    def format_signal(self, current_time, session, news, state, risk, signal):

        return f"""🤖 ULTRA V10 CORE ACTIVE ✔

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

💰 SIGNAL ENGINE:
📊 القرار: {signal['signal']}
📈 Entry: {signal.get('entry', 'N/A')}
🛑 SL: {signal.get('sl', 'N/A')}
🎯 TP: {signal.get('tp', 'N/A')}
💎 Confidence: {signal.get('confidence', 'N/A')}%
🏆 Quality: {signal.get('quality', 'N/A')}
"""


telegram_layer = TelegramLayer(TOKEN, signal_engine)


# =========================
# 🌐 WEBHOOK
# =========================
def telegram_webhook():

    try:

        data = request.get_json()

        print("📩 UPDATE RECEIVED:", data)

        if not data:
            return "OK"

        if "message" not in data:
            return "OK"

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # 📌 /start command
        if text == "/start":

            current_time = time_engine.get_current_time()
            session = time_engine.get_session()

            # 📰 NEWS ENGINE
            try:
                news = news_engine.analyze_news()

            except Exception as e:
                print("❌ NEWS ENGINE ERROR:", str(e))
                news = {"risk": "UNKNOWN", "impact_score": 0}

            # 🧠 MARKET STATE
            try:
                state = market.get_market_state(news_risk=news["risk"])

            except Exception as e:
                print("❌ MARKET STATE ERROR:", str(e))
                state = {"state": "UNKNOWN", "reason": "Fallback mode"}

            # 🛡 RISK MANAGER
            try:
                risk = risk_manager.evaluate(
                    market_state=state,
                    news=news,
                    volatility=0
                )

            except Exception as e:
                print("❌ RISK MANAGER ERROR:", str(e))
                risk = {
                    "decision": "ALLOW",
                    "score": 0,
                    "reason": "Fallback protection"
                }

            # 💰 SIGNAL ENGINE
            try:
                signal = signal_engine.analyze(
                    market_state=state,
                    news=news,
                    risk=risk
                )

            except Exception as e:
                print("❌ SIGNAL ENGINE ERROR:", str(e))
                traceback.print_exc()

                signal = {
                    "signal": "SYSTEM ERROR",
                    "entry": "N/A",
                    "sl": "N/A",
                    "tp": "N/A",
                    "confidence": "N/A",
                    "quality": "SAFE MODE"
                }

            # 📤 SEND RESPONSE (via Telegram Layer)
            message = telegram_layer.format_signal(
                current_time,
                session,
                news,
                state,
                risk,
                signal
            )

            telegram_layer.send_message(chat_id, message)

        return "OK"

    except Exception as e:
        print("❌ WEBHOOK CRASH:", str(e))
        traceback.print_exc()
        return "OK"
