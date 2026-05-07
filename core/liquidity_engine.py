class LiquidityEngine:

    def analyze(self, candles):

        if not candles or len(candles) < 20:
            return {
                "signal_hint": "NO_DATA",
                "reason": "Insufficient candles"
            }

        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]

        recent_high = max(highs[-20:])
        recent_low = min(lows[-20:])

        # 💧 Detect Equal Highs (Liquidity above)
        equal_highs = 0
        for i in range(-10, -1):
            if abs(highs[i] - highs[i-1]) < 0.0005:
                equal_highs += 1

        # 💧 Detect Equal Lows (Liquidity below)
        equal_lows = 0
        for i in range(-10, -1):
            if abs(lows[i] - lows[i-1]) < 0.0005:
                equal_lows += 1

        last_close = candles[-1]["close"]

        # 🔥 Scenario 1: Buy-side liquidity (above price)
        if equal_highs >= 2 and last_close < recent_high:
            return {
                "signal_hint": "WAIT_SWEEP",
                "bias": "BEARISH_SWEEP_SETUP",
                "reason": "Buy-side liquidity above detected (equal highs + resistance)"
            }

        # 🔥 Scenario 2: Sell-side liquidity (below price)
        if equal_lows >= 2 and last_close > recent_low:
            return {
                "signal_hint": "WAIT_SWEEP",
                "bias": "BULLISH_SWEEP_SETUP",
                "reason": "Sell-side liquidity below detected (equal lows + support)"
            }

        # 🧠 No clear liquidity trap
        return {
            "signal_hint": "NO_CLEAR_LIQUIDITY",
            "bias": "NEUTRAL",
            "reason": "No strong liquidity pool detected"
        }
