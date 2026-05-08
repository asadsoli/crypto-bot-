class BrainCore:

    def __init__(self, signal_engine, market=None, news=None, risk=None):

        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk

    # =========================
    # 🧠 COLLECT CONTEXT
    # =========================

    def collect_context(self, asset):

        # =========================
        # 📊 MARKET STATE
        # =========================

        try:

            if self.market:
                market_state = self.market.get_market_state()

            else:
                market_state = {
                    "state": "UNKNOWN"
                }

        except:

            market_state = {
                "state": "UNKNOWN"
            }

        # =========================
        # 📰 NEWS
        # =========================

        try:

            if self.news:
                news = self.news.analyze_news()

            else:
                news = {
                    "risk": "NORMAL",
                    "impact_score": 0
                }

        except:

            news = {
                "risk": "NORMAL",
                "impact_score": 0
            }

        # =========================
        # 🛡 RISK
        # =========================

        try:

            if self.risk:

                risk = self.risk.evaluate(
                    market_state=market_state,
                    news=news,
                    volatility=0
                )

            else:

                risk = {
                    "decision": "ALLOW",
                    "score": 0
                }

        except:

            risk = {
                "decision": "ALLOW",
                "score": 0
            }

        return market_state, news, risk

    # =========================
    # 🧠 MAIN AI ENGINE
    # =========================

    def analyze(self, asset):

        # =========================
        # 📦 CONTEXT
        # =========================

        market_state, news, risk = self.collect_context(asset)

        # =========================
        # 🛡 SAFETY FILTER
        # =========================

        if risk.get("decision") == "BLOCK":

            return {
                "decision": "NO TRADE",
                "signal": {
                    "signal": "NO TRADE",
                    "confidence": 0
                },
                "reason": "Risk Manager blocked trading"
            }

        # =========================
        # 📰 HIGH IMPACT NEWS
        # =========================

        if news.get("risk") == "HIGH":

            return {
                "decision": "WAIT NEWS",
                "signal": {
                    "signal": "HIGH NEWS",
                    "confidence": 0
                },
                "reason": "High impact news detected"
            }

        # =========================
        # ⚠️ MARKET RISK
        # =========================

        if market_state.get("state") == "HIGH_RISK":

            return {
                "decision": "WAIT",
                "signal": {
                    "signal": "HIGH RISK",
                    "confidence": 0
                },
                "reason": "Market volatility too high"
            }

        # =========================
        # 💰 SIGNAL ENGINE
        # =========================

        try:

            # 🔥 MULTI ASSET SUPPORT
            signal = self.signal_engine.analyze_asset(asset)

        except Exception as e:

            return {
                "decision": "ERROR",
                "signal": {
                    "signal": "ERROR",
                    "confidence": 0
                },
                "reason": f"Signal error: {str(e)}"
            }

        # =========================
        # 🧠 AI FILTER
        # =========================

        confidence = signal.get("confidence", 0)

        # =========================
        # 🔴 LOW CONFIDENCE
        # =========================

        if confidence < 75:

            return {
                "decision": "WAIT",
                "signal": signal,
                "reason": "Low confidence setup"
            }

        # =========================
        # 🟡 VALID SETUP
        # =========================

        if 75 <= confidence < 90:

            return {
                "decision": signal.get("signal", "WAIT"),
                "signal": signal,
                "reason": "Balanced setup confirmed"
            }

        # =========================
        # 🔥 HIGH QUALITY
        # =========================

        if confidence >= 90:

            return {
                "decision": signal.get("signal", "BUY/SELL"),
                "signal": signal,
                "reason": "Institutional setup confirmed"
            }

        # =========================
        # ⚠️ FALLBACK
        # =========================

        return {
            "decision": "WAIT",
            "signal": signal,
            "reason": "Fallback state"
        }
