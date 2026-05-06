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

        response = requests.get(url, params=params)
        data = response.json()

        candles = []

        for c in data:
            candles.append({
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5])
            })

        return candles
