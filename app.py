from flask import Flask
import os
from bot import telegram_webhook

app = Flask(__name__)

@app.route("/")
def home():
    return "ULTRA V10 WEBHOOK ACTIVE ✔"


@app.route("/webhook", methods=["POST"])
def webhook():
    return telegram_webhook()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
