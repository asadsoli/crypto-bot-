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

# 🛑 حماية من انهيار البوت
if not TOKEN:
    raise Exception("TELEGRAM_TOKEN is missing!")

bot = telepot.Bot(TOKEN)


# =========================
# 🤖 TELEGRAM LAYER
# =========================
class TelegramLayer:

    def __init__(self, token, signal_engine, market, news_engine, risk_manager, time_engine):

        self.bot = telepot.Bot(token)

        self.signal_engine = signal_engine
        self.market = market
        self.news_engine = news_engine
        self.risk_manager = risk_manager
        self.time_engine = time_engine

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


# =========================
# 🔥 INIT LAYER (FIXED)
# =========================
telegram_layer = TelegramLayer(
    TOKEN,
    signal_engine,
    market,
    news_engine,
    risk_manager,
    time_engine
)


# =========================
# 🌐 WEBHOOK
# =========================
def telegram_webhook():

    try:

        data = request.get_json()

        print("📩 UPDATE RECEIVED:", data)

        if not data or "message" not in data:
            return "OK"

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # =========================
        # /start
        # =========================
        if text == "/start":

            current_time = time_engine.get_current_time()
            session = time_engine.get_session()

            try:
                news = news_engine.analyze_news()
            except:
                news = {"risk": "UNKNOWN", "impact_score": 0}

            try:
                state = market.get_market_state(news_risk=news["risk"])
            except:
                state = {"state": "UNKNOWN", "reason": "Fallback mode"}

            try:
                risk = risk_manager.evaluate(
                    market_state=state,
                    news=news,
                    volatility=0
                )
            except:
                risk = {
                    "decision": "ALLOW",
                    "score": 0,
                    "reason": "Fallback protection"
                }

            try:
                signal = signal_engine.analyze(
                    market_state=state,
                    news=news,
                    risk=risk
                )
            except:
                signal = {
                    "signal": "SYSTEM ERROR",
                    "entry": "N/A",
                    "sl": "N/A",
                    "tp": "N/A",
                    "confidence": "N/A",
                    "quality": "SAFE MODE"
                }

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
