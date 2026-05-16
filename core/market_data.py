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
        # ⏱ CACHE SETTINGS
        # =========================
        self.ttl = 10  # seconds

        # =========================
        # 🌐 API SETTINGS
        # =========================
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.timeout = 10

        # =========================
        # 🟡 SYMBOL MAPPING (FINAL FIX)
        # =========================
        self.symbol_map = {
            "XAUUSD": "PAXGUSDT",
            "GOLD": "PAXGUSDT",
            "PAXG": "PAXGUSDT",
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT"
        }

    # =========================
    # 🔧 SAFE FLOAT
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
    # 📡 FETCH FROM BINANCE
    # =========================
    def fetch_candles(self, symbol):

        symbol = self.normalize_symbol(symbol)

        params = {
            "symbol": symbol,
            "interval": self.interval,
            "limit": 100   # 🔥 improved depth
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
                print(f"❌ Empty response for {symbol}")
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

            if len(candles) < 10:
                print(f"❌ Not enough valid candles for {symbol}")
                return None

            return candles

        except requests.exceptions.Timeout:
            print(f"❌ Timeout {symbol}")
            return None

        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error {symbol}")
            return None

        except Exception as e:
            print(f"❌ Fetch error {symbol}: {e}")
            return None

    # =========================
    # 🧠 GET CANDLES (ULTIMATE SAFE CACHE)
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

                if cached and isinstance(cached, list) and len(cached) > 0:
                    return cached

        # =========================
        # 📡 FETCH NEW DATA
        # =========================
        candles = self.fetch_candles(symbol)

        # =========================
        # 🟢 VALID DATA
        # =========================
        if candles and isinstance(candles, list) and len(candles) > 0:

            self.cache[symbol] = candles
            self.last_update[symbol] = now
            self.last_good[symbol] = candles

            return candles

        # =========================
        # 🔁 FALLBACK LAST GOOD DATA
        # =========================
        fallback = self.last_good.get(symbol)

        if fallback and isinstance(fallback, list) and len(fallback) > 0:
            print(f"⚠ Using last valid data for {symbol}")
            return fallback

        # =========================
        # ❌ FINAL SAFE RETURN (NO CRASH)
        # =========================
        print(f"❌ NO DATA SAFE MODE ACTIVATED for {symbol}")

        return self.cache.get(symbol, [])

    # =========================
    # 🔄 SWITCH SYMBOL
    # =========================
    def set_symbol(self, symbol):

        if not symbol:
            return

        symbol = self.normalize_symbol(symbol)
        self.symbol = symbol
