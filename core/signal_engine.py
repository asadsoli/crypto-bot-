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
            return {"signal": "NO TRADE", "reason": "Insufficient market data"}

        # ❌ Risk filter
        if risk["decision"] == "BLOCK":
            return {"signal": "NO TRADE", "reason": "Risk Manager blocked trading"}

        if market_state["state"] == "HIGH_RISK":
            return {"signal": "NO TRADE", "reason": "Market too risky"}

        if news["risk"] == "HIGH":
            return {"signal": "NO TRADE", "reason": "High impact news"}

        # =========================
        # 🧠 CORE ANALYSIS
        # =========================

        structure = self.smart_money.analyze_structure(candles)
        liquidity = self.liquidity_engine.analyze(candles)
        orderflow = self.orderflow_engine.analyze(candles)

        # =========================
        # 🔥 SAFE EXTRACT
        # =========================

        liquidity_hint = liquidity.get("signal_hint", "NONE")
        sweep = liquidity.get("sweep", {})
        sweep_type = sweep.get("type", "")

        ob_type = orderflow.get("type", "")
        confidence = orderflow.get("confidence", 0)

        # =========================
        # 💣 CONDITIONS
        # =========================

        confirmed_sweep = sweep_type in ["BUY_SIDE_SWEEP", "SELL_SIDE_SWEEP"]
        liquidity_setup = liquidity_hint == "WAIT_SWEEP"

        ob_valid = "OB" in ob_type
        fvg_valid = "FVG" in ob_type

        score = 0
        reasons = []

        # =========================
        # 🧠 STRUCTURE SCORE
        # =========================

        if structure["bias"] == "REVERSAL":
            score += 35
            reasons.append("CHoCH / Reversal")

        elif structure["bias"] == "TREND":
            score += 25
            reasons.append("Trend Structure")

        # =========================
        # 💧 LIQUIDITY SCORE
        # =========================

        if confirmed_sweep:
            score += 35
            reasons.append("Liquidity Sweep Confirmed")

        elif liquidity_setup:
            score += 20
            reasons.append("Liquidity Building")

        # =========================
        # 💎 ORDERFLOW SCORE
        # =========================

        if confidence >= 90:
            score += 40
            reasons.append("Strong OB / FVG")

        elif confidence >= 75:
            score += 25
            reasons.append("Moderate OrderFlow")

        # =========================
        # 🎯 FINAL DECISION ENGINE
        # =========================

        if score >= 85 and (confirmed_sweep and (ob_valid or fvg_valid)):

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "FULL CONFLUENCE",
                "direction": structure.get("direction", "BUY/SELL"),
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": score,
                "quality": "ULTRA SMART MONEY",
                "reason": " + ".join(reasons)
            }

        elif score >= 70:

            return {
                "signal": "WATCH ZONE",
                "type": "PARTIAL CONFLUENCE",
                "confidence": score,
                "quality": "MID SETUP",
                "reason": " + ".join(reasons)
            }

        return {
            "signal": "NO TRADE",
            "confidence": score,
            "quality": "NO CONFLUENCE",
            "reason": "Insufficient alignment between Liquidity + OB + Structure"
            }
