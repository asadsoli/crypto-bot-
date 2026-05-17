import requests
import time


class MarketDataV2:

    def __init__(self, symbol="BTCUSDT", interval="5m"):

        # =========================
        # 🪙 SYMBOL
        # =========================
        self.symbol = symbol.upper()
        self.interval = interval

        # =========================
        # 🧠 CACHE
        # =========================
        self.cache = {}
        self.last_update = {}

        # =========================
        # ⏱ CACHE TTL
        # =========================
        self.ttl = 5

        # =========================
        # 🌐 BINANCE API
        # =========================
        self.kline_url = "https://api.binance.com/api/v3/klines"
        self.price_url = "https://api.binance.com/api/v3/ticker/price"

        # =========================
        # 🔄 SYMBOL MAP
        # =========================
        self.symbol_map = {
            "GOLD": "PAXGUSDT",
            "XAUUSD": "PAXGUSDT",
            "PAXG": "PAXGUSDT"
        }

    # =========================
    # 🔄 NORMALIZE SYMBOL
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

        try:

            self.symbol = self.normalize_symbol(symbol)

            print(f"✅ SYMBOL SET: {self.symbol}")

            return True

        except Exception as e:

            print("❌ SET SYMBOL ERROR:", e)

            return False

    # =========================
    # 💰 GET LIVE PRICE
    # =========================
    def get_price(self, symbol=None):

        try:

            symbol = self.normalize_symbol(symbol or self.symbol)

            response = requests.get(
                self.price_url,
                params={"symbol": symbol},
                timeout=5
            )

            data = response.json()

            price = float(data["price"])

            print(f"💰 LIVE PRICE {symbol}: {price}")

            return price

        except Exception as e:

            print("❌ GET PRICE ERROR:", e)

            return None

    # =========================
    # 📊 GET RAW KLINES
    # =========================
    def get_klines(self, symbol=None):

        try:

            symbol = self.normalize_symbol(symbol or self.symbol)

            response = requests.get(
                self.kline_url,
                params={
                    "symbol": symbol,
                    "interval": self.interval,
                    "limit": 100
                },
                timeout=10
            )

            data = response.json()

            close = [float(x[4]) for x in data]
            high = [float(x[2]) for x in data]
            low = [float(x[3]) for x in data]

            print(f"✅ KLINES LOADED: {symbol} ({len(close)})")

            return close, high, low

        except Exception as e:

            print("❌ GET KLINES ERROR:", e)

            return [], [], []

    # =========================
    # 📡 FETCH CANDLES
    # =========================
    def fetch_candles(self, symbol=None):

        symbol = self.normalize_symbol(symbol or self.symbol)

        try:

            response = requests.get(
                self.kline_url,
                params={
                    "symbol": symbol,
                    "interval": self.interval,
                    "limit": 100
                },
                timeout=10
            )

            if response.status_code != 200:

                print(f"❌ BINANCE HTTP ERROR: {response.status_code}")

                return []

            data = response.json()

            candles = []

            for c in data:

                candles.append({

                    "timestamp": int(c[0]),

                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),

                    "volume": float(c[5])

                })

            print(f"✅ {symbol} CANDLES: {len(candles)}")

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

                    print(f"⚡ CACHE HIT: {symbol}")

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

            print(f"⚠ USING FALLBACK CACHE: {symbol}")

            return fallback

        print(f"❌ NO DATA: {symbol}")

        return []
