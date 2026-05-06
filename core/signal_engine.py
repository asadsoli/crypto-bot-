from core.liquidity_engine import LiquidityEngine

class SignalEngine:
    def __init__(self):
        self.liquidity_engine = LiquidityEngine()

    def analyze(self, market_state, news, risk):

        # ❌ إذا ممنوع تداول
        if risk["decision"] == "BLOCK":
            return {
                "signal": "NO TRADE",
                "reason": "Risk Manager blocked trading"
            }

        # 🧠 حالة السوق الضعيفة
        if market_state["state"] == "HIGH_RISK":
            return {
                "signal": "NO TRADE",
                "reason": "Market too risky"
            }

        # 📰 أخبار خطيرة
        if news["risk"] == "HIGH":
            return {
                "signal": "NO TRADE",
                "reason": "High impact news"
            }

        # 💧 Liquidity Engine (🔥 الجديد)
        liquidity = self.liquidity_engine.analyze()

        # 🧠 إذا السوق ينتظر سحب سيولة
        if liquidity["signal_hint"] == "WAIT_SWEEP":
            return {
                "signal": "WAIT FOR LIQUIDITY SWEEP",
                "entry": "AFTER SWEEP CONFIRMATION",
                "sl": "BEYOND LIQUIDITY ZONE",
                "tp": "NEXT LIQUIDITY POOL",
                "confidence": 85,
                "quality": "SMART MONEY",
                "reason": liquidity["reason"]
            }

        # 📈 (Fallback مؤسسي)
        return {
            "signal": "BUY / SELL (INSTITUTIONAL MODE)",
            "entry": "ORDER BLOCK / FVG",
            "sl": "BELOW STRUCTURE",
            "tp": "NEXT LIQUIDITY ZONE",
            "confidence": 80,
            "quality": "INSTITUTIONAL",
            "reason": "Market ready but no clear sweep setup yet"
        }
