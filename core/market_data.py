import requests
import time


class MarketDataV2:

    def __init__(self, symbol="BTCUSDT", interval="1m"):

        self.symbol = symbol
        self.interval = interval

        # =========================
        # 🧠 MULTI-ASSET CACHE
        # =========================
        self.cache = {}

        # =========================
        # ⏱ LAST UPDATE TIME
        # =========================
        self.last_update = {}

        # =========================
        # 🔥 CACHE TTL
        # =========================
        self.ttl = 10

        # =========================
        # 🧠 SAFE FALLBACK CACHE
        # =========================
        self.last_valid = {}

    # =========================
    # 🔧 SAFE FLOAT
    # =========================
    def safe_float(self, x):
        try:
            return float(x)
        except:
            return None

    # =========================
    # 📡 FETCH FROM BINANCE
    # =========================
    def fetch_candles(self, symbol):

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": symbol,
            "interval": self.interval,
            "limit": 50
        }

        try:
            res = requests.get(url, params=params, timeout=10)

            if res.status_code != 200:
                print(f"❌ HTTP ERROR {symbol}: {res.status_code}")
                return None

            data = res.json()

            if not isinstance(data, list):
                print(f"❌ INVALID DATA TYPE {symbol}")
                return None

            candles = []

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

            return candles if candles else None

        except Exception as e:
            print(f"❌ MarketData Exception {symbol}: {e}")
            return None

    # =========================
    # 🧠 GET CANDLES (MULTI-ASSET STABLE)
    # =========================
    def get_candles(self, symbol=None):

        symbol = symbol or self.symbol

        now = time.time()

        # =========================
        # 🧠 CACHE CHECK
        # =========================
        if symbol in self.cache:

            last_time = self.last_update.get(symbol, 0)

            if now - last_time < self.ttl:
                return self.cache[symbol]

        # =========================
        # 📡 FETCH NEW DATA
        # =========================
        candles = self.fetch_candles(symbol)

        if candles and len(candles) > 0:

            self.cache[symbol] = candles
            self.last_update[symbol] = now
            self.last_valid[symbol] = candles

            return candles

        # =========================
        # 🔁 SAFE FALLBACK (CRITICAL FIX)
        # =========================
        return self.last_valid.get(symbol, [])

    # =========================
    # 🔄 SWITCH SYMBOL
    # =========================
    def set_symbol(self, symbol):

        self.symbol = symbol

        # 🧠 RESET CACHE SAFELY
        if symbol not in self.cache:
            self.cache[symbol] = []
