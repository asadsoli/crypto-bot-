class RiskManager:
    def __init__(self):
        self.max_risk_score = 100

    def evaluate(self, market_state, news, volatility=0):
        """
        Returns: ALLOW / REDUCE / BLOCK
        """

        score = 0

        # 📰 News Risk
        if news["risk"] == "HIGH":
            score += 50
        elif news["risk"] == "MEDIUM":
            score += 25

        # 📊 Market State Risk
        if market_state["state"] == "HIGH_RISK":
            score += 50
        elif market_state["state"] == "CAUTION":
            score += 25

        # 📈 Volatility Risk
        if volatility > 70:
            score += 30
        elif volatility > 40:
            score += 15

        # 🧠 Decision Logic
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
