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
        # 🧠 SAFETY FLAGS (STABILITY LAYER)
        # =========================
        self.last_asset = None
        self.busy = False

    # =========================
    # 🧠 CONTEXT (SAFE)
    # =========================
    def collect_context(self, asset):

        try:
            market_state = self.market.get_market_state() if self.market else {"state": "UNKNOWN"}
        except Exception:
            market_state = {"state": "UNKNOWN"}

        try:
            news = self.news.analyze_news() if self.news else {"risk": "NORMAL", "impact_score": 0}
        except Exception:
            news = {"risk": "NORMAL", "impact_score": 0}

        try:
            risk = self.risk.evaluate(
                market_state=market_state,
                news=news,
                volatility=0
            ) if self.risk else {"decision": "ALLOW", "score": 0}
        except Exception:
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
    def fake_breakout_filter(self, signal, score):

        # STABILITY FIX: protect None signal
        if not signal or not isinstance(signal, dict):
            return True

        signal_type = signal.get("type", "")
        quality = signal.get("quality", "")

        if signal_type == "BREAKOUT" and score < 85:
            return True

        if "weak" in str(quality).lower():
            return True

        return False

    # =========================
    # 📊 TRADE SCORING ENGINE
    # =========================
    def score_trade(self, signal, regime):

        if not signal or not isinstance(signal, dict):
            return 0

        base = signal.get("confidence", 0)

        # regime boost / penalty
        if regime == "TRENDING":
            base += 10
        elif regime == "RANGE":
            base -= 10

        # memory learning (safe)
        try:
            if self.memory.get("wins", 0) > self.memory.get("losses", 0):
                base += 5
        except Exception:
            pass

        return max(0, min(base, 100))

    # =========================
    # 🧠 MAIN BRAIN (STABILIZED)
    # =========================
    def analyze(self, asset):

        try:

            # =========================
            # 🟡 PREVENT CONCURRENT RUNS
            # =========================
            if self.busy:
                return {
                    "decision": "WAIT",
                    "signal": {"signal": "BUSY", "confidence": 0},
                    "reason": "BrainCore already processing"
                }

            self.busy = True

            # =========================
            # CONTEXT
            # =========================
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
            except Exception:
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

        except Exception as e:
            return {
                "decision": "ERROR",
                "signal": {"signal": "ERROR", "confidence": 0},
                "reason": str(e)
            }

        finally:
            # =========================
            # ALWAYS RELEASE LOCK
            # =========================
            self.busy = False
