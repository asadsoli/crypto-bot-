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

        liquidity_hint = liquidity.get("signal
