import os
import traceback
import telepot

from flask import Flask, request

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
# 🤖 TELEGRAM LAYER CORE
# =========================

class TelegramLayer:

    def __init__(self, token):

        self.bot = telepot.Bot(token)

        # 🧠 STATE
        self.bot_active = True
        self.selected_asset = "BTCUSDT"

    # =========================
    # 📤 SEND SAFE
    # =========================

    def send(self, chat_id, text, keyboard=None):

        try:

            if keyboard:
                self.bot.sendMessage(chat_id, text, reply_markup=keyboard)
            else:
                self.bot.sendMessage(chat_id, text)

        except Exception as e:
            print("❌ SEND ERROR:", e)

    # =========================
    # 🎛 KEYBOARD
    # =========================

    def keyboard(self):

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
    # 📊 FORMAT
    # =========================

    def format(self, signal, state, risk, news):

        return f"""🤖 ULTRA V10 CORE

💰 ASSET: {self.selected_asset}

📊 SIGNAL: {signal.get('signal')}
🎯 ENTRY: {signal.get('entry', 'N/A')}
🛑 SL: {signal.get('sl', 'N/A')}
💰 TP: {signal.get('tp', 'N/A')}

💎 CONF: {signal.get('confidence', 0)}%
🏆 QUALITY: {signal.get('quality', 'N/A')}

📊 MARKET: {state.get('state')}
🛡 RISK: {risk.get('decision')}
📰 NEWS: {news.get('risk')}
"""

# =========================
# 🚀 INIT LAYER
# =========================

telegram_layer = TelegramLayer(TOKEN)

# =========================
# 🌐 FLASK APP
# =========================

app = Flask(__name__)

# =========================
# 🌐 WEBHOOK
# =========================

def telegram_webhook():

    try:

        data = request.get_json()

        if not data or "message" not in data:
            return "OK"

        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        # =========================
        # START
        # =========================

        if text == "/start":

            telegram_layer.send(
                chat_id,
                "🤖 ULTRA V10 READY",
                telegram_layer.keyboard()
            )

        # =========================
        # BOT CONTROL
        # =========================

        elif text == "🟢 تشغيل البوت":
            telegram_layer.bot_active = True
            telegram_layer.send(chat_id, "🟢 BOT ON")

        elif text == "🔴 إيقاف البوت":
            telegram_layer.bot_active = False
            telegram_layer.send(chat_id, "🔴 BOT OFF")

        # =========================
        # ASSET SWITCH
        # =========================

        elif text in ["💰 BTCUSDT", "💰 ETHUSDT"]:

            asset = text.split(" ")[1]
            telegram_layer.selected_asset = asset
            telegram_layer.send(chat_id, f"💰 {asset} SELECTED")

        # =========================
        # STATUS
        # =========================

        elif text == "⚙️ الحالة":

            status = "🟢 RUNNING" if telegram_layer.bot_active else "🔴 STOPPED"

            telegram_layer.send(
                chat_id,
                f"""⚙️ STATUS

🤖 BOT: {status}
💰 ASSET: {telegram_layer.selected_asset}
"""
            )

        # =========================
        # ANALYSIS CORE
        # =========================

        elif text == "📊 تحليل السوق":

            if not telegram_layer.bot_active:
                telegram_layer.send(chat_id, "🔴 BOT STOPPED")
                return "OK"

            try:

                news = news_engine.analyze_news()
            except:
                news = {"risk": "UNKNOWN"}

            try:

                state = market.get_market_state(news_risk=news["risk"])
            except:
                state = {"state": "UNKNOWN"}

            try:

                risk = risk_manager.evaluate(
                    market_state=state,
                    news=news,
                    volatility=0
                )
            except:
                risk = {"decision": "ALLOW"}

            try:

                signal = signal_engine.analyze(
                    market_state=state,
                    news=news,
                    risk=risk
                )
            except Exception as e:

                print("SIGNAL ERROR:", e)
                traceback.print_exc()

                signal = {"signal": "NO TRADE"}

            response = telegram_layer.format(signal, state, risk, news)

            telegram_layer.send(chat_id, response)

        return "OK"

    except Exception as e:

        print("❌ WEBHOOK ERROR:", e)
        traceback.print_exc()

        return "OK"

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return "ULTRA V10 ACTIVE ✔"

@app.route("/webhook", methods=["POST"])
def webhook():
    return telegram_webhook()

# =========================
# 🚀 START
# =========================

if __name__ == "__main__":

    # 🔥 هنا سنربط Scanner في المرحلة التالية فقط (Phase 2)
    # scanner.start()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
)
