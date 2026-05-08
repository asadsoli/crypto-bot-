import os
import traceback
import telepot
import threading
import time

from flask import Flask, request

from core.time_engine import TimeEngine
from core.market_state import MarketStateEngine
from core.news_engine import NewsEngine
from core.risk_manager import RiskManager
from core.signal_engine import SignalEngine

# 🧠 BRAIN CORE
from core.brain_core import BrainCore

# 🔍 SCANNER
from core.scanner_engine import ScannerEngine

# =========================
# 🧠 ENGINES
# =========================

time_engine = TimeEngine()
market = MarketStateEngine()
news_engine = NewsEngine()
risk_manager = RiskManager()
signal_engine = SignalEngine()

# =========================
# 🧠 BRAIN INIT
# =========================

brain = BrainCore(
    signal_engine=signal_engine,
    market=market,
    news=news_engine,
    risk=risk_manager
)

# =========================
# 🔍 INIT SCANNER
# =========================

scanner = ScannerEngine(signal_engine)

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
                self.bot.sendMessage(
                    chat_id,
                    text,
                    reply_markup=keyboard
                )

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

                [
                    {"text": "💰 BTCUSDT"},
                    {"text": "💰 ETHUSDT"}
                ],

                [
                    {"text": "🥇 XAUUSD"},
                    {"text": "⚡ SOLUSDT"}
                ],

                [
                    {"text": "🟢 تشغيل البوت"},
                    {"text": "🔴 إيقاف البوت"}
                ],

                [
                    {"text": "🔍 تشغيل Scanner"},
                    {"text": "⛔ إيقاف Scanner"}
                ],

                [{"text": "⚙️ الحالة"}]
            ],

            "resize_keyboard": True
        }

    # =========================
    # 📊 FORMAT
    # =========================

    def format(
        self,
        asset,
        decision,
        signal,
        state,
        risk,
        news,
        current_time,
        session
    ):

        return f"""🤖 ULTRA V10 AI CORE

🕒 الوقت: {current_time}
🌍 الجلسة: {session}

💰 الأصل: {asset}

📊 القرار:
{decision}

📈 الإشارة:
{signal.get('signal', 'N/A')}

🎯 ENTRY:
{signal.get('entry', 'N/A')}

🛑 SL:
{signal.get('sl', 'N/A')}

💰 TP:
{signal.get('tp', 'N/A')}

💎 CONFIDENCE:
{signal.get('confidence', 0)}%

🏆 QUALITY:
{signal.get('quality', 'N/A')}

📊 MARKET:
{state.get('state', 'UNKNOWN')}

🛡 RISK:
{risk.get('decision', 'UNKNOWN')}

📰 NEWS:
{news.get('risk', 'UNKNOWN')}

📍 السبب:
{signal.get('reason', 'N/A')}
"""

# =========================
# 🚀 INIT LAYER
# =========================

telegram_layer = TelegramLayer(TOKEN)

# =========================
# 🔍 SCANNER CALLBACK
# =========================

def scanner_callback(best_signal):

    try:

        msg = f"""🔍 ULTRA SCANNER SIGNAL

💰 ASSET:
{best_signal['asset']}

📊 SIGNAL:
{best_signal['signal']}

🎯 ENTRY:
{best_signal['entry']}

🛑 SL:
{best_signal['sl']}

💰 TP:
{best_signal['tp']}

💎 CONF:
{best_signal['confidence']}%

🏆 QUALITY:
{best_signal['quality']}

📍 REASON:
{best_signal['reason']}
"""

        # ⚠️ ضع CHAT ID لاحقاً
        telegram_layer.bot.sendMessage(
            "<CHAT_ID>",
            msg
        )

    except Exception as e:
        print("❌ Scanner Callback Error:", e)

# =========================
# 🔁 SCANNER THREAD
# =========================

