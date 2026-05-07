class SmartMoneyEngine:

    def __init__(self):
        pass

    def analyze_structure(self, candles):

        # 🛡 حماية
        if not candles or len(candles) < 10:
            return {
                "bias": "RANGE",
                "bos": False,
                "choch": False,
                "trend": "NEUTRAL",
                "reason": "Not enough candles"
            }

        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]
        closes = [c["close"] for c in candles]

        recent_high = max(highs[-5:])
        previous_high = max(highs[-10:-5])

        recent_low = min(lows[-5:])
        previous_low = min(lows[-10:-5])

        current_close = closes[-1]

        # 📈 BOS Bullish
        if recent_high > previous_high and current_close > previous_high:
            return {
                "bias": "BULLISH",
                "bos": True,
                "choch": False,
                "trend": "UPTREND",
                "reason": "Bullish BOS detected"
            }

        # 📉 BOS Bearish
        if recent_low < previous_low and current_close < previous_low:
            return {
                "bias": "BEARISH",
                "bos": True,
                "choch": False,
                "trend": "DOWNTREND",
                "reason": "Bearish BOS detected"
            }

        # 🔄 CHoCH
        if recent_high > previous_high and recent_low < previous_low:
            return {
                "bias": "REVERSAL",
                "bos": False,
                "choch": True,
                "trend": "REVERSAL",
                "reason": "CHoCH reversal detected"
            }

        # ⚪ Range
        return {
            "bias": "RANGE",
            "bos": False,
            "choch": False,
            "trend": "SIDEWAYS",
            "reason": "No clear structure"
        }
