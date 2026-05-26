# quality_engine.py
# 👑 محرك تقييم الجودة والفلترة النخبوية المطور - النسخة V4.0 الكبرى 👑
# 🛡️ مصفاة الأمان الذكية: تكيف كامل في حساب الأوزان الرياضية بين السكالبينج الخاطف والصفقات الموجية

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EliteQualityEngine:
    def __init__(self, time_engine, pre_move_engine):
        self.time_engine = time_engine
        self.pre_move_engine = pre_move_engine
        
        # وضع النخبة الافتراضي (يمكن التحكم به عبر لوحة التحكم)
        self.elite_mode_active = False

    def toggle_elite_mode(self, status: bool):
        """تفعيل أو إلغاء وضع صفقات النخبة من لوحة التحكم (Elite Mode ON/OFF)"""
        self.elite_mode_active = status
        logging.info(f"🔥 وضع صفقات النخبة (Elite Trade Mode) تم تعيينه إلى: {self.elite_mode_active}")

    def calculate_quality_score(self, signal_data: dict, market_conditions: dict) -> dict:
        """
        💰 تقييم جودة الصفقة بدقة رقمية (0-100) وبأوزان ديناميكية مرنة.
        يتكيف تلقائياً 100% إذا كانت الفرصة عبارة عن صفقة سكالبينج خاطفة أو صفقة سوينغ موجية.
        """
        pair = signal_data.get('pair', 'UNKNOWN').upper()
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')

        # ⚡ رصد نوع الصفقة (سكالبينج خاطف أم سوينغ طويل)
        is_scalp = signal_data.get('is_scalping_signal', False)
        
        score = 0
        
        if is_scalp:
            # ========================================================
            # 🎯 توزيع الأوزان الرياضية المخصصة لـ نمط السكالبينج (اضرب واهرب)
            # ========================================================
            
            # 1. حصة الذكاء الفني والـ AI Score اللحظي (وزن 25 نقطة)
            base_ai_score = signal_data.get('base_ai_score', signal_data.get('ai_score', 0.0))
            score += (base_ai_score / 100.0) * 25

            # 2. حصة محرك التوقع المسبق Pre-Move للفريمات الصغيرة (وزن 10 نقاط)
            prob_score = market_conditions.get('prediction_probability_score', 50.0)
            score += (prob_score / 100.0) * 10

            # 3. حصة فلتر الأخبار والاتجاه اللحظي المتوافق (وزن 15 نقطة)
            news_analysis = market_conditions.get('news_analysis', {})
            sentiment = news_analysis.get('sentiment', 'Neutral')
            if (sentiment == "Bullish" and signal_data.get('type') == "BUY") or \
               (sentiment == "Bearish" and signal_data.get('type') == "SELL"):
                score += 15
            else:
                score += 8

            # 4. حصة توقيت الجلسة وضخ سيولة الحيتان الكبرى - الملك في السكالب (وزن 25 نقطة)
            session_power = self.time_engine.calculate_session_power() if hasattr(self.time_engine, 'calculate_session_power') else {'power': 'MAXIMUM'}
            if session_power.get('power') == 'MAXIMUM':
                score += 25
            elif session_power.get('power') == 'HIGH':
                score += 20
            elif session_power.get('power') == 'MEDIUM_LOW':
                score += 12
            else:
                score += 5

            # 5. مستويات الثقة الفنية المقاسة ومؤشرات الزخم والـ SMC الحية (وزن 25 نقطة)
            confidence = signal_data.get('base_confidence', signal_data.get('confidence_score', 0.0))
            score += (confidence / 100.0) * 25

        else:
            # ========================================================
            # 🏆 توزيع الأوزان الرياضية الافتراضية المستقرة لـ صفقات السوينغ الموجية
            # ========================================================
            
            # 1. حصة الـ AI Score الفني والاتجاهي العام (وزن 30 نقطة)
            base_ai_score = signal_data.get('ai_score', signal_data.get('base_ai_score', 0.0))
            score += (base_ai_score / 100.0) * 30

            # 2. حصة احتمالية الانفجار من محرك الـ Pre-Move للموجات الكبرى (وزن 20 نقطة)
            prob_score = market_conditions.get('prediction_probability_score', 50.0)
            score += (prob_score / 100.0) * 20

            # 3. حصة فلتر الأخبار واستقرار السوق الماكرو (وزن 20 نقطة)
            news_analysis = market_conditions.get('news_analysis', {})
            impact_score = news_analysis.get('impact_score', 1)
            sentiment = news_analysis.get('sentiment', 'Neutral')
            if (sentiment == "Bullish" and signal_data.get('type') == "BUY") or \
               (sentiment == "Bearish" and signal_data.get('type') == "SELL"):
                score += 20
            elif sentiment == "Neutral" and impact_score <= 2:
                score += 15
            else:
                score += 5

            # 4. حصة توقيت الجلسة والسيولة (وزن 15 نقطة)
            session_power = self.time_engine.calculate_session_power() if hasattr(self.time_engine, 'calculate_session_power') else {'power': 'MAXIMUM'}
            if session_power.get('power') == 'MAXIMUM':
                score += 15
            elif session_power.get('power') == 'HIGH':
                score += 12
            elif session_power.get('power') == 'MEDIUM_LOW':
                score += 8
            else:
                score += 3

            # 5. حصة مستويات الثقة الفنية الماكرو المقاسة (وزن 15 نقطة)
            confidence = signal_data.get('confidence_score', signal_data.get('base_confidence', 0.0))
            score += (confidence / 100.0) * 15

        # حساب النتيجة النهائية وضبط الحدود برمجياً في النطاق الصارم
        final_quality_score = round(max(0.0, min(score, 100.0)), 1)

        # 2. تصنيف جودة الصفقات مؤسسياً بناءً على السكور النهائي
        if final_quality_score >= 85.0:
            classification = "Elite"
        elif final_quality_score >= 70.0:
            classification = "High"
        elif final_quality_score >= 58.0: # تعديل مرن طفيف لعدم تفويت فرص السكالبينج الخاطفة المستقرة
            classification = "Medium"
        else:
            classification = "Low"

        # 3. منطق التصفية والتحكم النخبوي التكيفي (Elite & Scalping Trade Logic)
        is_tradable = True
        reject_reason = ""

        # إلغاء أي صفقة ضعيفة تلقائياً لحماية المحفظة
        if classification == "Low":
            is_tradable = False
            reject_reason = f"إلغاء تلقائي: جودة الصفقة ضعيفة جداً ({final_quality_score}/100)"

        # فحص إضافي للسكالبينج: لو كانت الجلسة ميتة وبدون سيولة تقل الجودة ويتم الرفض فوراً
        if is_scalp and final_quality_score < 62.0:
            is_tradable = False
            reject_reason = f"إلغاء سكالبينج: قوة حركية الفرصة اللحظية الحالية منخفضة ({final_quality_score}/100)"

        # إذا تم تفعيل وضع النخبة الصارم من لوحة التحكم، نرفض أي شيء ليس بمستوى "Elite"
        if self.elite_mode_active and classification != "Elite":
            is_tradable = False
            reject_reason = f"حظر Elite Mode: تم تجاهل الفرصة لأن جودتها ({final_quality_score}) ليست بمستوى النخبة المطلوب (+85)"

        return {
            'pair': pair,
            'quality_score': final_quality_score,
            'classification': classification,
            'is_tradable': is_tradable,
            'reject_reason': reject_reason,
            'elite_mode_active': self.elite_mode_active,
            'trade_style': "⚡ SCALPING" if is_scalp else "🏆 SWING"
            }
            
