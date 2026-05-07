import os
import traceback
import telepot

from flask import request

from core.time_engine import TimeEngine
from core.market_state import MarketStateEngine
from core.news_engine import NewsEngine
from core.risk_manager import RiskManager
from core.signal_engine import SignalEngine

# =========================
# 🧠 ENGINES
# =========================

time_engine = TimeEngine()
market = MarketStateEngine()
news_engine = NewsEngine()
risk_manager = RiskManager()
signal_engine = SignalEngine()

# =========================
# 🔑 TOKEN
# =========================

TOKEN = os.environ.get("TELEGRAM_TOKEN")

print("🔑 TOKEN LOADED:", TOKEN is not None)

if not TOKEN:
    raise Exception("TELEGRAM_TOKEN is missing!")

bot = telepot.Bot(TOKEN)

# =========================
# 🤖 TELEGRAM LAYER PRO
# =========================

class TelegramLayer:

    def __init__(self, token):

        self.bot = telepot.Bot(token)

        self.bot_active = True
        self.selected_asset = "BTCUSDT"

    # =========================
    # 📤 SEND MESSAGE
    # =========================

    def send_message(self, chat_id, text, keyboard=None):

        try:

            if keyboard:
                self.bot.sendMessage(
                    chat_id,
                    text,
                    reply_markup=keyboard
                )

            else:
                self.bot.sendMessage(chat_id, text)

        except Exception as e:
            print("❌ Telegram Send Error:", e)

    # =========================
    # 🎛 MAIN PANEL
    # =========================

    def main_keyboard(self):

        return {
            "keyboard": [
                [{"text": "📊 تحليل السوق"}],
                [{"text": "💰 BTCUSDT"}, {"text": "💰 ETHUSDT"}],
                [{"text": "🟢 تشغيل البوت"}, {"text": "🔴 إيقاف البوت"}],
                [{"text": "⚙️ الحالة"}]
            ],
            "resize_keyboard": True
        }

    # =========================
    # 📊 FORMAT SIGNAL
    # =========================

    def format_signal(
        self,
        current_time,
        session,
        news,
        state,
        risk,
        signal
    ):

        return f"""🤖 ULTRA V10 CORE ACTIVE ✔

🕒 الوقت: {current_time}
🌍 الجلسة: {session}

📰 NEWS ENGINE
⚠️ Risk: {news['risk']}
📊 Impact: {news['impact_score']}

📊 MARKET STATE
⚡ الحالة: {state['state']}
🧠 السبب: {state['reason']}

🛡 RISK MANAGER
⚡ القرار: {risk['decision']}
📊 SCORE: {risk['score']}

💰 SIGNAL ENGINE
📊 القرار: {signal['signal']}
📈 Entry: {signal.get('entry', 'N/A')}
🛑 SL: {signal.get('sl', 'N/A')}
🎯 TP: {signal.get('tp', 'N/A')}
💎 Confidence: {signal.get('confidence', 'N/A')}%
🏆 Quality: {signal.get('quality', 'N/A')}

📍 ASSET: {self.selected_asset}
"""

# =========================
# 🚀 INIT TELEGRAM LAYER
# =========================

telegram_layer = TelegramLayer(TOKEN)

# =========================
# 🌐 WEBHOOK
# =========================

def telegram_webhook():

    try:

        data = request.get_json()

        print("📩 UPDATE:", data)

        if not data:
            return "OK"

        if "message" not in data:
            return "OK"

        message = data["message"]

        chat_id = message["chat"]["id"]

        text = message.get("text", "")

        # =========================
        # 🚀 START
        # =========================

        if text == "/start":

            telegram_layer.send_message(
                chat_id,
                "🤖 ULTRA V10 PANEL READY",
                telegram_layer.main_keyboard()
            )

            return "OK"

        # =========================
        # 🟢 START BOT
        # =========================

        if text == "🟢 تشغيل البوت":

            telegram_layer.bot_active = True

            telegram_layer.send_message(
                chat_id,
                "🟢 تم تشغيل البوت"
            )

            return "OK"

        # =========================
        # 🔴 STOP BOT
        # =========================

        if text == "🔴 إيقاف البوت":

            telegram_layer.bot_active = False

            telegram_layer.send_message(
                chat_id,
                "🔴 تم إيقاف البوت"
            )

            return "OK"

        # =========================
        # 💰 ASSET SWITCH
        # =========================

        if text == "💰 BTCUSDT":

            telegram_layer.selected_asset = "BTCUSDT"

            telegram_layer.send_message(
                chat_id,
                "💰 تم اختيار BTCUSDT"
            )

            return "OK"

        if text == "💰 ETHUSDT":

            telegram_layer.selected_asset = "ETHUSDT"

            telegram_layer.send_message(
                chat_id,
                "💰 تم اختيار ETHUSDT"
            )

            return "OK"

        # =========================
        # ⚙️ STATUS
        # =========================

        if text == "⚙️ الحالة":

            status = "🟢 يعمل" if telegram_layer.bot_active else "🔴 متوقف"

            telegram_layer.send_message(
                chat_id,
                f"""⚙️ ULTRA V10 STATUS

🤖 البوت: {status}

💰 العملة الحالية:
{telegram_layer.selected_asset}
"""
            )

            return "OK"

        # =========================
        # 📊 MARKET ANALYSIS
        # =========================

        if text == "📊 تحليل السوق":

            if not telegram_layer.bot_active:

                telegram_layer.send_message(
                    chat_id,
                    "🔴 البوت متوقف"
                )

                return "OK"

            current_time = time_engine.get_current_time()
            session = time_engine.get_session()

            # =========================
            # 📰 NEWS
            # =========================

            try:
                news = news_engine.analyze_news()

            except Exception as e:

                print("❌ NEWS ERROR:", e)

                news = {
                    "risk": "UNKNOWN",
                    "impact_score": 0
                }

            # =========================
            # 📊 MARKET STATE
            # =========================

            try:
                state = market.get_market_state(
                    news_risk=news["risk"]
                )

            except Exception as e:

                print("❌ MARKET ERROR:", e)

                state = {
                    "state": "UNKNOWN",
                    "reason": "Fallback"
                }

            # =========================
            # 🛡 RISK
            # =========================

            try:

                risk = risk_manager.evaluate(
                    market_state=state,
                    news=news,
                    volatility=0
                )

            except Exception as e:

                print("❌ RISK ERROR:", e)

                risk = {
                    "decision": "ALLOW",
                    "score": 0,
                    "reason": "Fallback"
                }

            # =========================
            # 💰 SIGNAL
            # =========================

            try:

                signal = signal_engine.analyze(
                    market_state=state,
                    news=news,
                    risk=risk
                )

            except Exception as e:

                print("❌ SIGNAL ERROR:", e)
                traceback.print_exc()

                signal = {
                    "signal": "SYSTEM ERROR",
                    "entry": "N/A",
                    "sl": "N/A",
                    "tp": "N/A",
                    "confidence": 0,
                    "quality": "SAFE MODE"
                }

            response = telegram_layer.format_signal(
                current_time,
                session,
                news,
                state,
                risk,
                signal
            )

            telegram_layer.send_message(chat_id, response)

            return "OK"

        return "OK"

    except Exception as e:

        print("❌ WEBHOOK CRASH:", e)
        traceback.print_exc()

        return "OK"
