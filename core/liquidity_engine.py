class LiquidityEngine:

    def __init__(self):
        self.recent_swing_highs = []
        self.recent_swing_lows = []

    # =========================
    # 📊 LOAD SWINGS FROM STRUCTURE
    # =========================

    def update_swings(self, swing_highs, swing_lows):

        self.recent_swing_highs = swing_highs[-10:] if swing_highs else []
        self.recent_swing_lows = swing_lows[-10:] if swing_lows else []

    # =========================
    # 💧 FIND LIQUIDITY ZONES
    # =========================

    def detect_liquidity_zones(self):

        liquidity_zones = []

        # 🔼 Buy-side liquidity (above highs)
        for i in range(1, len(self.recent_swing_highs)):
            prev = self.recent_swing_highs[i - 1]
            curr = self.recent_swing_highs[i]

            # Equal highs (liquidity pool)
            if abs(curr["price"] - prev["price"]) <= 0.0005 * curr["price"]:
                liquidity_zones.append({
                    "type": "BUY_SIDE_LIQUIDITY",
                    "zone": curr["price"],
                    "strength": "HIGH",
                    "reason": "Equal highs liquidity pool"
                })

        # 🔽 Sell-side liquidity (below lows)
        for i in range(1, len(self.recent_swing_lows)):
            prev = self.recent_swing_lows[i - 1]
            curr = self.recent_swing_lows[i]

            # Equal lows (liquidity pool)
            if abs(curr["price"] - prev["price"]) <= 0.0005 * curr["price"]:
                liquidity_zones.append({
                    "type": "SELL_SIDE_LIQUIDITY",
                    "zone": curr["price"],
                    "strength": "HIGH",
                    "reason": "Equal lows liquidity pool"
                })

        return liquidity_zones

    # =========================
    # 🔥 SWEEP DETECTION
    # =========================

    def detect_sweep(self, candles):

        if not candles:
            return {"signal_hint": "NO_DATA", "reason": "No candles"}

        last_close = candles[-1]["close"]
        last_high = candles[-1]["high"]
        last_low = candles[-1]["low"]

        # 🟢 Sweep buy-side liquidity (stop hunts above highs)
        for swing in self.recent_swing_highs:
            if last_high > swing["price"] and last_close < swing["price"]:
                return {
                    "signal_hint": "WAIT_SELL_CONFIRMATION",
                    "type": "BUY_SIDE_SWEEP",
                    "swept_level": swing["price"],
                    "reason": "Liquidity taken above highs (sell pressure expected)"
                }

        # 🔴 Sweep sell-side liquidity
        for swing in self.recent_swing_lows:
            if last_low < swing["price"] and last_close > swing["price"]:
                return {
                    "signal_hint": "WAIT_BUY_CONFIRMATION",
                    "type": "SELL_SIDE_SWEEP",
                    "swept_level": swing["price"],
                    "reason": "Liquidity taken below lows (buy pressure expected)"
                }

        return {
            "signal_hint": "NO_SWEEP",
            "reason": "No liquidity grab detected"
        }

    # =========================
    # 🧠 MAIN ANALYSIS
    # =========================

    def analyze(self, candles, swing_highs=None, swing_lows=None):

        if swing_highs and swing_lows:
            self.update_swings(swing_highs, swing_lows)

        liquidity_zones = self.detect_liquidity_zones()
        sweep = self.detect_sweep(candles)

        # =========================
        # 🎯 FINAL DECISION
        # =========================

        # 🔥 Strong sweep setup
        if sweep["signal_hint"] in ["WAIT_BUY_CONFIRMATION", "WAIT_SELL_CONFIRMATION"]:
            return {
                "signal_hint": "WAIT_SWEEP",
                "sweep": sweep,
                "zones": liquidity_zones,
                "reason": sweep["reason"]
            }

        # 💧 Liquidity exists but no sweep yet
        if liquidity_zones:
            return {
                "signal_hint": "LIQUIDITY_PRESENT",
                "zones": liquidity_zones,
                "reason": "Liquidity pools detected"
            }

        return {
            "signal_hint": "NO_LIQUIDITY",
            "zones": [],
            "reason": "No meaningful liquidity zones"
        }
