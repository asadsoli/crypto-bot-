import os

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN missing in Render environment")
