# execution_engine.py
# 👑 المحرك التنفيذي المركزي لبث الصفقات وإدارة النتائج - النسخة V12.1 النخبوية المحصنة 👑
# 🛡️ سحق تضارب الاتجاهات نهائياً وحقن فلتر صمام منع الإغراق والتكرار اللحظي (Anti-Flood)

import logging
import telebot
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExecutionEngineV1:
    def __init__(self, telegram_token, channel_id, self_learning_engine, risk_manager, is_scalp_active=True):
        self.bot = telebot.TeleBot(telegram_token)
        self.channel_id = channel_id
        self.self_learning_engine = self_learning_engine
        self.risk_manager = risk_manager
        
        # 🛡️ الحالة التشغيلية للمحرك (تمت إضافتها لمنع الخطأ الفادح)
        self.is_scalping_active = is_scalp_active
        
        # 🛡️ سجل الطوارئ اللحظي لمنع تكرار بث نفس العملة دفعة واحدة (Anti-Flood Cache)
        self.last_broadcast_time = {}
        self.cooldown_seconds = 45  # الحد الأدنى المسموح به بين الإشارة والأخرى لنفس العملة

    def clean_markdown(self, text: str) -> str:
        """
        تجميع وتطهير النصوص الحية من الرموز الحساسة التي تسبب انهيار التليغرام (Error 400)
        """
        if not text:
            return ""
        return str(text).replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("`", "\\`")

    def execute_and_broadcast_signal(self, signal_result: dict) -> bool:
        """
        📤 استقبال الإشارة المعتمدة، إرسالها لتيليغرام، وتثبيت إدارتها برمجياً بنمط مؤسسي نظيف
        """
        # 🚨 [إصلاح جذري] التحقق من حالة التفعيل قبل البدء
        if not self.is_scalping_active:
            logging.info("⏸️ المحرك التنفيذي في وضع الإيقاف (is_scalp_active=False).")
            return False

        if signal_result.get('status') != 'TRIGGERED':
            return False

        # جلب البيانات المفلترة أو بيانات الإشارة الأساسية بشكل آمن لمنع التضارب
        data = signal_result['filtered_signal'] if 'filtered_signal' in signal_result else signal_result.get('signal_data', signal_result)
        
        pair = self.clean_markdown(data.get('pair', 'UNKNOWN')).upper()
        
        # 🚨 صمام الأمان الفولاذي: منع تكديس وإغراق القناة بنفس العملة في فترات متقاربة
        current_time_now = time.time()
        if pair in self.last_broadcast_time:
            time_passed = current_time_now - self.last_broadcast_time[pair]
            if time_passed < self.cooldown_seconds:
                logging.warning(f"⚠️ [Anti-Flood] تم حظر محاولة بث مكررة لزوج {pair}. الوقت المنقضي: {time_passed:.1f} ثانية فقط!")
                return False

        # 🔥 جلب الاتجاه المعتمد الصريح مباشرة من المحرك التحليلي لتفادي فخ الهيكلية المعكوسة
        raw_type = data.get('type', '').upper()
        is_short = "SELL" in raw_type or "SHORT" in raw_type
        
        signal_type = "🔴 SELL (بيع مكشوف)" if is_short else "🟢 BUY (شراء صاعد)"
        trade_style = self.clean_markdown(data.get('trade_style', signal_result.get('trade_style', '⚡ SCALPING (خاطفة)')))
        classification = self.clean_markdown(data.get('classification', '🎖️ ELITE TARGET'))
        session_context = self.clean_markdown(data.get('session_context', 'LIVE INJECTION'))
        
        # جلب القيم الفنية بشكل آمن مع وضع قيم افتراضية من الحسابات الحية لمنع الـ KeyError
        quality_score = data.get('quality_score', round(data.get('base_ai_score', 89.5), 1))
        confidence_score = round(data.get('confidence_score', data.get('base_confidence', 88.0)), 1)
        allocated_risk = data.get('allocated_risk', 1.5) 
        
        # جلب التوقيت الحالي بشكل آمن في حال عدم وجود تايم ستامب جاهز
        current_timestamp = data.get('timestamp', str(int(time.time())))

        # 🎯 جلب وتنسيق الأسعار الفنية
        entry = data.get('entry_price', data.get('current_price', 0.0))
        sl = data.get('sl', data.get('stop_loss', 0.0))
        tp1 = data.get('tp1', 0.0)
        tp2 = data.get('tp2', 0.0)
        tp3 = data.get('tp3', 0.0)

        # 🪙 [فلتر الدقة وتصحيح أسعار أصول الذهب PAXG والعملات]
        if "PAXG" in pair:
            entry_str = f"{float(entry):.2f}"
            sl_str = f"{float(sl):.2f}"
            tp1_str = f"{float(tp1):.2f}" if tp1 else "---"
            tp2_str = f"{float(tp2):.2f}" if tp2 else "---"
            tp3_str = f"{float(tp3):.2f}" if tp3 else "---"
        elif "BTC" in pair:
            entry_str = f"{float(entry):.1f}"
            sl_str = f"{float(sl):.1f}"
            tp1_str = f"{float(tp1):.1f}" if tp1 else "---"
            tp2_str = f"{float(tp2):.1f}" if tp2 else "---"
            tp3_str = f"{float(tp3):.1f}" if tp3 else "---"
        else:
            entry_str = f"{float(entry):.4f}".rstrip('0').rstrip('.')
            sl_str = f"{float(sl):.4f}".rstrip('0').rstrip('.')
            tp1_str = f"{float(tp1):.4f}".rstrip('0').rstrip('.').rstrip('---') if tp1 else "---"
            tp2_str = f"{float(tp2):.4f}".rstrip('0').rstrip('.').rstrip('---') if tp2 else "---"
            tp3_str = f"{float(tp3):.4f}".rstrip('0').rstrip('.').rstrip('---') if tp3 else "---"

        # صياغة رسالة الإشارة باللغة العربية 100% بنمط مؤسسي مخصص مرن
        telegram_message = (
            f"👑 **إشارة تداول مؤسسية معتمدة لـ القائد** 👑\n"
            f"----------------------------------------\n"
            f"📊 **نمط التداول:** {trade_style}\n"
            f"🪙 **الزوج:** `{pair}`\n"
            f"**نوع الصفقة:** {signal_type}\n\n"
            f"📊 **نقطة الدخول الحالية:** {entry_str}\n"
            f"🛑 **وقف الخسارة (SL):** {sl_str}\n"
            f"🎯 **الهدف الأول (TP1):** {tp1_str}\n"
            f"🎯 **الهدف الثاني (TP2):** {tp2_str}\n"
            f"🎯 **الهدف الثالث (TP3):** {tp3_str}\n\n"
            f"💎 **جودة الصفقة:** {classification} ({quality_score}/100)\n"
            f"🧠 **نسبة الثقة:** {confidence_score}%\n"
            f"🛡️ **المخاطرة المخصصة:** {allocated_risk}% من رأس المال\n"
            f"🌍 **الجلسة الحالية:** {session_context}\n"
            f"----------------------------------------\n"
            f"⚠️ *تتم إدارة الصفقة تلقائياً بواسطة محرك التعديل الديناميكي ونظام الـ Break Even المؤسسي.*"
        )

        try:
            # 1. إرسال الإشارة الاحترافية المطهّرة لقناة تيليغرام فوراً بسلام وتثبيت التنسيق
            self.bot.send_message(self.channel_id, telegram_message, parse_mode="Markdown")
            logging.info(f"🚀 تم تنظيف وتمرير إشارة {pair} بنجاح إلى قناة تيليغرام وتحديد الاتجاه كـ [{'SELL' if is_short else 'BUY'}].")

            # تسجيل التوقيت الحالي لتوثيق صمام منع التكرار
            self.last_broadcast_time[pair] = current_time_now

            # 2. حجز وإقفال الزوج في سجل إدارة المخاطر لحمايته ومنع التداخل
            if self.risk_manager and hasattr(self.risk_manager, 'register_active_trade'):
                self.risk_manager.register_active_trade(pair, id=str(current_timestamp), risk_amount=allocated_risk)

            return True

        except Exception as e:
            logging.error(f"❌ خطأ فادح أثناء إرسال وتنفيذ الإشارة المؤسسية: {e}")
            return False

    def close_and_finalize_trade(self, pair: str, trade_data: dict, outcome: str):
        """
        🔄 عند إغلاق الصفقة، يتم فك الحجز وإرسال النتيجة إلى نظام التعلم الذاتي
        """
        pair_upper = pair.upper()
        try:
            if self.risk_manager and hasattr(self.risk_manager, 'remove_active_trade'):
                self.risk_manager.remove_active_trade(pair_upper)
            
            if self.self_learning_engine and hasattr(self.self_learning_engine, 'update_trade_result'):
                self.self_learning_engine.update_trade_result(trade_data, result=outcome)
            
            logging.info(f"🧠 تم ترحيل بيانات صفقة {pair_upper} المغلقة بنتيجة [{outcome}] إلى ملف التعلم الذاتي بنجاح.")
        except Exception as e:
            logging.error(f"⚠️ خطأ أثناء إغلاق وترحيل بيانات الصفقة: {e}")
