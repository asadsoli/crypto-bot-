class RiskManager:

    def __init__(self):
        self.max_risk_score = 100

    def evaluate(self, market_state, news, volatility=0):
        """
        Returns: ALLOW / REDUCE / BLOCK
        """

        # =========================
        # 🛡 SAFE INPUT HANDLING
        # =========================
        if not isinstance(news, dict):
            news = {"risk": "NORMAL"}

        if not isinstance(market_state, dict):
            market_state = {"state": "UNKNOWN"}

        if volatility is None:
            volatility = 0

        score = 0

        # =========================
        # 📰 NEWS RISK
        # =========================
        news_risk = news.get("risk", "NORMAL")

        if news_risk == "HIGH":
            score += 50
        elif news_risk == "MEDIUM":
            score += 25

        # =========================
        # 📊 MARKET STATE RISK
        # =========================
        market_state_value = market_state.get("state", "UNKNOWN")

        if market_state_value == "HIGH_RISK":
            score += 50
        elif market_state_value == "CAUTION":
            score += 25

        # =========================
        # 📈 VOLATILITY RISK
        # =========================
        try:
            volatility = float(volatility)
        except:
            volatility = 0

        if volatility > 70:
            score += 30
        elif volatility > 40:
            score += 15

        # =========================
        # 🧠 DECISION LOGIC
        # =========================
        if score >= 70:
            return {
                "decision": "BLOCK",
                "score": score,
                "reason": "High combined risk detected"
            }

        elif score >= 40:
            return {
                "decision": "REDUCE",
                "score": score,
                "reason": "Moderate risk - reduce exposure"
            }

        else:
            return {
                "decision": "ALLOW",
                "score": score,
                "reason": "Safe market conditions"
            }
