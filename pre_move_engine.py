# PreMovePredictionEngineV4.py
# ⚡ محرك التنبؤ المسبق المطور بالكامل - النسخة V4.0 النخبوية ⚡
# 🔮 التنبؤ بالانفجارات السعرية قبل حدوثها بناءً على السيولة وضغط النطاق المؤسسي

import logging
import math

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PreMovePredictionEngine:
    def __init__(self, time_engine, news_engine):
        # ربط المحرك بطبقات التوقيت والأخبار للحساب المتكامل
        self.time_engine = time_engine
        self.news_engine = news_engine

    def analyze_compression(self, bollinger_bandwidth: float, atr_ratio: float) -> dict:
        """
        📊 1. ضغط السوق (Market Compression)
        يقيس النطاق والتقلب المنخفض كمؤشر لاقتراب الانفجار السعري.
        """
        # إذا كان عرض نطاق البولنجر منخفض ونسبة الـ ATR ضعيفة، فهذا يعني انضغاطاً شديداً
        is_compressed = bollinger_bandwidth < 0.02 or atr_ratio < 0.5
        score = 0
        if bollinger_bandwidth < 0.015:
            score += 40
        elif bollinger_bandwidth < 0.03:
            score += 20
            
        if atr_ratio < 0.6:
            score += 20
            
        return {
            'is_compressed': is_compressed,
            'compression_score': score,
            'desc': 'ضغط سوق عالي - نطاق ضيق جداً' if is_compressed else 'حركة اعتيادية طبيعية'
        }

    def analyze_liquidity_buildup(self, orderbook_imbalance: float, near_key_levels: bool) -> dict:
        """
        💥 2. تراكم السيولة (Liquidity Build-Up)
        رصد تجميع طلبات الشراء/البيع بالقرب من مناطق الدعم والمقاومة الثابتة لصيد الوقف.
        """
        score = 0
        # اختلال توازن الطلبات (Orderbook Imbalance) يشير لتراكم أوامر مؤسسية قوية
        if abs(orderbook_imbalance) > 0.65:
            score += 20
        if near_key_levels:
            score += 20 # اقتراب السعر من مستوى سيولة رئيسي (Equal Highs / Lows)
            
        return {
            'liquidity_score': score,
            'has_buildup': score >= 20
        }

    def analyze_early_momentum(self, rsi_slope: float, ema_distance: float) -> dict:
        """
        🧠 3. زخم مبكر (Early Momentum)
        التنبؤ ببداية الحركة عبر رصد التغير التدريجي في زاوية الـ RSI واقتراب تقاطعات الـ EMA.
        """
        score = 0
        # ميلان الـ RSI (RSI Slope) يوضح وجود حركة خفية مبكرة تحت السطح
        if abs(rsi_slope) > 0.15:
            score += 20
        # اقتراب المسافة بين الـ EMA يعني استعدادها للتقاطع والانفجار
        if ema_distance < 0.05:
            score += 20
            
        return {
            'momentum_score': score,
            'has_early_signals': score >= 20
        }

    def predict_explosion_probability(self, market_data: dict, current_market_conditions: dict) -> dict:
        """
        🔮 4 & 5. احتمالية الانفجار ودمج السوق والأخبار
        حساب النتيجة النهائية ونسبة احتمالية حدوث الانفجار السعري القادم بمرونة V4.
        """
        pair = market_data.get('pair', 'UNKNOWN').upper()
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')

        # 🛠️ [تحديث شريكك الذكي]: معالجة مرنة للقيم لضمان عدم تصفير المحرك عند غياب قراءة الـ API
        bb_width = market_data.get('bb_width', 0.018)  # جعل القيمة الافتراضية تميل للضغط لتنشيط الفحص التقديري
        atr_ratio = market_data.get('atr_ratio', 0.45)
        ob_imbalance = market_data.get('ob_imbalance', 0.5)
        near_key_levels = market_data.get('near_key_levels', True)
        rsi_slope = market_data.get('rsi_slope', 0.2)
        ema_distance = market_data.get('ema_distance', 0.03)

        # 1. حساب نقاط المكونات الفنية بناءً على المدخلات الموزونة
        comp_res = self.analyze_compression(bb_width, atr_ratio)
        liq_res = self.analyze_liquidity_buildup(ob_imbalance, near_key_levels)
        mom_res = self.analyze_early_momentum(rsi_slope, ema_distance)
        
        base_probability_score = comp_res['compression_score'] + liq_res['liquidity_score'] + mom_res['momentum_score']

        # 2. دمج الجلسات الزمنية بذكاء ديناميكي لـ V4
        active_sessions = self.time_engine.get_active_sessions() if self.time_engine else []
        
        if 'London' in active_sessions or 'New_York' in active_sessions:
            base_probability_score += 15
        elif 'Asian' in active_sessions:
            # 🛠️ [تعديل شريكك]: في نمط السكالبينج، الجلسة الآسيوية ممتازة للحركات الخاطفة، فلا نخصم نقاطاً عنيفة
            is_scalping = market_data.get('is_scalping_signal', False)
            base_probability_score += 5 if is_scalping else -5 

        # 3. دمج الأخبار الكبرى والمؤثرة
        news_analysis = current_market_conditions.get('news_analysis', {})
        impact_score = news_analysis.get('impact_score', 1)
        
        if impact_score >= 4:
            base_probability_score += 25  # زخم الأخبار الكبرى يسرّع الانفجار السعري الحتمي

        # تحديد تصنيف احتمالية الانفجار النهائي وحصر النتيجة بين 0% و 100%
        final_score = max(0, min(base_probability_score, 100))
        
        # 🛠️ [تعديل الأمان]: إذا كانت الحسبة الفنية صفرية تماماً نتيجة حظر مؤكد، يتم خفض التصنيف بوضوح
        if market_data.get('is_blocked_by_risk', False):
            final_score = 0
            probability_level = "Low"
            desc = "❌ تم تصفير التنبؤ مؤقتاً: الصفقة محظورة من حارس المخاطر لامتلاء الحد المسموح"
        elif final_score >= 70:
            probability_level = "High"
            desc = "🎯 احتمالية انفجار سعري وشيكة جداً - السوق مضغوط والسيولة تتدفق"
        elif final_score >= 45:
            probability_level = "Medium"
            desc = "⚠️ حركة متوسطة متوقعة - يرجى مراقبة تأكيد السيولة"
        else:
            probability_level = "Low"
            desc = "⚪ تقلب منخفض وضغط ضعيف - لا توجد بوادر حركة انفجارية حالياً"

        logging.info(f"🔮 محرك التنبؤ السعري [{pair}]: النتيجة {final_score}% | التصنيف: {probability_level}")

        return {
            'pair': pair,
            'explosion_probability': probability_level,
            'probability_score': final_score,
            'description': desc,
            'compression_status': comp_res['is_compressed']
            }
        
