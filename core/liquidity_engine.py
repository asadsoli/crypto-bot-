class LiquidityEngine:

    def __init__(self, debug=False):
        self.recent_swing_highs = []
        self.recent_swing_lows = []
        self.debug = debug  # 🟢 تشغيل/إيقاف الطباعة

    # =========================
    # 📊 LOAD SWINGS
    # =========================

    def update_swings(self, swing_highs, swing_lows):

        self.recent_swing_highs = swing_highs[-10:] if swing_highs else []
        self.recent_swing_lows = swing_lows[-10:] if swing_lows else []

        if self.debug:
            print("📊 Swings Updated")
            print("🔼 Highs:", len(self.recent_swing_highs))
            print("🔽 Lows:", len(self.recent_swing_lows))

    # =========================
    # 💧 LIQUIDITY ZONES
    # =========================

    def detect_liquidity_zones(self):

        liquidity_zones = []

        for i in range(1, len(self.recent_swing_highs)):

            prev = self.recent_swing_highs[i - 1]
            curr = self.recent_swing_highs[i]

            if abs(curr["price"] - prev["price"]) <= 0.0005 * curr["price"]:
                liquidity_zones.append({
                    "type": "BUY_SIDE_LIQUIDITY",
                    "zone": curr["price"],
                    "strength": "HIGH",
                    "reason": "Equal highs liquidity pool"
                })

        for i in range(1, len(self.recent_swing_lows)):

            prev = self.recent_swing_lows[i - 1]
            curr = self.recent_swing_lows[i]

            if abs(curr["price"] - prev["price"]) <= 0.0005 * curr["price"]:
                liquidity_zones.append({
                    "type": "SELL_SIDE_LIQUIDITY",
                    "zone": curr["price"],
                    "strength": "HIGH",
                    "reason": "Equal lows liquidity pool"
                })

        if self.debug:
            print("📍 Zones Found:", len(liquidity_zones))
            print("📍 Zones Data:", liquidity_zones)

        return liquidity_zones

    # =========================
    # 🔥 SWEEP DETECTION
    # =========================

    def detect_sweep(self, candles):

        if not candles:
            return {"signal_hint": "NO_DATA", "reason": "No candles"}

        last = candles[-1]

        last_close = last["close"]
        last_high = last["high"]
        last_low = last["low"]

        for swing in self.recent_swing_highs:
            if last_high > swing["price"] and last_close < swing["price"]:
                result = {
                    "signal_hint": "WAIT_SELL_CONFIRMATION",
                    "type": "BUY_SIDE_SWEEP",
                    "swept_level": swing["price"],
                    "reason": "Liquidity taken above highs"
                }

                if self.debug:
                    print("⚡ Sweep Detected:", result)

                return result

        for swing in self.recent_swing_lows:
            if last_low < swing["price"] and last_close > swing["price"]:
                result = {
                    "signal_hint": "WAIT_BUY_CONFIRMATION",
                    "type": "SELL_SIDE_SWEEP",
                    "swept_level": swing["price"],
                    "reason": "Liquidity taken below lows"
                }

                if self.debug:
                    print("⚡ Sweep Detected:", result)

                return result

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

        if self.debug:
            print("💧 Liquidity V2 ACTIVE")
            print("⚡ Sweep:", sweep)

        # =========================
        # 🎯 DECISION
        # =========================

        if sweep["signal_hint"] in ["WAIT_BUY_CONFIRMATION", "WAIT_SELL_CONFIRMATION"]:
            return {
                "signal_hint": "WAIT_SWEEP",
                "sweep": sweep,
                "zones": liquidity_zones,
                "reason": sweep["reason"]
            }

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
