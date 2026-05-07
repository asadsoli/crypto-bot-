class MultiAssetScanner:

    def __init__(self, signal_engine):
        self.signal_engine = signal_engine

        self.assets = [
            "BTCUSDT",
            "ETHUSDT",
            "XAUUSD",
            "SOLUSDT",
            "BNBUSDT",
            "TONUSDT"
        ]

    # =========================
    # 📊 SCORE EACH ASSET
    # =========================

    def score_asset(self, asset):

        try:

            result = self.signal_engine.analyze_asset(asset)

            if not result:
                return None

            score = result.get("confidence", 0)

            return {
                "asset": asset,
                "score": score,
                "signal": result.get("signal"),
                "direction": result.get("direction"),
                "entry": result.get("entry"),
                "sl": result.get("sl"),
                "tp": result.get("tp"),
                "reason": result.get("reason")
            }

        except Exception as e:
            print(f"❌ Scanner error on {asset}:", e)
            return None

    # =========================
    # 🔍 SCAN ALL MARKETS
    # =========================

    def scan(self):

        results = []

        for asset in self.assets:

            data = self.score_asset(asset)

            if data:
                results.append(data)

        # ترتيب حسب القوة
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    # =========================
    # 🏆 TOP PICKS
    # =========================

    def get_top_opportunities(self, limit=3):

        scan = self.scan()

        return scan[:limit]
