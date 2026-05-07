from telepot import Bot
from telepot.loop import MessageLoop
import time

class TelegramPanel:

    def __init__(self, token, signal_engine):

        self.bot = Bot(token)
        self.signal_engine = signal_engine

        self.bot_active = True
        self.selected_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

    # =========================
    # 🧠 MAIN HANDLER
    # =========================

    def handle(self, msg):

        content_type, chat_type, chat_id = telepot.glance(msg)
        text = msg.get("text", "")

        # =========================
        # 🟢 لوحة التحكم
        # =========================

        if text == "/start":

            self.bot.sendMessage(chat_id,
                "🤖 ULTRA V10 BOT\n\n"
                "🟢 لوحة التحكم جاهزة\n\n"
                "الأوامر:\n"
                "▶ تشغيل البوت\n"
                "⛔ إيقاف البوت\n"
                "📊 تحليل السوق\n"
                "💰 تغيير العملة BTC / ETH\n"
                "⚙️ الحالة"
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

            result = self.signal_engine.analyze(
                market_state={"state": "ACTIVE"},
                news={"risk": "NORMAL"},
                risk={"decision": "ALLOW"}
            )

            self.bot.sendMessage(chat_id,
                f"📊 النتيجة:\n"
                f"📌 Signal: {result.get('signal')}\n"
                f"🎯 Entry: {result.get('entry', 'N/A')}\n"
                f"🛑 SL: {result.get('sl', 'N/A')}\n"
                f"💰 TP: {result.get('tp', 'N/A')}\n"
                f"💎 Confidence: {result.get('confidence', 0)}%\n"
                f"🏆 Quality: {result.get('quality', 'N/A')}\n"
                f"📍 Reason: {result.get('reason', '')}"
            )

        # =========================
        # 💰 تغيير العملة
        # =========================

        elif text.startswith("عملة"):

            try:
                symbol = text.split(" ")[1].upper()
                self.selected_asset = symbol
                self.bot.sendMessage(chat_id, f"💰 تم تغيير العملة إلى: {symbol}")
            except:
                self.bot.sendMessage(chat_id, "❌ مثال: عملة BTCUSDT")

        # =========================
        # ⚙️ الحالة
        # =========================

        elif text == "حالة":

            self.bot.sendMessage(chat_id,
                f"🤖 الحالة:\n"
                f"🟢 البوت: {'شغال' if self.bot_active else 'متوقف'}\n"
                f"💰 العملة: {self.selected_asset}\n"
                f"⚙️ Risk Mode: {self.risk_mode}"
            )

    # =========================
    # 🚀 START BOT
    # =========================

    def run(self):

        MessageLoop(self.bot, self.handle).run_as_thread()

        print("🤖 Telegram Panel Running...")

        while True:
            time.sleep(10)
