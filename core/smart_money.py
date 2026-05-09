class SmartMoneyEngine:

    def __init__(self):

        self.internal_trend = "NEUTRAL"

    # =====================================================
    # 📊 SWING DETECTION
    # =====================================================

    def detect_swings(self, candles):

        swing_highs = []
        swing_lows = []

        try:

            for i in range(2, len(candles) - 2):

                current = candles[i]

                # 🔼 Swing High
                if (
                    current["high"] > candles[i - 1]["high"]
                    and current["high"] > candles[i - 2]["high"]
                    and current["high"] > candles[i + 1]["high"]
                    and current["high"] > candles[i + 2]["high"]
                ):

                    swing_highs.append({
                        "index": i,
                        "price": current["high"]
                    })

                # 🔽 Swing Low
                if (
                    current["low"] < candles[i - 1]["low"]
                    and current["low"] < candles[i - 2]["low"]
                    and current["low"] < candles[i + 1]["low"]
                    and current["low"] < candles[i + 2]["low"]
                ):

                    swing_lows.append({
                        "index": i,
                        "price": current["low"]
                    })

        except Exception as e:
            print("❌ Swing detection error:", e)

        return swing_highs, swing_lows

    # =====================================================
    # 💧 LIQUIDITY SWEEP
    # =====================================================

    def detect_liquidity_sweep(
        self,
        candles,
        swing_highs,
        swing_lows
    ):

        try:

            if not candles:
                return None

            last = candles[-1]

            # 🔥 Buy Side Sweep
            for swing in swing_highs[-5:]:

                if (
                    last["high"] > swing["price"]
                    and last["close"] < swing["price"]
                ):

                    return {
                        "type": "BUY_SIDE_SWEEP",
                        "level": swing["price"],
                        "direction": "SELL"
                    }

            # 🔥 Sell Side Sweep
            for swing in swing_lows[-5:]:

                if (
                    last["low"] < swing["price"]
                    and last["close"] > swing["price"]
                ):

                    return {
                        "type": "SELL_SIDE_SWEEP",
                        "level": swing["price"],
                        "direction": "BUY"
                    }

        except Exception as e:
            print("❌ Liquidity sweep error:", e)

        return None

    # =====================================================
    # 🧠 MAIN STRUCTURE ENGINE
    # =====================================================

    def analyze_structure(self, candles):

        # =====================================================
        # 🛡 SAFETY
        # =====================================================

        if not candles or len(candles) < 20:

            return {
                "bias": "RANGE",
                "bos": False,
                "choch": False,
                "trend": "NEUTRAL",
                "direction": "WAIT",
                "confidence": 0,
                "reason": "Not enough candles"
            }

        # =====================================================
        # 📊 SWINGS
        # =====================================================

        swing_highs, swing_lows = self.detect_swings(candles)

        if len(swing_highs) < 2 or len(swing_lows) < 2:

            return {
                "bias": "RANGE",
                "bos": False,
                "choch": False,
                "trend": "SIDEWAYS",
                "direction": "WAIT",
                "confidence": 20,
                "reason": "Weak structure"
            }

        # =====================================================
        # 📈 RECENT STRUCTURE
        # =====================================================

        last_high = swing_highs[-1]["price"]
        prev_high = swing_highs[-2]["price"]

        last_low = swing_lows[-1]["price"]
        prev_low = swing_lows[-2]["price"]

        current_close = candles[-1]["close"]

        # =====================================================
        # 💧 LIQUIDITY
        # =====================================================

        sweep = self.detect_liquidity_sweep(
            candles,
            swing_highs,
            swing_lows
        )

        # =====================================================
        # 📈 BULLISH BOS
        # =====================================================

        if last_high > prev_high and current_close > prev_high:

            confidence = 75

            if sweep and sweep["direction"] == "BUY":
                confidence += 15

            return {
                "bias": "TREND",
                "bos": True,
                "choch": False,
                "trend": "BULLISH",
                "direction": "BUY",
                "confidence": confidence,
                "sweep": sweep,
                "internal_structure": "HIGHER_HIGHS",
                "reason": "Bullish BOS confirmed"
            }

        # =====================================================
        # 📉 BEARISH BOS
        # =====================================================

        if last_low < prev_low and current_close < prev_low:

            confidence = 75

            if sweep and sweep["direction"] == "SELL":
                confidence += 15

            return {
                "bias": "TREND",
                "bos": True,
                "choch": False,
                "trend": "BEARISH",
                "direction": "SELL",
                "confidence": confidence,
                "sweep": sweep,
                "internal_structure": "LOWER_LOWS",
                "reason": "Bearish BOS confirmed"
            }

        # =====================================================
        # 🔄 CHOCH REVERSAL
        # =====================================================

        bullish_choch = (
            last_high > prev_high
            and last_low < prev_low
            and current_close > prev_high
        )

        bearish_choch = (
            last_low < prev_low
            and last_high > prev_high
            and current_close < prev_low
        )

        if bullish_choch:

            return {
                "bias": "REVERSAL",
                "bos": False,
                "choch": True,
                "trend": "BULLISH_REVERSAL",
                "direction": "BUY",
                "confidence": 85,
                "sweep": sweep,
                "internal_structure": "REVERSAL_UP",
                "reason": "Bullish CHOCH detected"
            }

        if bearish_choch:

            return {
                "bias": "REVERSAL",
                "bos": False,
                "choch": True,
                "trend": "BEARISH_REVERSAL",
                "direction": "SELL",
                "confidence": 85,
                "sweep": sweep,
                "internal_structure": "REVERSAL_DOWN",
                "reason": "Bearish CHOCH detected"
            }

        # =====================================================
        # ⚪ RANGE
        # =====================================================

        return {
            "bias": "RANGE",
            "bos": False,
            "choch": False,
            "trend": "SIDEWAYS",
            "direction": "WAIT",
            "confidence": 40,
            "sweep": sweep,
            "internal_structure": "RANGE",
            "reason": "No confirmed structure"
        }
