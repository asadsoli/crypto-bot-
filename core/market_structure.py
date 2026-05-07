class MarketStructure:

    def analyze(self, candles):

        if not candles or len(candles) < 20:
            return {
                "bias": "UNKNOWN",
                "direction": "NONE",
                "confidence": 0,
                "reason": "Not enough data"
            }

        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        closes = [c["close"] for c in candles]

        # =========================
        # 📊 Detect Swing Points
        # =========================

        higher_highs = 0
        higher_lows = 0
        lower_highs = 0
        lower_lows = 0

        for i in range(2, len(candles)):

            # previous structure
            prev_high = highs[i - 1]
            prev_low = lows[i - 1]

            curr_high = highs[i]
            curr_low = lows[i]

            # 📈 Higher High / Higher Low
            if curr_high > prev_high:
                higher_highs += 1

            if curr_low > prev_low:
                higher_lows += 1

            # 📉 Lower High / Lower Low
            if curr_high < prev_high:
                lower_highs += 1

            if curr_low < prev_low:
                lower_lows += 1

        # =========================
        # 🧠 Market Bias Decision
        # =========================

        score_bull = higher_highs + higher_lows
        score_bear = lower_highs + lower_lows

        # 🔼 Bullish Structure
        if score_bull > score_bear * 1.2:

            return {
                "bias": "TREND",
                "direction": "BUY",
                "confidence": min(95, score_bull * 2),
                "reason": "Bullish structure (HH + HL)"
            }

        # 🔽 Bearish Structure
        if score_bear > score_bull * 1.2:

            return {
                "bias": "TREND",
                "direction": "SELL",
                "confidence": min(95, score_bear * 2),
                "reason": "Bearish structure (LH + LL)"
            }

        # 🔄 Reversal / CHoCH Zone
        if abs(score_bull - score_bear) < 3:

            return {
                "bias": "REVERSAL",
                "direction": "WAIT",
                "confidence": 75,
                "reason": "Market indecision / CHoCH possible"
            }

        # ⚪ Range Market
        return {
            "bias": "RANGE",
            "direction": "NONE",
            "confidence": 60,
            "reason": "No clear structure"
            }
