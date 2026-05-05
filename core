from datetime import datetime
import pytz

class TimeEngine:
    def __init__(self):
        self.timezone = pytz.timezone("Asia/Damascus")

    def get_current_time(self):
        now = datetime.now(self.timezone)
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def get_session(self):
        now = datetime.now(self.timezone)
        hour = now.hour

        if 0 <= hour < 8:
            return "ASIA"
        elif 8 <= hour < 16:
            return "LONDON"
        else:
            return "NEW YORK"
