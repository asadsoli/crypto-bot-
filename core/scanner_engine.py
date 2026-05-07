import time


class ScannerEngine:

    def __init__(self, signal_engine, assets=None):

        self.signal_engine = signal_engine

        self.assets = assets or [
            "BTCUSDT",
            "ETHUSDT",
            "XAUUSD",
            "SOLUSDT"
        ]

        self.active = False
        self.scan_interval = 60  # كل دقيقة

    # =========================
    # 🔍 SCAN SINGLE ASSET
    # =========================

    def scan_asset(self, asset):

        try:

            result = self.signal_engine.analyze_asset(asset)

            if not result:
                return None

            if result.get("signal") in ["NO TRADE", "ERROR", "NO_DATA"]:
                return None

            return {
                "asset": asset,
                "signal": result.get("signal"),
                "entry": result.get("entry"),
                "sl": result.get("sl"),
                "tp": result.get("tp"),
                "confidence": result.get("confidence", 0),
                "quality": result.get("quality", ""),
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

            if result["confidence"] > best_conf:

                best = result
                best_conf = result["confidence"]

        return best

    # =========================
    # 🔁 LOOP SCANNER
    # =========================

    def start(self, callback=None):

        self.active = True

        print("🔍 Scanner V3 Started")

        while self.active:

            try:

                best = self.find_best()

                if best and best["confidence"] >= 75:

                    print("🔥 BEST SIGNAL FOUND:", best)

                    # إذا تريد ربط لاحقاً مع Telegram
                    if callback:
                        callback(best)

            except Exception as e:
                print("❌ Scanner Loop Error:", e)

            time.sleep(self.scan_interval)

    # =========================
    # ⛔ STOP SCANNER
    # =========================

    def stop(self):

        self.active = False
        print("⛔ Scanner Stopped")
