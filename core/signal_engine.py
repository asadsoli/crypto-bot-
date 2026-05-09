from core.liquidity_engine import LiquidityEngine
from core.orderflow_engine import OrderFlowEngine
from core.market_data import MarketData
from core.smart_money import SmartMoneyEngine


class SignalEngine:

    def __init__(self):

        self.liquidity_engine = LiquidityEngine()
        self.orderflow_engine = OrderFlowEngine()
        self.smart_money = SmartMoneyEngine()

        # =========================
        # 🧠 MARKET DATA (DEFAULT)
        # =========================
        self.market_data = MarketData("BTCUSDT", "1m")

    # =====================================================
    # 🔥 SCANNER SUPPORT LAYER (NEW - SAFE ADDITION)
    # =====================================================

    def set_asset(self, asset):

        """
        🔥 هذه أهم إضافة للـ Scanner
        بدونها Scanner ما يشتغل صح
        """

        try:
            self.market_data.symbol = asset
            return True
        except Exception as e:
            print("❌ set_asset error:", e)
            return False

    # =====================================================
    # 🧠 MULTI-ASSET ENTRY (SAFE)
    # =====================================================

    def analyze_asset(self, asset):

        try:

            # 🔥 ربط آمن مع السوق
            self.set_asset(asset)

            return self.analyze(
                market_state={"state": "ACTIVE"},
                news={"risk": "NORMAL"},
                risk={"decision": "ALLOW"}
            )

        except Exception as e:

            print(f"❌ analyze_asset error ({asset}):", e)

            return {
                "signal": "ERROR",
                "reason": f"Asset failed: {asset}",
                "confidence": 0
            }

    # =====================================================
    # 🧠 CORE ENGINE (UNCHANGED - SAFE)
    # =====================================================

    def analyze(self, market_state, news, risk):

        candles = self.market_data.get_candles()

        # =========================
        # 🛡 SAFETY LAYER
        # =========================

        if not candles or len(candles) < 30:
            return {"signal": "NO TRADE", "reason": "Insufficient market data"}

        if risk.get("decision") == "BLOCK":
            return {"signal": "NO TRADE", "reason": "Risk blocked trading"}

        if market_state.get("state") == "HIGH_RISK":
            return {"signal": "NO TRADE", "reason": "Market too risky"}

        if news.get("risk") == "HIGH":
            return {"signal": "NO TRADE", "reason": "High impact news"}

        # =========================
        # 🧠 CORE ANALYSIS
        # =========================

        structure = self.smart_money.analyze_structure(candles)
        liquidity = self.liquidity_engine.analyze(candles)
        orderflow = self.orderflow_engine.analyze(candles)

        # =========================
        # 🔥 EXTRACTION SAFE
        # =========================

        liquidity_hint = liquidity.get("signal_hint", "NONE")

        sweep_data = liquidity.get("sweep") or {}
        sweep_type = sweep_data.get("type", "")

        ob_type = orderflow.get("type", "")
        ob_conf = orderflow.get("confidence", 0)

        # =========================
        # 💧 CONDITIONS
        # =========================

        confirmed_sweep = sweep_type in ["BUY_SIDE_SWEEP", "SELL_SIDE_SWEEP"]
        liquidity_setup = liquidity_hint == "WAIT_SWEEP"

        ob_valid = "OB" in ob_type
        fvg_valid = "FVG" in ob_type

        # =========================
        # 🧠 FIX: SmartMoney Compatibility Patch
        # =========================

        structure_bias = structure.get("bias")
        direction = structure.get("trend", "NEUTRAL")  # 🔥 FIX ADDED

        structure_ok = structure_bias in [
            "BULLISH",
            "BEARISH",
            "REVERSAL"
        ]

        # =====================================================
        # 💣 1) STRONG ENTRY (LIQUIDITY + OB)
        # =====================================================

        if confirmed_sweep and ob_valid and structure_ok:

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + OB",
                "direction": direction,
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": 95,
                "quality": "ULTRA SMART MONEY",
                "reason": "Liquidity Sweep + OrderBlock + Structure"
            }

        # =====================================================
        # 💣 2) LIQUIDITY + FVG
        # =====================================================

        if confirmed_sweep and fvg_valid and structure_ok:

            return {
                "signal": "INSTITUTIONAL ENTRY",
                "type": "LIQUIDITY + FVG",
                "direction": direction,
                "entry": orderflow.get("entry", "MARKET"),
                "sl": orderflow.get("sl", "AUTO"),
                "tp": orderflow.get("tp", "AUTO"),
                "confidence": 90,
                "quality": "IMBALANCE",
                "reason": "Liquidity Sweep + FVG + Structure"
            }

        # =====================================================
        # ⚠️ 3) SETUP READY
        # =====================================================

        if liquidity_setup and (ob_valid or fvg_valid):

            return {
                "signal": "SETUP READY",
                "type": "PRE-LIQUIDITY",
                "direction": direction,
                "entry": orderflow.get("entry", "WAIT"),
                "confidence": 75,
                "quality": "WAIT CONFIRMATION",
                "reason": "Liquidity building zone"
            }

        # =====================================================
        # 📊 4) STRUCTURE ONLY
        # =====================================================

        if structure_ok:

            return {
                "signal": "STRUCTURE ONLY",
                "type": structure_bias,
                "direction": direction,
                "confidence": structure.get("confidence", 60),
                "quality": "STRUCTURE",
                "reason": structure.get("reason")
            }

        # =====================================================
        # ❌ NO TRADE
        # =====================================================

        return {
            "signal": "NO TRADE",
            "confidence": 0,
            "quality": "NO CONFLUENCE",
            "reason": "No valid setup"
            }
