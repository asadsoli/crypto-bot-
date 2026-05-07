class OrderFlowEngine:

    def analyze(self, candles):

        if not candles or len(candles) < 20:
            return {
                "signal": "NO_DATA",
                "confidence": 0,
                "reason": "Not enough candles"
            }

        order_blocks = []
        fvg_zones = []

        # =========================
        # 🧱 ORDER BLOCK DETECTION
        # =========================

        for i in range(2, len(candles) - 2):

            prev = candles[i - 1]
            curr = candles[i]
            nxt = candles[i + 1]

            # 🔥 Bullish Order Block
            if curr["close"] < curr["open"] and nxt["close"] > curr["high"]:
                order_blocks.append({
                    "type": "BULLISH_OB",
                    "zone_low": curr["low"],
                    "zone_high": curr["high"],
                    "entry": curr["high"],
                    "sl": curr["low"],
                    "confidence": 85,
                    "reason": "Bullish rejection + break"
                })

            # 🔥 Bearish Order Block
            if curr["close"] > curr["open"] and nxt["close"] < curr["low"]:
                order_blocks.append({
                    "type": "BEARISH_OB",
                    "zone_low": curr["low"],
                    "zone_high": curr["high"],
                    "entry": curr["low"],
                    "sl": curr["high"],
                    "confidence": 85,
                    "reason": "Bearish rejection + break"
                })

        # =========================
        # ⚡ FVG DETECTION
        # =========================

        for i in range(1, len(candles) - 2):

            c1 = candles[i - 1]
            c2 = candles[i]
            c3 = candles[i + 1]

            # 🟢 Bullish FVG
            if c1["high"] < c3["low"]:
                fvg_zones.append({
                    "type": "BULLISH_FVG",
                    "zone_low": c1["high"],
                    "zone_high": c3["low"],
                    "entry": (c1["high"] + c3["low"]) / 2,
                    "confidence": 80,
                    "reason": "Imbalance bullish"
                })

            # 🔴 Bearish FVG
            if c1["low"] > c3["high"]:
                fvg_zones.append({
                    "type": "BEARISH_FVG",
                    "zone_low": c3["high"],
                    "zone_high": c1["low"],
                    "entry": (c1["low"] + c3["high"]) / 2,
                    "confidence": 80,
                    "reason": "Imbalance bearish"
                })

        # =========================
        # 🎯 FINAL DECISION
        # =========================

        best_signal = None

        if order_blocks:
            best_signal = order_blocks[-1]

        elif fvg_zones:
            best_signal = fvg_zones[-1]

        if best_signal:

            return {
                "signal": "ORDERFLOW ENTRY",
                "type": best_signal["type"],
                "entry": best_signal["entry"],
                "sl": best_signal["sl"],
                "tp": None,
                "confidence": best_signal["confidence"],
                "reason": best_signal["reason"]
            }

        return {
            "signal": "NO_ORDERFLOW",
            "confidence": 0,
            "reason": "No valid OB or FVG detected"
        }
