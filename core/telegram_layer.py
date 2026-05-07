from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


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

            [InlineKeyboardButton("⚙️ الحالة", callback_data="status")]
        ])

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
"""

    # =========================
    # 🧠 CORE HANDLER
    # =========================

    def handle(self, msg):

        try:

            flavor = msg.get("flavor")

            # =========================
            # 📩 NORMAL MESSAGE
            # =========================

            if flavor != "callback_query":

                content_type, chat_type, chat_id = glance(msg)
                text = msg.get("text", "").strip()

                if text == "/start":

                    self.bot.sendMessage(
                        chat_id,
                        "🤖 ULTRA V10 SYSTEM\n\nاختر من اللوحة:",
                        reply_markup=self.menu()
                    )

            # =========================
            # 🎛 CALLBACKS
            # =========================

            else:

                query_id, chat_id, data = glance(msg, flavor="callback_query")

                # =========================
                # ▶ BOT ON
                # =========================

                if data == "bot_on":
                    self.bot_active = True
                    self.bot.sendMessage(chat_id, "🟢 BOT STARTED")

                # =========================
                # ⛔ BOT OFF
                # =========================

                elif data == "bot_off":
                    self.bot_active = False
                    self.bot.sendMessage(chat_id, "🔴 BOT STOPPED")

                # =========================
                # 💰 CHANGE ASSET
                # =========================

                elif data.startswith("asset_"):

                    self.selected_asset = data.split("_")[1]

                    if self.market:
                        self.market.symbol = self.selected_asset

                    self.bot.sendMessage(chat_id, f"💰 ASSET SET: {self.selected_asset}")

                # =========================
                # 📊 ANALYZE (SAFE FIXED)
                # =========================

                elif data == "analyze":

                    if not self.bot_active:
                        self.bot.sendMessage(chat_id, "⛔ BOT STOPPED")
                        return

                    try:

                        # 🔥 دعم كلا النسختين بدون كسر النظام
                        if hasattr(self.signal_engine, "analyze_asset"):
                            result = self.signal_engine.analyze_asset(self.selected_asset)
                        else:
                            result = self.signal_engine.analyze(
                                market_state={"state": "ACTIVE"},
                                news={"risk": "NORMAL"},
                                risk={"decision": "ALLOW"}
                            )

                        if not result:
                            self.bot.sendMessage(chat_id, "⚠️ NO VALID SETUP")
                            return

                        self.bot.sendMessage(chat_id, self.format_result(result))

                    except Exception as e:
                        self.bot.sendMessage(chat_id, f"❌ ERROR: {str(e)}")

                # =========================
                # ⚙️ STATUS
                # =========================

                elif data == "status":
                    self.bot.sendMessage(chat_id, self.status())

        except Exception as e:
            print("❌ Telegram Layer Crash:", e)

    # =========================
    # 🚀 RUN BOT
    # =========================

    def run(self):

        MessageLoop(self.bot, self.handle).run_as_thread()

        print("🤖 ULTRA V10 TELEGRAM LAYER READY ✔")
