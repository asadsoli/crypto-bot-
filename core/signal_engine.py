from core.liquidity_engine import LiquidityEngine
from core.orderflow_engine import OrderFlowEngine
from core.market_data import MarketData
from core.smart_money import SmartMoneyEngine


class SignalEngine:

    def __init__(self):
        self.liquidity_engine = LiquidityEngine()
        self.orderflow_engine = OrderFlowEngine()
        self.smart_money = SmartMoneyEngine()
        self.market_data = MarketData("BTCUSDT", "1m")

    def analyze(self, market_state, news, risk):

        candles = self.market_data.get_candles()

        # 🛡 Safety check
        if not candles or len(candles) < 30:
            return {
                "signal": "NO TRADE",
                "reason": "Insufficient market data"
            }

        # ❌ Risk Block
        if risk["decision"] == "BLOCK":
            return {
                "signal": "NO TRADE",
                "reason": "Risk Manager blocked trading"
            }

        # 🧠 Market Risk
        if market_state["state"] == "HIGH_RISK":
            return {
                "signal": "NO TRADE",
                "reason": "Market too risky"
            }

        # 📰 News Risk
        if news["risk"] == "HIGH":
            return {
                "signal": "NO TRADE",
                "reason": "High impact news"
            }

        # =========================
        # 🧠 CORE DATA
        # =========================

        structure = self.smart_money.analyze_structure(candles)
        liquidity = self.liquidity_engine.analyze(candles)
        orderflow = self.orderflow_engine.analyze(candles)

        # =========================
        # 🔥 FIX: SAFE EXTRACTION (IMPORTANT)
        # =========================

        liquidity_hint = liquidity.get("signal_hint", "NONE")
        sweep_data = liquidity.get("sweep", {})
        sweep_type = sweep_data.get("type", "")

        ob_type = orderflow.get("type", "")
        ob_conf = orderflow.get("confidence", 0)

        # =========================
        # 💧 STATES
        # =========================

        liquidity_sweep = liquidity_hint == "WAIT_SWEEP"
        confirmed_sweep = sweep_type in ["BUY_SIDE_SWEEP", "SELL_SIDE_SWEEP"]

        ob_valid = "OB" in ob_type
        fvg_valid = "FVG" in ob_type

        # =========================
        # 🔥 CONFLUENCE ENGINE
        # =========================

        reasons = []

        # 💣 1) STRONG ENTRY (Sweep + OB)
        if confirmed_sweep and ob_valid:

            reasons = ["Liquidity Sweep Confirmed", "Order Block Aligned"]

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + OB",
                "direction": structure.get("direction", "BUY/SELL"),
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": 95,
                "quality": "SMART MONEY CONFLUENCE",
                "reason": " + ".join(reasons)
            }

        # 💣 2) LIQUIDITY + FVG
        if confirmed_sweep and fvg_valid:

            reasons = ["Liquidity Sweep Confirmed", "FVG Imbalance Zone"]

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + FVG",
                "direction": structure.get("direction", "BUY/SELL"),
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": 90,
                "quality": "SMART MONEY IMBALANCE",
                "reason": " + ".join(reasons)
            }

        # ⚠️ 3) PRE-SWEEP SETUP (important upgrade)
        if liquidity_sweep and (ob_valid or fvg_valid):

            return {
                "signal": "SETUP READY",
                "type": "PRE-LIQUIDITY",
                "direction": structure.get("direction", "WAIT"),
                "entry": orderflow.get("entry", "WAIT"),
                "confidence": 75,
                "quality": "WAITING CONFIRMATION",
                "reason": "Liquidity building near Smart Money zone"
            }

        # 📉 4) STRUCTURE ONLY (new important layer)
        if structure.get("bias") in ["TREND", "REVERSAL"]:

            return {
                "signal": "STRUCTURE ONLY",
                "type": structure.get("bias"),
                "direction": structure.get("direction"),
                "confidence": structure.get("confidence", 60),
                "quality": "STRUCTURE SIGNAL",
                "reason": structure.get("reason")
            }

        # ❌ NO CONFLUENCE
        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "quality": "NO SMART MONEY SETUP",
            "reason": "No Liquidity + OrderBlock alignment"
        }
