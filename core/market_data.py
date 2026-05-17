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
        # 🌐 API URLS (FAILOVER)
        # =========================
        self.urls = [
            "https://api.binance.com/api/v3/klines",
            "https://api1.binance.com/api/v3/klines",
            "https://api2.binance.com/api/v3/klines",
            "https://api3.binance.com/api/v3/klines"
        ]

        self.timeout = 15

        # =========================
        # 🌍 HEADERS (IMPORTANT)
        # =========================
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

        # =========================
        # 🟡 SYMBOL MAPPING
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
            "limit": 50
        }

        # =========================
        # 🔁 TRY MULTIPLE URLS
        # =========================
        for url in self.urls:

            try:

                print(f"📡 Fetching {symbol} from {url}")

                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )

                print(f"📊 STATUS {symbol}: {response.status_code}")

                # =========================
                # ❌ BAD STATUS
                # =========================
                if response.status_code != 200:

                    print(f"❌ HTTP ERROR {response.status_code}")

                    try:
                        print(response.text)
                    except:
                        pass

                    continue

                # =========================
                # 📦 JSON
                # =========================
                try:
                    data = response.json()
                except Exception as e:
                    print("❌ JSON ERROR:", e)
                    continue

                # =========================
                # ❌ INVALID DATA
                # =========================
                if not isinstance(data, list):

                    print("❌ INVALID RESPONSE TYPE")
                    print(data)

                    continue

                if len(data) == 0:

                    print("❌ EMPTY DATA")

                    continue

                candles = []

                # =========================
                # 📊 PARSE
                # =========================
                for candle in data:

                    try:

                        if len(candle) < 6:
                            continue

                        parsed = {
                            "open": self.safe_float(candle[1]),
                            "high": self.safe_float(candle[2]),
                            "low": self.safe_float(candle[3]),
                            "close": self.safe_float(candle[4]),
                            "volume": self.safe_float(candle[5])
                        }

                        if None in parsed.values():
                            continue

                        candles.append(parsed)

                    except Exception as e:
                        print("❌ PARSE ERROR:", e)

                # =========================
                # ✅ SUCCESS
                # =========================
                if len(candles) > 0:

                    print(f"✅ SUCCESS {symbol} candles={len(candles)}")

                    return candles

            except requests.exceptions.Timeout:

                print(f"❌ TIMEOUT {symbol}")

            except requests.exceptions.ConnectionError:

                print(f"❌ CONNECTION ERROR {symbol}")

            except Exception as e:

                print(f"❌ FETCH EXCEPTION {symbol}: {e}")

        # =========================
        # ❌ FAILED ALL URLS
        # =========================
        print(f"❌ ALL BINANCE ENDPOINTS FAILED {symbol}")

        return None

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

            last_time = self.last_update.get(symbol, 0)

            if now - last_time < self.ttl:

                cached = self.cache.get(symbol)

                if cached and isinstance(cached, list):

                    print(f"⚡ CACHE HIT {symbol}")

                    return cached

        # =========================
        # 📡 FETCH NEW
        # =========================
        candles = self.fetch_candles(symbol)

        # =========================
        # ✅ VALID DATA
        # =========================
        if candles and isinstance(candles, list):

            self.cache[symbol] = candles
            self.last_update[symbol] = now
            self.last_good[symbol] = candles

            return candles

        # =========================
        # 🔁 FALLBACK
        # =========================
        fallback = self.last_good.get(symbol)

        if fallback:

            print(f"⚠ USING FALLBACK {symbol}")

            return fallback

        # =========================
        # ❌ FINAL SAFE RETURN
        # =========================
        print(f"❌ NO MARKET DATA {symbol}")

        return []

    # =========================
    # 🔄 SET SYMBOL
    # =========================
    def set_symbol(self, symbol):

        symbol = self.normalize_symbol(symbol)

        self.symbol = symbol

        print(f"🔄 ACTIVE SYMBOL = {self.symbol}")
