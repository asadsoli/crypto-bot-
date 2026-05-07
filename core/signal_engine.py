from core.liquidity_engine import LiquidityEngine
from core.orderflow_engine import OrderFlowEngine
from core.market_data import MarketData
from core.smart_money import SmartMoneyEngine


class SignalEngine:

    def __init__(self):
        self.liquidity_engine = LiquidityEngine()
        self.orderflow_engine = OrderFlowEngine()
        self.smart_money = SmartMoneyEngine()

        # =========================
        # 🧠 DEFAULT MARKET DATA
        # =========================
        self.market_data = MarketData("BTCUSDT", "1m")

    # =====================================================
    # 🧠 MULTI-ASSET ENTRY (SAFE ADDITION - NO BREAKING)
    # =====================================================

    def analyze_asset(self, asset):

        try:
            # 🔥 تغيير الأداة بدون كسر النظام
            self.market_data.symbol = asset

            return self.analyze(
                market_state={"state": "ACTIVE"},
                news={"risk": "NORMAL"},
                risk={"decision": "ALLOW"}
            )

        except Exception as e:
            print(f"❌ analyze_asset error ({asset}):", e)
            return {
                "signal": "ERROR",
                "reason": f"Asset analysis failed: {asset}"
            }

    # =====================================================
    # 🧠 MAIN ENGINE (CORE - FULLY PRESERVED)
    # =====================================================

    def analyze(self, market_state, news, risk):

        candles = self.market_data.get_candles()

        # =========================
        # 🛡 SAFETY LAYER
        # =========================
        if not candles or len(candles) < 30:
            return {"signal": "NO TRADE", "reason": "Insufficient market data"}

        if risk.get("decision") == "BLOCK":
            return {"signal": "NO TRADE", "reason": "Risk Manager blocked trading"}

        if market_state.get("state") == "HIGH_RISK":
            return {"signal": "NO TRADE", "reason": "Market too risky"}

        if news.get("risk") == "HIGH":
            return {"signal": "NO TRADE", "reason": "High impact news"}

        # =========================
        # 🧠 CORE ENGINE
        # =========================

        structure = self.smart_money.analyze_structure(candles)
        liquidity = self.liquidity_engine.analyze(candles)
        orderflow = self.orderflow_engine.analyze(candles)

        # =========================
        # 🔥 SAFE EXTRACTION
        # =========================

        liquidity_hint = liquidity.get("signal_hint", "NONE")

        sweep_data = liquidity.get("sweep") or {}
        sweep_type = sweep_data.get("type", "")

        ob_type = orderflow.get("type", "")
        ob_conf = orderflow.get("confidence", 0)

        # =========================
        # 💧 STATES
        # =========================

        confirmed_sweep = sweep_type in ["BUY_SIDE_SWEEP", "SELL_SIDE_SWEEP"]
        liquidity_setup = liquidity_hint == "WAIT_SWEEP"

        ob_valid = "OB" in ob_type
        fvg_valid = "FVG" in ob_type

        # =========================
        # 🔒 CONFLUENCE GATE (STABILITY LAYER)
        # =========================

        structure_ok = structure.get("bias") in ["TREND", "REVERSAL"]

        liquidity_ok = confirmed_sweep or liquidity_setup

        orderflow_ok = (
            (ob_valid or fvg_valid)
            and ob_conf >= 75
        )

        # =========================
        # 💣 1) LIQUIDITY + OB (STRONGEST)
        # =========================

        if confirmed_sweep and ob_valid and structure_ok:

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + OB CONFLUENCE",
                "direction": structure.get("direction", "BUY/SELL"),
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": 95,
                "quality": "ULTRA SMART MONEY",
                "reason": "Liquidity Sweep + Order Block + Structure aligned"
            }

        # =========================
        # 💣 2) LIQUIDITY + FVG
        # =========================

        if confirmed_sweep and fvg_valid and structure_ok:

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + FVG CONFLUENCE",
                "direction": structure.get("direction", "BUY/SELL"),
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": 90,
                "quality": "SMART MONEY IMBALANCE",
                "reason": "Liquidity Sweep + FVG + Structure aligned"
            }

        # =========================
        # ⚠️ 3) SETUP READY
        # =========================

        if liquidity_setup and (ob_valid or fvg_valid):

            return {
                "signal": "SETUP READY",
                "type": "PRE-LIQUIDITY",
                "direction": structure.get("direction", "WAIT"),
                "entry": orderflow.get("entry", "WAIT"),
                "confidence": 75,
                "quality": "WAITING CONFIRMATION",
                "reason": "Liquidity building near Smart Money zone"
            }

        # =========================
        # 📊 4) STRUCTURE ONLY
        # =========================

        if structure.get("bias") in ["TREND", "REVERSAL"]:

            return {
                "signal": "STRUCTURE ONLY",
                "type": structure.get("bias"),
                "direction": structure.get("direction"),
                "confidence": structure.get("confidence", 60),
                "quality": "STRUCTURE SIGNAL",
                "reason": structure.get("reason")
            }

        # =========================
        # ❌ NO TRADE
        # =========================

        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "quality": "NO CONFLUENCE",
            "reason": "No Liquidity + OrderBlock + Structure alignment"
        }
