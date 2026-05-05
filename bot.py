from core.time_engine import TimeEngine
import os
import telepot
from telepot.loop import MessageLoop
import time

time_engine = TimeEngine()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telepot.Bot(TOKEN)


def handle(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":
        current_time = time_engine.get_current_time()
        session = time_engine.get_session()

        bot.sendMessage(
            chat_id,
            f"🤖 ULTRA V10 ONLINE ✔\n"
            f"🕒 الوقت: {current_time}\n"
            f"🌍 الجلسة: {session}"
        )


def start_bot():
    print("🔥 BOT STARTED")
    MessageLoop(bot, handle).run_as_thread()

    while True:
        time.sleep(10)
