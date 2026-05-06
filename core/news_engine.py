class NewsEngine:
    def __init__(self):
        # 🔴 أخبار عالية التأثير
        self.high_impact_keywords = [
            "FOMC",
            "Powell",
            "CPI",
            "Interest Rate",
            "inflation",
            "rate hike",
            "war",
            "sanctions"
        ]

    def analyze_news(self, news_list=None):
        """
        Returns: HIGH / MEDIUM / LOW / NORMAL
        """

        if not news_list:
            return {
                "risk": "NORMAL",
                "sentiment": "NEUTRAL",
                "impact_score": 0
            }

        risk_score = 0

        for news in news_list:
            news_lower = news.lower()

            for keyword in self.high_impact_keywords:
                if keyword.lower() in news_lower:
                    risk_score += 3

        # 🧠 تحديد الحالة
        if risk_score >= 6:
            return {
                "risk": "HIGH",
                "sentiment": "VOLATILE",
                "impact_score": risk_score
            }

        elif risk_score >= 3:
            return {
                "risk": "MEDIUM",
                "sentiment": "CAUTION",
                "impact_score": risk_score
            }

        else:
            return {
                "risk": "NORMAL",
                "sentiment": "STABLE",
                "impact_score": risk_score
            }
