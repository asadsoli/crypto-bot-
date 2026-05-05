import os
import telepot
from flask import request
from core.time_engine import TimeEngine

time_engine = TimeEngine()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telepot.Bot(TOKEN)


def telegram_webhook():
    data = request.get_json()

    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            current_time = time_engine.get_current_time()
            session = time_engine.get_session()

            bot.sendMessage(
                chat_id,
                f"🤖 ULTRA V10 ONLINE ✔\n"
                f"🕒 الوقت: {current_time}\n"
                f"🌍 الجلسة: {session}"
            )

    return "OK"
