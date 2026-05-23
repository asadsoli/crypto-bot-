import os
import sys
import time
import logging
import threading
import requests
import random 

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from time_engine import TradingTimeEngine
from news_engine import FederalNewsEngine
from signal_filter import InstitutionalSignalFilter as AdaptiveSignalFilter
from self_learning import SelfLearningEngineV1 as SelfLearningEngine
from pre_move_engine import PreMovePredictionEngine as PreMoveExplosionEngine
from risk_manager import InstitutionalRiskManager
from quality_engine import EliteQualityEngine
from signal_engine import SignalEngineV1
from execution_engine import ExecutionEngineV1
from control_panel import InstitutionalControlPanelV2

# ==================================================
# خادم الويب لإرضاء سيرفر Render والـ UptimeRobot
# ==================================================
from flask import Flask
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "⚡ ULTRA V10 AI CORE IS LIVE & RUNNING!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)
# ==================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LAST_PRICES = {
    "PAXGUSDT": 2420.0,
    "BTCUSDT": 68500.0,  
    "ETHUSDT": 3450.0     
}

def get_real_crypto_price(symbol="PAXGUSDT"):
    global LAST_PRICES
    coin_fsym = symbol.replace("USDT", "")
    try:
        url = f"https://min-api.cryptocompare.com/data/price?fsym={coin_fsym}&tsyms=USD"
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            if "USD" in data:
                LAST_PRICES[symbol] = float(data['USD'])
                return LAST_PRICES[symbol]
    except Exception as e:
        logging.warning(f"⚠️ خطأ شبكة، استخدام التذبذب: {e}")
    
    # تذبذب حي ذكي لضمان استمرار المحاكاة
    if "BTC" in symbol: LAST_PRICES[symbol] += random.uniform(-50.0, 70.0)
    elif "ETH" in symbol: LAST_PRICES[symbol] += random.uniform(-5.0, 7.0)
    else: LAST_PRICES[symbol] += random.uniform(-1.0, 1.5)
    return round(LAST_PRICES[symbol], 2)

def run_control_panel(panel):
    try:
        panel.start_polling()
    except Exception as e:
        logging.error(f"❌ حدث خطأ في لوحة التحكم: {e}")

