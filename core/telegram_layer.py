from telepot import Bot
from telepot.loop import MessageLoop
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
        # 🧠 CONTROL STATE
        # =========================
        self.bot_active = True
        self.selected_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

    # =========================
    # 🧠 MAIN HANDLER
    # =========================

    def handle(self, msg):

        content_type, chat_type, chat_id = telepot.glance(msg)
        text = msg.get("text", "").strip()

        # =========================
        # /start - لوحة التحكم
        # =========================

        if text == "/start":

            self.bot.sendMessage(chat_id,
                "🤖 ULTRA V10 CONTROL PANEL\n\n"
                "🟢 لوحة التحكم جاهزة\n\n"
                "📌 الأوامر:\n"
                "▶ تشغيل\n"
                "⛔ إيقاف\n"
                "📊 تحليل\n"
                "💰 عملة BTCUSDT / ETHUSDT\n"
                "⚙️ حالة"
            )

        # =========================
        # ▶ تشغيل البوت
        # =========================

        elif text == "تشغيل":

            self.bot_active = True
            self.bot.sendMessage(chat_id, "🟢 تم تشغيل البوت")

        # =========================
        # ⛔ إيقاف البوت
        # =========================

        elif text == "إيقاف":

            self.bot_active = False
            self.bot.sendMessage(chat_id, "🔴 تم إيقاف البوت")

        # =========================
        # 📊 تحليل مباشر
        # =========================

        elif text == "تحليل":

            if not self.bot_active:
                self.bot.sendMessage(chat_id, "⛔ البوت متوقف")
                return

            try:

                result = self.signal_engine.analyze(
                    market_state={"state": "ACTIVE"},
                    news={"risk": "NORMAL"},
                    risk={"decision": "ALLOW"}
                )

            except Exception as e:
                self.bot.sendMessage(chat_id, f"❌ خطأ في التحليل: {str(e)}")
                return

            self.bot.sendMessage(chat_id,
                f"""📊 ANALYSIS RESULT

📌 Signal: {result.get('signal')}
🎯 Entry: {result.get('entry', 'N/A')}
🛑 SL: {result.get('sl', 'N/A')}
💰 TP: {result.get('tp', 'N/A')}
💎 Confidence: {result.get('confidence', 0)}%
🏆 Quality: {result.get('quality', 'N/A')}
📍 Reason: {result.get('reason', '')}
"""
            )

        # =========================
        # 💰 تغيير العملة
        # =========================

        elif text.startswith("عملة"):

            try:
                symbol = text.split(" ")[1].upper()
                self.selected_asset = symbol

                # 🔥 ربط العملة لاحقاً مع Market Data
                if self.market:
                    self.market.symbol = symbol

                self.bot.sendMessage(chat_id, f"💰 تم تغيير العملة إلى: {symbol}")

            except:
                self.bot.sendMessage(chat_id, "❌ مثال: عملة BTCUSDT")

        # =========================
        # ⚙️ الحالة
        # =========================

        elif text == "حالة":

            self.bot.sendMessage(chat_id,
                f"""⚙️ SYSTEM STATUS

🤖 البوت: {'شغال' if self.bot_active else 'متوقف'}
💰 العملة: {self.selected_asset}
⚙️ Risk Mode: {self.risk_mode}
"""
            )

    # =========================
    # 🚀 START BOT
    # =========================

    def run(self):

        MessageLoop(self.bot, self.handle).run_as_thread()

        print("🤖 Telegram Layer V1 PRO RUNNING...")

        while True:
            time.sleep(10)
