from telepot import Bot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from core.brain_core import BrainCore


class TelegramLayer:

    def __init__(self, token, signal_engine, market=None, news=None, risk=None, time_engine=None):

        # =========================
        # 🤖 BOT CLIENT
        # =========================
        self.bot = Bot(token)

        # =========================
        # 🧠 DEPENDENCIES
        # =========================
        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        self.time_engine = time_engine

        # =========================
        # 🧠 BRAIN CORE
        # =========================
        self.brain = BrainCore(
            signal_engine=self.signal_engine,
            market=self.market,
            news=self.news,
            risk=self.risk
        )

        # =========================
        # ⚙️ STATE
        # =========================
        self.is_bot_active = True
        self.current_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

        # =========================
        # 🔍 WATCHLIST (FINAL FIXED)
        # =========================
        self.watchlist_assets = [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "PAXGUSDT",
            "SOLUSDT"
        ]

        # =========================
        # 🔁 SCANNER
        # =========================
        self.scanner = None

        # =========================
        # 🧠 SAFETY FLAG
        # =========================
        self.busy = False

    # =========================
    # 🔗 LINK SCANNER
    # =========================
    def set_scanner(self, scanner):

        self.scanner = scanner

        # sync watchlist -> scanner
        if hasattr(scanner, "assets"):
            scanner.assets = list(self.watchlist_assets)

        # 🔥 CRITICAL FIX: ensure scanner uses correct asset set
        if hasattr(scanner, "brain"):
            scanner.brain = self.brain

    # =========================
    # 🎛 MENU
    # =========================
    def menu(self):

        return InlineKeyboardMarkup(inline_keyboard=[

            [InlineKeyboardButton("📊 تحليل السوق", callback_data="analyze")],

            [
                InlineKeyboardButton("🥇 BTCUSDT", callback_data="asset_BTCUSDT"),
                InlineKeyboardButton("💎 ETHUSDT", callback_data="asset_ETHUSDT")
            ],

            [
                InlineKeyboardButton("💰 BNBUSDT", callback_data="asset_BNBUSDT"),
                InlineKeyboardButton("🏅 PAXGUSDT", callback_data="asset_PAXGUSDT")
            ],

            [
                InlineKeyboardButton("⚡ SOLUSDT", callback_data="asset_SOLUSDT")
            ],

            [
                InlineKeyboardButton("🟢 تشغيل", callback_data="bot_on"),
                InlineKeyboardButton("🔴 إيقاف", callback_data="bot_off")
            ],

            [
                InlineKeyboardButton("🔍 Scanner ON", callback_data="scan_on"),
                InlineKeyboardButton("⛔ Scanner OFF", callback_data="scan_off")
            ],

            [
                InlineKeyboardButton("⚙️ الحالة", callback_data="status")
            ]
        ])

    # =========================
    # 📊 FORMAT OUTPUT SAFE
    # =========================
    def format_result(self, signal_data):

        if not isinstance(signal_data, dict):
            return "❌ No signal data"

        return f"""🤖 ULTRA V10 AI CORE

💰 ASSET: {self.current_asset}

📊 SIGNAL: {signal_data.get('signal', 'N/A')}
🎯 ENTRY: {signal_data.get('entry', 'N/A')}
🛑 SL: {signal_data.get('sl', 'N/A')}
💰 TP: {signal_data.get('tp', 'N/A')}

💎 CONFIDENCE: {signal_data.get('confidence', 0)}%
🏆 QUALITY: {signal_data.get('quality', 'N/A')}

📍 REASON:
{signal_data.get('reason', 'N/A')}
"""

    # =========================
    # 📌 SET ASSET (FULL SYNC FIX)
    # =========================
    def set_asset(self, asset_symbol):

        try:

            if not asset_symbol:
                return False

            asset_symbol = str(asset_symbol).upper().strip()

            if asset_symbol not in self.watchlist_assets:
                return False

            self.current_asset = asset_symbol

            # =========================
            # SYNC SIGNAL ENGINE
            # =========================
            if self.signal_engine and hasattr(self.signal_engine, "set_asset"):
                try:
                    self.signal_engine.set_asset(asset_symbol)
                except:
                    pass

            # =========================
            # SYNC SCANNER (IMPORTANT FIX)
            # =========================
            if self.scanner and hasattr(self.scanner, "assets"):
                try:
                    self.scanner.assets = list(self.watchlist_assets)
                except:
                    pass

            return True

        except Exception as e:
            print("❌ set_asset error:", e)
            return False
