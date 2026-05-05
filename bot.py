from core.time_engine import TimeEngine
import os
import telepot
from telepot.loop import MessageLoop
import time

# 🧠 Time Engine
time_engine = TimeEngine()

# 🔑 Token from Render Environment
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ❌ حماية من الخطأ
if not TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN is missing in environment variables")

# 🤖 Bot init
bot = telepot.Bot(TOKEN)


# 📩 Handle messages
def handle(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":
        current_time = time_engine.get_current_time()
        session = time_engine.get_session()

        bot.sendMessage(
            chat_id,
            "🤖 ULTRA V10 ONLINE ✔\n"
            f"🕒 الوقت: {current_time}\n"
            f"🌍 الجلسة: {session}"
        )


# 🚀 Start bot safely
def start_bot():
    print("🔥 BOT STARTED - ULTRA V10 RUNNING")

    # حماية من تشغيل مزدوج (مهم لـ Render)
    try:
        MessageLoop(bot, handle).run_as_thread()
    except Exception as e:
        print(f"⚠ ERROR IN MESSAGE LOOP: {e}")

    # إبقاء السيرفر حي
    while True:
        time.sleep(10)
