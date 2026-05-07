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
        # 🔍 SCANNER (SAFE)
        # =========================

        self.scan_assets = [
            "BTCUSDT",
            "ETHUSDT",
            "XAUUSD",
            "SOLUSDT"
        ]

        self.scanner_active = False

        # =========================
        # 🔗 SCANNER LINK (NEW - SAFE ADDITION)
        # =========================

        self.scanner = None

        # =========================
        # 🧠 V3 MULTI TIMEFRAME
        # =========================

        self.timeframes = {
            "scalp": "1m",
            "confirm": "5m",
            "trend": "15m"
        }

        # =========================
        # 📰 V3 NEWS AI
        # =========================

        self.news_block_level = {
            "LOW": 0,
            "NORMAL": 10,
            "MEDIUM": 25,
            "HIGH": 100
        }

        self.block_high_news = True

    # =========================
    # 🔗 LINK SCANNER (NEW)
    # =========================

    def set_scanner(self, scanner):

        self.scanner = scanner
        print("🔗 Scanner linked to TelegramLayer")

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
    # 🧠 NEWS AI ENGINE
    # =========================

    def get_news_ai(self):

        try:

            if not self.news:
                return {"risk": "NORMAL", "score": 10, "impact": 0}

            news = self.news.analyze_news()

            risk = news.get("risk", "NORMAL")

            return {
                "risk": risk,
                "score": self.news_block_level.get(risk, 10),
                "impact": news.get("impact_score", 0)
            }

        except Exception as e:

            print("NEWS AI ERROR:", e)

            return {"risk": "NORMAL", "score": 10, "impact": 0}

    # =========================
    # 🌍 SESSION AI ENGINE
    # =========================

    def get_session_ai(self):

        try:

            if not self.time_engine:
                return {"session": "UNKNOWN", "bias": "NORMAL"}

            session = self.time_engine.get_session()

            if session in ["LONDON", "NEW YORK"]:
                return {"session": session, "bias": "HIGH_VOLATILITY"}

            return {"session": session, "bias": "LOW_VOLATILITY"}

        except:

            return {"session": "UNKNOWN", "bias": "NORMAL"}

    # =========================
    # 📊 FORMAT RESULT
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

🧠 NEWS: {r.get('ai_context', {}).get('news_risk', 'N/A')}
🌍 SESSION: {r.get('ai_context', {}).get('session', 'N/A')}

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
    # 🔍 SCANNER LOOP
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
    # 🚀 CONTROL SCANNER
    # =========================

    def start_scanner(self):

        if self.scanner_active:
            return

        self.scanner_active = True
        threading.Thread(target=self.scanner_loop).start()

    def stop_scanner(self):

        self.scanner_active = False

    # =========================
    # 🧠 HANDLER
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

                        news_ai = self.get_news_ai()
                        session_ai = self.get_session_ai()

                        if self.block_high_news and news_ai["risk"] == "HIGH":
                            self.bot.sendMessage(chat_id, "⛔ BLOCKED: HIGH IMPACT NEWS")
                            return

                        if hasattr(self.signal_engine, "analyze_asset"):
                            result = self.signal_engine.analyze_asset(self.selected_asset)
                        else:
                            result = self.signal_engine.analyze(
                                market_state={"state": "ACTIVE"},
                                news={"risk": "NORMAL"},
                                risk={"decision": "ALLOW"}
                            )

                        result["ai_context"] = {
                            "news_risk": news_ai["risk"],
                            "session": session_ai["session"],
                            "bias": session_ai["bias"]
                        }

                        if news_ai["risk"] == "HIGH":
                            result["confidence"] = max(0, result.get("confidence", 0) - 30)

                        self.bot.sendMessage(chat_id, self.format_result(result))

                    except Exception as e:
                        self.bot.sendMessage(chat_id, f"❌ ERROR: {str(e)}")

                elif data == "scan_on":

                    if self.scanner:
                        self.scanner.start()
                    else:
                        self.start_scanner()

                    self.bot.sendMessage(chat_id, "🔍 SCANNER STARTED")

                elif data == "scan_off":

                    if self.scanner:
                        self.scanner.stop()
                    else:
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

        print("🤖 ULTRA V10 TELEGRAM LAYER READY ✔")
