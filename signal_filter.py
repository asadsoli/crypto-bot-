# signal_filter.py
# 👑 موديول الفلترة المؤسسية والتصفية النخبوية - النسخة V11 AI CORE المحدثة 👑
# 🛡️ فلترة ثنائية المسار: اقتناص الشراء في الصعود وتفعيل البيع (Short) في ذروة الذعر الجيوسياسي والـ Risk OFF
# 🚨 تم سحق خطأ الفاصلة العربية وتأمين فلاتر السيولة لتعمل بالتوازي مع السعر المباشر (4500$)

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalSignalFilter:
    def __init__(self, time_engine, news_engine):
        self.time_engine = time_engine
        self.news_engine = news_engine
        self.min_confidence_score = 50.0
        self.expected_gold_floor = 4000.0

    def filter_signal(self, raw_signal: dict, current_market_conditions: dict) -> dict:
        signal = raw_signal or {}
        conditions = current_market_conditions or {}
        
        pair = str(signal.get('pair', 'UNKNOWN')).upper()
        
        # 1. نظام المعالجة الذكي للذهب مع حماية من None والقيم المشوهة
        if 'XAU' in pair or 'PAXG' in pair:
            if 'XAU' in pair:
                pair = pair.replace('XAU', 'PAXG')
                signal['pair'] = pair
            
            entry_price = float(signal.get('entry_price') or signal.get('price', 0.0))
            if entry_price > 0.0 and entry_price < self.expected_gold_floor:
                logging.error(f"❌ خطأ فادح في جلب الأسعار: سعر الذهب الممرر ({entry_price}) مشوه!")
                return {
                    'status': 'REJECTED',
                    'reason': f"فشل فلتر سلامة الأسعار: السعر {entry_price} أقل من حد الأمان {self.expected_gold_floor}"
                }

        logging.info(f"🔍 فحص فلترة مؤسسية للإشارة على زوج: {pair}")

        structure = str(signal.get('structure', ''))
        is_short_trade = "Bearish" in structure

        # 2. فلترة الثقة
        confidence = float(signal.get('confidence_score') or signal.get('base_confidence', 0.0))
        if confidence < self.min_confidence_score:
            return {'status': 'REJECTED', 'reason': f"فشل بوابة الثقة: {confidence}% أقل من الحد الأدنى {self.min_confidence_score}%"}

        # 3. فلترة الجلسات والسيولة
        active_sessions = []
        if hasattr(self.time_engine, 'get_active_sessions'):
            active_sessions = self.time_engine.get_active_sessions() or []
        
        session_power = {'power': 'NORMAL', 'multiplier': 1.0}
        if hasattr(self.time_engine, 'calculate_session_power'):
            session_power = self.time_engine.calculate_session_power() or session_power
        
        if 'Asian' in active_sessions and session_power.get('power') == 'MEDIUM_LOW' and pair not in ['BTCUSDT', 'ETHUSDT']:
            if not bool(signal.get('is_scalping_signal', False)):
                return {'status': 'REJECTED', 'reason': "فشل فلتر الجلسة: الجلسة الآسيوية ضعيفة للعملة"}

        # 4. فلترة الأخبار والماكرو
        news_status = conditions.get('news_analysis') or {}
        if news_status.get('risk_regime') == 'Risk OFF':
            if is_short_trade:
                logging.info(f"🚨 وضع Risk OFF: تم قبول صفقة البيع على {pair}.")
            else:
                if pair != 'PAXGUSDT':
                    return {'status': 'REJECTED', 'reason': "فشل فلتر الأخبار: Risk OFF، يمنع الشراء للعملات البديلة"}
                else:
                    logging.info("⚠️ وضع Risk OFF: اعتماد الشراء على PAXG كملاذ آمن.")

        # 5. فلترة التوقيت للأحداث الاقتصادية
        if self.news_engine and hasattr(self.news_engine, 'get_event_timing_status'):
            event_timing = self.news_engine.get_event_timing_status(conditions.get('next_event_epoch', 0)) or {}
            if event_timing.get('action') == 'STOP_TRADING':
                return {'status': 'REJECTED', 'reason': f"فشل فلتر التوقيت: إيقاف إجباري بسبب {event_timing.get('desc', 'حدث اقتصادي')}"}
        
        # 6. دمج الأوزان وتعديل السكور
        ai_score = float(signal.get('ai_score') or signal.get('base_ai_score', 0.0))
        multiplier = float(session_power.get('multiplier', 1.0))
        adjusted_score = ai_score * multiplier
        
        min_required_score = 55.0 if bool(signal.get('is_scalping_signal', False)) else 60.0
        if adjusted_score < min_required_score:
            return {'status': 'REJECTED', 'reason': f"تصفية الجودة: السكور المعدل {adjusted_score:.1f} غير كافٍ"}

        signal['adjusted_score'] = min(float(adjusted_score), 100.0)
        signal['session_context'] = str(session_power.get('power', 'NORMAL'))
        
        return {
            'status': 'APPROVED',
            'reason': "اجتازت الصفقة الفلترة المؤسسية بنجاح عالي",
            'filtered_signal': signal
        }
        
