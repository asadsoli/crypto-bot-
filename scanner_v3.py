import time
import threading


class ScannerV3:

    def __init__(self, signal_engine, telegram_layer, scan_assets=None):

        self.signal_engine = signal_engine
        self.telegram = telegram_layer

        self.scan_assets = scan_assets or [
            "BTCUSDT",
            "ETHUSDT",
            "XAUUSD",
            "SOLUSDT"
        ]

        # =========================
        # 🧠 CONTROL STATE
        # =========================
        self.active = False

        # =========================
        # ⛔ ANTI-SPAM MEMORY
        # =========================
        self.last_signal = {}

        self.cooldown = 300  # 5 minutes per asset

    # =========================
    # 🔍 CORE SCAN LOOP
    # =========================

    def scan_loop(self):

        print("🔍 ULTRA V3 SCANNER STARTED")

        while self.active:

            try:

                for asset in self.scan_assets:

                    result = self.signal_engine.analyze_asset(asset)

                    if not result:
                        continue

                    signal = result.get("signal")
                    confidence = result.get("confidence", 0)

                    # =========================
                    # 🚫 FILTER 1: NO TRADE SKIP
                    # =========================
                    if signal == "NO TRADE":
                        continue

                    # =========================
                    # 🚫 FILTER 2: CONFIDENCE
                    # =========================
                    if confidence < 75:
                        continue

                    # =========================
                    # 🚫 FILTER 3: COOLDOWN
                    # =========================
                    now = time.time()

                    last_time = self.last_signal.get(asset, 0)

                    if now - last_time < self.cooldown:
                        continue

                    # =========================
                    # 📡 SEND SIGNAL
                    # =========================

                    msg = f"""🔍 ULTRA SCANNER V3

💰 ASSET: {asset}

📊 SIGNAL: {signal}
🎯 ENTRY: {result.get('entry', 'N/A')}
🛑 SL: {result.get('sl', 'N/A')}
💰 TP: {result.get('tp', 'N/A')}

💎 CONFIDENCE: {confidence}%
🏆 QUALITY: {result.get('quality', 'N/A')}

📍 REASON:
{result.get('reason', '')}
"""

                    self.telegram.bot.sendMessage("<CHAT_ID>", msg)

                    # تحديث آخر إرسال
                    self.last_signal[asset] = now

            except Exception as e:
                print("❌ Scanner Error:", e)

            time.sleep(60)

    # =========================
    # 🚀 START
    # =========================

    def start(self):

        if self.active:
            return

        self.active = True

        thread = threading.Thread(target=self.scan_loop)
        thread.start()

        print("🟢 Scanner V3 Activated")

    # =========================
    # ⛔ STOP
    # =========================

    def stop(self):

        self.active = False

        print("🔴 Scanner V3 Stopped")
