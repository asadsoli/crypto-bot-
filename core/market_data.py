import requests
import time


class MarketDataV2:

    def __init__(self, symbol="BTCUSDT", interval="1m"):

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
        self.base_url = "https://api.binance.com/api/v3/klines"

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

            symbol = self.normalize_symbol(symbol)

            self.symbol = symbol

            print(f"✅ SYMBOL SET: {self.symbol}")

            return True

        except Exception as e:

            print("❌ SET SYMBOL ERROR:", e)

            return False

    # =========================
    # 📡 FETCH CANDLES
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

            print(f"📡 FETCHING: {symbol}")

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            # =========================
            # ❌ HTTP ERROR
            # =========================
            if response.status_code != 200:

                print(f"❌ BINANCE HTTP ERROR: {response.status_code}")
                print(response.text)

                return []

            # =========================
            # 📦 JSON
            # =========================
            data = response.json()

            if not isinstance(data, list):

                print("❌ INVALID BINANCE RESPONSE")
                print(data)

                return []

            if len(data) == 0:

                print("❌ EMPTY BINANCE DATA")

                return []

            candles = []

            for c in data:

                try:

                    candles.append({

                        "timestamp": int(c[0]),

                        "open": float(c[1]),
                        "high": float(c[2]),
                        "low": float(c[3]),
                        "close": float(c[4]),

                        "volume": float(c[5])

                    })

                except Exception as parse_error:

                    print("❌ CANDLE PARSE ERROR:", parse_error)

            # =========================
            # ✅ SUCCESS
            # =========================
            print(f"✅ {symbol} LOADED: {len(candles)} candles")

            if candles:
                print(f"💰 LAST PRICE: {candles[-1]['close']}")

            return candles

        except requests.exceptions.Timeout:

            print("❌ REQUEST TIMEOUT")

            return []

        except requests.exceptions.ConnectionError:

            print("❌ CONNECTION ERROR")

            return []

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
        # ⚡ CACHE HIT
        # =========================
        if symbol in self.cache:

            last = self.last_update.get(symbol, 0)

            if now - last < self.ttl:

                cached = self.cache.get(symbol)

                if cached and len(cached) > 0:

                    print(f"⚡ CACHE HIT: {symbol}")

                    return cached

        # =========================
        # 📡 FETCH NEW DATA
        # =========================
        candles = self.fetch_candles(symbol)

        # =========================
        # ✅ SAVE CACHE
        # =========================
        if candles and len(candles) > 0:

            self.cache[symbol] = candles
            self.last_update[symbol] = now

            return candles

        # =========================
        # 🔁 FALLBACK CACHE
        # =========================
        fallback = self.cache.get(symbol)

        if fallback and len(fallback) > 0:

            print(f"⚠ USING FALLBACK CACHE: {symbol}")

            return fallback

        # =========================
        # ❌ FINAL FAIL
        # =========================
        print(f"❌ NO MARKET DATA: {symbol}")

        return []

    # =========================
    # 💰 GET CURRENT PRICE
    # =========================
    def get_price(self, symbol=None):

        try:

            candles = self.get_candles(symbol)

            if not candles:
                return None

            return candles[-1]["close"]

        except Exception as e:

            print("❌ GET PRICE ERROR:", e)

            return None
