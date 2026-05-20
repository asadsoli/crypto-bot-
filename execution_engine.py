import telebot
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExecutionEngineV1:
    def __init__(self, telegram_token, channel_id, self_learning_engine, risk_manager):
        self.bot = telebot.TeleBot(telegram_token)
        self.channel_id = channel_id
        self.self_learning_engine = self_learning_engine
        self.risk_manager = risk_manager

    def execute_and_broadcast_signal(self, signal_result: dict) -> bool:
        """
        📤 استقبال الإشارة المعتمدة، إرسالها لتيليغرام، وتثبيت إدارتها برمجياً
        """
        if signal_result.get('status') != 'TRIGGERED':
            return False

        data = signal_result['filtered_signal'] if 'filtered_signal' in signal_result else signal_result['signal_data']
        pair = data['pair']
        signal_type = "🟢 BUY" if data['type'] == "BUY" else "🔴 SELL"
        
        # صياغة رسالة الإشارة باللغة العربية 100% بنمط مؤسسي منظم
        telegram_message = (
            f"⚡ **إشارة تداول مؤسسية معتمدة** ⚡\n"
            f"----------------------------------------\n"
            f"🪙 **الزوج:** {pair}\n"
            f"نوع الصفقة: {signal_type}\n\n"
            f"📊 **نقطة الدخول الحالية:** {data['entry_price']}\n"
            f"🛑 **وقف الخسارة (SL):** {data['sl']}\n"
            f"🎯 **الهدف الأول (TP1):** {data['tp1']}\n"
            f"🎯 **الهدف الثاني (TP2):** {data['tp2']}\n"
            f"🎯 **الهدف الثالث (TP3):** {data['tp3']}\n\n"
            f"💎 **جودة الصفقة:** {data['classification']} ({data['quality_score']}/100)\n"
            f"🧠 **نسبة الثقة:** {data['confidence_score']}%\n"
            f"🛡️ **المخاطرة المخصصة:** {data['allocated_risk'] * 100:.2f}% من رأس المال\n"
            f"🌍 **الجلسة الحالية:** {data['session_context']}\n"
            f"----------------------------------------\n"
            f"⚠️ *تتم إدارة الصفقة تلقائياً بواسطة محرك التعديل الديناميكي و الـ Break Even.*"
        )

        try:
            # 1. إرسال الإشارة الاحترافية لقناة تيليغرام فوراً
            self.bot.send_message(self.channel_id, telegram_message, parse_mode="Markdown")
            logging.info(f"🚀 تم إرسال إشارة {pair} بنجاح إلى قناة تيليغرام.")

            # 2. حجز وإقفال الزوج في سجل إدارة المخاطر لحمايته ومنع التداخل
            # نعتبر قيمة افتراضية لحجم المخاطرة المالية بناءً على النسبة المخصصة
            self.risk_manager.register_active_trade(pair, id=str(data['timestamp']), risk_amount=data['allocated_risk'])

            # 3. [طبقة مستقبلية لتنفيذ الأمر على المنصات Binance/MT5]
            # self._open_api_trade(data)
            
            return True

        except Exception as e:
            logging.error(f"خطأ أثناء إرسال وتنفيذ الإشارة المؤسسية: {e}")
            return False

    def close_and_finalize_trade(self, pair: str, trade_data: dict, outcome: str):
        """
        🔄 عند إغلاق الصفقة (ضربت الهدف أو الوقف)، يتم فك الحجز وإرسال النتيجة 
        إلى نظام التعلم الذاتي Self-Learning Engine للتطور التلقائي.
        """
        # فك قفل المخاطر عن الزوج لإتاحة الفرص الجديدة
        self.risk_manager.remove_active_trade(pair)
        
        # تدوير النتيجة داخل ذاكرة الذكاء الاصطناعي لتحديث الأوزان التكيفية
        self.self_learning_engine.update_trade_result(trade_data, result=outcome)
        
        logging.info(f"🧠 تم ترحيل بيانات صفقة {pair} المغلرة بنتيجة [{outcome}] إلى ملف التعلم الذاتي.")
      
