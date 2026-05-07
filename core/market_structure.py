class MarketStructure:

    def __init__(self):
        self.last_swing_high = None
        self.last_swing_low = None
        self.trend = "UNKNOWN"

    # =========================
    # 📊 SWING DETECTION
    # =========================

    def get_swings(self, candles, strength=3):

        swing_highs = []
        swing_lows = []

        for i in range(strength, len(candles) - strength):

            current = candles[i]

            highs = [candles[j]["high"] for j in range(i - strength, i + strength + 1)]
            lows = [candles[j]["low"] for j in range(i - strength, i + strength + 1)]

            # 🔼 Swing High
            if current["high"] == max(highs):
                swing_highs.append({
                    "index": i,
                    "price": current["high"]
                })

            # 🔽 Swing Low
            if current["low"] == min(lows):
                swing_lows.append({
                    "index": i,
                    "price": current["low"]
                })

        return swing_highs, swing_lows

    # =========================
    # 🧠 STRUCTURE ANALYSIS
    # =========================

    def analyze(self, candles):

        if not candles or len(candles) < 30:
            return {
                "bias": "UNKNOWN",
                "direction": "NONE",
                "confidence": 0,
                "reason": "Not enough data"
            }

        swing_highs, swing_lows = self.get_swings(candles)

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return {
                "bias": "RANGE",
                "direction": "NONE",
                "confidence": 50,
                "reason": "Not enough swing structure"
            }

        last_high = swing_highs[-1]["price"]
        prev_high = swing_highs[-2]["price"]

        last_low = swing_lows[-1]["price"]
        prev_low = swing_lows[-2]["price"]

        # =========================
        # 📈 TREND DETECTION
        # =========================

        bullish = last_high > prev_high and last_low > prev_low
        bearish = last_high < prev_high and last_low < prev_low

        # =========================
        # 🔥 BOS (Break of Structure)
        # =========================

        close = candles[-1]["close"]

        bos_bull = close > last_high
        bos_bear = close < last_low

        # =========================
        # 🔄 CHoCH DETECTION
        # =========================

        choch_bull = self.trend == "BEARISH" and bos_bull
        choch_bear = self.trend == "BULLISH" and bos_bear

        # =========================
        # 🧠 FINAL DECISION
        # =========================

        if choch_bull:
            self.trend = "BULLISH"
            return {
                "bias": "REVERSAL",
                "direction": "BUY",
                "confidence": 90,
                "reason": "CHoCH bullish (trend reversal)"
            }

        if choch_bear:
            self.trend = "BEARISH"
            return {
                "bias": "REVERSAL",
                "direction": "SELL",
                "confidence": 90,
                "reason": "CHoCH bearish (trend reversal)"
            }

        if bullish:
            self.trend = "BULLISH"
            return {
                "bias": "TREND",
                "direction": "BUY",
                "confidence": 85,
                "reason": "Bullish structure (HH + HL)"
            }

        if bearish:
            self.trend = "BEARISH"
            return {
                "bias": "TREND",
                "direction": "SELL",
                "confidence": 85,
                "reason": "Bearish structure (LH + LL)"
            }

        return {
            "bias": "RANGE",
            "direction": "NONE",
            "confidence": 60,
            "reason": "Sideways / indecision"
        }
