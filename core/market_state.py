from datetime import datetime
import pytz

class MarketStateEngine:
    def __init__(self):
        self.timezone = pytz.timezone("Asia/Damascus")

    def get_session(self):
        hour = datetime.now(self.timezone).hour

        if 0 <= hour < 8:
            return "ASIA"
        elif 8 <= hour < 16:
            return "LONDON"
        else:
            return "NEW YORK"

    def get_market_state(self, news_risk="NORMAL", volatility="NORMAL"):
        """
        returns: ACTIVE / CAUTION / HIGH_RISK
        """

        session = self.get_session()

        # 🔴 قواعد السوق المؤسسية
        if news_risk == "HIGH":
            return {
                "state": "HIGH_RISK",
                "reason": "High impact news active",
                "session": session
            }

        if session == "ASIA" and volatility == "LOW":
            return {
                "state": "CAUTION",
                "reason": "Low liquidity Asian session",
                "session": session
            }

        if volatility == "HIGH":
            return {
                "state": "CAUTION",
                "reason": "High volatility detected",
                "session": session
            }

        return {
            "state": "ACTIVE",
            "reason": "Normal market conditions",
            "session": session
        }
