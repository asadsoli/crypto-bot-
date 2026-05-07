import requests


class MarketData:
    def __init__(self, symbol="BTCUSDT", interval="1m"):
        self.symbol = symbol
        self.interval = interval

    def safe_float(self, x):
        try:
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

            # 🛡 تأكد من status code
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                return []

            data = response.json()

            # 🛡 Binance error check
            if isinstance(data, dict):
                print(f"❌ Binance API Error: {data}")
                return []

            if not isinstance(data, list):
                print(f"❌ Unexpected response: {data}")
                return []

            candles = []

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

                # 🛡 إذا أي قيمة خربانة تجاهل الشمعة
                if None in (o, h, l, cl, v):
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
