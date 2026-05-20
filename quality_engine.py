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
        💰 تقييم جودة الصفقة بدقة رقمية (0-100)
        بناءً على: الذكاء الفني، قوة الاتجاه، الأخبار، الجلسة، المخاطر، واحتمالية الانفجار.
        """
        pair = signal_data.get('pair', 'UNKNOWN').upper()
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')

        score = 0
        
        # 1. حصة الـ AI Score الفني والاتجاهي (وزن 30 نقطة)
        base_ai_score = signal_data.get('ai_score', 0.0)
        score += (base_ai_score / 100.0) * 30

        # 2. حصة احتمالية الانفجار من محرك الـ Pre-Move (وزن 20 نقطة)
        prob_score = market_conditions.get('prediction_probability_score', 50.0)
        score += (prob_score / 100.0) * 20

        # 3. حصة فلتر الأخبار واستقرار السوق (وزن 20 نقطة)
        news_analysis = market_conditions.get('news_analysis', {})
        impact_score = news_analysis.get('impact_score', 1)
        sentiment = news_analysis.get('sentiment', 'Neutral')
        
        # إذا كان اتجاه الخبر يطابق نوع الصفقة (مثال: خبر إيجابي وصفقة BUY) يرتفع السكور
        if (sentiment == "Bullish" and signal_data.get('type') == "BUY") or \
           (sentiment == "Bearish" and signal_data.get('type') == "SELL"):
            score += 20
        elif sentiment == "Neutral" and impact_score <= 2:
            score += 15 # سوق مستقر بدون أخبار عاصفة
        else:
            score += 5  # معاكسة للاتجاه أو أخبار خطيرة

        # 4. حصة توقيت الجلسة والسيولة (وزن 15 نقطة)
        session_power = self.time_engine.calculate_session_power()
        if session_power['power'] == 'MAXIMUM':
            score += 15
        elif session_power['power'] == 'HIGH':
            score += 12
        elif session_power['power'] == 'MEDIUM_LOW':
            score += 8
        else:
            score += 3

        # 5. حصة مستويات الثقة الفنية المقاسة (وزن 15 نقطة)
        confidence = signal_data.get('confidence_score', 0.0)
        score += (confidence / 100.0) * 15

        # حساب النتيجة النهائية وضبط الحدود برمجياً
        final_quality_score = round(max(0.0, min(score, 100.0)), 1)

        # 2. تصنيف الصفقات (Low / Medium / High / Elite)
        if final_quality_score >= 85.0:
            classification = "Elite"
        elif final_quality_score >= 70.0:
            classification = "High"
        elif final_quality_score >= 55.0:
            classification = "Medium"
        else:
            classification = "Low"

        # 3. منطق التصفية والتحكم النخبوي (Elite Trade Mode Logic)
        is_tradable = True
        reject_reason = ""

        # إلغاء أي صفقة ضعيفة تلقائياً
        if classification == "Low":
            is_tradable = False
            reject_reason = f"إلغاء تلقائي: جودة الصفقة ضعيفة جداً ({final_quality_score}/100)"

        # إذا تم تفعيل وضع النخبة الصارم، نرفض أي شيء ليس "Elite"
        if self.elite_mode_active and classification != "Elite":
            is_tradable = False
            reject_reason = f"حظر Elite Mode: تم تجاهل الفرصة لأن جودتها ({final_quality_score}) ليست بمستوى النخبة المطلوب (+85)"

        return {
            'pair': pair,
            'quality_score': final_quality_score,
            'classification': classification,
            'is_tradable': is_tradable,
            'reject_reason': reject_reason,
            'elite_mode_active': self.elite_mode_active
        }
      
