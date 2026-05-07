class OrderFlowEngine:

    def analyze(self, candles):

        if not candles or len(candles) < 20:
            return {
                "confidence": 0,
                "reason": "Not enough data"
            }

        bullish_ob = None
        bearish_ob = None

        # 🔍 البحث عن Order Blocks
        for i in range(2, len(candles) - 2):

            prev = candles[i - 1]
            curr = candles[i]
            nxt = candles[i + 1]

            # 🚀 Bullish Order Block
            # آخر شمعة هابطة قبل صعود قوي
            if (
                prev["close"] < prev["open"] and
                nxt["close"] > curr["high"] and
                (nxt["close"] - nxt["open"]) > (curr["high"] - curr["low"])
            ):
                bullish_ob = {
                    "entry": curr["low"],
                    "sl": curr["low"] - (curr["high"] - curr["low"]),
                    "tp": nxt["close"],
                    "confidence": 90,
                    "reason": "Bullish Order Block detected"
                }

            # 🔻 Bearish Order Block
            if (
                prev["close"] > prev["open"] and
                nxt["close"] < curr["low"] and
                (nxt["open"] - nxt["close"]) > (curr["high"] - curr["low"])
            ):
                bearish_ob = {
                    "entry": curr["high"],
                    "sl": curr["high"] + (curr["high"] - curr["low"]),
                    "tp": nxt["close"],
                    "confidence": 90,
                    "reason": "Bearish Order Block detected"
                }

        # 📊 القرار النهائي
        if bullish_ob:
            return bullish_ob

        if bearish_ob:
            return bearish_ob

        return {
            "confidence": 0,
            "reason": "No valid Order Block found"
                }