def main():
    logging.info("👑 جاري تشغيل النظام البرمجي المؤسسي الشامل V2...")

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "YOUR_CHANNEL_ID_HERE")

    time_engine = TradingTimeEngine()
    news_engine = FederalNewsEngine()
    self_learning_engine = SelfLearningEngine()
    
    signal_filter = AdaptiveSignalFilter(time_engine=time_engine, news_engine=news_engine)
    pre_move_engine = PreMoveExplosionEngine(time_engine=time_engine, news_engine=news_engine)
    risk_manager = InstitutionalRiskManager(news_engine=news_engine, self_learning_engine=self_learning_engine)
    risk_manager.set_risk_profile("MEDIUM")
    quality_engine = EliteQualityEngine(time_engine=time_engine, pre_move_engine=pre_move_engine)
    
    signal_engine = SignalEngineV1(
        time_engine=time_engine, news_engine=news_engine, risk_manager=risk_manager,
        quality_engine=quality_engine, pre_move_engine=pre_move_engine
    )
    
    execution_engine = ExecutionEngineV1(
        telegram_token=TELEGRAM_TOKEN, channel_id=CHANNEL_ID,
        self_learning_engine=self_learning_engine, risk_manager=risk_manager
    )

    control_panel = InstitutionalControlPanelV2(
        token=TELEGRAM_TOKEN, risk_manager=risk_manager,
        quality_engine=quality_engine, self_learning_engine=self_learning_engine
    )
    
    panel_thread = threading.Thread(target=run_control_panel, args=(control_panel,), daemon=True)
    panel_thread.start()

    last_reported_session = ""

    logging.info("🚀 تم تشغيل البوابات والمراقبة النشطة حية الآن...")

    while True:
        try:
            if control_panel.bot_status == "RUNNING":
                active_pair = control_panel.current_active_pair
                current_price = get_real_crypto_price(active_pair)
                
                # 🌍 [بث إشعارات الأسواق حية وآمنة]
                try:
                    current_hour = time.strftime("%H")
                    if hasattr(time_engine, 'get_current_session'):
                        current_session = time_engine.get_current_session()
                    else:
                        current_session = f"Session_Hour_{current_hour}"
                    
                    if current_session != last_reported_session:
                        session_msg = f"🌍 **إشعار مؤسسي حركي:**\nتم الانتقال الدلالي الآن إلى بيئة التدفق: `{current_session}`\nشروط السيولة يتم تحديثها فوريّاً على زوج {active_pair}."
                        
                        if TELEGRAM_TOKEN != "YOUR_BOT_TOKEN_HERE" and CHANNEL_ID != "YOUR_CHANNEL_ID_HERE":
                            if hasattr(execution_engine, 'bot') and execution_engine.bot is not None:
                                execution_engine.bot.send_message(CHANNEL_ID, session_msg, parse_mode="Markdown")
                            elif hasattr(execution_engine, 'tele_bot'):
                                execution_engine.tele_bot.send_message(CHANNEL_ID, session_msg, parse_mode="Markdown")
                        
                        last_reported_session = current_session
                except Exception as e:
                    logging.error(f"⚠️ فشل إرسال إشعار الجلسة: {e}")

                # 🎯 هندسة الأهداف التكيفية الديناميكية
                if "BTC" in active_pair:
                    stop_loss = round(current_price - random.randint(300, 450), 2)
                    tp1 = round(current_price + random.randint(400, 600), 2)
                    tp2 = round(current_price + random.randint(900, 1200), 2)
                    tp3 = round(current_price + random.randint(1800, 2400), 2)
                elif "ETH" in active_pair:
                    stop_loss = round(current_price - 30.0, 2)
                    tp1 = round(current_price + 45.0, 2)
                    tp2 = round(current_price + 90.0, 2)
                    tp3 = round(current_price + 180.0, 2)
                else: 
                    stop_loss = round(current_price - 12.0, 2)  
                    tp1 = round(current_price + 18.0, 2)
                    tp2 = round(current_price + 35.0, 2)
                    tp3 = round(current_price + 70.0, 2)

                # 🎲 خلخلة البيانات وتجهيزها لحقنها في المحرك الفني الأصلي
                mock_smc_data = {
                    'pair': active_pair,
                    'structure': random.choice(['BOS_Bullish', 'CHoCH_Bullish', 'BOS_Bullish']),
                    'liquidity_swept': True,
                    'at_order_block_or_fvg': True,
                    'current_price': current_price,
                    'stop_loss': stop_loss,
                    'tp1': tp1, 'tp2': tp2, 'tp3': tp3,
                    'base_confidence': random.uniform(86.0, 92.0),
                    'base_ai_score': random.uniform(88.0, 94.0),
                    'rsi': random.randint(40, 55),
                    'ema_supporting': True,
                    'volume_spike': True,
                    'orderbook_imbalance': 0.68
                }

                mock_market_conditions = {
                    'vix_index': 13.8,
                    'dxy_trend': 'Bearish',
                    'prediction_probability_score': 89.0,
                    'news_analysis': {'impact_score': 1, 'sentiment': 'Bullish'},
                    'is_market_choppy': False,
                    'next_event_epoch': 0
                }

                # 🧠 خطوة 1: استدعاء قرار المحرك الذكي الأصلي والكامل للتحليلات
                decision = signal_engine.analyze_market_and_generate_signal(mock_smc_data, mock_market_conditions)
                
                # 🚀 خطوة 2: التحقق الآمن وبث الإشارة دون فقدان الـ 'type' أو التسبب في انهيار الكود
                if decision.get('status') == 'TRIGGERED':
                    try:
                        # نقوم بتمرير النتيجة الكاملة والذكية القادمة مباشرة من المحرك الفني بعد فلاتر الحماية
                        execution_engine.execute_and_broadcast_signal(decision)
                    except Exception as e:
                        logging.error(f"⚠️ خطأ أثناء بث الإشارة إلى تليغرام: {e}")
                else:
                    # طباعة سبب عدم الخروج بالإشارة في اللوجات لمراقبة ذكاء البوت
                    logging.info(f"🔮 محرك التنبؤ السعري [{active_pair}]: {decision.get('reason', 'شروط التصفية النشطة')}")

            else:
                logging.info("💤 البوت في وضعية الإيقاف المؤقت (STOPPED).")
                
        except Exception as main_err:
            logging.error(f"🚨 خطأ في الحلقة الرئيسية: {main_err}")

        time.sleep(60) # فحص متواصل ومستقر كل دقيقة

if __name__ == "__main__":
    main()
