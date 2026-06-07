# main.py
# 👑 المحرك التنفيذي المركزي لمنظومة الوحش المؤسسية - النسخة V12.2 AI CORE المستقرة 👑
# 🛡️ نظام المسارات المنفصلة المعزولة لحل مشكلة الـ Port Timeout على Render نهائياً
# 🚨 سحق تضارب متغيرات وضع السكالبينج وتأمين الإقلاع النظيف دون انهيار 100%

import os
import sys
import time
import logging
import threading
import requests
import random 

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# تعريف المتغيرات العالمية بشكل صريح لمنع خطأ NameError
is_scalp_active = False

# استدعاءات المنظومة الفنية المطورة
from time_engine import TradingTimeEngine
from news_engine import FederalNewsEngine
from signal_filter import InstitutionalSignalFilter as AdaptiveSignalFilter
from self_learning import SelfLearningEngineV1 as SelfLearningEngine
from pre_move_engine import PreMovePredictionEngine as PreMoveExplosionEngine
from quality_engine import EliteQualityEngine
from execution_engine import ExecutionEngineV1

# 🔥 ترقية العقل المركزي: ربط المحركات المحدثة V4 بنجاح كامل لمنع الـ ImportError
from signal_engine import SignalEngineV4
from risk_manager import InstitutionalRiskManagerV4
from control_panel import InstitutionalControlPanelV2 as InstitutionalControlPanelV3

# ========================================================
# خادم الويب لإرضاء سيرفر Render والـ UptimeRobot
# ========================================================
from flask import Flask
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "⚡ ULTRA V12 AI CORE V4 SCALPING CORE IS LIVE & RUNNING PROUDLY!"

def run_flask_main_thread():
    """تشغيل خادم الويب في المسار الرئيسي بشكل مباشر ليحجز البورت فوراً ويرضي Render"""
    port = int(os.environ.get("PORT", 8080))
    logging.info(f"✨ [Render Protection] خادم الويب متمسك بالبورت الحركي الفوري: {port}")
    app_flask.run(host='0.0.0.0', port=port)
# ========================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# تحديث قاموس الطوارئ بمستويات أسعار عام 2026 الحالية لمنع الجمود البرمجي
LAST_PRICES = {
    "PAXGUSDT": 4340.0,
    "BTCUSDT": 60580.0,  
    "ETHUSDT": 3450.0,
    "SOLUSDT": 145.0
}

def get_real_crypto_price(symbol="BTCUSDT"):
    """
    🟢 موديول قنص السعر المطور:
    يلف على 4 روابط وسيرفرات بديلة لبينانس لضمان قراءة السعر الحركي من الشارت رغماً عن قيود Render وحظره الجغرافي.
    """
    global LAST_PRICES
    symbol = symbol.upper()
    
    urls = [
        f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api2.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api3.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://data-api.binance.vision/api/v3/ticker/price?symbol={symbol}"
    ]
    
    if symbol != "PAXGUSDT":
        urls.insert(0, f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}")
    
    for url in urls:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    LAST_PRICES[symbol] = float(data['price'])
                    logging.info(f"🎯 تم قنص السعر الحي المباشر لـ {symbol} بنجاح: {LAST_PRICES[symbol]}")
                    return LAST_PRICES[symbol]
        except Exception:
            continue
            
    logging.warning(f"⚠️ فشلت كافة الروابط البديلة لـ ({symbol}) | قراءة السعر الاحتياطي بالذاكرة: {LAST_PRICES[symbol]}")
    return LAST_PRICES[symbol]


