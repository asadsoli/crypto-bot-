from core.liquidity_engine import LiquidityEngine
from core.orderflow_engine import OrderFlowEngine
from core.market_data import MarketData
from core.smart_money import SmartMoneyEngine

from datetime import datetime


class SignalEngine:

    def __init__(self):

        self.liquidity_engine = LiquidityEngine()
        self.orderflow_engine = OrderFlowEngine()
        self.smart_money = SmartMoneyEngine()

        self.market_data = MarketData("BTCUSDT", "1m")

        # 🧠 FIX: Brain reference (optional safe link)
        self.brain = None

    # =========================
    # 🔗 BRAIN CONNECT (NEW SAFE ADDITION)
    # =========================

    def connect_brain(self, brain):

        """
        ربط Brain V17 مع SignalEngine
        """
        self.brain = brain

    # =========================
    # 🔥 SCANNER SUPPORT
    # =========================

    def set_asset(self, asset):

        try:
            self.market_data.symbol = asset

            # 🧠 FIX IMPORTANT: sync brain asset if connected
            if self.brain:
                self.brain.last_asset = asset

            return True

        except Exception as e:
            print("❌ set_asset error:", e)
            return False

    # =========================
    # 🧠 MULTI ASSET
    # =========================

    def analyze_asset(self, asset):

        try:

            self.set_asset(asset)

            result = self.analyze(
                market_state={"state": "ACTIVE"},
                news={"risk": "NORMAL"},
                risk={"decision": "ALLOW"}
            )

            # 🆕 FIX: context injection
            result["asset"] = asset
            result["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            return result

        except Exception as e:

            return {
                "signal": "ERROR",
                "reason": str(e),
                "confidence": 0
            }

    # =========================
    # 🧠 CORE ENGINE
    # =========================

    def analyze(self, market_state, news, risk):

        candles = self.market_data.get_candles()

        # =========================
        # 🧠 FIXED SAFETY LOGIC
        # =========================

        if not candles:
            return {
                "signal": "NO DATA",
                "reason": "No candles received",
                "confidence": 0
            }

        if len(candles) < 30:
            return {
                "signal": "WAIT",
                "reason": "Market still warming up (low candles)",
                "confidence": 10
            }

        if risk.get("decision") == "BLOCK":
            return {"signal": "NO TRADE", "reason": "Risk blocked trading"}

        if market_state.get("state") == "HIGH_RISK":
            return {"signal": "NO TRADE", "reason": "Market too risky"}

        if news.get("risk") == "HIGH":
            return {"signal": "NO TRADE", "reason": "High impact news"}

        # =========================
        # 🧠 ANALYSIS CORE
        # =========================

        structure = self.smart_money.analyze_structure(candles)
        liquidity = self.liquidity_engine.analyze(candles)
        orderflow = self.orderflow_engine.analyze(candles)

        # =========================
        # 🔥 FIXED LINE (THE ERROR WAS HERE)
        # =========================

        liquidity_hint = liquidity.get("signal_hint", "NONE")

        sweep_data = liquidity.get("sweep") or {}
        sweep_type = sweep_data.get("type", "")

        ob_type = orderflow.get("type", "")

        confirmed_sweep = sweep_type in ["BUY_SIDE_SWEEP", "SELL_SIDE_SWEEP"]
        liquidity_setup = liquidity_hint == "WAIT_SWEEP"

        ob_valid = "OB" in ob_type
        fvg_valid = "FVG" in ob_type

        structure_ok = structure.get("bias") in ["TREND", "REVERSAL"]

        # =========================
        # 💣 STRONG ENTRY
        # =========================

        if confirmed_sweep and ob_valid and structure_ok:

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + OB",
                "direction": structure.get("direction", "BUY/SELL"),
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": 95,
                "quality": "ULTRA SMART MONEY",
                "reason": "Liquidity Sweep + OrderBlock + Structure"
            }

        # =========================
        # 💣 FVG ENTRY
        # =========================

        if confirmed_sweep and fvg_valid and structure_ok:

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + FVG",
                "direction": structure.get("direction", "BUY/SELL"),
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": 90,
                "quality": "IMBALANCE",
                "reason": "Liquidity Sweep + FVG + Structure"
            }

        # =========================
        # ⚠️ SETUP READY
        # =========================

        if liquidity_setup and (ob_valid or fvg_valid):

            return {
                "signal": "SETUP READY",
                "type": "PRE-LIQUIDITY",
                "direction": structure.get("direction", "WAIT"),
                "entry": orderflow.get("entry", "WAIT"),
                "confidence": 75,
                "quality": "WAIT CONFIRMATION",
                "reason": "Liquidity building zone"
            }

        # =========================
        # 📊 STRUCTURE ONLY
        # =========================

        if structure.get("bias") in ["TREND", "REVERSAL"]:

            return {
                "signal": "STRUCTURE ONLY",
                "type": structure.get("bias"),
                "direction": structure.get("direction"),
                "confidence": structure.get("confidence", 60),
                "quality": "STRUCTURE",
                "reason": structure.get("reason")
            }

        # =========================
        # ❌ NO TRADE FIXED
        # =========================

        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "quality": "NO CONFLUENCE",
            "reason": "Market conditions not aligned"
            }
