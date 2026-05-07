from telepot import Bot, glance
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

import time


class TelegramLayer:

    def __init__(
        self,
        token,
        signal_engine,
        market=None,
        news=None,
        risk=None,
        time_engine=None
    ):

        self.bot = Bot(token)

        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        self.time_engine = time_engine

        # =========================
        # 🧠 CONTROL STATE
        # =========================

        self.bot_active = True
        self.selected_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

    # =========================
    # 🎛 MAIN MENU
    # =========================

    def main_menu(self):

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[

                [
                    InlineKeyboardButton(
                        text="📊 تحليل السوق",
                        callback_data="analyze"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="💰 BTC",
                        callback_data="asset_BTCUSDT"
                    ),

                    InlineKeyboardButton(
                        text="💎 ETH",
                        callback_data="asset_ETHUSDT"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="🟢 تشغيل",
                        callback_data="bot_on"
                    ),

                    InlineKeyboardButton(
                        text="🔴 إيقاف",
                        callback_data="bot_off"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="⚙️ الحالة",
                        callback_data="status"
                    )
                ]
            ]
        )

        return keyboard

    # =========================
    # 📊 FORMAT ANALYSIS
    # =========================

    def format_analysis(self, result):

        return f"""🤖 ULTRA V10 ANALYSIS

💰 ASSET: {self.selected_asset}

📊 Signal:
{result.get('signal')}

🎯 Entry:
{result.get('entry', 'N/A')}

🛑 Stop Loss:
{result.get('sl', 'N/A')}

💰 Take Profit:
{result.get('tp', 'N/A')}

💎 Confidence:
{result.get('confidence', 0)}%

🏆 Quality:
{result.get('quality', 'N/A')}

📍 Reason:
{result.get('reason', '')}
"""

    # =========================
    # ⚙️ STATUS MESSAGE
    # =========================

    def format_status(self):

        return f"""⚙️ ULTRA V10 STATUS

🤖 البوت:
{'🟢 يعمل' if self.bot_active else '🔴 متوقف'}

💰 العملة الحالية:
{self.selected_asset}

⚙️ Risk Mode:
{self.risk_mode}
"""

    # =========================
    # 🧠 MESSAGE HANDLER
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

                # =========================
                # /start
                # =========================

                if text == "/start":

                    self.bot.sendMessage(
                        chat_id,

                        "🤖 ULTRA V10 CONTROL PANEL\n\n"
                        "🔥 Institutional Smart Money System\n\n"
                        "اختر من لوحة التحكم:",

                        reply_markup=self.main_menu()
                    )

            # =========================
            # 🎛 CALLBACK BUTTONS
            # =========================

            else:

                query_id, chat_id, query_data = glance(
                    msg,
                    flavor="callback_query"
                )

                # =========================
                # 📊 ANALYZE
                # =========================

                if query_data == "analyze":

                    if not self.bot_active:

                        self.bot.sendMessage(
                            chat_id,
                            "⛔ البوت متوقف حالياً"
                        )

                        return

                    try:

                        result = self.signal_engine.analyze(
                            market_state={"state": "ACTIVE"},
                            news={"risk": "NORMAL"},
                            risk={"decision": "ALLOW"}
                        )

                        self.bot.sendMessage(
                            chat_id,
                            self.format_analysis(result)
                        )

                    except Exception
