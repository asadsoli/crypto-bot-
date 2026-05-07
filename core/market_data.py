import requests


class MarketData:
    def __init__(self, symbol="BTCUSDT", interval="1m"):
        self.symbol = symbol
        self.interval = interval

    def get_candles(self, limit=50):

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "limit": limit
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            data = response.json()

            # 🛡 حماية إذا Binance رجع Error JSON
            if not isinstance(data, list):
                print(f"❌ Binance Error: {data}")
                return []

            candles = []

            for c in data:

                # 🛡 حماية إضافية
                if not isinstance(c, list):
                    continue

                # 🛡 تأكد أن البيانات كاملة
                if len(c) < 6:
                    continue

                try:
                    candles.append({
                        "open": float(c[1]),
                        "high": float(c[2]),
                        "low": float(c[3]),
                        "close": float(c[4]),
                        "volume": float(c[5])
                    })

                except Exception as e:
                    print(f"❌ Candle Parse Error: {e}")
                    continue

            return candles

        except Exception as e:
            print(f"❌ MarketData Error: {e}")
            return []
