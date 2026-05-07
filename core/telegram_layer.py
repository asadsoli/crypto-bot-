from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time


class TelegramLayer:

    def __init__(self, token, signal_engine, market=None, news=None, risk=None, time_engine=None):

        self.bot = Bot(token)

        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        self.time_engine = time_engine

        # =========================
        # 🧠 STATE CONTROL
        # =========================

        self.bot_active = True
        self.selected_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

        # =========================
        # 🔍 SCANNER (ADDED - SAFE EXTENSION)
        # =========================

        self.scan_assets = [
            "BTCUSDT",
            "ETHUSDT",
            "XAUUSD",
            "SOLUSDT"
        ]

        self.scanner_active = False

        # =========================
        # 🧠 V3 AI MULTI TIMEFRAME (ADDED)
        # =========================

        self.timeframes = {
            "scalp": "1m",
            "confirm": "5m",
            "trend": "15m"
        }

    # =========================
    # 🎛 UI MENU
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
    # 🧠 V3 MULTI TIMEFRAME CONTEXT (ADDED)
    # =========================

    def get_multi_timeframe_context(self, asset):

        try:

            context = {
                "scalp": {"trend": "neutral", "strength": 50},
                "confirm": {"trend": "neutral", "strength": 55},
                "trend": {"trend": "neutral", "strength": 60}
            }

            if self.market and hasattr(self.market, "get_multi_tf"):
                context = self.market.get_multi_tf(asset)

            return context

        except Exception as e:

            print("MTF error:", e)

            return {
                "scalp": {"trend": "neutral", "strength": 50},
                "confirm": {"trend": "neutral", "strength": 50},
                "trend": {"trend": "neutral", "strength": 50}
            }

    # =========================
    # 📊 FORMAT SIGNAL
    # =========================

    def format_result(self, r):

        return f"""🤖 ULTRA V10 ANALYSIS

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
    # ⚙️ STATUS
    # =========================

    def status(self):

        return f"""⚙️ ULTRA V10 STATUS

🤖 BOT: {'🟢 RUNNING' if self.bot_active else '🔴 STOPPED'}

💰 ASSET: {self.selected_asset}
⚙️ MODE: {self.risk_mode}
🔍 SCANNER: {'🟢 ACTIVE' if self.scanner_active else '🔴 OFF'}
"""

    # =========================
    # 🔍 SCANNER LOOP (UNCHANGED)
    # =========================

    def scanner_loop(self):

        print("🔍 SCANNER STARTED")

        while self.scanner_active:

            best_signal = None
            best_asset = None
            best_confidence = 0

            for asset in self.scan_assets:

                try:

                    if hasattr(self.signal_engine, "analyze_asset"):
                        result = self.signal_engine.analyze_asset(asset)
                    else:
                        result = self.signal_engine.analyze(
                            market_state={"state": "ACTIVE"},
                            news={"risk": "NORMAL"},
                            risk={"decision": "ALLOW"}
                        )

                    if not result:
                        continue

                    confidence = result.get("confidence", 0)

                    if confidence > best_confidence and result.get("signal") != "NO TRADE":

                        best_signal = result
                        best_asset = asset
                        best_confidence = confidence

                except Exception as e:
                    print("Scanner error:", e)

            if best_signal and best_confidence >= 75:

                try:

                    msg = f"""🔍 ULTRA SCANNER

💰 ASSET: {best_asset}

📊 SIGNAL: {best_signal.get('signal')}
🎯 ENTRY: {best_signal.get('entry', 'N/A')}
🛑 SL: {best_signal.get('sl', 'N/A')}
💰 TP: {best_signal.get('tp', 'N/A')}

💎 CONF: {best_signal.get('confidence', 0)}%
🏆 QUALITY: {best_signal.get('quality', '')}
📍 REASON: {best_signal.get('reason', '')}
"""

                    self.bot.sendMessage("<CHAT_ID>", msg)

                except:
                    pass

            time.sleep(60)

    # =========================
    # 🚀 SCANNER CONTROL
    # =========================

    def start_scanner(self):

        if self.scanner_active:
            return

        self.scanner_active = True
        threading.Thread(target=self.scanner_loop).start()

    def stop_scanner(self):

        self.scanner_active = False

    # =========================
    # 🧠 HANDLER (UNCHANGED)
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
                        "🤖 ULTRA V10 SYSTEM\n\nاختر من اللوحة:",
                        reply_markup=self.menu()
                    )

            else:

                query_id, chat_id, data = glance(msg, flavor="callback_query")

                if data == "bot_on":
                    self.bot_active = True
                    self.bot.sendMessage(chat_id, "🟢 BOT STARTED")

                elif data == "bot_off":
                    self.bot_active = False
                    self.bot.sendMessage(chat_id, "🔴 BOT STOPPED")

                elif data.startswith("asset_"):

                    self.selected_asset = data.split("_")[1]

                    if self.market:
                        self.market.symbol = self.selected_asset

                    self.bot.sendMessage(chat_id, f"💰 ASSET SET: {self.selected_asset}")

                elif data == "analyze":

                    if not self.bot_active:
                        self.bot.sendMessage(chat_id, "⛔ BOT STOPPED")
                        return

                    try:

                        # =========================
                        # 🧠 V3 CONTEXT ADDED HERE
                        # =========================

                        mtf = self.get_multi_timeframe_context(self.selected_asset)

                        if hasattr(self.signal_engine, "analyze_asset"):
                            result = self.signal_engine.analyze_asset(self.selected_asset)
                        else:
                            result = self.signal_engine.analyze(
                                market_state={"state": "ACTIVE"},
                                news={"risk": "NORMAL"},
                                risk={"decision": "ALLOW"}
                            )

                        # 🔥 إضافة سياق V3 للنتيجة بدون كسر النظام
                        result["mtf"] = mtf

                        self.bot.sendMessage(chat_id, self.format_result(result))

                    except Exception as e:
                        self.bot.sendMessage(chat_id, f"❌ ERROR: {str(e)}")

                elif data == "scan_on":
                    self.start_scanner()
                    self.bot.sendMessage(chat_id, "🔍 SCANNER STARTED")

                elif data == "scan_off":
                    self.stop_scanner()
                    self.bot.sendMessage(chat_id, "⛔ SCANNER STOPPED")

                elif data == "status":
                    self.bot.sendMessage(chat_id, self.status())

        except Exception as e:
            print("Telegram Layer Crash:", e)

    # =========================
    # 🚀 RUN
    # =========================

    def run(self):

        MessageLoop(self.bot, self.handle).run_as_thread()

        print("🤖
