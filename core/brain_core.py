import logging
from typing import Dict, Any, Optional, Tuple
from threading import Lock

logger = logging.getLogger(__name__)


class BrainCore:
    """
    🧠 Brain Core - Main decision engine for crypto trading
    Handles context collection, regime detection, and trade analysis
    """

    def __init__(self, signal_engine, market=None, news=None, risk=None):
        """
        Initialize BrainCore with required engines

        Args:
            signal_engine: Engine for analyzing trading signals
            market: Market analysis engine (optional)
            news: News analysis engine (optional)
            risk: Risk evaluation engine (optional)
        """
        if signal_engine is None:
            raise ValueError("signal_engine is required")

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
        self._lock = Lock()  # Thread safety

    # =========================
    # 🧠 CONTEXT SAFE
    # =========================
    def collect_context(self, asset: str) -> Tuple[Dict, Dict, Dict]:
        """
        Safely collect market, news, and risk context

        Args:
            asset: Asset symbol to analyze

        Returns:
            Tuple of (market_state, news, risk) dictionaries
        """
        if not isinstance(asset, str) or not asset.strip():
            logger.warning(f"Invalid asset provided: {asset}")
            asset = "UNKNOWN"

        # Collect market state
        market_state = self._safe_call(
            self.market.get_market_state if self.market else None,
            default={"state": "UNKNOWN"},
            context="market.get_market_state"
        )

        # Collect news analysis
        news = self._safe_call(
            self.news.analyze_news if self.news else None,
            default={"risk": "NORMAL", "impact_score": 0},
            context="news.analyze_news"
        )

        # Collect risk evaluation
        risk = self._safe_call(
            lambda: self.risk.evaluate(
                market_state=market_state,
                news=news,
                volatility=0
            ) if self.risk else None,
            default={"decision": "ALLOW", "score": 0},
            context="risk.evaluate"
        )

        return market_state, news, risk

    def _safe_call(self, func, default: Dict, context: str = "") -> Dict:
        """
        Safely call a function with exception handling

        Args:
            func: Function to call
            default: Default value if function fails
            context: Context description for logging

        Returns:
            Function result or default value
        """
        if func is None:
            return default

        try:
            result = func()
            if not isinstance(result, dict):
                logger.warning(f"{context} returned non-dict: {type(result)}")
                return default
            return result
        except Exception as e:
            logger.error(f"Error in {context}: {str(e)}", exc_info=True)
            return default

    # =========================
    # 🌍 REGIME
    # =========================
    def detect_regime(self, market_state: Dict, news: Dict) -> str:
        """
        Detect current market regime

        Args:
            market_state: Current market state dictionary
            news: Current news analysis dictionary

        Returns:
            Regime string: "NEWS_VOLATILE", "HIGH_VOLATILITY", "TRENDING", or "RANGE"
        """
        if not isinstance(market_state, dict) or not isinstance(news, dict):
            logger.warning("Invalid market_state or news format in detect_regime")
            return "RANGE"

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
    def fake_breakout_filter(self, signal: Dict, score: int) -> bool:
        """
        Filter out fake breakouts and low-quality signals

        Args:
            signal: Signal dictionary
            score: Signal score (0-100)

        Returns:
            True if signal should be filtered (rejected), False otherwise
        """
        if not isinstance(signal, dict):
            logger.warning(f"Invalid signal type in fake_breakout_filter: {type(signal)}")
            return True

        if not isinstance(score, (int, float)):
            logger.warning(f"Invalid score type: {type(score)}")
            return True

        # Filter weak breakouts
        if signal.get("type") == "BREAKOUT" and score < 85:
            logger.debug(f"Filtered breakout: score {score} < 85")
            return True

        # Filter low-quality signals
        quality = str(signal.get("quality", "")).lower()
        if "weak" in quality:
            logger.debug(f"Filtered weak quality signal")
            return True

        return False

    # =========================
    # 📊 SCORING
    # =========================
    def score_trade(self, signal: Dict, regime: str) -> int:
        """
        Calculate trade score based on signal and regime

        Args:
            signal: Signal dictionary
            regime: Current market regime

        Returns:
            Score between 0-100
        """
        if not isinstance(signal, dict):
            logger.warning(f"Invalid signal in score_trade: {type(signal)}")
            return 0

        if not isinstance(regime, str):
            logger.warning(f"Invalid regime in score_trade: {type(regime)}")
            return 0

        # Base score from signal confidence
        try:
            base = int(signal.get("confidence", 0))
            base = max(0, min(base, 100))  # Clamp to 0-100
        except (ValueError, TypeError):
            logger.warning(f"Invalid confidence value: {signal.get('confidence')}")
            base = 0

        # Regime adjustments
        if regime == "TRENDING":
            base += 10
        elif regime == "RANGE":
            base -= 10

        # Win/loss adjustment
        wins = int(self.memory.get("wins", 0))
        losses = int(self.memory.get("losses", 0))
        if wins > losses:
            base += 5

        return max(0, min(base, 100))

    # =========================
    # 🧠 MAIN BRAIN (LOCK SAFE)
    # =========================
    def analyze(self, asset: str) -> Dict[str, Any]:
        """
        Analyze asset and make trading decision

        Args:
            asset: Asset symbol to analyze

        Returns:
            Decision dictionary with analysis details
        """
        # Input validation
        if not isinstance(asset, str) or not asset.strip():
            logger.error(f"Invalid asset parameter: {asset}")
            return {
                "decision": "ERROR",
                "signal": {"signal": "ERROR", "confidence": 0},
                "reason": "Invalid asset parameter"
            }

        try:
            # Thread-safe lock to prevent concurrent analysis
            with self._lock:
                if self.busy:
                    logger.debug(f"Brain is busy, waiting for asset {asset}")
                    return {
                        "decision": "WAIT",
                        "signal": {"signal": "BUSY", "confidence": 0},
                        "reason": "Brain is busy"
                    }

                self.busy = True

            # =========================
            # CONTEXT COLLECTION
            # =========================
            market_state, news, risk = self.collect_context(asset)

            # =========================
            # HARD BLOCK CHECK
            # =========================
            if risk.get("decision") == "BLOCK":
                logger.warning(f"Trade blocked for {asset} - Risk block active")
                return {
                    "decision": "NO TRADE",
                    "signal": {"signal": "BLOCKED", "confidence": 0},
                    "reason": "Risk block active"
                }

            # =========================
            # SIGNAL ENGINE ANALYSIS
            # =========================
            try:
                signal = self.signal_engine.analyze_asset(asset)
                if not isinstance(signal, dict):
                    logger.error(f"Signal engine returned non-dict: {type(signal)}")
                    return {
                        "decision": "ERROR",
                        "signal": {"signal": "ERROR", "confidence": 0},
                        "reason": "Invalid signal format"
                    }
            except Exception as e:
                logger.error(f"Signal engine failure for {asset}: {str(e)}", exc_info=True)
                return {
                    "decision": "ERROR",
                    "signal": {"signal": "ERROR", "confidence": 0},
                    "reason": f"Signal engine failure: {str(e)}"
                }

            # =========================
            # REGIME DETECTION
            # =========================
            regime = self.detect_regime(market_state, news)
            logger.debug(f"Detected regime for {asset}: {regime}")

            # =========================
            # TRADE SCORING
            # =========================
            score = self.score_trade(signal, regime)
            logger.debug(f"Trade score for {asset}: {score}")

            # =========================
            # FAKE BREAKOUT FILTER
            # =========================
            if self.fake_breakout_filter(signal, score):
                logger.info(f"Signal filtered for {asset}: fake breakout detected")
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
                logger.info(f"Low quality signal for {asset}: score {score}")
                return {
                    "decision": "WAIT",
                    "signal": signal,
                    "score": score,
                    "regime": regime,
                    "reason": "Low quality"
                }

            if 70 <= score < 90:
                decision = signal.get("signal", "WAIT")
                logger.info(f"Valid setup for {asset}: {decision} (score {score})")
                return {
                    "decision": decision,
                    "signal": signal,
                    "score": score,
                    "regime": regime,
                    "reason": "Valid setup"
                }

            # High probability trade
            decision = signal.get("signal", "BUY/SELL")
            logger.info(f"High probability move for {asset}: {decision} (score {score})")
            return {
                "decision": decision,
                "signal": signal,
                "score": score,
                "regime": regime,
                "prediction": "HIGH PROBABILITY MOVE",
                "reason": "Institutional grade setup"
            }

        except Exception as e:
            logger.error(f"Critical error in analyze for {asset}: {str(e)}", exc_info=True)
            return {
                "decision": "ERROR",
                "signal": {"signal": "ERROR", "confidence": 0},
                "reason": f"Critical error: {str(e)}"
            }

        finally:
            with self._lock:
                self.busy = False

    # =========================
    # 📈 MEMORY MANAGEMENT
    # =========================
    def record_win(self) -> None:
        """Record a successful trade"""
        self.memory["wins"] += 1
        logger.info(f"Win recorded. Total wins: {self.memory['wins']}")

    def record_loss(self) -> None:
        """Record a failed trade"""
        self.memory["losses"] += 1
        logger.info(f"Loss recorded. Total losses: {self.memory['losses']}")

    def reset_memory(self) -> None:
        """Reset trading memory"""
        self.memory = {
            "wins": 0,
            "losses": 0,
            "last_bias": None
        }
        logger.info("Memory reset")

    def get_stats(self) -> Dict[str, Any]:
        """Get current trading statistics"""
        total = self.memory.get("wins", 0) + self.memory.get("losses", 0)
        win_rate = (self.memory.get("wins", 0) / total * 100) if total > 0 else 0

        return {
            "wins": self.memory["wins"],
            "losses": self.memory["losses"],
            "total_trades": total,
            "win_rate": f"{win_rate:.2f}%"
        }