def trading_radar_loop(control_panel, signal_engine, execution_engine, monitored_assets):
    """عزل الحلقة التكرارية اللانهائية للسكالبينج والرادار في Thread منفصل تماماً لحماية البورت"""
    global is_scalp_active
    last_checked_hour = -1
    CHANNEL_ID = os.getenv("CHANNEL_ID", "YOUR_CHANNEL_ID_HERE")
    
    # قاموس لتسجيل آخر وقت تم إرسال صفقة فيه لكل عملة لمنع التكديس والتكرار المباشر
    last_signal_time = {asset: 0 for asset in monitored_assets}
    
    logging.info("🚀 تم تشغيل بوابات المراقبة والرادار الخلفي النخبوي لـ V4 حياً في مسار معزول...")
    
    while True:
        try:
            # 🛡️ الدرع البرمجي: تحديث الحالة من اللوحة
            is_scalp_active = getattr(control_panel, 'scalp_mode_active', False)
            is_active = False
            
            if hasattr(control_panel, 'bot_status'):
                is_active = (control_panel.bot_status == "RUNNING")
            elif hasattr(control_panel, 'is_bot_active'):
                is_active = control_panel.is_bot_active

            if is_active:  
                current_hour = int(time.strftime("%H"))
                
                if current_hour != last_checked_hour:
                    session_events = {
                        0:  ("سوق طوكيو (الآسيوي)", "افتتاح 🟢"),
                        9:  ("سوق طوكيو (الآسيوي)", "إغلاق 🔴"),
                        8:  ("سوق لندن (الأوروبي)", "افتتاح 🟢"),
                        17: ("سوق لندن (الأوروبي)", "إغلاق 🔴"),
                        13: ("سوق نيويورك (الأمريكي)", "افتتاح 🟢"),
                        22: ("سوق نيويورك (الأمريكي)", "إغلاق 🔴")
                    }
                    
                    if current_hour in session_events:
                        session_name, session_status = session_events[current_hour]
                        status_emoji = "🔥 تتدفق الآن أموال الحيتان وصناديق التحوط!" if "افتتاح" in session_status else "⚠️ ترقب هدوء نسبي في السيولة التقليدية الحية."
                        private_alert_msg = (
                            f"🌍 **[رادار السيولة الذكي - إشعار خاص]**\n"
                            f"----------------------------------------\n"
                            f"🚨 **تنبيه فوري لـ القائد:** تم الآن وبشكل رسمي **[{session_status}]** لـ **{session_name}**.\n\n"
                            f"💡 *حالة التداول:* {status_emoji}\n"
                            f"🛡️ المنظومة في الخلفية تقوم بضبط فلاتر القنص التلقائي لتتوافق مع حجم السوق الحالي."
                        )
                        
                        try:
                            if hasattr(control_panel, 'bot') and control_panel.bot:
                                control_panel.bot.send_message(CHANNEL_ID, private_alert_msg, parse_mode="Markdown")
                                logging.info(f"📢 تم بث حالة {session_name} - {session_status} بنجاح.")
                        except Exception as session_err:
                            logging.error(f"⚠️ فشل موديول بث جلسات السيولة الخاص: {session_err}")
                            
                    last_checked_hour = current_hour

                active_pair = random.choice(monitored_assets)
                current_time_now = time.time()
                
                if current_time_now - last_signal_time[active_pair] < 45:
                    time.sleep(2)
                    continue

                current_price = get_real_crypto_price(active_pair)
                
                chosen_structure = random.choice(['BOS_Bullish', 'CHoCH_Bullish', 'BOS_Bearish', 'CHoCH_Bearish'])
                is_bullish = "Bullish" in chosen_structure
                trade_direction = "BUY" if is_bullish else "SELL"

                if "BTC" in active_pair:
                    if is_scalp_active:
                        stop_loss = round(current_price - 50 if is_bullish else current_price + 50, 2)
                        tp1 = round(current_price + 60 if is_bullish else current_price - 60, 2)
                        tp2 = round(current_price + 100 if is_bullish else current_price - 100, 2)
                        tp3 = round(current_price + 150 if is_bullish else current_price - 150, 2)
                    else:
                        stop_loss = round(current_price - 400 if is_bullish else current_price + 400, 2)
                        tp1 = round(current_price + 500 if is_bullish else current_price - 500, 2)
                        tp2 = round(current_price + 1000 if is_bullish else current_price - 1000, 2)
                        tp3 = round(current_price + 2000 if is_bullish else current_price - 2000, 2)
                        
                elif "ETH" in active_pair:
                    if is_scalp_active:
                        stop_loss = round(current_price - 3.5 if is_bullish else current_price + 3.5, 2)
                        tp1 = round(current_price + 4.5 if is_bullish else current_price - 4.5, 2)
                        tp2 = round(current_price + 9.0 if is_bullish else current_price - 9.0, 2)
                        tp3 = round(current_price + 15.0 if is_bullish else current_price - 15.0, 2)
                    else:
                        stop_loss = round(current_price - 30.0 if is_bullish else current_price + 30.0, 2)
                        tp1 = round(current_price + 45.0 if is_bullish else current_price - 45.0, 2)
                        tp2 = round(current_price + 90.0 if is_bullish else current_price - 90.0, 2)
                        tp3 = round(current_price + 180.0 if is_bullish else current_price - 180.0, 2)
                        
                elif "SOL" in active_pair:
                    if is_scalp_active:
                        stop_loss = round(current_price - 0.35 if is_bullish else current_price + 0.35, 2)
                        tp1 = round(current_price + 0.50 if is_bullish else current_price - 0.50, 2)
                        tp2 = round(current_price + 0.95 if is_bullish else current_price - 0.95, 2)
                        tp3 = round(current_price + 1.60 if is_bullish else current_price - 1.60, 2)
                    else:
                        stop_loss = round(current_price - 2.5 if is_bullish else current_price + 2.5, 2)
                        tp1 = round(current_price + 4.0 if is_bullish else current_price - 4.0, 2)
                        tp2 = round(current_price + 8.5 if is_bullish else current_price - 8.5, 2)
                        tp3 = round(current_price + 15.0 if is_bullish else current_price - 15.0, 2)
                else: 
                    if is_scalp_active:
                        stop_loss = round(current_price - 4.0 if is_bullish else current_price + 4.0, 2)  
                        tp1 = round(current_price + 6.0 if is_bullish else current_price - 6.0, 2)
                        tp2 = round(current_price + 12.0 if is_bullish else current_price - 12.0, 2)
                        tp3 = round(current_price + 20.0 if is_bullish else current_price - 20.0, 2)
                    else:
                        stop_loss = round(current_price - 20.0 if is_bullish else current_price + 20.0, 2)  
                        tp1 = round(current_price + 30.0 if is_bullish else current_price - 30.0, 2)
                        tp2 = round(current_price + 60.0 if is_bullish else current_price - 60.0, 2)
                        tp3 = round(current_price + 120.0 if is_bullish else current_price - 120.0, 2)

                mock_smc_data = {
                    'pair': active_pair, 
                    'structure': chosen_structure, 
                    'type': trade_direction,          
                    'signal_type': trade_direction,   
                    'liquidity_swept': True, 
                    'at_order_block_or_fvg': True,
                    'current_price': current_price, 
                    'stop_loss': stop_loss, 
                    'tp1': tp1, 'tp2': tp2, 'tp3': tp3,
                    'base_confidence': random.uniform(88.0, 93.5), 
                    'base_ai_score': random.uniform(89.5, 95.0),
                    'rsi': random.randint(35, 48) if not is_bullish else random.randint(52, 68), 
                    'ema_supporting': False if not is_bullish else True, 
                    'volume_spike': True, 
                    'orderbook_imbalance': 0.68, 
                    'is_scalping_signal': is_scalp_active 
                }

                mock_market_conditions = {
                    'vix_index': 13.8, 
                    'dxy_trend': 'Bearish' if is_bullish else 'Bearish' if is_bullish else 'Bullish', 
                    'prediction_probability_score': 89.0,
                    'news_analysis': {'impact_score': 1, 'sentiment': 'Bullish' if is_bullish else 'Bearish', 'risk_regime': 'Risk ON'},
                    'is_market_choppy': False, 
                    'next_event_epoch': 0
                }

                decision = signal_engine.analyze_market_and_generate_signal(mock_smc_data, mock_market_conditions)
                
                if decision.get('status') == 'TRIGGERED':
                    try:
                        decision['trade_style'] = "⚡ SCALPING (خاطفة)" if is_scalp_active else "🏆 SWING (موجية)"
                        if 'type' not in decision or decision['type'] != trade_direction:
                            decision['type'] = trade_direction
                        
                        execution_engine.execute_and_broadcast_signal(decision)
                        last_signal_time[active_pair] = time.time() 
                    except Exception as e:
                        logging.error(f"⚠️ خطأ أثناء بث الإشارة عبر موديول التنفيذ: {e}")
                else:
                    style_label = "سكالبينج" if is_scalp_active else "طويلة الأمد"
                    logging.info(f"🔮 محرك التنبؤ [{style_label}] لـ [{active_pair}]: {decision.get('reason', 'تجميع سيولة')}")

            else:
                logging.info("💤 البوت في وضعية الإيقاف المؤقت عبر اللوحة الرئيسية (STOPPED).")
                
        except Exception as main_err:
            logging.error(f"🚨 خطأ فادح في الحلقة التنفيذية المفتوحة: {main_err}")

        # معدل نوم الحلقة بين كل فحص فردي لعملة وأخرى لضمان توزيع الإشارات بفارق زمني احترافي
        time.sleep(12)


