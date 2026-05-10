import requests
import time


class MarketDataV2:

    def __init__(self, symbol="BTCUSDT", interval="1m"):

        self.symbol = symbol
        self.interval = interval

        # =========================
        # 🧠 CACHE STORAGE
        # =========================
        self.cache = {}          # symbol -> candles
        self.last_update = {}    # symbol -> timestamp
        self.last_good = {}      # symbol -> last valid candles

        # =========================
        # ⏱ CACHE TIMEOUT
        # =========================
        self.ttl = 10

        # =========================
        # 🌐 REQUEST SETTINGS
        # =========================
        self.timeout = 10
        self.base_url = "https://api.binance.com/api/v3/klines"

    # =========================
    # 🔧 SAFE CONVERTER
    # =========================
    def safe_float(self, x):
        try:
            return float(x)
        except:
            return None

    # =========================
    # 📡 FETCH DATA
    # =========================
    def fetch_candles(self, symbol):

        params = {
            "symbol": symbol,
            "interval": self.interval,
            "limit": 50
        }

        try:
            res = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )

            # =========================
            # ❌ HTTP ERROR HANDLING
            # =========================
            if res.status_code != 200:
                print(f"❌ HTTP {res.status_code} for {symbol}")
                return None

            # =========================
            # ❌ JSON SAFETY
            # =========================
            try:
                data = res.json()
            except:
                print(f"❌ JSON decode error for {symbol}")
                return None

            if not isinstance(data, list):
                print(f"❌ Invalid response type for {symbol}")
                return None

            candles = []

            # =========================
            # 📊 PARSE CANDLES
            # =========================
            for c in data:

                if len(c) < 6:
                    continue

                o = self.safe_float(c[1])
                h = self.safe_float(c[2])
                l = self.safe_float(c[3])
                cl = self.safe_float(c[4])
                v = self.safe_float(c[5])

                if None in (o, h, l, cl, v):
                    continue

                candles.append({
                    "open": o,
                    "high": h,
                    "low": l,
                    "close": cl,
                    "volume": v
                })

            return candles if len(candles) > 0 else None

        except Exception as e:
            print(f"❌ Fetch exception {symbol}: {e}")
            return None

    # =========================
    # 🧠 GET CANDLES (SMART CACHE)
    # =========================
    def get_candles(self, symbol=None):

        symbol = symbol or self.symbol
        now = time.time()

        # =========================
        # ⚡ CACHE HIT
        # =========================
        if symbol in self.cache:
            last_time = self.last_update.get(symbol, 0)

            if now - last_time < self.ttl:
                return self.cache[symbol]

        # =========================
        # 📡 FETCH NEW DATA
        # =========================
        candles = self.fetch_candles(symbol)

        # =========================
        # 🟢 VALID DATA
        # =========================
        if candles:

            self.cache[symbol] = candles
            self.last_update[symbol] = now
            self.last_good[symbol] = candles

            return candles

        # =========================
        # 🔁 FALLBACK (CRITICAL FIX)
        # =========================
        fallback = self.last_good.get(symbol)

        if fallback:
            return fallback

        # =========================
        # ❌ FINAL SAFE RETURN
        # =========================
        return []

    # =========================
    # 🔄 SWITCH SYMBOL
    # =========================
    def set_symbol(self, symbol):

        self.symbol = symbol
