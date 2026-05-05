import os
import telepot
from telepot.loop import MessageLoop
import time

TOKEN = os.environ.get("TELEGRAM_TOKEN")

bot = telepot.Bot(TOKEN)

def handle(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":
        bot.sendMessage(chat_id, "🤖 ULTRA V10 BOT ONLINE ✔")

def start_bot():
    print("🔥 BOT STARTED")
    MessageLoop(bot, handle).run_as_thread()

    while True:
        time.sleep(10)