def main():
    logging.info("👑 جاري تشغيل النظام البرمجي المؤسسي الشامل لـ النسخة V12 السكالبينج الشاملة...")

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "YOUR_CHANNEL_ID_HERE")

    time_engine = TradingTimeEngine()
    news_engine = FederalNewsEngine()
    self_learning_engine = SelfLearningEngine()
    
    signal_filter = AdaptiveSignalFilter(time_engine=time_engine, news_engine=news_engine)
    pre_move_engine = PreMoveExplosionEngine(time_engine=time_engine, news_engine=news_engine)
    
    risk_manager = InstitutionalRiskManagerV4(news_engine=news_engine, self_learning_engine=self_learning_engine)
    risk_manager.set_risk_profile("MEDIUM")
    
    quality_engine = EliteQualityEngine(time_engine=time_engine, pre_move_engine=pre_move_engine)
    
    signal_engine = SignalEngineV4(
        time_engine=time_engine, news_engine=news_engine, risk_manager=risk_manager,
        quality_engine=quality_engine, pre_move_engine=pre_move_engine
    )
    
    execution_engine = ExecutionEngineV1(
        telegram_token=TELEGRAM_TOKEN, channel_id=CHANNEL_ID,
        self_learning_engine=self_learning_engine, risk_manager=risk_manager
    )

    control_panel = InstitutionalControlPanelV3(
        token=TELEGRAM_TOKEN, risk_manager=risk_manager, quality_engine=quality_engine, self_learning_engine=self_learning_engine
    )
    
    def run_polling_isolated():
        while True:
            try:
                logging.info("🔄 جاري محاولة تشغيل الاستماع لتليغرام (Polling) بعناد...")
                # تم استدعاء start_polling بدون معاملات لتتوافق مع تعريف الكلاس الخاص بك
                control_panel.start_polling()
            except Exception as e:
                logging.error(f"❌ حدث انقطاع في تليغرام، جاري إعادة المحاولة خلال 10 ثوانٍ: {e}")
                time.sleep(10)

    panel_thread = threading.Thread(target=run_polling_isolated, daemon=True)
    panel_thread.start()

    monitored_assets = ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "SOLUSDT"]
    trading_thread = threading.Thread(
        target=trading_radar_loop, 
        args=(control_panel, signal_engine, execution_engine, monitored_assets), 
        daemon=True
    )
    trading_thread.start()

    run_flask_main_thread()

if __name__ == "__main__":
    main()
                    
