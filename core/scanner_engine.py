import time


class ScannerEngine:

    def __init__(self, brain, assets=None):

        # =========================
        # 🧠 BRAIN CORE
        # =========================
        self.brain = brain

        # =========================
        # 📊 WATCHLIST (SOURCE OF TRUTH)
        # =========================
        self.assets = assets or [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "PAXGUSDT",
            "SOLUSDT"
        ]

        # =========================
        # ⚙️ SCANNER STATE
        # =========================
        self.active = False
        self.scan_interval = 60

        # =========================
        # 🤖 TELEGRAM
        # =========================
        self.telegram = None
        self.last_sent_asset = None

    # =========================
    # 🔗 CONNECT TELEGRAM
    # =========================
    def set_telegram(self, telegram):
        self.telegram = telegram

    # =========================
    # 🔍 SCAN SINGLE ASSET (SAFE)
    # =========================
    def scan_asset(self, asset):

        try:

            if not asset:
                return None

            result = self.brain.analyze(asset)

            if not isinstance(result, dict):
                return None

            signal = result.get("signal")

            if not isinstance(signal, dict):
                return None

            # =========================
            # ❌ FILTER BAD SIGNALS
            # =========================
            if signal.get("signal") in [
                "NO TRADE",
                "ERROR",
                "NO DATA",
                "NO_DATA",
                "WAIT",
                "BUSY"
            ]:
                return None

            return {
                "asset": asset,
                "decision": result.get("decision"),
                "signal": signal.get("signal"),
                "entry": signal.get("entry"),
                "sl": signal.get("sl"),
                "tp": signal.get("tp"),
                "confidence": signal.get("confidence", 0),
                "quality": signal.get("quality", ""),
                "reason": result.get("reason", "")
            }

        except Exception as e:
            print(f"❌ Scanner error ({asset}):", e)
            return None

    # =========================
    # 🔥 BEST SIGNAL
    # =========================
    def find_best(self):

        best = None
        best_conf = 0

        for asset in self.assets:

            result = self.scan_asset(asset)

            if not result:
                continue

            confidence = result.get("confidence", 0)

            if confidence > best_conf:
                best = result
                best_conf = confidence

        return best

    # =========================
    # 🔁 MAIN LOOP (STABLE)
    # =========================
    def start(self, callback=None):

        self.active = True

        print("🔍 Scanner Stable V1 Started")

        while self.active:

            try:

                best = self.find_best()

                # =========================
                # VALIDATION SAFE
                # =========================
                if not best:
                    time.sleep(self.scan_interval)
                    continue

                confidence = best.get("confidence", 0)
                asset = best.get("asset")

                # =========================
                # QUALITY FILTER
                # =========================
                if confidence < 75:
                    time.sleep(self.scan_interval)
                    continue

                # =========================
                # DUPLICATE PREVENTION (FIXED)
                # =========================
                if asset == self.last_sent_asset:
                    time.sleep(self.scan_interval)
                    continue

                self.last_sent_asset = asset

                print("🔥 BEST SIGNAL:", best)

                # =========================
                # TELEGRAM SAFE SEND
                # =========================
                if self.telegram:

                    try:
                        # FIX: telepot uses sendMessage (not send_message)
                        self.telegram.sendMessage(
                            "<CHAT_ID>",
                            f"""🔍 ULTRA SCANNER

💰 ASSET: {asset}
📊 SIGNAL: {best.get('signal')}
🧠 DECISION: {best.get('decision')}

🎯 ENTRY: {best.get('entry')}
🛑 SL: {best.get('sl')}
💰 TP: {best.get('tp')}

💎 CONFIDENCE: {confidence}%
🏆 QUALITY: {best.get('quality')}

📍 REASON:
{best.get('reason')}
"""
                        )

                    except Exception as e:
                        print("❌ Telegram send error:", e)

                # =========================
                # CALLBACK SAFE
                # =========================
                if callback:
                    try:
                        callback(best)
                    except Exception as e:
                        print("❌ Callback error:", e)

            except Exception as e:
                print("❌ Scanner loop error:", e)

            time.sleep(self.scan_interval)

    # =========================
    # ⛔ STOP
    # =========================
    def stop(self):
        self.active = False
        print("⛔ Scanner Stopped")
