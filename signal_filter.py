import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalSignalFilter:
    def __init__(self, time_engine, news_engine):
        # ربط الفلتر بطبقات التوقيت والأخبار التي برمجناها سابقاً
        self.time_engine = time_engine
        self.news_engine = news_engine
        
        # بوابات الفلترة الأدنى (Confidence Gate)
        self.min_confidence_score = 55.0  # أقل من 55% مرفوض قطعاً

    def filter_signal(self, raw_signal: dict, current_market_conditions: dict) -> dict:
        """
        تصفية الإشارات الواردة لضمان الجودة العالية فقط.
        تحليل متقاطع بين التوقيت، السيولة، الأخبار، والمخاطر.
        """
        pair = raw_signal.get('pair', 'UNKNOWN').upper()
        # استبدال XAU بـ PAXG تلقائياً إن وجد في الإشارة لضمان حصر التداول في الذهب الرقمي
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')
            raw_signal['pair'] = pair

        logging.info(f"🔍 فحص فلترة مؤسسية للإشارة على زوج: {pair}")

        # 1. فلترة الثقة (Confidence Gate)
        confidence = raw_signal.get('confidence_score', 0.0)
        if confidence < self.min_confidence_score:
            return {'status': 'REJECTED', 'reason': f"فشل بوابة الثقة: {confidence}% أقل من الحد الأدنى 55%"}

        # 2. فلترة الجلسات والسيولة (Session Filter)
        active_sessions = self.time_engine.get_active_sessions()
        session_power = self.time_engine.calculate_session_power()
        
        # إذا كانت الجلسة آسيوية وزوج العملة يتطلب سيولة عالية، نرفع الحذر
        if 'Asian' in active_sessions and session_power['power'] == 'MEDIUM_LOW' and pair not in ['BTCUSDT', 'ETHUSDT']:
            return {'status': 'REJECTED', 'reason': "فشل فلتر الجلسة: الجلسة الآسيوية ضعيفة السيولة لهذه العملة"}

        # 3. فلترة الأخبار والماكرو والوضع الجيوسياسي (News & Macro Filter)
        # نقوم بطلب تقييم حالة المخاطر الحالية من محرك الأخبار
        news_status = current_market_conditions.get('news_analysis', {})
        if news_status.get('risk_regime') == 'Risk OFF':
            # إذا كان هناك خطر جيوسياسي أو فدرالي، نسمح فقط بـ PAXG كملاذ آمن تحت شروط صارمة أو نمنع التداول
            if pair != 'PAXGUSDT':
                return {'status': 'REJECTED', 'reason': "فشل فلتر الأخبار: وضع السوق Risk OFF (توترات/ماكرو)، التداول محظور للعملات"}
            else:
                logging.info("⚠️ وضع السوق Risk OFF ولكن يتم فحص PAXG كملاذ آمن بحذر.")

        # 4. فلترة التوقيت للأحداث الاقتصادية القوية (Event Timing Filter)
        event_timing = self.news_engine.get_event_timing_status(current_market_conditions.get('next_event_epoch', 0))
        if event_timing['action'] == 'STOP_TRADING':
            return {'status': 'REJECTED', 'reason': f"فشل فلتر التوقيت: إيقاف إجباري بسبب {event_timing['desc']}"}
        
        # 5. دمج الأوزان وتعديل الـ Score النهائي بناءً على بيئة السوق
        ai_score = raw_signal.get('ai_score', 0.0)
        # تعديل السكور بناءً على قوة الجلسة الحالية لرفع جودة الفلترة
        adjusted_score = ai_score * session_power['multiplier']
        
        if adjusted_score < 60.0:
            return {'status': 'REJECTED', 'reason': f"تصفية الجودة: السكور المعدل {adjusted_score:.1f} غير كافٍ"}

        # إرجاع الإشارة كإشارة معتمدة ذات جودة عالية
        raw_signal['adjusted_score'] = min(adjusted_score, 100.0)
        raw_signal['session_context'] = session_power['power']
        
        return {
            'status': 'APPROVED',
            'reason': "اجتازت الصفقة الفلترة المؤسسية بنجاح عالي",
            'filtered_signal': raw_signal
        }
      
