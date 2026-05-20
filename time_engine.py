import datetime
import pytz
import logging

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TimeEngineV2:
    def __init__(self):
        # تحديد التوقيت الرسمي (سوريا)
        self.timezone = pytz.timezone('Asia/Damascus')
        
        # تعريف مواعيد الجلسات الافتراضية (بتوقيت سوريا)
        # ملاحظة: يمكن تعديل الساعات بناءً على التوقيت الصيفي/الشتوي العالمي
        self.sessions_config = {
            'Asian': {'open': datetime.time(2, 0), 'close': datetime.time(10, 0)},
            'London': {'open': datetime.time(9, 0), 'close': datetime.time(17, 0)},
            'New_York': {'open': datetime.time(15, 0), 'close': datetime.time(23, 0)}
        }
        
        # سجل داخلي لمنع تكرار التنبيهات في نفس الساعة والدقيقة
        self.fired_alerts = {
            'pre_open': set(),
            'open': set(),
            'close': set()
        }

    def get_local_time(self) -> datetime.datetime:
        """الحصول على الوقت الحالي الفعلي بتوقيت سوريا"""
        return datetime.datetime.now(self.timezone)

    def get_active_sessions(self) -> list:
        """تحديد الجلسات النشطة حالياً بناءً على توقيت سوريا"""
        current_time = self.get_local_time().time()
        active = []
        
        for session, hours in self.sessions_config.items():
            # معالجة الجلسات التي تتداخل عبر منتصف الليل إذا وجدت
            if hours['open'] <= hours['close']:
                if hours['open'] <= current_time <= hours['close']:
                    active.append(session)
            else: 
                if current_time >= hours['open'] or current_time <= hours['close']:
                    active.append(session)
        return active

    def calculate_session_power(self) -> dict:
        """
        ربط الجلسات بقوة التحليل (Session Power)
        تداخل نيويورك ولندن يعطي أعلى قوة للسوق.
        """
        active_sessions = self.get_active_sessions()
        
        if 'London' in active_sessions and 'New_York' in active_sessions:
            return {'power': 'MAXIMUM', 'multiplier': 1.2, 'desc': 'تداخل لندن ونيويورك - سيولة ضخمة'}
        elif 'New_York' in active_sessions:
            return {'power': 'HIGH', 'multiplier': 1.0, 'desc': 'جلسة نيويورك نشطة'}
        elif 'London' in active_sessions:
            return {'power': 'HIGH', 'multiplier': 1.0, 'desc': 'جلسة لندن نشطة'}
        elif 'Asian' in active_sessions:
            return {'power': 'MEDIUM_LOW', 'multiplier': 0.6, 'desc': 'الجلسة الآسيوية - حركة هادئة غلباً'}
        else:
            return {'power': 'LOW', 'multiplier': 0.4, 'desc': 'خارج أوقات الجلسات الرئيسية - سيولة ضعيفة'}

    def check_alerts(self) -> list:
        """
        محرك فحص التوقيت وإطلاق التنبيهات (يتم استدعاؤه كل دقيقة)
        يمنع التكرار ويعمل كـ Layer منفصل تماماً.
        """
        now = self.get_local_time()
        current_date_str = now.strftime('%Y-%m-%d')
        alerts_to_send = []

        for session, hours in self.sessions_config.items():
            # 1. تحويل الـ time إلى datetime لغرض الحسابات والـ Timestamps
            session_open_dt = self.timezone.localize(datetime.datetime.combine(now.date(), hours['open']))
            session_close_dt = self.timezone.localize(datetime.datetime.combine(now.date(), hours['close']))

            # حساب التنبيه قبل الافتتاح بـ 15 دقيقة
            pre_open_dt = session_open_dt - datetime.timedelta(minutes=15)

            # معرفات فريدة لمنع التكرار في نفس اليوم
            pre_open_id = f"{session}_{current_date_str}_{hours['open'].strftime('%H%M')}_pre"
            open_id = f"{session}_{current_date_str}_{hours['open'].strftime('%H%M')}_open"
            close_id = f"{session}_{current_date_str}_{hours['close'].strftime('%H%M')}_close"

            # فحص تنبيه قبل الافتتاح بـ 15 دقيقة
            if pre_open_dt <= now < session_open_dt and pre_open_id not in self.fired_alerts['pre_open']:
                alerts_to_send.append({
                    'type': 'PRE_OPEN',
                    'session': session,
                    'message': f"🔔 تنبيه: متبقي 15 دقيقة على افتتاح جلسة {session}! جهز الفلاتر."
                })
                self.fired_alerts['pre_open'].add(pre_open_id)

            # فحص تنبيه وقت الافتتاح بدقة
            if session_open_dt <= now < (session_open_dt + datetime.timedelta(minutes=2)) and open_id not in self.fired_alerts['open']:
                alerts_to_send.append({
                    'type': 'OPEN',
                    'session': session,
                    'message': f"🟢 تم افتتاح جلسة {session} الآن رسميًا! تدفق السيولة يبدأ."
                })
                self.fired_alerts['open'].add(open_id)

            # فحص تنبيه وقت الإغلاق بدقة
            if session_close_dt <= now < (session_close_dt + datetime.timedelta(minutes=2)) and close_id not in self.fired_alerts['close']:
                alerts_to_send.append({
                    'type': 'CLOSE',
                    'session': session,
                    'message': f"🔕 تنبيه: تم إغلاق جلسة {session} الآن. انتبه لتغيرات السيولة."
                })
                self.fired_alerts['close'].add(close_id)

        # تنظيف السجل للأيام السابقة لمنع استهلاك الذاكرة
        self._clean_old_alerts_cache(current_date_str)

        return alerts_to_send

    def _clean_old_alerts_cache(self, current_date_str: str):
        """تنظيف الكاش الداخلي للحفاظ على كفاءة الذاكرة"""
        for alert_type in self.fired_alerts:
            self.fired_alerts[alert_type] = {
                alert_id for alert_id in self.fired_alerts[alert_type] if current_date_str in alert_id
      }
          
