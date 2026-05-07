import requests


class MarketData:

    def __init__(self, symbol="BTCUSDT", interval="1m"):

        self.symbol = symbol
        self.interval = interval

        # =========================
        # 🧠 CACHE (NEW - SAFE ADDITION)
        # =========================
        self.last_candles = []

    # =========================
    # 🔧 SAFE CONVERTER
    # =========================

    def safe_float(self, x):

        try:
            if x is None:
                return None
            return float(x)
        except:
            return None

    # =========================
    # 📊 GET CANDLES (CORE)
    # =========================

    def get_candles(self, limit=50):

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "limit": limit
        }

        try:

            response = requests.get(url, params=params, timeout=10)

            # =========================
            # 🛡 HTTP CHECK
            # =========================

            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                return self.last_candles

            # =========================
            # 🧠 JSON SAFE PARSE
            # =========================

            try:
                data = response.json()
            except Exception:
                print("❌ JSON Decode Error")
                return self.last_candles

            # =========================
            # 🛡 BINANCE ERROR CHECK
            # =========================

            if isinstance(data, dict):
                print(f"❌ Binance API Error: {data}")
                return self.last_candles

            if not isinstance(data, list):
                print(f"❌ Invalid response type: {type(data)}")
                return self.last_candles

            candles = []

            # =========================
            # 📊 PARSE CANDLES
            # =========================

            for c in data:

                if not isinstance(c, list):
                    continue

                if len(c) < 6:
                    continue

                o = self.safe_float(c[1])
                h = self.safe_float(c[2])
                l = self.safe_float(c[3])
                cl = self.safe_float(c[4])
                v = self.safe_float(c[5])

                if None in (o, h, l, cl, v):
                    continue

                # =========================
                # 🧠 SANITY CHECK
                # =========================

                if not all(isinstance(x, (int, float)) for x in (o, h, l, cl, v)):
                    continue

                candles.append({
                    "open": o,
                    "high": h,
                    "low": l,
                    "close": cl,
                    "volume": v
                })

            # =========================
            # 🔥 CACHE UPDATE (NEW)
            # =========================

            if len(candles) > 0:
                self.last_candles = candles

            return candles

        except Exception as e:
            print(f"❌ MarketData Exception: {e}")

            # 🔥 fallback (لا يوقف النظام)
            return self.last_candles
