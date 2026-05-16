import requests
import time


class MarketDataV2:

    def __init__(self, symbol="BTCUSDT", interval="1m"):

        self.symbol = symbol
        self.interval = interval

        # =========================
        # 🧠 CACHE STORAGE
        # =========================
        self.cache = {}
        self.last_update = {}
        self.last_good = {}

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
        # 🟡 SYMBOL MAPPING (FINAL FIX)
        # =========================
        self.symbol_map = {
            "XAUUSD": "PAXGUSDT",
            "GOLD": "PAXGUSDT",
            "PAXG": "PAXGUSDT"
        }

    # =========================
    # 🔧 SAFE CONVERTER
    # =========================
    def safe_float(self, x):
        try:
            return float(x)
        except:
            return None

    # =========================
    # 🧠 NORMALIZE SYMBOL
    # =========================
    def normalize_symbol(self, symbol):

        if not symbol:
            return self.symbol

        symbol = str(symbol).upper().strip()

        return self.symbol_map.get(symbol, symbol)

    # =========================
    # 📡 FETCH DATA
    # =========================
    def fetch_candles(self, symbol):

        symbol = self.normalize_symbol(symbol)

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

            if res.status_code != 200:
                print(f"❌ HTTP {res.status_code} for {symbol}")
                return None

            try:
                data = res.json()
            except:
                print(f"❌ JSON decode error for {symbol}")
                return None

            if not isinstance(data, list) or len(data) == 0:
                print(f"❌ Invalid/empty response for {symbol}")
                return None

            candles = []

            for c in data:

                if not isinstance(c, list) or len(c) < 6:
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

            if len(candles) == 0:
                print(f"❌ No valid candles for {symbol}")
                return None

            return candles

        except requests.exceptions.Timeout:
            print(f"❌ Timeout {symbol}")
            return None

        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error {symbol}")
            return None

        except Exception as e:
            print(f"❌ Fetch exception {symbol}: {e}")
            return None

    # =========================
    # 🧠 GET CANDLES (STABLE CACHE)
    # =========================
    def get_candles(self, symbol=None):

        symbol = self.normalize_symbol(symbol or self.symbol)
        now = time.time()

        # =========================
        # ⚡ CACHE HIT
        # =========================
        if symbol in self.cache:

            last_time = self.last_update.get(symbol, 0)

            if now - last_time < self.ttl:
                cached = self.cache.get(symbol)

                if isinstance(cached, list) and len(cached) > 0:
                    return cached

        # =========================
        # 📡 FETCH NEW DATA
        # =========================
        candles = self.fetch_candles(symbol)

        # =========================
        # 🟢 VALID UPDATE
        # =========================
        if candles:

            self.cache[symbol] = candles
            self.last_update[symbol] = now
            self.last_good[symbol] = candles

            return candles

        # =========================
        # 🔁 FALLBACK
        # =========================
        fallback = self.last_good.get(symbol)

        if isinstance(fallback, list) and len(fallback) > 0:
            print(f"⚠ Using fallback for {symbol}")
            return fallback

        # =========================
        # ❌ FINAL SAFE OUTPUT (IMPORTANT FIX)
        # =========================
        print(f"❌ NO DATA SAFE RETURN {symbol}")

        return self.cache.get(symbol, [])

    # =========================
    # 🔄 SWITCH SYMBOL
    # =========================
    def set_symbol(self, symbol):

        symbol = self.normalize_symbol(symbol)
        self.symbol = symbol
