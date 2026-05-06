from core.liquidity_engine import LiquidityEngine
from core.market_structure import MarketStructure
from core.orderflow_engine import OrderFlowEngine
from core.market_data import MarketData  # 💰 NEW: Live Market Data

class SignalEngine:
    def __init__(self):
        self.liquidity_engine = LiquidityEngine()
        self.structure_engine = MarketStructure()
        self.orderflow_engine = OrderFlowEngine()

        # 💰 LIVE MARKET DATA (NEW)
        self.market_data = MarketData("BTCUSDT", "1m")

    def analyze(self, market_state, news, risk):

        # 📊 🔥 جلب بيانات السوق الحقيقية
        candles = self.market_data.get_candles()

        # ❌ Risk Block
        if risk["decision"] == "BLOCK":
            return {
                "signal": "NO TRADE",
                "reason": "Risk Manager blocked trading"
            }

        # 🧠 High Risk Market
        if market_state["state"] == "HIGH_RISK":
            return {
                "signal": "NO TRADE",
                "reason": "Market too risky"
            }

        # 📰 High Impact News
        if news["risk"] == "HIGH":
            return {
                "signal": "NO TRADE",
                "reason": "High impact news"
            }

        # 💧 Liquidity Analysis (الآن يمكن ترقيته لاحقًا باستخدام candles)
        liquidity = self.liquidity_engine.analyze(candles)

        # 🧱 Market Structure (حقيقي مع البيانات)
        structure = self.structure_engine.analyze(candles)

        # 💎 Order Flow (OB + FVG)
        orderflow = self.orderflow_engine.analyze(candles)

        # ⚪ Range Market → لا دخول
        if structure["bias"] == "RANGE":
            return {
                "signal": "NO TRADE",
                "reason": "Market ranging - no structure"
            }

        # 🔄 Reversal Setup (CHoCH)
        if structure["bias"] == "REVERSAL":
            return {
                "signal": "REVERSAL TRADE",
                "entry": "CHoCH CONFIRMATION ZONE",
                "sl": "BEYOND STRUCTURE",
                "tp": "NEXT LIQUIDITY POOL",
                "confidence": structure["confidence"],
                "quality": "SMART MONEY REVERSAL",
                "reason": structure["reason"]
            }

        # 💧 Liquidity Sweep Setup
        if liquidity["signal_hint"] == "WAIT_SWEEP":
            return {
                "signal": "WAIT FOR LIQUIDITY SWEEP",
                "entry": "AFTER SWEEP CONFIRMATION",
                "sl": "BEYOND LIQUIDITY ZONE",
                "tp": "NEXT LIQUIDITY POOL",
                "confidence": 85,
                "quality": "SMART MONEY LIQUIDITY",
                "reason": liquidity["reason"]
            }

        # 💎 Order Block + FVG (Elite Entry)
        if orderflow["confidence"] >= 90:
            return {
                "signal": "INSTITUTIONAL ENTRY",
                "entry": orderflow["entry"],
                "sl": orderflow["sl"],
                "tp": orderflow["tp"],
                "confidence": orderflow["confidence"],
                "quality": "ULTRA SMART MONEY",
                "reason": orderflow["reason"]
            }

        # 📈 Final Institutional Trend Trade
        return {
            "signal": "INSTITUTIONAL ENTRY",
            "entry": "ORDER BLOCK / FVG ZONE",
            "sl": "BELOW STRUCTURE",
            "tp": "NEXT LIQUIDITY ZONE",
            "confidence": 80,
            "quality": "INSTITUTIONAL SMART MONEY",
            "reason": "Structure + Liquidity aligned (LIVE DATA)"
        }
