# signal_filter.py
# 👑 موديول الفلترة المؤسسية والتصفية النخبوية - النسخة V10 AI CORE المحدثة 👑
# 🛡️ فلترة ثنائية المسار: اقتناص الشراء في الصعود وتفعيل البيع (Short) في ذروة الذعر الجيوسياسي والـ Risk OFF

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalSignalFilter:
    def __init__(self, time_engine, news_engine):
        # ربط الفلتر بطبقات التوقيت والأخبار التي برمجناها سابقاً
        self.time_engine = time_engine
        self.news_engine = news_engine
        
        # بوابات الفلترة الأدنى (Confidence Gate) - تم تعديلها لتناسب مرونة السكالبينج
        self.min_confidence_score = 50.0  # حد أدنى مرن لمنع تفويت فرص السكالبينج الخاطفة

    def filter_signal(self, raw_signal: dict, current_market_conditions: dict) -> dict:
        """
        تصفية الإشارات الواردة لضمان الجودة العالية فقط.
        تحليل متقاطع ذكي يدعم صفقات البيع والشراء بناءً على بيئة الماكرو.
        """
        pair = raw_signal.get('pair', 'UNKNOWN').upper()
        # استبدال XAU بـ PAXG تلقائياً إن وجد في الإشارة لضمان حصر التداول في الذهب الرقمي
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')
            raw_signal['pair'] = pair

        logging.info(f"🔍 فحص فلترة مؤسسية للإشارة على زوج: {pair}")

        # استخراج اتجاه الصفقة (شراء Long أم بيع Short) من هيكل الـ SMC
        structure = raw_signal.get('structure', '')
        is_short_trade = "Bearish" in structure

        # 1. فلترة الثقة (Confidence Gate)
        confidence = raw_signal.get('confidence_score', raw_signal.get('base_confidence', 0.0))
        if confidence < self.min_confidence_score:
            return {'status': 'REJECTED', 'reason': f"فشل بوابة الثقة: {confidence}% أقل من الحد الأدنى {self.min_confidence_score}%"}

        # 2. فلترة الجلسات والسيولة (Session Filter)
        active_sessions = self.time_engine.get_active_sessions()
        session_power = self.time_engine.calculate_session_power()
        
        # إذا كانت الجلسة آسيوية وزوج العملة يتطلب سيولة عالية، نرفع الحذر (إلا لو كانت صفقة سكالبينج خاطفة)
        if 'Asian' in active_sessions and session_power['power'] == 'MEDIUM_LOW' and pair not in ['BTCUSDT', 'ETHUSDT']:
            if not raw_signal.get('is_scalping_signal', False):
                return {'status': 'REJECTED', 'reason': "فشل فلتر الجلسة: الجلسة الآسيوية ضعيفة السيولة لهذه العملة في الفريمات الكبيرة"}

        # 3. فلترة الأخبار والماكرو والوضع الجيوسياسي (News & Macro Filter)
        news_status = current_market_conditions.get('news_analysis', {})
        if news_status.get('risk_regime') == 'Risk OFF':
            if is_short_trade:
                # 🟢 تعديل جوهري: إذا كان الوضع Risk OFF والصفقة بيع (Short)، نرحب بها لأن السوق ينهار!
                logging.info(f"🚨 وضع السوق Risk OFF ولكن يتم قبول صفقة البيع [{pair}] للاستفادة من الهبوط المؤسسي.")
            else:
                # إذا كان الوضع Risk OFF والصفقة شراء (Long)، نمنع العملات البديلة ونسمح فقط بالذهب كملاذ آمن
                if pair != 'PAXGUSDT':
                    return {'status': 'REJECTED', 'reason': "فشل فلتر الأخبار: وضع السوق Risk OFF (ذعر/هبوط)، صفقات الشراء للعملات محظورة حالياً"}
                else:
                    logging.info("⚠️ وضع السوق Risk OFF ويتم اعتماد الشراء على PAXG كملاذ آمن بحذر شديد.")

        # 4. فلترة التوقيت للأحداث الاقتصادية القوية (Event Timing Filter)
        event_timing = self.news_engine.get_event_timing_status(current_market_conditions.get('next_event_epoch', 0))
        if event_timing['action'] == 'STOP_TRADING':
            return {'status': 'REJECTED', 'reason': f"فشل فلتر التوقيت: إيقاف إجباري بسبب {event_timing['desc']}"}
        
        # 5. دمج الأوزان وتعديل الـ Score النهائي بناءً على بيئة السوق
        ai_score = raw_signal.get('ai_score', raw_signal.get('base_ai_score', 0.0))
        # تعديل السكور بناءً على قوة الجلسة، مع وضع حد مرن للسكالبينج الخاطف لضمان عدم تفويت الفرص
        multiplier = session_power.get('multiplier', 1.0)
        adjusted_score = ai_score * multiplier
        
        min_required_score = 55.0 if raw_signal.get('is_scalping_signal', False) else 60.0
        if adjusted_score < min_required_score:
            return {'status': 'REJECTED', 'reason': f"تصفية الجودة: السكور المعدل {adjusted_score:.1f} غير كافٍ للحد الأدنى {min_required_score}"}

        # إرجاع الإشارة كإشارة معتمدة ذات جودة عالية
        raw_signal['adjusted_score'] = min(adjusted_score, 100.0)
        raw_signal['session_context'] = session_power.get('power', 'NORMAL')
        
        return {
            'status': 'APPROVED',
            'reason': "اجتازت الصفقة الفلترة المؤسسية بنجاح عالي وتوافقت مع حركة السيولة",
            'filtered_signal': raw_signal
                    }
        
