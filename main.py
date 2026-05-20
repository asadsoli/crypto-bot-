import os
import time
import logging
from time_engine import TradingTimeEngine
from news_engine import FederalNewsEngine
from signal_filter import AdaptiveSignalFilter
from self_learning import SelfLearningEngine
from pre_move_engine import PreMoveExplosionEngine
from risk_manager import InstitutionalRiskManager
from quality_engine import EliteQualityEngine
from signal_engine import SignalEngineV1
from execution_engine import ExecutionEngineV1
from control_panel import InstitutionalControlPanelV2
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_control_panel(panel):
    """تشغيل لوحة تحكم تيليغرام في مسار منفصل لمنع حظر البرنامج الرئيسي"""
    try:
        panel.start_polling()
    except Exception as e:
        logging.error(f"❌ حدث خطأ في لوحة التحكم: {e}")

def main():
    logging.info("👑 جاري تشغيل النظام البرمجي المؤسسي الشامل V2...")

    # 1. جلب التوكنز والمعرفات من متغيرات البيئة (Environment Variables) لحماية الخصوصية
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "YOUR_CHANNEL_ID_HERE")

    # 2. تهيئة وتدشين كافة المحركات الفرعية للمشروع
    time_engine = TradingTimeEngine()
    news_engine = FederalNewsEngine()
    signal_filter = AdaptiveSignalFilter()
    self_learning_engine = SelfLearningEngine()
    pre_move_engine = PreMoveExplosionEngine()
    
    # تهيئة إدارة المخاطر برأس مال افتراضي 100,000$ ونمط متوسط
    risk_manager = InstitutionalRiskManager(total_capital=100000.0, risk_profile="MEDIUM")
    
    quality_engine = EliteQualityEngine(time_engine=time_engine, pre_move_engine=pre_move_engine)
    
    # 3. تهيئة المحركات الكبرى لاتخاذ القرار والتنفيذ
    signal_engine = SignalEngineV1(
        time_engine=time_engine,
        news_engine=news_engine,
        risk_manager=risk_manager,
        quality_engine=quality_engine,
        pre_move_engine=pre_move_engine
    )
    
    execution_engine = ExecutionEngineV1(
        telegram_token=TELEGRAM_TOKEN,
        channel_id=CHANNEL_ID,
        self_learning_engine=self_learning_engine,
        risk_manager=risk_manager
    )

    # 4. تهيئة وتشغيل لوحة التحكم الاحترافية في الخلفية (Multithreading)
    control_panel = InstitutionalControlPanelV2(
        token=TELEGRAM_TOKEN,
        risk_manager=risk_manager,
        quality_engine=quality_engine,
        self_learning_engine=self_learning_engine
    )
    
    panel_thread = threading.Thread(target=run_control_panel, args=(control_panel,), daemon=True)
    panel_thread.start()

    logging.info("🚀 تم ربط كافة البوابات بنجاح. النظام مستعد الآن لاستقبال وتحليل بيانات السوق...")

    # 5. حلقة محاكاة السوق اللحظية (Market Live Simulation Loop)
    # هنا نقوم بضخ بيانات تجريبية تفصيلية تحاكي ما يتم استقباله من منصات البيانات مثل TradingView Webhooks
    while True:
        if control_panel.bot_status == "RUNNING":
            logging.info("🔍 جاري سحب لقطة حية للسوق وتمريرها عبر فلاتر الأموال الذكية...")
            
            # محاكاة لبيانات قادمة لزوج الذهب الرقمي المثبت PAXG
            mock_smc_data = {
                'pair': 'XAUUSDT', # سيقوم المحرك بتحويلها تلقائياً إلى PAXGUSDT داخلياً لحظر الذهب العادي
                'structure': 'BOS_Bullish',
                'liquidity_swept': True,
                'at_order_block_or_fvg': True,
                'current_price': 2350.0,
                'stop_loss': 2335.0,
                'tp1': 2370.0,
                'tp2': 2390.0,
                'tp3': 2420.0,
                'base_confidence': 88.0,
                'base_ai_score': 90.0,
                'rsi': 48,
                'ema_supporting': True,
                'volume_spike': True,
                'orderbook_imbalance': 0.65
            }

            mock_market_conditions = {
                'vix_index': 14.5,
                'dxy_trend': 'Bearish',
                'prediction_probability_score': 87.5,
                'news_analysis': {
                    'impact_score': 1,
                    'sentiment': 'Bullish'
                }
            }

            # معالجة الإشارة عبر عقل اتخاذ القرار
            decision = signal_engine.analyze_market_and_generate_signal(mock_smc_data, mock_market_conditions)
            
            # إذا تمت الموافقة المتقاطعة، نقوم بالتنفيذ والبث فوراً
            if decision.get('status') == 'TRIGGERED':
                execution_engine.execute_and_broadcast_signal(decision)
            else:
                logging.info(f"⏸️ تم تعليق/حظر الفرصة المبدئية. السبب: {decision.get('reason')}")

        else:
            logging.info("💤 البوت في وضعية الإيقاف المؤقت (STOPPED) عبر لوحة التحكم.")

        # فحص دوري للسوق كل 60 ثانية
        time.sleep(60)

if __name__ == "__main__":
    main()
  
