import telepot
from telepot.loop import MessageLoop
import time

TOKEN = "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE"

bot = telepot.Bot(TOKEN)

def handle(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', '')

    if text == "/start":
        bot.sendMessage(chat_id, "🤖 ULTRA V10 BOT ONLINE ✔")

def start_bot():
    MessageLoop(bot, handle).run_as_thread()

    while True:
        time.sleep(10)
