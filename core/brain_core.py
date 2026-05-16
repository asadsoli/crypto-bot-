class BrainCore:

    def __init__(self, signal_engine, market=None, news=None, risk=None):

        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk

        # =========================
        # 🧠 MEMORY
        # =========================
        self.memory = {
            "wins": 0,
            "losses": 0,
            "last_bias": None
        }

        # =========================
        # 🧠 SAFETY STATE
        # =========================
        self.last_asset = None
        self.busy = False

    # =========================
    # 🧠 CONTEXT SAFE
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
    # 🌍 REGIME
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
    # 💣 FAKE BREAKOUT FILTER (STABLE)
    # =========================
    def fake_breakout_filter(self, signal, score):

        if not isinstance(signal, dict):
            return True

        if signal.get("type") == "BREAKOUT" and score < 85:
            return True

        quality = str(signal.get("quality", "")).lower()
        if "weak" in quality:
            return True

        return False

    # =========================
    # 📊 SCORING
    # =========================
    def score_trade(self, signal, regime):

        if not isinstance(signal, dict):
            return 0

        base = signal.get("confidence", 0)

        if regime == "TRENDING":
            base += 10
        elif regime == "RANGE":
            base -= 10

        if self.memory.get("wins", 0) > self.memory.get("losses", 0):
            base += 5

        return max(0, min(base, 100))

    # =========================
    # 🧠 MAIN BRAIN (LOCK SAFE)
    # =========================
    def analyze(self, asset):

        try:

            # =========================
            # LOCK PREVENTION
            # =========================
            if self.busy:
                return {
                    "decision": "WAIT",
                    "signal": {"signal": "BUSY", "confidence": 0},
                    "reason": "Brain is busy"
                }

            self.busy = True

            # =========================
            # CONTEXT
            # =========================
            market_state, news, risk = self.collect_context(asset)

            # =========================
            # HARD BLOCK
            # =========================
            if risk.get("decision") == "BLOCK":
                return {
                    "decision": "NO TRADE",
                    "signal": {"signal": "BLOCKED", "confidence": 0},
                    "reason": "Risk block active"
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
                    "reason": "Signal engine failure"
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
            # FILTER
            # =========================
            if self.fake_breakout_filter(signal, score):
                return {
                    "decision": "WAIT",
                    "signal": signal,
                    "score": score,
                    "regime": regime,
                    "reason": "Fake breakout filter"
                }

            # =========================
            # DECISION ENGINE
            # =========================
            if score < 70:
                return {
                    "decision": "WAIT",
                    "signal": signal,
                    "score": score,
                    "regime": regime,
                    "reason": "Low quality"
                }

            if 70 <= score < 90:
                return {
                    "decision": signal.get("signal", "WAIT"),
                    "signal": signal,
                    "score": score,
                    "regime": regime,
                    "reason": "Valid setup"
                }

            return {
                "decision": signal.get("signal", "BUY/SELL"),
                "signal": signal,
                "score": score,
                "regime": regime,
                "prediction": "HIGH PROBABILITY MOVE",
                "reason": "Institutional grade setup"
            }

        except Exception as e:

            return {
                "decision": "ERROR",
                "signal": {"signal": "ERROR", "confidence": 0},
                "reason": str(e)
            }

        finally:
            self.busy = False
