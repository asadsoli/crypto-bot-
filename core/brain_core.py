class BrainCore:

    def __init__(self, signal_engine, market=None, news=None, risk=None):

        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk

    # =========================
    # 🧠 COLLECT CONTEXT
    # (KEEP - بدون تغيير)
    # =========================

    def collect_context(self, asset):

        try:
            market_state = self.market.get_market_state() if self.market else {"state": "UNKNOWN"}
        except:
            market_state = {"state": "UNKNOWN"}

        try:
            news = self.news.analyze_news() if self.news else {"risk": "NORMAL", "impact_score": 0}
        except:
            news = {"risk": "NORMAL", "impact_score": 0}

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
    # 🧠 FINAL BRAIN ENGINE (V2 UPGRADED)
    # =========================

    def analyze(self, asset):

        market_state, news, risk = self.collect_context(asset)

        # =========================
        # ❌ HARD BLOCK LAYERS
        # =========================

        if risk.get("decision") == "BLOCK":
            return {
                "decision": "NO TRADE",
                "signal": {"signal": "BLOCKED", "confidence": 0},
                "reason": "Risk Manager blocked trade"
            }

        if news.get("risk") == "HIGH":
            return {
                "decision": "NO TRADE",
                "signal": {"signal": "NEWS BLOCK", "confidence": 0},
                "reason": "High impact news"
            }

        if market_state.get("state") == "HIGH_RISK":
            return {
                "decision": "WAIT",
                "signal": {"signal": "RISK MARKET", "confidence": 0},
                "reason": "Market too volatile"
            }

        # =========================
        # 📊 SIGNAL ENGINE
        # =========================

        try:
            signal = self.signal_engine.analyze_asset(asset)
        except Exception as e:
            return {
                "decision": "ERROR",
                "signal": {"signal": "ERROR", "confidence": 0},
                "reason": str(e)
            }

        # =========================
        # 🧠 SAFE DEFAULTS
        # =========================

        if not isinstance(signal, dict):
            signal = {"signal": "NO TRADE", "confidence": 0}

        confidence = signal.get("confidence", 0)

        # =========================
        # 🧠 SESSION BIAS (SAFE FIX)
        # =========================

        session_bias = market_state.get("state", "UNKNOWN")

        # =========================
        # 🧠 FINAL BRAIN FILTER (V2)
        # =========================

        # 🔴 LOW QUALITY
        if confidence < 70:
            return {
                "decision": "WAIT",
                "signal": signal,
                "reason": "BrainCore: low confidence filtered"
            }

        # 🟡 NORMAL TRADE
        if 70 <= confidence < 90:
            return {
                "decision": signal.get("signal", "WAIT"),
                "signal": signal,
                "reason": "BrainCore: valid setup"
            }

        # 🔥 HIGH QUALITY + SESSION BOOST
        if confidence >= 90:
            return {
                "decision": signal.get("signal", "BUY/SELL"),
                "signal": signal,
                "session": session_bias,
                "reason": "BrainCore: institutional grade setup"
            }

        return {
            "decision": "WAIT",
            "signal": signal,
            "reason": "BrainCore fallback"
            }
