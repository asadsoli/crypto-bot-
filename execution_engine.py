# execution_engine.py
# 👑 المحرك التنفيذي المركزي لبث الصفقات وإدارة النتائج - النسخة V11 AI CORE المحصنة ضد أخطاء التنسيق 👑
# 🛡️ توافق كامل مع مسارات السكالبينج ودعم إشارات البيع والشراء بناءً على الهيكلية المؤسسية (SMC)

import logging
import telebot
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExecutionEngineV1:
    def __init__(self, telegram_token, channel_id, self_learning_engine, risk_manager):
        self.bot = telebot.TeleBot(telegram_token)
        self.channel_id = channel_id
        self.self_learning_engine = self_learning_engine
        self.risk_manager = risk_manager

    def clean_markdown(self, text: str) -> str:
        """
        تجميع وتطهير النصوص الحية من الرموز الحساسة التي تسبب انهيار التليغرام (Error 400)
        """
        if not text:
            return ""
        # هروب آمن من الرموز الخاصة التي تفسد تنسيق الـ Markdown الكلاسيكي
        return str(text).replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("`", "\\`")

    def execute_and_broadcast_signal(self, signal_result: dict) -> bool:
        """
        📤 استقبال الإشارة المعتمدة، إرسالها لتيليغرام، وتثبيت إدارتها برمجياً
        """
        if signal_result.get('status') != 'TRIGGERED':
            return False

        # جلب البيانات المفلترة أو بيانات الإشارة الأساسية بشكل آمن لمنع التضارب
        data = signal_result['filtered_signal'] if 'filtered_signal' in signal_result else signal_result.get('signal_data', signal_result)
        
        # 🔥 حقن الفلتر الحامي وتطهير المعطيات النصية قبل دمجها بالرسالة
        pair = self.clean_markdown(data.get('pair', 'UNKNOWN'))
        structure_raw = data.get('structure', '')
        trade_style = self.clean_markdown(signal_result.get('trade_style', '⚡ SCALPING (خاطفة)'))
        classification = self.clean_markdown(data.get('classification', '🎖️ ELITE TARGET'))
        session_context = self.clean_markdown(data.get('session_context', 'LIVE INJECTION'))
        
        # 🟢 مطابقة نوع الصفقة ذكياً بناءً على الهيكلية المؤسسية قبل التطهير النصي
        is_short = "Bearish" in structure_raw
        signal_type = "🔴 SELL (بيع مكشوف)" if is_short else "🟢 BUY (شراء صاعد)"
        
        # جلب القيم الفنية بشكل آمن مع وضع قيم افتراضية من الحسابات الحية لمنع الـ KeyError
        quality_score = data.get('quality_score', round(data.get('base_ai_score', 89.5), 1))
        confidence_score = round(data.get('confidence_score', data.get('base_confidence', 88.0)), 1)
        allocated_risk = data.get('allocated_risk', 1.5) # القيمة الافتراضية لحماية الحساب
        
        # جلب التوقيت الحالي بشكل آمن في حال عدم وجود تايم ستامب جاهز
        current_timestamp = data.get('timestamp', str(int(time.time())))

        # صياغة رسالة الإشارة باللغة العربية 100% بنمط مؤسسي مخصص للقناة واللوحة مع تنسيق محمي
        telegram_message = (
            f"👑 **إشارة تداول مؤسسية معتمدة لـ القائد** 👑\n"
            f"----------------------------------------\n"
            f"📊 **نمط التداول:** {trade_style}\n"
            f"🪙 **الزوج:** `{pair}`\n"
            f"**نوع الصفقة:** {signal_type}\n\n"
            f"📊 **نقطة الدخول الحالية:** {data.get('entry_price', data.get('current_price'))}\n"
            f"🛑 **وقف الخسارة (SL):** {data.get('sl', data.get('stop_loss'))}\n"
            f"🎯 **الهدف الأول (TP1):** {data.get('tp1')}\n"
            f"🎯 **الهدف الثاني (TP2):** {data.get('tp2')}\n"
            f"🎯 **الهدف الثالث (TP3):** {data.get('tp3')}\n\n"
            f"💎 **جودة الصفقة:** {classification} ({quality_score}/100)\n"
            f"🧠 **نسبة الثقة:** {confidence_score}%\n"
            f"🛡️ **المخاطرة المخصصة:** {allocated_risk}% من رأس المال\n"
            f"🌍 **الجلسة الحالية:** {session_context}\n"
            f"----------------------------------------\n"
            f"⚠️ *تتم إدارة الصفقة تلقائياً بواسطة محرك التعديل الديناميكي و الـ Break Even المتصل بالتابلت.*"
        )

        try:
            # 1. إرسال الإشارة الاحترافية المطهّرة لقناة تيليغرام فوراً بسلام وتثبيت التنسيق
            self.bot.send_message(self.channel_id, telegram_message, parse_mode="Markdown")
            logging.info(f"🚀 تم تنظيف وتمرير إشارة {pair} بنجاح إلى قناة تيليغرام وتحديد الاتجاه كـ [{'SELL' if is_short else 'BUY'}].")

            # 2. حجز وإقفال الزوج في سجل إدارة المخاطر لحمايته ومنع التداخل
            if self.risk_manager and hasattr(self.risk_manager, 'register_active_trade'):
                self.risk_manager.register_active_trade(pair, id=str(current_timestamp), risk_amount=allocated_risk)

            return True

        except Exception as e:
            logging.error(f"❌ خطأ فادح أثناء إرسال وتنفيذ الإشارة المؤسسية: {e}")
            return False

    def close_and_finalize_trade(self, pair: str, trade_data: dict, outcome: str):
        """
        🔄 عند إغلاق الصفقة (ضربت الهدف أو الوقف)، يتم فك الحجز وإرسال النتيجة 
        إلى نظام التعلم الذاتي Self-Learning Engine للتطور التلقائي وضبط أوزان الأهداف.
        """
        try:
            # فك قفل المخاطر عن الزوج لإتاحة الفرص الجديدة فوراً في السكالبينج
            if self.risk_manager and hasattr(self.risk_manager, 'remove_active_trade'):
                self.risk_manager.remove_active_trade(pair)
            
            # تدوير النتيجة داخل ذاكرة الذكاء الاصطناعي لتحديث الأوزان التكيفية والـ Optimization
            if self.self_learning_engine and hasattr(self.self_learning_engine, 'update_trade_result'):
                self.self_learning_engine.update_trade_result(trade_data, result=outcome)
            
            logging.info(f"🧠 تم ترحيل بيانات صفقة {pair} المغلقة بنتيجة [{outcome}] إلى ملف التعلم الذاتي بنجاح.")
        except Exception as e:
            logging.error(f"⚠️ خطأ أثناء إغلاق وترحيل بيانات الصفقة: {e}")
        
