import requests


class MarketData:
    def __init__(self, symbol="BTCUSDT", interval="1m"):
        self.symbol = symbol
        self.interval = interval

    def safe_float(self, x):
        try:
            if x is None:
                return None
            return float(x)
        except:
            return None

    def get_candles(self, limit=50):

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "limit": limit
        }

        try:
            response = requests.get(url, params=params, timeout=10)

            # 🛡 HTTP check
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                return []

            # 🛡 JSON decode safe
            try:
                data = response.json()
            except Exception:
                print("❌ JSON Decode Error from Binance")
                return []

            # 🛡 Binance API error (dict response)
            if isinstance(data, dict):
                print(f"❌ Binance API Error: {data}")
                return []

            # 🛡 invalid type
            if not isinstance(data, list):
                print(f"❌ Invalid response type: {type(data)}")
                return []

            candles = []

            for c in data:

                # 🛡 structure check
                if not isinstance(c, list):
                    continue

                if len(c) < 6:
                    continue

                # 🧠 safe parsing
                o = self.safe_float(c[1])
                h = self.safe_float(c[2])
                l = self.safe_float(c[3])
                cl = self.safe_float(c[4])
                v = self.safe_float(c[5])

                # 🛡 ignore broken candles
                if None in (o, h, l, cl, v):
                    continue

                # 🧠 extra sanity check (prevents 'o' type bugs)
                if not all(isinstance(x, (int, float)) for x in (o, h, l, cl, v)):
                    continue

                candles.append({
                    "open": o,
                    "high": h,
                    "low": l,
                    "close": cl,
                    "volume": v
                })

            return candles

        except Exception as e:
            print(f"❌ MarketData Exception: {e}")
            return []
