import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalControlPanelV2:
    def __init__(self, token, risk_manager, quality_engine, self_learning_engine):
        self.bot = telebot.TeleBot(token)
        self.risk_manager = risk_manager
        self.quality_engine = quality_engine
        self.self_learning_engine = self_learning_engine
        
        # حالات النظام الافتراضية للوحة التحكم
        self.bot_status = "RUNNING" # RUNNING or STOPPED
        self.intelligence_level = "INSTITUTIONAL" # NORMAL / SMART / INSTITUTIONAL
        self.news_filter_active = True
        self.market_regime = "Risk ON"
        self.tracked_pairs = ["BTCUSDT", "ETHUSDT", "PAXGUSDT"] 
        
        # 🔥 [ميزة العملة النشطة]: العملة الافتراضية عند التشغيل
        self.current_active_pair = "PAXGUSDT"

        # نظام تتبع القوائم الفرعية للكيبورد الثابت
        self.current_menu_state = "MAIN" # MAIN / RISK / PAIRS

        # تسجيل معالجات الرسائل النصية للكيبورد الثابت
        self._setup_message_handlers()

    def get_main_menu_keyboard(self) -> ReplyKeyboardMarkup:
        """إنشاء الكيبورد الأساسي الثابت والمدمج أسفل شاشة التيلغرام تلقائياً"""
        # resize_keyboard=True تجعل الأزرار متناسقة وصغيرة الحجم لتناسب شاشة الهاتف
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        # السطر 1: تشغيل / إيقاف البوت
        status_text = "🟢 تشغيل البوت (نشط)" if self.bot_status == "RUNNING" else "🔴 إيقاف البوت (معطل)"
        markup.row(KeyboardButton(status_text))
        
        # السطر 2: مستوى الذكاء والوضع النخبوي
        intel_text = f"🧠 الذكاء: {self.intelligence_level}"
        elite_text = "🔥 وضع النخبة: ON" if self.quality_engine.elite_mode_active else "🔥 وضع النخبة: OFF"
        markup.row(KeyboardButton(intel_text), KeyboardButton(elite_text))
        
        # السطر 3: فلاتر الأخبار وحالة السوق
        news_text = "📰 الأخبار: ON" if self.news_filter_active else "📰 الأخبار: OFF"
        regime_text = f"🌍 السوق: {self.market_regime}"
        markup.row(KeyboardButton(news_text), KeyboardButton(regime_text))
        
        # السطر 4: أقسام إدارة العملات والمخاطر
        pair_short = self.current_active_pair.split('USDT')[0]
        markup.row(KeyboardButton(f"🪙 العملة النشطة: {pair_short}"), KeyboardButton("🛡️ مستويات المخاطرة"))
        
        # السطر 5: الإحصائيات والتوقعات
        markup.row(KeyboardButton("📊 إحصائيات الأداء"), KeyboardButton("🔮 محرك التوقعات Pre-Move"))
        
        # السطر الأخير: زر الطوارئ الحاسم
        markup.row(KeyboardButton("🛑 إغلاق الطوارئ الشامل"))
        
        return markup

    def get_risk_menu_keyboard(self) -> ReplyKeyboardMarkup:
        """لوحة تحكم كيبورد فرعية ثابتة لإدارة المخاطر"""
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.row(KeyboardButton("📉 منخفض (1%)"), KeyboardButton("⚖️ متوسط (2%)"))
        markup.row(KeyboardButton("🔥 عالي (3%)"), KeyboardButton("🏦 مؤسسي صارم (0.5%)"))
        markup.row(KeyboardButton("⬅️ العودة للقائمة الرئيسية"))
        return markup

    def get_pairs_menu_keyboard(self) -> ReplyKeyboardMarkup:
        """لوحة تحكم كيبورد فرعية ثابتة لاختيار أزواج التداول"""
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.row(KeyboardButton("🪙 الذهب الرقمي (PAXGUSDT)"))
        markup.row(KeyboardButton("⚡ البيتكوين (BTCUSDT)"))
        markup.row(KeyboardButton("🔷 الإيثيريوم (ETHUSDT)"))
        markup.row(KeyboardButton("⬅️ العودة للقائمة الرئيسية"))
        return markup

    def send_dashboard_status(self, chat_id):
        """إرسال تقرير نصي بحالة النظام الحالية لتأكيد التحديث للمستخدم"""
        text = (
            "👑 **تحديث لوحة التحكم المؤسسية V2** 👑\n"
            "-------------------------------------------\n"
            f"⚡ **الحالة العامة:** {self.bot_status}\n"
            f"🪙 **العملة المراقبة حالياً:** `{self.current_active_pair}`\n"
            f"🧠 **نمط التحليل الحركي:** {self.intelligence_level}\n"
            f"🛡️ **ملف المخاطر النشط:** {self.risk_manager.current_profile}\n"
            f"🔥 **تصفية النخبة (Elite Mode):** {'مفعلة' if self.quality_engine.elite_mode_active else 'معطلة'}\n"
            f"🌍 **بيئة حركة السوق:** {self.market_regime}"
        )
        # إرسال الرسالة مع الكيبورد المناسب بناءً على الحالة الحالية
        if self.current_menu_state == "RISK":
            kb = self.get_risk_menu_keyboard()
        elif self.current_menu_state == "PAIRS":
            kb = self.get_pairs_menu_keyboard()
        else:
            kb = self.get_main_menu_keyboard()
            
        self.bot.send_message(chat_id, text, reply_markup=kb, parse_mode="Markdown")

    def _setup_message_handlers(self):
        """تفكيك ومعالجة الأوامر والضغطات القادمة من أزرار الكيبورد المدمج الجديد"""
        
        @self.bot.message_handler(commands=['start', 'menu'])
        def handle_start_command(message):
            self.current_menu_state = "MAIN"
            self.send_dashboard_status(message.chat.id)

        @self.bot.message_handler(func=lambda msg: True)
        def handle_keyboard_inputs(message):
            chat_id = message.chat.id
            text = message.text

            # 1️⃣ العودة للقائمة الرئيسية بأمان
            if text == "⬅️ العودة للقائمة الرئيسية":
                self.current_menu_state = "MAIN"
                self.send_dashboard_status(chat_id)
                return

            # 2️⃣ معالجة مدخلات القائمة الرئيسية
            if self.current_menu_state == "MAIN":
                if "تشغيل البوت" in text or "إيقاف البوت" in text:
                    self.bot_status = "STOPPED" if self.bot_status == "RUNNING" else "RUNNING"
                    
                elif "🧠 الذكاء:" in text:
                    levels = ["NORMAL", "SMART", "INSTITUTIONAL"]
                    current_idx = levels.index(self.intelligence_level)
                    self.intelligence_level = levels[(current_idx + 1) % len(levels)]
                    
                elif "📰 الأخبار:" in text:
                    self.news_filter_active = not self.news_filter_active
                    
                elif "🔥 وضع النخبة:" in text:
                    new_status = not self.quality_engine.elite_mode_active
                    self.quality_engine.toggle_elite_mode(new_status)
                    
                elif "🌍 السوق:" in text:
                    self.market_regime = "Risk OFF" if self.market_regime == "Risk ON" else "Risk ON"
                    
                elif "🛡️ مستويات المخاطرة" in text:
                    self.current_menu_state = "RISK"
                    self.bot.send_message(chat_id, "🛡️ **اختر نمط إدارة المخاطر المؤسسي للمحرك:**", 
                                          reply_markup=self.get_risk_menu_keyboard(), parse_mode="Markdown")
                    return
                    
                elif "🪙 العملة النشطة:" in text:
                    self.current_menu_state = "PAIRS"
                    self.bot.send_message(chat_id, "🪙 **اختر العملة المؤسسية المراد فحص حركتها اللحظية الآن:**", 
                                          reply_markup=self.get_pairs_menu_keyboard(), parse_mode="Markdown")
                    return
                    
                elif text == "📊 إحصائيات الأداء" or text == "🔮 محرك التوقعات Pre-Move":
                    self.bot.send_message(chat_id, "📊 المحرك يقوم بجمع البيانات الإحصائية في الخلفية وتحديث المخرجات تلقائياً...")
                    return
                    
                elif text == "🛑 إغلاق الطوارئ الشامل":
                    self.bot_status = "STOPPED"
                    self.risk_manager.active_trades.clear()
                    self.bot.send_message(chat_id, "⚠️ **إجراء طوارئ إجباري!** تم إيقاف التداول الشامل وتصفير بوابات المخاطر فوراً.", reply_markup=self.get_main_menu_keyboard(), parse_mode="Markdown")
                    return

            # 3️⃣ معالجة مدخلات قائمة المخاطر الفرعية
            elif self.current_menu_state == "RISK":
                if "منخفض" in text: self.risk_manager.set_risk_profile("LOW")
                elif "متوسط" in text: self.risk_manager.set_risk_profile("MEDIUM")
                elif "عالي" in text: self.risk_manager.set_risk_profile("HIGH")
                elif "مؤسسي صارم" in text: self.risk_manager.set_risk_profile("STRICT")
                self.current_menu_state = "MAIN"

            # 4️⃣ معالجة مدخلات قائمة العملات الفرعية
            elif self.current_menu_state == "PAIRS":
                if "PAXGUSDT" in text: self.current_active_pair = "PAXGUSDT"
                elif "BTCUSDT" in text: self.current_active_pair = "BTCUSDT"
                elif "ETHUSDT" in text: self.current_active_pair = "ETHUSDT"
                self.current_menu_state = "MAIN"

            # إرسال رسالة التحديث وإعادة توليد القائمة الرئيسية بعد أي عملية
            self.send_dashboard_status(chat_id)

    def start_polling(self):
        """تشغيل محرك استقبال البيانات من تيليغرام"""
        logging.info("📱 لوحة التحكم الاحترافية المدمجة بدأت العمل بنظام الكيبورد الثابت...")
        self.bot.infinity_polling()
                    
