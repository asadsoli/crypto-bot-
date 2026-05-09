class BrainCore:

    def __init__(self, signal_engine, market=None, news=None, risk=None):

        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk

        # =========================
        # 🧠 SELF LEARNING MEMORY
        # =========================
        self.memory = {
            "wins": 0,
            "losses": 0,
            "last_bias": None
        }

    # =========================
    # 🧠 CONTEXT (UNCHANGED SAFE)
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
    # 🌍 MARKET REGIME DETECTOR
    # =========================

    def detect_regime(self, market_state, news):

        if news.get("risk") == "HIGH":
            return "NEWS_VOLATILE"

        if market_state.get("state") == "HIGH_RISK":
            return "HIGH_VOLATILITY"

        if market_state.get("state") == "ACTIVE":
            return "TRENDING"

        return "RANGE"

    # =========================
    # 💣 FAKE BREAKOUT FILTER
    # =========================

    def fake_breakout_filter(self, signal, confidence):

        if signal.get("type") == "BREAKOUT" and confidence < 85:
            return True

        if "weak" in signal.get("quality", "").lower():
            return True

        return False

    # =========================
    # 📊 TRADE SCORING ENGINE
    # =========================

    def score_trade(self, signal, regime):

        base = signal.get("confidence", 0)

        # regime boost
        if regime == "TRENDING":
            base += 10

        if regime == "RANGE":
            base -= 10

        # memory learning
        if self.memory["wins"] > self.memory["losses"]:
            base += 5

        return min(max(base, 0), 100)

    # =========================
    # 🧠 MAIN BRAIN V17
    # =========================

    def analyze(self, asset):

        market_state, news, risk = self.collect_context(asset)

        # =========================
        # HARD BLOCKS
        # =========================

        if risk.get("decision") == "BLOCK":
            return {
                "decision": "NO TRADE",
                "signal": {"signal": "BLOCKED", "confidence": 0},
                "reason": "Risk block"
            }

        # =========================
        # SIGNAL ENGINE
        # =========================

        try:
            signal = self.signal_engine.analyze_asset(asset)
        except:
            return {
                "decision": "ERROR",
                "signal": {"signal": "ERROR", "confidence": 0},
                "reason": "Signal failure"
            }

        # =========================
        # REGIME
        # =========================

        regime = self.detect_regime(market_state, news)

        # =========================
        # SCORE
        # =========================

        score = self.score_trade(signal, regime)

        # =========================
        # FAKE BREAKOUT FILTER
        # =========================

        if self.fake_breakout_filter(signal, score):
            return {
                "decision": "WAIT",
                "signal": signal,
                "score": score,
                "regime": regime,
                "reason": "Fake breakout detected"
            }

        # =========================
        # FINAL DECISION ENGINE
        # =========================

        if score < 70:
            return {
                "decision": "WAIT",
                "signal": signal,
                "score": score,
                "regime": regime,
                "reason": "Low quality setup"
            }

        if 70 <= score < 90:
            return {
                "decision": signal.get("signal", "WAIT"),
                "signal": signal,
                "score": score,
                "regime": regime,
                "reason": "Valid setup"
            }

        # =========================
        # HIGH PROBABILITY SETUP
        # =========================

        return {
            "decision": signal.get("signal", "BUY/SELL"),
            "signal": signal,
            "score": score,
            "regime": regime,
            "prediction": "HIGH PROBABILITY MOVE",
            "reason": "Institutional grade setup"
        }
