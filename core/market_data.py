import requests
import time


class MarketDataV2:

    def __init__(self, symbol="BTCUSDT", interval="1m"):

        self.symbol = symbol
        self.interval = interval

        # =========================
        # 🧠 MULTI-ASSET CACHE
        # key = symbol
        # =========================
        self.cache = {}

        # =========================
        # ⏱ LAST UPDATE TIME
        # =========================
        self.last_update = {}

        # =========================
        # 🔥 CACHE TTL (seconds)
        # =========================
        self.ttl = 10

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
                return None

            data = res.json()

            if not isinstance(data, list):
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
            print(f"❌ MarketData fetch error {symbol}:", e)
            return None

    # =========================
    # 🧠 GET CANDLES (MULTI-ASSET SMART)
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

        if candles:

            self.cache[symbol] = candles
            self.last_update[symbol] = now

            return candles

        # =========================
        # 🔁 FALLBACK (LAST GOOD DATA)
        # =========================
        return self.cache.get(symbol, [])

    # =========================
    # 🔄 SWITCH SYMBOL
    # =========================
    def set_symbol(self, symbol):

        self.symbol = symbol
