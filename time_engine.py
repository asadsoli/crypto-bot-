# TradingTimeEngine.py
# ⚡ محرك التوقيت والتحكم الزمني المطور - النسخة V4.0 النخبوية ⚡
# ⏱️ صمام الأمان الزمني: ضبط الجلسات العالمية بدقة لعام 2026 لفك حظر السيرفر ومنع فخ 'عاطل'

import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingTimeEngine:
    def __init__(self):
        self.target_offset = datetime.timedelta(hours=3)
        self.timezone = datetime.timezone(self.target_offset)
        
        self.sessions_config = {
            'Asian': {'open': datetime.time(2, 0), 'close': datetime.time(10, 0)},
            'London': {'open': datetime.time(9, 0), 'close': datetime.time(17, 0)},
            'New_York': {'open': datetime.time(15, 0), 'close': datetime.time(23, 0)}
        }
        
        self.fired_alerts = {
            'pre_open': set(),
            'open': set(),
            'close': set()
        }

    def get_local_time(self) -> datetime.datetime:
        try:
            return datetime.datetime.now(datetime.timezone.utc) + self.target_offset
        except:
            return datetime.datetime.utcnow() + self.target_offset

    def get_active_sessions(self) -> list:
        now_time = self.get_local_time().time()
        active = []
        
        for session, hours in self.sessions_config.items():
            s_open = hours.get('open')
            s_close = hours.get('close')
            
            if s_open <= s_close:
                if s_open <= now_time <= s_close:
                    active.append(session)
            else: 
                if now_time >= s_open or now_time <= s_close:
                    active.append(session)
        return active

    def calculate_session_power(self) -> dict:
        active_sessions = self.get_active_sessions() or []
        
        if 'London' in active_sessions and 'New_York' in active_sessions:
            return {'power': 'MAXIMUM', 'multiplier': 1.2, 'desc': '🎯 تداخل لندن ونيويورك - ذروة السيولة المؤسسية الخاطفة'}
        elif 'New_York' in active_sessions:
            return {'power': 'HIGH', 'multiplier': 1.0, 'desc': 'جلسة نيويورك نشطة حالياً'}
        elif 'London' in active_sessions:
            return {'power': 'HIGH', 'multiplier': 1.0, 'desc': 'جلسة لندن نشطة حالياً'}
        elif 'Asian' in active_sessions:
            return {'power': 'MEDIUM_LOW', 'multiplier': 0.6, 'desc': 'الجلسة الآسيوية - ملائمة لسكالبينج العملات الرقمية فقط'}
        else:
            return {'power': 'LOW', 'multiplier': 0.4, 'desc': 'خارج أوقات الجلسات الرئيسية - السوق خادع والسيولة ضعيفة'}

    def check_alerts(self) -> list:
        now = self.get_local_time()
        current_date_str = now.strftime('%Y-%m-%d')
        alerts_to_send = []

        for session, hours in self.sessions_config.items():
            try:
                session_open_dt = datetime.datetime.combine(now.date(), hours['open']).replace(tzinfo=self.timezone)
                session_close_dt = datetime.datetime.combine(now.date(), hours['close']).replace(tzinfo=self.timezone)
                pre_open_dt = session_open_dt - datetime.timedelta(minutes=15)

                pre_open_id = f"{session}_{current_date_str}_{hours['open'].strftime('%H%M')}_pre"
                open_id = f"{session}_{current_date_str}_{hours['open'].strftime('%H%M')}_open"
                close_id = f"{session}_{current_date_str}_{hours['close'].strftime('%H%M')}_close"

                if pre_open_dt <= now < session_open_dt and pre_open_id not in self.fired_alerts.get('pre_open', set()):
                    alerts_to_send.append({
                        'type': 'PRE_OPEN',
                        'session': session,
                        'message': f"🔔 **[تنبيه زمن المؤسسات]:** متبقي 15 دقيقة على افتتاح جلسة {session}! ⏱️"
                    })
                    self.fired_alerts['pre_open'].add(pre_open_id)

                if session_open_dt <= now < (session_open_dt + datetime.timedelta(minutes=2)) and open_id not in self.fired_alerts.get('open', set()):
                    alerts_to_send.append({
                        'type': 'OPEN',
                        'session': session,
                        'message': f"🟢 **[افتتاح رسمي]:** تم افتتاح جلسة {session} الآن! 🚀"
                    })
                    self.fired_alerts['open'].add(open_id)

                if session_close_dt <= now < (session_close_dt + datetime.timedelta(minutes=2)) and close_id not in self.fired_alerts.get('close', set()):
                    alerts_to_send.append({
                        'type': 'CLOSE',
                        'session': session,
                        'message': f"🔕 **[إغلاق الجلسة]:** تم إغلاق جلسة {session} الآن. 🛡️"
                    })
                    self.fired_alerts['close'].add(close_id)
            except:
                continue

        self._clean_old_alerts_cache(current_date_str)
        return alerts_to_send

    def _clean_old_alerts_cache(self, current_date_str: str):
        for alert_type in self.fired_alerts:
            self.fired_alerts[alert_type] = {
                alert_id for alert_id in self.fired_alerts[alert_type] if current_date_str in alert_id
                                }
                                                            
