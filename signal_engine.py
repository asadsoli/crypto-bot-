import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SignalEngineV1:
    def __init__(self, time_engine, news_engine, risk_manager, quality_engine, pre_move_engine):
        self.time_engine = time_engine
        self.news_engine = news_engine
        self.risk_manager = risk_manager
        self.quality_engine = quality_engine
        self.pre_move_engine = pre_move_engine

    def analyze_market_and_generate_signal(self, smc_data: dict, market_conditions: dict) -> dict:
        """
        ⚙️ محرك تحليل الهيكلية واتخاذ قرار الدخول المؤسسي
        """
        pair = smc_data.get('pair', 'UNKNOWN').upper()
        # استبدال الذهب التقليدي بالذهب الرقمي المشفر بشكل صارم ومثبت
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')

        logging.info(f"📊 جاري فحص الشروط الفنية والمؤسسية لزوج: {pair}")

        # 1. استخراج معطيات هيكلية الأموال الذكية (SMC)
        structure = smc_data.get('structure')        # BOS_Bullish / BOS_Bearish / CHoCH
        liquidity_swept = smc_data.get('liquidity_swept', False)  # تم سحب السيولة أم لا
        has_ob_or_fvg = smc_data.get('at_order_block_or_fvg', False)
        
        # المؤشرات التأكيدية المساعدة (Indicator Confirmation)
        rsi = smc_data.get('rsi', 50)
        ema_support = smc_data.get('ema_supporting', False)

        signal_type = None

        # منطق الدخول المؤسسي لشروط الشراء (BUY)
        if (structure == "BOS_Bullish" or structure == "CHoCH_Bullish") and liquidity_swept and has_ob_or_fvg:
            if rsi > 45 and ema_support: # شروط تأكيدية إضافية للمؤشرات
                signal_type = "BUY"

        # منطق الدخول المؤسسي لشروط البيع (SELL)
        elif (structure == "BOS_Bearish" or structure == "CHoCH_Bearish") and liquidity_swept and has_ob_or_fvg:
            if rsi < 55 and ema_support:
                signal_type = "SELL"

        if not signal_type:
            return {'status': 'NO_SIGNAL', 'reason': "لم تتحقق شروط توافق هيكلية الأموال الذكية وسحب السيولة"}

        # 2. بناء بيانات الإشارة المبدئية
        raw_signal = {
            'pair': pair,
            'type': signal_type,
            'entry_price': smc_data.get('current_price'),
            'sl': smc_data.get('stop_loss'),
            'tp1': smc_data.get('tp1'),
            'tp2': smc_data.get('tp2'),
            'tp3': smc_data.get('tp3'),
            'confidence_score': smc_data.get('base_confidence', 65.0),
            'ai_score': smc_data.get('base_ai_score', 70.0),
            'timestamp': datetime.datetime.utcnow().timestamp()
        }

        # 3. المزامنة المتقاطعة مع باقي محركات النظام الكامل (Sync Layers)
        
        # أ: مزامنة محرك التوقعات قبل الحركة Pre-Move Sync
        pred_res = self.pre_move_engine.predict_explosion_probability(smc_data, market_conditions)
        if pred_res['explosion_probability'] == 'High':
            raw_signal['confidence_score'] = min(raw_signal['confidence_score'] + 10, 100)
            raw_signal['ai_score'] = min(raw_signal['ai_score'] + 10, 100)

        # ب: مزامنة تقييم الجودة ونظام النخبة Quality & Elite Sync
        quality_res = self.quality_engine.calculate_quality_score(raw_signal, market_conditions)
        if not quality_res['is_tradable']:
            return {'status': 'FILTERED', 'reason': quality_res['reject_reason']}

        # ج: المزامنة والتحقق الإجباري من إدارة المخاطر Risk Manager Sync
        risk_res = self.risk_manager.can_open_trade(raw_signal, market_conditions)
        if risk_res['status'] == 'BLOCK':
            return {'status': 'BLOCKED_BY_RISK', 'reason': risk_res['reason']}

        # تجميع وحقن البيانات المفلترة بالكامل لتمريرها لمحرك التنفيذ
        raw_signal['quality_score'] = quality_res['quality_score']
        raw_signal['classification'] = quality_res['classification']
        raw_signal['allocated_risk'] = risk_res['allocated_risk_percentage']
        raw_signal['session_context'] = self.time_engine.get_active_sessions()[0] if self.time_engine.get_active_sessions() else 'Out of Sessions'

        return {
            'status': 'TRIGGERED',
            'signal_data': raw_signal
        }
      
