import os
import traceback
import threading
import time

import telepot   # 🔥 FIX 1: كان ناقص وهذا سبب الكراش

from flask import Flask, request

from core.time_engine import TimeEngine
from core.market_state import MarketStateEngine
from core.news_engine import NewsEngine
from core.risk_manager import RiskManager
from core.signal_engine import SignalEngine

from core.brain_core import BrainCore
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

# 🔥 FIX: ربط Brain مع SignalEngine
signal_engine.connect_brain(brain)


# =========================
# 🔍 SCANNER INIT
# =========================

scanner = ScannerEngine(brain)


# =========================
# 🔑 TOKEN
# =========================

TOKEN = os.environ.get("TELEGRAM_TOKEN")

print("🔑 TOKEN LOADED:", TOKEN is not None)

if not TOKEN:
    raise Exception("TELEGRAM_TOKEN is missing!")

bot = telepot.Bot(TOKEN)


# =========================
# 🔒 GLOBAL LOCKS
# =========================

scanner_lock = threading.Lock()
scanner_thread_started = False
analysis_lock = threading.Lock()


# =========================
# 🤖 TELEGRAM LAYER
# =========================

class TelegramLayer:

    def __init__(self, token):

        self.bot = telepot.Bot(token)

        self.bot_active = True
        self.selected_asset = "BTCUSDT"

    # =========================
    # 📤 SEND
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

                [
                    {"text": "💰 BTCUSDT"},
                    {"text": "💰 ETHUSDT"}
                ],

                [
                    {"text": "🥇 PAXGUSDT"},
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
    def format(self, asset, decision, signal, state, risk, news, current_time, session):

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


telegram_layer = TelegramLayer(TOKEN)


# =========================
# 🔍 SCANNER CALLBACK
# =========================

def scanner_callback(best_signal):

    if not best_signal:
        return

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

        telegram_layer.bot.sendMessage("<CHAT_ID>", msg)

    except Exception as e:
        print("❌ Scanner Callback Error:", e)


# =========================
# 🔁 SCANNER THREAD
# =========================

def start_scanner_thread():

    global scanner_thread_started

    with scanner_lock:

        if scanner_thread_started:
            return

        scanner_thread_started = True

        def run():
            scanner.start(callback=scanner_callback)

        threading.Thread(target=run, daemon=True).start()


# =========================
# 🌐 FLASK
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
            telegram_layer.send(chat_id, "🤖 ULTRA V10 READY", telegram_layer.keyboard())

        # =========================
        # BOT ON/OFF
        # =========================
        elif text == "🟢 تشغيل البوت":
            telegram_layer.bot_active = True

        elif text == "🔴 إيقاف البوت":
            telegram_layer.bot_active = False

        # =========================
        # SCANNER
        # =========================
        elif text == "🔍 تشغيل Scanner":
            start_scanner_thread()

        elif text == "⛔ إيقاف Scanner":
            scanner.stop()

        # =========================
        # ASSETS
        # =========================
        elif text in ["💰 BTCUSDT", "💰 ETHUSDT", "🥇 PAXGUSDT", "⚡ SOLUSDT"]:

            asset_map = {
                "💰 BTCUSDT": "BTCUSDT",
                "💰 ETHUSDT": "ETHUSDT",
                "🥇 PAXGUSDT": "PAXGUSDT",
                "⚡ SOLUSDT": "SOLUSDT"
            }

            asset = asset_map[text]

            telegram_layer.selected_asset = asset

            try:
                signal_engine.set_asset(asset)
            except:
                pass

        # =========================
        # ANALYSIS
        # =========================
        elif text == "📊 تحليل السوق":

            if not analysis_lock.acquire(blocking=False):
                telegram_layer.send(chat_id, "⚠ تحليل قيد التنفيذ")
                return "OK"

            try:

                asset = telegram_layer.selected_asset

                current_time = time_engine.get_current_time()
                session = time_engine.get_session()

                try:
                    signal_engine.set_asset(asset)
                    result = brain.analyze(asset)
                except Exception as e:
                    print("Brain error:", e)
                    result = {
                        "decision": "ERROR",
                        "signal": {"signal": "SYSTEM ERROR", "confidence": 0}
                    }

                signal = result.get("signal", {})
                decision = result.get("decision", "WAIT")

                news = news_engine.analyze_news()
                state = market.get_market_state(news_risk=news.get("risk", "NORMAL"))
                risk = risk_manager.evaluate(state, news, 0)

                response = telegram_layer.format(
                    asset, decision, signal, state, risk, news, current_time, session
                )

                telegram_layer.send(chat_id, response)

            finally:
                analysis_lock.release()

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
# 🚀 RUN
# =========================

if __name__ == "__main__":

    print("🧠 BrainCore Connected ✔")
    print("🔍 Scanner Ready ✔")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False,
        use_reloader=False
        )