def start_scanner_thread():

    def run():

        scanner.start(
            callback=scanner_callback
        )

    thread = threading.Thread(
        target=run,
        daemon=True
    )

    thread.start()

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
        # 🚀 START
        # =========================

        if text == "/start":

            telegram_layer.send(
                chat_id,
                "🤖 ULTRA V10 READY",
                telegram_layer.keyboard()
            )

        # =========================
        # 🟢 BOT ON
        # =========================

        elif text == "🟢 تشغيل البوت":

            telegram_layer.bot_active = True

            telegram_layer.send(
                chat_id,
                "🟢 تم تشغيل البوت"
            )

        # =========================
        # 🔴 BOT OFF
        # =========================

        elif text == "🔴 إيقاف البوت":

            telegram_layer.bot_active = False

            telegram_layer.send(
                chat_id,
                "🔴 تم إيقاف البوت"
            )

        # =========================
        # 🔍 SCANNER ON
        # =========================

        elif text == "🔍 تشغيل Scanner":

            start_scanner_thread()

            telegram_layer.send(
                chat_id,
                "🔍 تم تشغيل Scanner"
            )

        # =========================
        # ⛔ SCANNER OFF
        # =========================

        elif text == "⛔ إيقاف Scanner":

            scanner.stop()

            telegram_layer.send(
                chat_id,
                "⛔ تم إيقاف Scanner"
            )

        # =========================
        # 💰 ASSET SWITCH
        # =========================

        elif text in [
            "💰 BTCUSDT",
            "💰 ETHUSDT",
            "🥇 XAUUSD",
            "⚡ SOLUSDT"
        ]:

            asset = text.split(" ")[1]

            telegram_layer.selected_asset = asset

            telegram_layer.send(
                chat_id,
                f"✅ تم اختيار {asset}"
            )

        # =========================
        # ⚙️ STATUS
        # =========================

        elif text == "⚙️ الحالة":

            status = (
                "🟢 يعمل"
                if telegram_layer.bot_active
                else "🔴 متوقف"
            )

            telegram_layer.send(
                chat_id,
                f"""⚙️ ULTRA STATUS

🤖 البوت:
{status}

💰 الأصل الحالي:
{telegram_layer.selected_asset}
"""
            )

        # =========================
        # 📊 ANALYSIS
        # =========================

        elif text == "📊 تحليل السوق":

            if not telegram_layer.bot_active:

                telegram_layer.send(
                    chat_id,
                    "🔴 البوت متوقف"
                )

                return "OK"

            asset = telegram_layer.selected_asset

            # =========================
            # 🕒 TIME + SESSION
            # =========================

            try:
                current_time = time_engine.get_current_time()
            except:
                current_time = "UNKNOWN"

            try:
                session = time_engine.get_session()
            except:
                session = "UNKNOWN"

            # =========================
            # 🧠 BRAIN ANALYSIS
            # =========================

            try:

                result = brain.analyze(asset)

                signal = result.get(
                    "signal",
                    {}
                )

                decision = result.get(
                    "decision",
                    "WAIT"
                )

            except Exception as e:

                print("❌ BRAIN ERROR:", e)

                traceback.print_exc()

                result = {
                    "decision": "ERROR",
                    "signal": {
                        "signal": "SYSTEM ERROR",
                        "confidence": 0
                    }
                }

                signal = result["signal"]

                decision = result["decision"]

            # =========================
            # 📰 NEWS
            # =========================

            try:
                news = news_engine.analyze_news()
            except:
                news = {"risk": "UNKNOWN"}

            # =========================
            # 📊 MARKET
            # =========================

            try:
                state = market.get_market_state(
                    news_risk=news["risk"]
                )
            except:
                state = {"state": "UNKNOWN"}

            # =========================
            # 🛡 RISK
            # =========================

            try:
                risk = risk_manager.evaluate(
                    market_state=state,
                    news=news,
                    volatility=0
                )
            except:
                risk = {"decision": "UNKNOWN"}

            # =========================
            # 📤 RESPONSE
            # =========================

            response = telegram_layer.format(
                asset=asset,
                decision=decision,
                signal=signal,
                state=state,
                risk=risk,
                news=news,
                current_time=current_time,
                session=session
            )

            telegram_layer.send(
                chat_id,
                response
            )

        return "OK"

    except Exception as e:

        print("❌ WEBHOOK ERROR:", e)

        traceback.print_exc()

        return "OK"

# =========================
# 🌐 ROUTES
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

    print("🧠 BrainCore Connected ✔")

    print("🔍 Scanner Ready ✔")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False
                )
