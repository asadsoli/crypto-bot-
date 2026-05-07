def analyze(self, market_state, news, risk):

    candles = self.market_data.get_candles()

    # 🛡 Safety check (مهم جدًا)
    if not candles or len(candles) < 20:
        return {
            "signal": "NO TRADE",
            "reason": "Insufficient market data"
        }

    # ❌ Risk Block
    if risk["decision"] == "BLOCK":
        return {
            "signal": "NO TRADE",
            "reason": "Risk Manager blocked trading"
        }

    # 🧠 Market Risk
    if market_state["state"] == "HIGH_RISK":
        return {
            "signal": "NO TRADE",
            "reason": "Market too risky"
        }

    # 📰 News Risk
    if news["risk"] == "HIGH":
        return {
            "signal": "NO TRADE",
            "reason": "High impact news"
        }

    # =========================
    # 🧠 CORE ANALYSIS
    # =========================

    structure = self.smart_money.analyze_structure(candles)
    liquidity = self.liquidity_engine.analyze(candles)
    orderflow = self.orderflow_engine.analyze(candles)

    score = 0
    reasons = []

    # 🧱 Structure Weight
    if structure["bias"] == "REVERSAL":
        score += 35
        reasons.append("Structure Reversal")

    elif structure["bias"] == "TREND":
        score += 25
        reasons.append("Trend Structure")

    # 💧 Liquidity Weight
    if liquidity["signal_hint"] == "WAIT_SWEEP":
        score += 35
        reasons.append("Liquidity Sweep Setup")

    # 💎 OrderFlow Weight
    if orderflow.get("confidence", 0) >= 90:
        score += 40
        reasons.append("Order Block / FVG Strong")

    elif orderflow.get("confidence", 0) >= 75:
        score += 25
        reasons.append("Moderate Order Flow")

    # =========================
    # 📊 FINAL DECISION ENGINE
    # =========================

    if score >= 85:

        return {
            "signal": "INSTITUTIONAL ENTRY",
            "direction": structure.get("direction", "BUY/SELL"),
            "entry": orderflow.get("entry", "MARKET"),
            "sl": orderflow.get("sl", "AUTO"),
            "tp": orderflow.get("tp", "AUTO"),
            "confidence": score,
            "quality": "ULTRA SMART MONEY",
            "reason": " + ".join(reasons)
        }

    elif score >= 60:

        return {
            "signal": "WATCH ZONE",
            "confidence": score,
            "quality": "MID SETUP",
            "reason": " + ".join(reasons)
        }

    return {
        "signal": "NO TRADE",
        "confidence": score,
        "quality": "LOW PROBABILITY",
        "reason": "No confluence detected"
    }
