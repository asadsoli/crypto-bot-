from telepot import Bot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

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
        # 🧠 BRAIN CORE
        # =========================
        self.brain = BrainCore(
            signal_engine=self.signal_engine,
            market=self.market,
            news=self.news,
            risk=self.risk
        )

        # =========================
        # 🧠 STATE
        # =========================
        self.bot_active = True
        self.selected_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

        # =========================
        # 🔍 SCANNER ASSETS (MASTER LIST)
        # =========================
        self.scan_assets = [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "PAXGUSDT",
            "SOLUSDT"
        ]

        self.scanner_active = False
        self.scanner = None

    # =========================
    # 🔗 LINK SCANNER
    # =========================
    def set_scanner(self, scanner):

        self.scanner = scanner

        # 🔥 force sync assets
        if hasattr(scanner, "assets"):
            scanner.assets = list(self.scan_assets)

    # =========================
    # 🎛 TELEGRAM MENU
    # =========================
    def menu(self):

        return InlineKeyboardMarkup(inline_keyboard=[

            [
                InlineKeyboardButton("📊 تحليل السوق", callback_data="analyze")
            ],

            [
                InlineKeyboardButton("🥇 BTC", callback_data="asset_BTCUSDT"),
                InlineKeyboardButton("💎 ETH", callback_data="asset_ETHUSDT")
            ],

            [
                InlineKeyboardButton("💰 BNB", callback_data="asset_BNBUSDT"),
                InlineKeyboardButton("🏅 PAXG", callback_data="asset_PAXGUSDT")
            ],

            [
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

            [
                InlineKeyboardButton("⚙️ الحالة", callback_data="status")
            ]
        ])

    # =========================
    # 📊 FORMAT RESULT
    # =========================
    def format_result(self, r):

        return f"""🤖 ULTRA V10 AI CORE

💰 ASSET: {self.selected_asset}

📊 SIGNAL: {r.get('signal', 'N/A')}
🎯 ENTRY: {r.get('entry', 'N/A')}
🛑 SL: {r.get('sl', 'N/A')}
💰 TP: {r.get('tp', 'N/A')}

💎 CONFIDENCE: {r.get('confidence', 0)}%
🏆 QUALITY: {r.get('quality', 'N/A')}

📍 REASON:
{r.get('reason', 'N/A')}
"""

    # =========================
    # 📌 SAFE ASSET SWITCH
    # =========================
    def set_asset(self, asset):

        # منع أي رمز غير موجود
        if asset not in self.scan_assets:
            return False

        self.selected_asset = asset

        # 🔥 sync with signal engine
        if self.signal_engine and hasattr(self.signal_engine, "set_asset"):
            try:
                self.signal_engine.set_asset(asset)
            except:
                pass

        return True
