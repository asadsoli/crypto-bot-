class BrainCore:

    def __init__(self, signal_engine, market=None, news=None, risk=None):

        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk

    # =========================
    # 🧠 COLLECT DATA
    # =========================

    def collect_context(self, asset):

        # 📊 Market State
        try:
            market_state = self.market.get_market_state() if self.market else {"state": "UNKNOWN"}
        except:
            market_state = {"state": "UNKNOWN"}

        # 📰 News
        try:
            news = self.news.analyze_news() if self.news else {"risk": "NORMAL", "impact_score": 0}
        except:
            news = {"risk": "NORMAL", "impact_score": 0}

        # 🛡 Risk
        try:
            risk = self.risk.evaluate(
                market_state=market_state,
                news=news,
                volatility=0
            ) if self.risk else {"decision": "ALLOW", "score": 0}
        except:
            risk = {"decision": "ALLOW", "score": 0}

        return market_state, news, risk

    # =========================
    # 🧠 MAIN DECISION ENGINE
    # =========================

    def analyze(self, asset):

        # =========================
        # 📦 COLLECT CONTEXT
        # =========================

        market_state, news, risk = self.collect_context(asset)

        # =========================
        # 🛡 SAFETY FILTER
        # =========================

        if risk.get("decision") == "BLOCK":
            return {
                "decision": "NO TRADE",
                "reason": "Risk Manager blocked trading"
            }

        if news.get("risk") == "HIGH":
            return {
                "decision": "NO TRADE",
                "reason": "High impact news"
            }

        if market_state.get("state") == "HIGH_RISK":
            return {
                "decision": "WAIT",
                "reason": "Market too volatile"
            }

        # =========================
        # 💰 SIGNAL ENGINE
        # =========================

        try:
            signal = self.signal_engine.analyze(
                market_state=market_state,
                news=news,
                risk=risk
            )
        except Exception as e:
            return {
                "decision": "NO TRADE",
                "reason": f"Signal error: {str(e)}"
            }

        # =========================
        # 🧠 FINAL FILTER (BALANCED MODE)
        # =========================

        confidence = signal.get("confidence", 0)

        # 🟡 WAIT ZONE
        if confidence < 75:
            return {
                "decision": "WAIT",
                "signal": signal,
                "reason": "Low confidence setup"
            }

        # 🟢 GOOD TRADE
        if confidence >= 75 and confidence < 90:
            return {
                "decision": signal.get("signal", "WAIT"),
                "signal": signal,
                "reason": "Valid setup (Balanced mode)"
            }

        # 🔥 STRONG TRADE
        if confidence >= 90:
            return {
                "decision": signal.get("signal", "BUY/SELL"),
                "signal": signal,
                "reason": "High quality institutional setup"
            }

        return {
            "decision": "WAIT",
            "signal": signal,
            "reason": "Fallback state"
            }
