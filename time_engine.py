# TradingTimeEngine.py
# ⚡ محرك التوقيت والتحكم الزمني المطور - النسخة V4.0 النخبوية ⚡
# ⏱️ صمام الأمان الزمني: ضبط الجلسات العالمية بدقة لعام 2026 لفك حظر السيرفر ومنع فخ 'عاطل'

import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingTimeEngine:
    def __init__(self):
        # 🇸🇾 تحديد فارق التوقيت الرسمي المستقر (توقيت سوريا إقليمياً هو UTC+3)
        # نستخدم الفارق الرقمي الثابت (Fixed Offset) كحزام أمان فولاذي لمنع حظر مكتبات pytz الخارجية على Render
        self.target_offset = datetime.timedelta(hours=3)
        self.timezone = datetime.timezone(self.target_offset)
        
        # تعريف مواعيد الجلسات الافتراضية بدقة (بتوقيت سوريا الحقيقي)
        self.sessions_config = {
            'Asian': {'open': datetime.time(2, 0), 'close': datetime.time(10, 0)},
            'London': {'open': datetime.time(9, 0), 'close': datetime.time(17, 0)},
            'New_York': {'open': datetime.time(15, 0), 'close': datetime.time(23, 0)}
        }
        
        # سجل داخلي محصن لمنع تكرار التنبيهات في نفس الساعة والدقيقة
        self.fired_alerts = {
            'pre_open': set(),
            'open': set(),
            'close': set()
        }

    def get_local_time(self) -> datetime.datetime:
        """الحصول على الوقت الحالي الفعلي بدقة متناهية متوافق مع نبض دمشق اللحظي لعام 2026"""
        return datetime.datetime.now(datetime.timezone.utc) + self.target_offset

    def get_active_sessions(self) -> list:
        """تحديد الجلسات النشطة حالياً بناءً على توقيت المنظومة المركزي"""
        current_time = self.get_local_time().time()
        active = []
        
        for session, hours in self.sessions_config.items():
            if hours['open'] <= hours['close']:
                if hours['open'] <= current_time <= hours['close']:
                    active.append(session)
            else: 
                if current_time >= hours['open'] or current_time <= hours['close']:
                    active.append(session)
        return active

    def calculate_session_power(self) -> dict:
        """
        ربط الجلسات بقوة التحليل (Session Power) لعام 2026
        تداخل نيويورك ولندن يعطي أعلى قوة للسوق وضخ السيولة المؤسسية.
        """
        active_sessions = self.get_active_sessions()
        
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
        """
        محرك فحص التوقيت وإطلاق التنبيهات اللحظية المطهّر بالكامل من فخ تكرار الأيام
        """
        now = self.get_local_time()
        current_date_str = now.strftime('%Y-%m-%d')
        alerts_to_send = []

        for session, hours in self.sessions_config.items():
            # دمج التواريخ بحزام الأمان الزمني الجديد لمنع الالتواء التوقيتي للسيرفر
            session_open_dt = datetime.datetime.combine(now.date(), hours['open']).replace(tzinfo=self.timezone)
            session_close_dt = datetime.datetime.combine(now.date(), hours['close']).replace(tzinfo=self.timezone)

            pre_open_dt = session_open_dt - datetime.timedelta(minutes=15)

            pre_open_id = f"{session}_{current_date_str}_{hours['open'].strftime('%H%M')}_pre"
            open_id = f"{session}_{current_date_str}_{hours['open'].strftime('%H%M')}_open"
            close_id = f"{session}_{current_date_str}_{hours['close'].strftime('%H%M')}_close"

            # 1. فحص تنبيه قبل الافتتاح بـ 15 دقيقة
            if pre_open_dt <= now < session_open_dt and pre_open_id not in self.fired_alerts['pre_open']:
                alerts_to_send.append({
                    'type': 'PRE_OPEN',
                    'session': session,
                    'message': f"🔔 **[تنبيه زمن المؤسسات]:** متبقي 15 دقيقة على افتتاح جلسة {session}! يرجى تجهيز الفلاتر والرادارات. ⏱️"
                })
                self.fired_alerts['pre_open'].add(pre_open_id)

            # 2. فحص تنبيه وقت الافتتاح بدقة (نافذة دقيقتين أمان)
            if session_open_dt <= now < (session_open_dt + datetime.timedelta(minutes=2)) and open_id not in self.fired_alerts['open']:
                alerts_to_send.append({
                    'type': 'OPEN',
                    'session': session,
                    'message': f"🟢 **[افتتاح رسمي]:** تم افتتاح جلسة {session} الآن! حيتان السيولة بدأت بضخ الأوامر اللحظية. 🚀"
                })
                self.fired_alerts['open'].add(open_id)

            # 3. فحص تنبيه وقت الإغلاق بدقة (نافذة دقيقتين أمان)
            if session_close_dt <= now < (session_close_dt + datetime.timedelta(minutes=2)) and close_id not in self.fired_alerts['close']:
                alerts_to_send.append({
                    'type': 'CLOSE',
                    'session': session,
                    'message': f"🔕 **[إغلاق الجلسة]:** تم إغلاق جلسة {session} الآن. يرجى الحذر من تغيرات السيولة العشوائية والارتدادات الحامضة. 🛡️"
                })
                self.fired_alerts['close'].add(close_id)

        # تنظيف السجل للتخلص من كاش الأيام السابقة وحماية رامات السيرفر
        self._clean_old_alerts_cache(current_date_str)

        return alerts_to_send

    def _clean_old_alerts_cache(self, current_date_str: str):
        """تنظيف الكاش الداخلي دورياً لضمان بقاء السيرفر خفيفاً وسريعاً"""
        for alert_type in self.fired_alerts:
            self.fired_alerts[alert_type] = {
                alert_id for alert_id in self.fired_alerts[alert_type] if current_date_str in alert_id
    }
        
