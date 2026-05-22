import os
import sys
import time
import logging
import threading
import requests  # 🌐 استيراد مكتبة الطلبات لجلب الأسعار الحقيقية

# 🌍 أخبر بايثون بالبحث داخل مجلد src أولاً لتفادي خطأ الـ ImportError على سيرفر Render
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from time_engine import TradingTimeEngine
from news_engine import FederalNewsEngine
# 🛠️ تم حل مشكلة مرشح الإشارة بالاسم المستعار
from signal_filter import InstitutionalSignalFilter as AdaptiveSignalFilter
# 🧠 تم حل مشكلة محرك التعلم الذاتي هنا بإضافة V1 كاسم مستعار ليتوافق مع السيرفر وباقي الكود
from self_learning import SelfLearningEngineV1 as SelfLearningEngine
from pre_move_engine import PreMovePredictionEngine as PreMoveExplosionEngine
from risk_manager import InstitutionalRiskManager
from quality_engine import EliteQualityEngine
from signal_engine import SignalEngineV1
from execution_engine import ExecutionEngineV1
from control_panel import InstitutionalControlPanelV2

# ==================================================
# 🌐 إضافة خادم ويب زائف (Flask) لإرضاء سيرفر Render ومنعه من إعادة التشغيل
# ==================================================
from flask import Flask
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "⚡ ULTRA V10 AI CORE IS LIVE & RUNNING!"

def run_flask():
    # جلب المنفذ التلقائي الذي يفرضه Render، وإلا استخدام 8080 كافتراضي
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)
# ==================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_real_crypto_price(symbol="PAXGUSDT"):
    """دالة آمنة تضمن جلب السعر الحقيقي مباشرة من Binance API العام دون تجميد الكود"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
    except Exception as e:
        logging.error(f"⚠️ تعذر جلب السعر الحقيقي لـ {symbol} بسبب: {e}")
    return None

def run_control_panel(panel):
    """تشغيل لوحة تحكم تيليغرام في مسار منفصل لمنع حظر البرنامج الرئيسي"""
    try:
        panel.start_polling()
    except Exception as e:
        logging.error(f"❌ حدث خطأ في لوحة التحكم: {e}")

def main():
    logging.info("👑 جاري تشغيل النظام البرمجي المؤسسي الشامل V2...")

    # 1. تشغيل خادم الويب في مسار منفصل تماماً قبل بدء محركات البوت
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logging.info("🌐 تم تشغيل خادم الويب الخلفي لتأمين استقرار السيرفر.")

    # 2. جلب التوكنز والمعرفات من متغيرات البيئة (Environment Variables) لحماية الخصوصية
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "YOUR_CHANNEL_ID_HERE")

    # 3. تهيئة وتدشين كافة المحركات الفرعية للمشروع بالتسلسل المتناسق الصحيح
    time_engine = TradingTimeEngine()
    news_engine = FederalNewsEngine()
    self_learning_engine = SelfLearningEngine()
    
    # تمرير المحركات المطلوبة لمرشح الإشارة ومحرك التنبؤ
    signal_filter = AdaptiveSignalFilter(time_engine=time_engine, news_engine=news_engine)
    pre_move_engine = PreMoveExplosionEngine(time_engine=time_engine, news_engine=news_engine)
    
    # تمرير المحركات المطلوبة لـ Risk Manager بناءً على ملفك الأصلي تماماً
    risk_manager = InstitutionalRiskManager(news_engine=news_engine, self_learning_engine=self_learning_engine)
    
    # تعديل نمط المخاطرة إلى MEDIUM بعد التهيئة
    risk_manager.set_risk_profile("MEDIUM")
    
    quality_engine = EliteQualityEngine(time_engine=time_engine, pre_move_engine=pre_move_engine)
    
    # 4. تهيئة المحركات الكبرى لاتخاذ القرار والتنفيذ
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

    # 5. تهيئة وتشغيل لوحة التحكم الاحترافية في الخلفية (Multithreading)
    control_panel = InstitutionalControlPanelV2(
        token=TELEGRAM_TOKEN,
        risk_manager=risk_manager,
        quality_engine=quality_engine,
        self_learning_engine=self_learning_engine
    )
    
    panel_thread = threading.Thread(target=run_control_panel, args=(control_panel,), daemon=True)
    panel_thread.start()

    logging.info("🚀 تم ربط كافة البوابات بنجاح. النظام مستعد الآن لاستقبال وتحليل بيانات السوق...")

    # 6. حلقة محاكاة السوق اللحظية (Market Live Simulation Loop)
    while True:
        if control_panel.bot_status == "RUNNING":
            logging.info("🔍 جاري سحب لقطة حية للسوق وتمريرها عبر فلاتر الأموال الذكية...")
            
            # 🔄 محاولة جلب السعر اللحظي الحقيقي للذهب الرقمي
            live_paxg_price = get_real_crypto_price("PAXGUSDT")
            if live_paxg_price is None:
                live_paxg_price = 2350.0  # قيمة احتياطية في حال انقطع الاتصال بـ Binance
            
            # نقوم بحساب الأهداف ديناميكياً بناءً على السعر الحقيقي الحالي بدلاً من القيم الثابتة
            current_price = live_paxg_price
            stop_loss = current_price - 15.0
            tp1 = current_price + 20.0
            tp2 = current_price + 40.0
            tp3 = current_price + 70.0

            mock_smc_data = {
                'pair': 'XAUUSDT',
                'structure': 'BOS_Bullish',
                'liquidity_swept': True,
                'at_order_block_or_fvg': True,
                'current_price': current_price,
                'stop_loss': stop_loss,
                'tp1': tp1,
                'tp2': tp2,
                'tp3': tp3,
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
                },
                'is_market_choppy': False,
                'next_event_epoch': 0
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
            
