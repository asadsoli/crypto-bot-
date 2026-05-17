from core.liquidity_engine import LiquidityEngine
from core.orderflow_engine import OrderFlowEngine
from core.market_data import MarketDataV2 as MarketData
from core.smart_money import SmartMoneyEngine
from datetime import datetime


class SignalEngine:

    def __init__(self):

        # =========================
        # 🧠 CORE ENGINES
        # =========================
        self.liquidity_engine = LiquidityEngine()
        self.orderflow_engine = OrderFlowEngine()
        self.smart_money = SmartMoneyEngine()

        # =========================
        # 📡 MARKET DATA
        # =========================
        self.market_data = MarketData("BTCUSDT", "1m")

        # =========================
        # 🧠 BRAIN LINK
        # =========================
        self.brain = None

        # =========================
        # 🟡 STATE TRACKING
        # =========================
        self.current_asset = "BTCUSDT"

    # =========================
    # 🔗 CONNECT BRAIN
    # =========================
    def connect_brain(self, brain):
        self.brain = brain

    # =========================
    # 🔄 SET ASSET
    # =========================
    def set_asset(self, asset):

        try:

            if not asset:
                return False

            asset = str(asset).upper().strip()

            # 🔥 SAFE SYMBOL UPDATE
            self.market_data.set_symbol(asset)

            self.current_asset = asset

            if self.brain:
                self.brain.last_asset = asset

            print(f"✅ ASSET SET: {asset}")

            return True

        except Exception as e:
            print("❌ set_asset error:", e)
            return False

    # =========================
    # 📊 ANALYZE ENTRY
    # =========================
    def analyze_asset(self, asset):

        try:

            if not self.set_asset(asset):
                return {
                    "signal": "ERROR",
                    "reason": "Asset sync failed",
                    "confidence": 0
                }

            result = self.analyze(
                market_state={"state": "ACTIVE"},
                news={"risk": "NORMAL"},
                risk={"decision": "ALLOW"}
            )

            result["asset"] = self.current_asset
            result["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            return result

        except Exception as e:

            print("❌ analyze_asset error:", e)

            return {
                "signal": "ERROR",
                "reason": str(e),
                "confidence": 0
            }

    # =========================
    # 🧠 CORE ANALYSIS ENGINE
    # =========================
    def analyze(self, market_state, news, risk):

        try:

            # =========================
            # 📡 FETCH MARKET DATA
            # =========================
            print(f"📡 LOADING DATA FOR {self.current_asset}")

            candles = self.market_data.get_candles(
                self.current_asset
            )

            print("📊 CANDLES TYPE:", type(candles))

            if candles:
                print("📊 CANDLES COUNT:", len(candles))
            else:
                print("❌ EMPTY CANDLES")

            # =========================
            # ❌ NO DATA
            # =========================
            if not candles:
                return {
                    "signal": "NO DATA",
                    "reason": "Market data unavailable",
                    "confidence": 0
                }

            # =========================
            # ⚠️ NOT ENOUGH DATA
            # =========================
            if len(candles) < 30:

                print("⚠️ INSUFFICIENT DATA")

                return {
                    "signal": "WAIT",
                    "reason": "Insufficient market data",
                    "confidence": 10
                }

            # =========================
            # 🛑 RISK FILTERS
            # =========================
            if risk.get("decision") == "BLOCK":

                print("🛑 RISK BLOCKED")

                return {
                    "signal": "NO TRADE",
                    "reason": "Risk blocked"
                }

            if market_state.get("state") == "HIGH_RISK":

                print("🛑 HIGH RISK MARKET")

                return {
                    "signal": "NO TRADE",
                    "reason": "High risk market"
                }

            if news.get("risk") == "HIGH":

                print("🛑 HIGH IMPACT NEWS")

                return {
                    "signal": "NO TRADE",
                    "reason": "High impact news"
                }

            # =========================
            # 🧠 SMART MONEY
            # =========================
            try:

                structure = self.smart_money.analyze_structure(candles) or {}

                print("✅ SMART MONEY OK")

            except Exception as e:

                print("❌ SMART MONEY ERROR:", e)

                structure = {}

            # =========================
            # 💧 LIQUIDITY
            # =========================
            try:

                liquidity = self.liquidity_engine.analyze(candles) or {}

                print("✅ LIQUIDITY OK")

            except Exception as e:

                print("❌ LIQUIDITY ERROR:", e)

                liquidity = {}

            # =========================
            # 📦 ORDERFLOW
            # =========================
            try:

                orderflow = self.orderflow_engine.analyze(candles) or {}

                print("✅ ORDERFLOW OK")

            except Exception as e:

                print("❌ ORDERFLOW ERROR:", e)

                orderflow = {}

            # =========================
            # 🔍 SIGNAL LOGIC
            # =========================
            liquidity_hint = liquidity.get("signal_hint", "NONE")

            sweep = liquidity.get("sweep") or {}

            sweep_type = sweep.get("type", "")

            ob_type = orderflow.get("type", "")

            confirmed_sweep = sweep_type in [
                "BUY_SIDE_SWEEP",
                "SELL_SIDE_SWEEP"
            ]

            liquidity_setup = liquidity_hint == "WAIT_SWEEP"

            ob_valid = "OB" in ob_type
            fvg_valid = "FVG" in ob_type

            structure_ok = structure.get("bias") in [
                "TREND",
                "REVERSAL"
            ]

            direction = structure.get(
                "direction",
                "UNKNOWN"
            )

            # =========================
            # 💣 STRONG ENTRY OB
            # =========================
            if confirmed_sweep and ob_valid and structure_ok:

                print("🔥 INSTITUTIONAL ENTRY OB")

                return {
                    "signal": "INSTITUTIONAL ENTRY",
                    "type": "LIQUIDITY + OB",
                    "direction": direction,
                    "entry": orderflow.get("entry", "MARKET"),
                    "sl": orderflow.get("sl", "AUTO"),
                    "tp": orderflow.get("tp", "AUTO"),
                    "confidence": 95,
                    "quality": "SMART MONEY",
                    "reason": "Liquidity + OB + Structure"
                }

            # =========================
            # 💣 STRONG ENTRY FVG
            # =========================
            if confirmed_sweep and fvg_valid and structure_ok:

                print("🔥 INSTITUTIONAL ENTRY FVG")

                return {
                    "signal": "INSTITUTIONAL ENTRY",
                    "type": "LIQUIDITY + FVG",
                    "direction": direction,
                    "entry": orderflow.get("entry", "MARKET"),
                    "sl": orderflow.get("sl", "AUTO"),
                    "tp": orderflow.get("tp", "AUTO"),
                    "confidence": 90,
                    "quality": "IMBALANCE",
                    "reason": "Liquidity + FVG + Structure"
                }

            # =========================
            # ⚠️ SETUP READY
            # =========================
            if liquidity_setup and (ob_valid or fvg_valid):

                print("⚠️ SETUP READY")

                return {
                    "signal": "SETUP READY",
                    "type": "PRE-LIQUIDITY",
                    "direction": direction,
                    "entry": orderflow.get("entry", "WAIT"),
                    "confidence": 75,
                    "quality": "WAIT CONFIRMATION",
                    "reason": "Liquidity building zone"
                }

            # =========================
            # 📊 STRUCTURE ONLY
            # =========================
            if structure.get("bias") in [
                "TREND",
                "REVERSAL"
            ]:

                print("📊 STRUCTURE DETECTED")

                return {
                    "signal": "STRUCTURE ONLY",
                    "type": structure.get("bias"),
                    "direction": direction,
                    "confidence": structure.get("confidence", 60),
                    "quality": "STRUCTURE",
                    "reason": structure.get(
                        "reason",
                        "Structure detected"
                    )
                }

            # =========================
            # ❌ NO TRADE
            # =========================
            print("❌ NO VALID SETUP")

            return {
                "signal": "NO TRADE",
                "confidence": 0,
                "quality": "NO CONFLUENCE",
                "reason": "No valid setup"
            }

        except Exception as e:

            print("❌ SIGNAL ENGINE FATAL ERROR:", e)

            return {
                "signal": "ERROR",
                "reason": str(e),
                "confidence": 0
            }
