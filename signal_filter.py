# signal_filter.py
# 👑 موديول الفلترة المؤسسية والتصفية النخبوية - النسخة V11 AI CORE المحدثة 👑
# 🛡️ فلترة ثنائية المسار: اقتناص الشراء في الصعود وتفعيل البيع (Short) في ذروة الذعر الجيوسياسي والـ Risk OFF
# 🚨 تم سحق خطأ الفاصلة العربية وتأمين فلاتر السيولة لتعمل بالتوازي مع السعر المباشر (4500$)

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalSignalFilter:
    def __init__(self, time_engine, news_engine):
        # ربط الفلتر بطبقات التوقيت والأخبار التي برمجناها سابقاً
        self.time_engine = time_engine
        self.news_engine = news_engine
        
        # بوابات الفلترة الأدنى (Confidence Gate) - تم تعديلها لتناسب مرونة السكالبينج
        self.min_confidence_score = 50.0  # حد أدنى مرن لمنع تفويت فرص السكالبينج الخاطفة
        
        # حد الأمان لأسعار الذهب لمنع الأخطاء البرمجية الناتجة عن التحديثات الصباحية القديمة
        self.expected_gold_floor = 4000.0  # الحد الأدنى المتوقع لسعر الذهب في بيئة السوق الحالية لعام 2026

    def filter_signal(self, raw_signal: dict, current_market_conditions: dict) -> dict:
        """
        تصفية الإشارات الواردة لضمان الجودة العالية فقط.
        تحليل متقاطع ذكي يدعم صفقات البيع والشراء بناءً على بيئة الماكرو.
        تتضمن فحصاً صارماً لمنع جلب الأسعار الخاطئة أو القديمة لزوج PAXGUSDT.
        """
        pair = raw_signal.get('pair', 'UNKNOWN').upper()
        
        # 1. نظام المعالجة الذكي لرمز الذهب دون تشويه السعر السائد على الشارت
        if 'XAU' in pair or 'PAXG' in pair:
            # توحيد التسمية لضمان التداول على الذهب الرقمي بالسيولة الصحيحة
            if 'XAU' in pair:
                pair = pair.replace('XAU', 'PAXG')
                raw_signal['pair'] = pair
            
            # فحص السعر الوارد في الإشارة لمنع غلطة الـ 2420.00 إذا كان السعر الحقيقي 4500$
            entry_price = float(raw_signal.get('entry_price', raw_signal.get('price', 0.0)))
            if entry_price > 0.0 and entry_price < self.expected_gold_floor:
                logging.error(f"❌ خطأ فادح في جلب الأسعار: تم رصد سعر مشوه للذهب ({entry_price}) بينما السعر الحقيقي الحالي يقارب الـ 4500$!")
                return {
                    'status': 'REJECTED',
                    'reason': f"فشل فلتر سلامة الأسعار: السكور الوارد للذهب ({entry_price}) قديم أو مقسم بشكل خاطئ بالذاكرة. السعر المتوقع فوق {self.expected_gold_floor}"
                }

        logging.info(f"🔍 فحص فلترة مؤسسية للإشارة على زوج: {pair}")

        # استخراج اتجاه الصفقة (شراء Long أم بيع Short) من هيكل الـ SMC
        structure = raw_signal.get('structure', '')
        is_short_trade = "Bearish" in structure

        # 2. فلترة الثقة (Confidence Gate)
        confidence = raw_signal.get('confidence_score', raw_signal.get('base_confidence', 0.0))
        if confidence < self.min_confidence_score:
            return {'status': 'REJECTED', 'reason': f"فشل بوابة الثقة: {confidence}% أقل من الحد الأدنى {self.min_confidence_score}%"}

        # 3. فلترة الجلسات والسيولة (Session Filter)
        active_sessions = self.time_engine.get_active_sessions()
        session_power = self.time_engine.calculate_session_power()
        
        # إذا كانت الجلسة آسيوية وزوج العملة يتطلب سيولة عالية، نرفع الحذر (إلا لو كانت صفقة سكالبينج خاطفة)
        if 'Asian' in active_sessions and session_power['power'] == 'MEDIUM_LOW' and pair not in ['BTCUSDT', 'ETHUSDT']:
            if not raw_signal.get('is_scalping_signal', False):
                return {'status': 'REJECTED', 'reason': "فشل فلتر الجلسة: الجلسة الآسيوية ضعيفة السيولة لهذه العملة في الفريمات الكبيرة"}

        # 4. فلترة الأخبار والماكرو والوضع الجيوسياسي (News & Macro Filter)
        news_status = current_market_conditions.get('news_analysis', {})
        if news_status.get('risk_regime') == 'Risk OFF':
            if is_short_trade:
                # 🟢 قبول صفقات البيع (Short) أثناء انهيار السوق والـ Risk OFF للاستفادة من الهبوط المؤسسي
                logging.info(f"🚨 وضع السوق Risk OFF ولكن يتم قبول صفقة البيع [{pair}] للاستفادة من الهبوط المؤسسي.")
            else:
                # إذا كان الوضع Risk OFF والصفقة شراء (Long)، نمنع العملات البديلة ونسمح فقط بالذهب كملاذ آمن
                if pair != 'PAXGUSDT':
                    return {'status': 'REJECTED', 'reason': "فشل فلتر الأخبار: وضع السوق Risk OFF (ذعر/هبوط)، صفقات الشراء للعملات محظورة حالياً"}
                else:
                    logging.info("⚠️ وضع السوق Risk OFF ويتم اعتماد الشراء على PAXG كملاذ آمن بحذر شديد.")

        # 5. فلترة التوقيت للأحداث الاقتصادية القوية (Event Timing Filter)
        event_timing = self.news_engine.get_event_timing_status(current_market_conditions.get('next_event_epoch', 0))
        if event_timing['action'] == 'STOP_TRADING':
            return {'status': 'REJECTED', 'reason': f"فشل فلتر التوقيت: إيقاف إجباري بسبب {event_timing['desc']}"}
        
        # 6. دمج الأوزان وتعديل الـ Score النهائي بناءً على بيئة السوق
        ai_score = raw_signal.get('ai_score', raw_signal.get('base_ai_score', 0.0))
        multiplier = session_power.get('multiplier', 1.0)
        adjusted_score = ai_score * multiplier
        
        min_required_score = 55.0 if raw_signal.get('is_scalping_signal', False) else 60.0
        if adjusted_score < min_required_score:
            return {'status': 'REJECTED', 'reason': f"تصفية الجودة: السكور المعدل {adjusted_score:.1f} غير كافٍ للحد الأدنى {min_required_score}"}

        # إرجاع الإشارة كإشارة معتمدة ذات جودة عالية
        raw_signal['adjusted_score'] = min(adjusted_score, 100.0)
        raw_signal['session_context'] = session_power.get('power', 'NORMAL')
        
        # 🟢 تم استبدال الفاصلة العربية (،) بفاصلة برمجية صحيحة (,) لتأمين تشغيل المنظومة بالكامل
        return {
            'status': 'APPROVED',
            'reason': "اجتازت الصفقة الفلترة المؤسسية بنجاح عالي وتوافقت مع حركة السيولة الصحيحة",
            'filtered_signal': raw_signal
                                                                                                  }
            
