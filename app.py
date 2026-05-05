from flask import Flask
import threading
from bot import start_bot

app = Flask(__name__)

@app.route('/')
def home():
    return "ULTRA V10 BOT IS RUNNING ✔"

def run_bot():
    start_bot()

if __name__ == "__main__":
    port = 10000
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=port)
