class SignalEngine:
    def __init__(self):
        pass

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

        # 📈 (مؤقت) منطق دخول بسيط مؤسسي
        return {
            "signal": "BUY / SELL (PENDING LOGIC)",
            "entry": "MARKET PRICE",
            "sl": "AUTO",
            "tp": "AUTO",
            "confidence": 75,
            "quality": "INSTITUTIONAL"
        }
