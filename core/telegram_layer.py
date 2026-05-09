from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time

# 🧠 BRAIN IMPORT
from core.brain_core import BrainCore


class TelegramLayer:

    def __init__(self, token, signal_engine, market=None, news=None, risk=None, time_engine=None):

        self.bot = Bot(token)

        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        self.time_engine = time_engine

        # =========================
        # 🧠 BRAIN CORE CONNECT
        # =========================
        self.brain = BrainCore(
            signal_engine=self.signal_engine,
            market=self.market,
            news=self.news,
            risk=self.risk
        )

        # =========================
        # 🧠 STATE CONTROL
        # =========================
        self.bot_active = True
        self.selected_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

        # =========================
        # 🔍 SCANNER
        # =========================
        self.scan_assets = ["BTCUSDT", "ETHUSDT", "XAUUSD", "SOLUSDT"]
        self.scanner_active = False
        self.scanner = None

    # =========================
    # 🔗 LINK SCANNER
    # =========================
    def set_scanner(self, scanner):
        self.scanner = scanner

    # =========================
    # 🎛 MENU
    # =========================
    def menu(self):

        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("📊 تحليل السوق", callback_data="analyze")],
            [
                InlineKeyboardButton("🥇 BTC", callback_data="asset_BTCUSDT"),
                InlineKeyboardButton("💎 ETH", callback_data="asset_ETHUSDT")
            ],
            [
                InlineKeyboardButton("💰 GOLD", callback_data="asset_XAUUSD"),
                InlineKeyboardButton("⚡ SOL", callback_data="asset_SOLUSDT")
            ],
            [
                InlineKeyboardButton("🟢 تشغيل", callback_data="bot_on"),
                InlineKeyboardButton("🔴 إيقاف", callback_data="bot_off")
            ],
            [
                InlineKeyboardButton("🔍 Scanner ON", callback_data="scan_on"),
                InlineKeyboardButton("⛔ Scanner OFF", callback_data="scan_off")
            ],
            [InlineKeyboardButton("⚙️ الحالة", callback_data="status")]
        ])

    # =========================
    # 📊 FORMAT
    # =========================
    def format_result(self, r):

        return f"""🤖 ULTRA V10 AI CORE

💰 ASSET: {self.selected_asset}

📊 SIGNAL: {r.get('signal')}
🎯 ENTRY: {r.get('entry', 'N/A')}
🛑 SL: {r.get('sl', 'N/A')}
💰 TP: {r.get('tp', 'N/A')}

💎 CONFIDENCE: {r.get('confidence', 0)}%
🏆 QUALITY: {r.get('quality', 'N/A')}

📍 REASON:
{r.get('reason', '')}
"""

    # =========================
    # 🔍 ANALYZE (🔥 BRAIN USED HERE)
    # =========================
    def analyze_asset(self):

        return self.brain.analyze(self.selected_asset)

    # =========================
    # 🧠 HANDLER (IMPORTANT CHANGE)
    # =========================
    def handle(self, msg):

        try:

            flavor = msg.get("flavor")

            if flavor != "callback_query":

                content_type, chat_type, chat_id = glance(msg)
                text = msg.get("text", "").strip()

                if text == "/start":

                    self.bot.sendMessage(
                        chat_id,
                        "🤖 ULTRA V10 SYSTEM",
                        reply_markup=self.menu()
                    )

            else:

                query_id, chat_id, data = glance(msg, flavor="callback_query")

                # =========================
                # 📊 ANALYZE (🔥 BRAIN CALL)
                # =========================
                if data == "analyze":

                    if not self.bot_active:
                        self.bot.sendMessage(chat_id, "⛔ BOT STOPPED")
                        return

                    result = self.brain.analyze(self.selected_asset)

                    self.bot.sendMessage(chat_id, self.format_result(result))

                elif data == "bot_on":
                    self.bot_active = True
                    self.bot.sendMessage(chat_id, "🟢 BOT STARTED")

                elif data == "bot_off":
                    self.bot_active = False
                    self.bot.sendMessage(chat_id, "🔴 BOT STOPPED")

                elif data.startswith("asset_"):
                    self.selected_asset = data.split("_")[1]
                    self.bot.sendMessage(chat_id, f"💰 {self.selected_asset}")

                elif data == "status":
                    self.bot.sendMessage(chat_id, "⚙️ SYSTEM ACTIVE")

        except Exception as e:
            print("Telegram Layer Crash:", e)

    # =========================
    # 🚀 RUN
    # =========================
    def run(self):
        MessageLoop(self.bot, self.handle).run_as_thread()
        print("🤖 ULTRA V10 READY WITH BRAIN ✔")
