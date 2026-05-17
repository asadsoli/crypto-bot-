import requests
import time


class MarketDataV2:

    def __init__(self, symbol="BTCUSDT", interval="1m"):

        self.symbol = symbol
        self.interval = interval

        # =========================
        # 🧠 CACHE
        # =========================
        self.cache = {}
        self.last_update = {}

        # =========================
        # ⏱ CACHE TTL
        # =========================
        self.ttl = 10

        # =========================
        # 🌐 API URLs (MULTI BACKUP)
        # =========================
        self.urls = [
            "https://api.binance.com/api/v3/klines",
            "https://api1.binance.com/api/v3/klines",
            "https://api2.binance.com/api/v3/klines",
            "https://api3.binance.com/api/v3/klines"
        ]

        self.timeout = 15

        # =========================
        # 🥇 GOLD FIX
        # =========================
        self.symbol_map = {
            "XAUUSD": "PAXGUSDT",
            "GOLD": "PAXGUSDT",
            "PAXG": "PAXGUSDT"
        }

    # =========================
    # 🔧 SAFE FLOAT
    # =========================
    def safe_float(self, value):

        try:
            return float(value)
        except:
            return None

    # =========================
    # 🔄 NORMALIZE
    # =========================
    def normalize_symbol(self, symbol):

        if not symbol:
            return self.symbol

        symbol = str(symbol).upper().strip()

        return self.symbol_map.get(symbol, symbol)

    # =========================
    # 🔄 SET SYMBOL
    # =========================
    def set_symbol(self, symbol):

        self.symbol = self.normalize_symbol(symbol)

    # =========================
    # 📡 FETCH
    # =========================
    def fetch_candles(self, symbol):

        symbol = self.normalize_symbol(symbol)

        params = {
            "symbol": symbol,
            "interval": self.interval,
            "limit": 100
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        # =========================
        # 🔁 TRY ALL BINANCE SERVERS
        # =========================
        for url in self.urls:

            try:

                print(f"📡 Fetching {symbol} from {url}")

                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )

                print(f"📊 STATUS: {response.status_code}")

                if response.status_code != 200:
                    continue

                data = response.json()

                if not isinstance(data, list):
                    print("❌ Invalid Binance response")
                    continue

                candles = []

                for c in data:

                    try:

                        candles.append({
                            "open": self.safe_float(c[1]),
                            "high": self.safe_float(c[2]),
                            "low": self.safe_float(c[3]),
                            "close": self.safe_float(c[4]),
                            "volume": self.safe_float(c[5])
                        })

                    except:
                        continue

                # =========================
                # ✅ SUCCESS
                # =========================
                if len(candles) > 20:

                    print(f"✅ Loaded {len(candles)} candles for {symbol}")

                    return candles

            except Exception as e:

                print(f"❌ API ERROR {url}: {e}")

                continue

        # =========================
        # ❌ FAILED
        # =========================
        print(f"❌ ALL BINANCE SERVERS FAILED FOR {symbol}")

        return []

    # =========================
    # 📊 GET CANDLES
    # =========================
    def get_candles(self, symbol=None):

        symbol = self.normalize_symbol(symbol or self.symbol)

        now = time.time()

        # =========================
        # ⚡ CACHE
        # =========================
        if symbol in self.cache:

            age = now - self.last_update.get(symbol, 0)

            if age < self.ttl:

                cached = self.cache.get(symbol)

                if cached:
                    return cached

        # =========================
        # 📡 FETCH
        # =========================
        candles = self.fetch_candles(symbol)

        # =========================
        # ✅ SAVE CACHE
        # =========================
        if candles:

            self.cache[symbol] = candles
            self.last_update[symbol] = now

            return candles

        # =========================
        # ⚠ FALLBACK CACHE
        # =========================
        fallback = self.cache.get(symbol)

        if fallback:

            print(f"⚠ Using cached fallback for {symbol}")

            return fallback

        # =========================
        # ❌ FINAL
        # =========================
        return []
