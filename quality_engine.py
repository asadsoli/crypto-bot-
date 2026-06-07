# quality_engine.py
# 👑 محرك تقييم الجودة والفلترة النخبوية المطور - النسخة V4.0 الكبرى 👑
# 🛡️ مصفاة الأمان الذكية: تكيف كامل في حساب الأوزان الرياضية

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EliteQualityEngine:
    def __init__(self, time_engine, pre_move_engine):
        self.time_engine = time_engine
        self.pre_move_engine = pre_move_engine
        self.elite_mode_active = False

    def toggle_elite_mode(self, status: bool):
        self.elite_mode_active = bool(status)
        logging.info(f"🔥 وضع صفقات النخبة (Elite Trade Mode) تم تعيينه إلى: {self.elite_mode_active}")

    def calculate_quality_score(self, signal_data: dict, market_conditions: dict) -> dict:
        data = signal_data or {}
        conditions = market_conditions or {}
        
        pair = str(data.get('pair', 'UNKNOWN')).upper()
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')

        is_scalp = bool(data.get('is_scalping_signal', False))
        score = 0.0
        
        # استخراج مؤشرات الأمان من البيانات
        base_ai_score = float(data.get('base_ai_score') or data.get('ai_score', 0.0))
        prob_score = float(conditions.get('prediction_probability_score', 50.0))
        news_analysis = conditions.get('news_analysis') or {}
        sentiment = str(news_analysis.get('sentiment', 'Neutral'))
        impact_score = int(news_analysis.get('impact_score', 1))
        
        # حساب الجلسة مع حماية من None
        session_power = {'power': 'NORMAL'}
        if hasattr(self.time_engine, 'calculate_session_power'):
            session_power = self.time_engine.calculate_session_power() or {'power': 'NORMAL'}
        
        power = str(session_power.get('power', 'NORMAL'))
        confidence = float(data.get('base_confidence') or data.get('confidence_score', 0.0))

        if is_scalp:
            # توزيع أوزان السكالبينج
            score += (base_ai_score / 100.0) * 25
            score += (prob_score / 100.0) * 10
            
            if (sentiment == "Bullish" and data.get('type') == "BUY") or \
               (sentiment == "Bearish" and data.get('type') == "SELL"):
                score += 15
            else:
                score += 8

            if power == 'MAXIMUM': score += 25
            elif power == 'HIGH': score += 20
            elif power == 'MEDIUM_LOW': score += 12
            else: score += 5

            score += (confidence / 100.0) * 25

        else:
            # توزيع أوزان السوينغ
            score += (base_ai_score / 100.0) * 30
            score += (prob_score / 100.0) * 20

            if (sentiment == "Bullish" and data.get('type') == "BUY") or \
               (sentiment == "Bearish" and data.get('type') == "SELL"):
                score += 20
            elif sentiment == "Neutral" and impact_score <= 2:
                score += 15
            else:
                score += 5

            if power == 'MAXIMUM': score += 15
            elif power == 'HIGH': score += 12
            elif power == 'MEDIUM_LOW': score += 8
            else: score += 3

            score += (confidence / 100.0) * 15

        final_quality_score = round(max(0.0, min(float(score), 100.0)), 1)

        # التصنيف
        if final_quality_score >= 85.0: classification = "Elite"
        elif final_quality_score >= 70.0: classification = "High"
        elif final_quality_score >= 58.0: classification = "Medium"
        else: classification = "Low"

        # منطق التصفية والرفض
        is_tradable = True
        reject_reason = ""

        if classification == "Low":
            is_tradable = False
            reject_reason = f"إلغاء تلقائي: جودة الصفقة ضعيفة ({final_quality_score}/100)"

        if is_scalp and final_quality_score < 62.0:
            is_tradable = False
            reject_reason = f"إلغاء سكالبينج: قوة حركية منخفضة ({final_quality_score}/100)"

        if self.elite_mode_active and classification != "Elite":
            is_tradable = False
            reject_reason = f"حظر Elite Mode: جودة {final_quality_score} ليست بمستوى النخبة"

        return {
            'pair': pair,
            'quality_score': final_quality_score,
            'classification': classification,
            'is_tradable': is_tradable,
            'reject_reason': reject_reason,
            'elite_mode_active': self.elite_mode_active,
            'trade_style': "⚡ SCALPING" if is_scalp else "🏆 SWING"
                   }
    
