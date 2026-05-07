from core.liquidity_engine import LiquidityEngine
from core.orderflow_engine import OrderFlowEngine
from core.market_data import MarketData
from core.smart_money import SmartMoneyEngine  # 🔥 NEW CORE

class SignalEngine:

    def __init__(self):
        self.liquidity_engine = LiquidityEngine()
        self.orderflow_engine = OrderFlowEngine()
        self.smart_money = SmartMoneyEngine()

        # 💰 Live Market Data
        self.market_data = MarketData("BTCUSDT", "1m")

    def analyze(self, market_state, news, risk):

        # 📊 Live candles
        candles = self.market_data.get_candles()

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

        # 🧠 SMART MONEY STRUCTURE (NEW CORE)
        structure = self.smart_money.analyze_structure(candles)

        # 💧 Liquidity
        liquidity = self.liquidity_engine.analyze(candles)

        # 💎 Order Flow (OB + FVG)
        orderflow = self.orderflow_engine.analyze(candles)

        # ⚪ Range
        if structure["bias"] == "RANGE":
            return {
                "signal": "NO TRADE",
                "reason": "No Smart Money structure"
            }

        # 🔄 Reversal (CHoCH)
        if structure["bias"] == "REVERSAL":
            return {
                "signal": "REVERSAL TRADE",
                "entry": "CHoCH CONFIRMATION",
                "sl": "BEYOND STRUCTURE",
                "tp": "LIQUIDITY POOL",
                "confidence": 85,
                "quality": "SMART MONEY REVERSAL",
                "reason": structure["reason"]
            }

        # 💧 Liquidity Sweep
        if liquidity["signal_hint"] == "WAIT_SWEEP":
            return {
                "signal": "WAIT SWEEP",
                "entry": "AFTER SWEEP",
                "sl": "LIQUIDITY ZONE",
                "tp": "NEXT POOL",
                "confidence": 85,
                "quality": "LIQUIDITY",
                "reason": liquidity["reason"]
            }

        # 💎 Order Block / FVG Elite Entry
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

        # 📈 Default Institutional
        return {
            "signal": "INSTITUTIONAL ENTRY",
            "entry": "ORDER BLOCK / FVG",
            "sl": "STRUCTURE",
            "tp": "LIQUIDITY ZONE",
            "confidence": 80,
            "quality": "SMART MONEY",
            "reason": "Structure + Liquidity aligned"
        }
