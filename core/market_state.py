from datetime import datetime
import pytz


class MarketStateEngine:
    def __init__(self):
        # Safe timezone initialization
        try:
            self.timezone = pytz.timezone("Asia/Damascus")
        except Exception:
            self.timezone = pytz.utc

    def get_session(self):
        """
        Detect active trading session safely.
        Returns:
            ASIA / LONDON / NEW_YORK
        """

        try:
            hour = datetime.now(self.timezone).hour

            if 0 <= hour < 8:
                return "ASIA"

            elif 8 <= hour < 16:
                return "LONDON"

            else:
                return "NEW_YORK"

        except Exception as e:
            print(f"[MarketStateEngine] Session Error: {e}")
            return "UNKNOWN"

    def get_market_state(self, news_risk="NORMAL", volatility="NORMAL"):
        """
        Market condition classifier.

        Returns:
            {
                "state": ACTIVE / CAUTION / HIGH_RISK,
                "reason": str,
                "session": str
            }
        """

        try:
            session = self.get_session()

            # Normalize inputs
            news_risk = str(news_risk).upper()
            volatility = str(volatility).upper()

            # 🔴 High Risk News
            if news_risk == "HIGH":
                return {
                    "state": "HIGH_RISK",
                    "reason": "High impact news active",
                    "session": session
                }

            # 🟡 Asian low liquidity
            if session == "ASIA" and volatility == "LOW":
                return {
                    "state": "CAUTION",
                    "reason": "Low liquidity Asian session",
                    "session": session
                }

            # 🟠 High volatility protection
            if volatility == "HIGH":
                return {
                    "state": "CAUTION",
                    "reason": "High volatility detected",
                    "session": session
                }

            # 🟢 Normal conditions
            return {
                "state": "ACTIVE",
                "reason": "Normal market conditions",
                "session": session
            }

        except Exception as e:
            print(f"[MarketStateEngine] Market State Error: {e}")

            return {
                "state": "CAUTION",
                "reason": "Fallback protection triggered",
                "session": "UNKNOWN"
            }
