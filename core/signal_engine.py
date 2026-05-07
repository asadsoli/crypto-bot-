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
        if not candles or len(candles) < 20:
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
        # 💧 LIQUIDITY STATE
        # =========================

        liquidity_sweep = liquidity.get("signal") == "LIQUIDITY_SWEEP"
        wait_sweep = liquidity.get("signal_hint") == "WAIT_SWEEP"

        # =========================
        # 🧱 ORDER BLOCK STATE
        # =========================

        ob_valid = orderflow.get("type", "").endswith("OB")
        fvg_valid = orderflow.get("type", "").endswith("FVG")

        # =========================
        # 🔥 CONFLUENCE ENGINE
        # =========================

        reasons = []

        # 💣 CASE 1: STRONG ENTRY (Liquidity + Order Block)
        if liquidity_sweep and ob_valid:

            reasons.append("Liquidity Sweep Confirmed")
            reasons.append("Order Block Aligned")

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

        # 💣 CASE 2: LIQUIDITY + FVG
        if liquidity_sweep and fvg_valid:

            reasons.append("Liquidity Sweep Confirmed")
            reasons.append("FVG Imbalance Zone")

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + FVG",
                "entry": orderflow.get("entry"),
                "sl": orderflow.get("sl"),
                "tp": orderflow.get("tp"),
                "confidence": 90,
                "quality": "SMART MONEY IMBALANCE",
                "reason": " + ".join(reasons)
            }

        # ⚠️ CASE 3: SETUP READY (waiting liquidity)
        if wait_sweep and (ob_valid or fvg_valid):

            return {
                "signal": "SETUP READY",
                "type": "PRE-LIQUIDITY",
                "entry": orderflow.get("entry"),
                "confidence": 75,
                "quality": "WAITING CONFIRMATION",
                "reason": "Liquidity building near smart money zone"
            }

        # ❌ NO CONFLUENCE
        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "quality": "NO SMART MONEY SETUP",
            "reason": "Liquidity + OrderBlock not aligned"
            }
