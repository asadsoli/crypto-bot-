class FVGEngine:

    def analyze(self, candles):

        if not candles or len(candles) < 5:
            return {
                "signal": "NO_FVG",
                "reason": "Not enough data"
            }

        bullish_fvg = None
        bearish_fvg = None

        for i in range(1, len(candles) - 2):

            c1 = candles[i - 1]
            c2 = candles[i]
            c3 = candles[i + 1]

            # 🟢 Bullish FVG (gap up)
            if c1["high"] < c3["low"]:
                bullish_fvg = {
                    "type": "BULLISH_FVG",
                    "zone_low": c1["high"],
                    "zone_high": c3["low"],
                    "entry": (c1["high"] + c3["low"]) / 2,
                    "confidence": 88,
                    "reason": "Bullish imbalance detected"
                }

            # 🔴 Bearish FVG (gap down)
            if c1["low"] > c3["high"]:
                bearish_fvg = {
                    "type": "BEARISH_FVG",
                    "zone_low": c3["high"],
                    "zone_high": c1["low"],
                    "entry": (c1["low"] + c3["high"]) / 2,
                    "confidence": 88,
                    "reason": "Bearish imbalance detected"
                }

        if bullish_fvg:
            return bullish_fvg

        if bearish_fvg:
            return bearish_fvg

        return {
            "signal": "NO_FVG",
            "confidence": 0,
            "reason": "No imbalance found"
        }
