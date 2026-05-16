import time


class ScannerEngine:

    def __init__(self, brain, assets=None):

        # =========================
        # 🧠 BRAIN CORE (Decision Engine)
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
        # 🤖 TELEGRAM INTEGRATION
        # =========================
        self.telegram = None
        self.last_sent_asset = None

    # =========================
    # 🔗 CONNECT TELEGRAM
    # =========================
    def set_telegram(self, telegram):
        self.telegram = telegram

    # =========================
    # 🔍 SCAN SINGLE ASSET (STABILIZED)
    # =========================
    def scan_asset(self, asset):

        try:

            if not asset:
                return None

            # 🧠 BRAIN ANALYSIS
            result = self.brain.analyze(asset)

            if not result or not isinstance(result, dict):
                return None

            signal = result.get("signal")

            if not signal or not isinstance(signal, dict):
                return None

            # ❌ FILTER BAD SIGNALS
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
    # 🔥 FIND BEST OPPORTUNITY
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
    # 🔁 MAIN LOOP
    # =========================
    def start(self, callback=None):

        self.active = True

        print("🔍 Scanner Stable V1 Started")

        while self.active:

            try:

                best = self.find_best()

                # =========================
                # 🎯 HIGH QUALITY FILTER
                # =========================
                if best and best.get("confidence", 0) >= 75:

                    # منع التكرار
                    if self.last_sent_asset == best.get("asset"):
                        time.sleep(self.scan_interval)
                        continue

                    self.last_sent_asset = best.get("asset")

                    print("🔥 BEST SIGNAL:", best)

                    # =========================
                    # 🤖 TELEGRAM SEND
                    # =========================
                    if self.telegram:

                        try:
                            self.telegram.send_message(
                                "<CHAT_ID>",
                                f"""🔍 ULTRA SCANNER

💰 ASSET: {best.get('asset')}
📊 SIGNAL: {best.get('signal')}
🧠 DECISION: {best.get('decision')}

🎯 ENTRY: {best.get('entry')}
🛑 SL: {best.get('sl')}
💰 TP: {best.get('tp')}

💎 CONFIDENCE: {best.get('confidence')}%
🏆 QUALITY: {best.get('quality')}

📍 REASON:
{best.get('reason')}
"""
                            )

                        except Exception as e:
                            print("❌ Telegram send error:", e)

                    # =========================
                    # 🔗 CALLBACK
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
    # ⛔ STOP SCANNER
    # =========================
    def stop(self):
        self.active = False
        print("⛔ Scanner Stopped")
