from flask import Flask
import os
import traceback

from bot import telegram_webhook

app = Flask(__name__)


@app.route("/")
def home():
    return "ULTRA V10 WEBHOOK ACTIVE ✔"


@app.route("/webhook", methods=["POST"])
def webhook():

    try:
        return telegram_webhook()

    except Exception as e:

        print("❌ WEBHOOK CRASH:", str(e))
        traceback.print_exc()

        # 🔥 منع Flask 500
        return "OK"


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
