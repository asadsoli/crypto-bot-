from flask import Flask
import os
import traceback
import logging

# إعداد Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# استيراد الـ webhook من bot.py
from bot import telegram_webhook, app as bot_app

# استخدام نفس Flask app من bot.py بدلاً من إنشاء واحد جديد
app = bot_app


@app.route("/")
def home():
    return "ULTRA V10 WEBHOOK ACTIVE ✔"


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    معالج الـ webhook للتواصل مع Telegram
    """
    try:
        return telegram_webhook()

    except Exception as e:
        logger.error(f"❌ WEBHOOK CRASH: {str(e)}")
        traceback.print_exc()
        
        # 🔥 منع Flask 500 - لكن تسجيل الخطأ
        return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    logger.info(f"🚀 Starting ULTRA V10 on port {port}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
