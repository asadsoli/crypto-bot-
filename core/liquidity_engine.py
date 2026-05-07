class LiquidityEngine:

    def analyze(self, candles):

        if not candles or len(candles) < 20:
            return {
                "signal": "NO_LIQUIDITY",
                "signal_hint": "NONE",
                "reason": "Not enough data"
            }

        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]

        liquidity_zones = []
        sweep_detected = False

        # =========================
        # 💧 EQUAL HIGHS / LOWS
        # =========================

        for i in range(2, len(candles) - 2):

            # 🟢 Equal Highs (Buy-side liquidity)
            if abs(highs[i] - highs[i - 1]) < 0.0005:
                liquidity_zones.append({
                    "type": "EQUAL_HIGHS",
                    "level": highs[i],
                    "side": "BUY_SIDE"
                })

            # 🔴 Equal Lows (Sell-side liquidity)
            if abs(lows[i] - lows[i - 1]) < 0.0005:
                liquidity_zones.append({
                    "type": "EQUAL_LOWS",
                    "level": lows[i],
                    "side": "SELL_SIDE"
                })

        # =========================
        # 💥 SWEEP DETECTION
        # =========================

        latest = candles[-1]

        for zone in liquidity_zones:

            # 🟢 Sweep Buy-side liquidity (price goes above highs then drops)
            if zone["type"] == "EQUAL_HIGHS":
                if latest["high"] > zone["level"] and latest["close"] < zone["level"]:
                    sweep_detected = True
                    return {
                        "signal": "LIQUIDITY_SWEEP",
                        "signal_hint": "REVERSAL_SELL",
                        "zone": zone,
                        "reason": "Buy-side liquidity grabbed"
                    }

            # 🔴 Sweep Sell-side liquidity (price goes below lows then rises)
            if zone["type"] == "EQUAL_LOWS":
                if latest["low"] < zone["level"] and latest["close"] > zone["level"]:
                    sweep_detected = True
                    return {
                        "signal": "LIQUIDITY_SWEEP",
                        "signal_hint": "REVERSAL_BUY",
                        "zone": zone,
                        "reason": "Sell-side liquidity grabbed"
                    }

        # =========================
        # ⚠️ WAIT STATE
        # =========================

        if liquidity_zones:
            return {
                "signal": "LIQUIDITY_BUILDUP",
                "signal_hint": "WAIT_SWEEP",
                "zones": liquidity_zones[-3:],
                "reason": "Liquidity building, waiting for sweep"
            }

        return {
            "signal": "NO_LIQUIDITY",
            "signal_hint": "NONE",
            "reason": "No clear liquidity structure"
        }
