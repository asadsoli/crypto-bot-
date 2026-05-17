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
        # ⏱ TTL
        # =========================
        self.ttl = 5

        # =========================
        # 🌐 BINANCE
        # =========================
        self.base_url = "https://api.binance.com/api/v3/klines"

        # =========================
        # 🟡 SYMBOL MAP
        # =========================
        self.symbol_map = {
            "GOLD": "PAXGUSDT",
            "XAUUSD": "PAXGUSDT",
            "PAXG": "PAXGUSDT"
        }

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
    def fetch_candles(self, symbol=None):

        symbol = self.normalize_symbol(symbol or self.symbol)

        try:

            url = (
                f"{self.base_url}"
                f"?symbol={symbol}"
                f"&interval={self.interval}"
                f"&limit=100"
            )

            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                print(f"❌ Binance HTTP {response.status_code}")
                return []

            data = response.json()

            if not isinstance(data, list):
                print("❌ Invalid Binance data")
                return []

            candles = []

            for c in data:

                try:

                    candles.append({
                        "open": float(c[1]),
                        "high": float(c[2]),
                        "low": float(c[3]),
                        "close": float(c[4]),
                        "volume": float(c[5])
                    })

                except Exception as e:
                    print("CANDLE PARSE ERROR:", e)

            print(f"✅ {symbol} candles loaded: {len(candles)}")

            return candles

        except Exception as e:

            print("❌ FETCH ERROR:", e)

            return []

    # =========================
    # 🧠 GET CANDLES
    # =========================
    def get_candles(self, symbol=None):

        symbol = self.normalize_symbol(symbol or self.symbol)

        now = time.time()

        # =========================
        # ⚡ CACHE
        # =========================
        if symbol in self.cache:

            last = self.last_update.get(symbol, 0)

            if now - last < self.ttl:

                cached = self.cache.get(symbol)

                if cached:
                    print(f"⚡ CACHE HIT {symbol}")
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
        # 🔁 FALLBACK
        # =========================
        fallback = self.cache.get(symbol)

        if fallback:
            print(f"⚠ USING FALLBACK {symbol}")
            return fallback

        print(f"❌ NO DATA {symbol}")

        return []
