import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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

        # تسجيل معالجات الضغط على الأزرار (Callback Queries)
        self._setup_callbacks()

        # 🎯 تسجيل أمر /start لكي يظهر الكيبورد فوراً بمجرد كتابته للبوت
        self._setup_commands()

    def _setup_commands(self):
        """تسجيل الأوامر النصية مثل /start لإظهار اللوحة الرئيسية تلقائياً"""
        @self.bot.message_handler(commands=['start', 'menu'])
        def send_welcome(message):
            self.send_dashboard(message.chat.id)

    def get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """إنشاء الأزرار التفاعلية للقائمة الرئيسية للتحكم بالمحرك"""
        markup = InlineKeyboardMarkup(row_width=2)
        
        # السطر 1: تشغيل / إيقاف البوت
        status_text = "🟢 تشغيل البوت (نشط)" if self.bot_status == "RUNNING" else "🔴 إيقاف البوت (معطل)"
        markup.add(InlineKeyboardButton(status_text, callback_data="toggle_bot_status"))
        
        # السطر 2: مستوى الذكاء الحالي للـ AI
        intel_text = f"🧠 الذكاء: {self.intelligence_level}"
        markup.add(InlineKeyboardButton(intel_text, callback_data="cycle_intelligence"))
        
        # السطر 3: فلاتر الأخبار والوضع الجيوسياسي
        news_text = "📰 الأخبار والسياسة: ON" if self.news_filter_active else "📰 الأخبار والسياسة: OFF"
        markup.add(InlineKeyboardButton(news_text, callback_data="toggle_news_filter"))
        
        # السطر 4: حالة المخاطر والوضع النخبوي
        regime_text = f"🌍 حالة السوق: {self.market_regime}"
        elite_text = "🔥 وضع النخبة: ON" if self.quality_engine.elite_mode_active else "🔥 وضع النخبة: OFF"
        markup.add(InlineKeyboardButton(regime_text, callback_data="toggle_regime"),
                   InlineKeyboardButton(elite_text, callback_data="toggle_elite_mode"))
        
        # السطر 5: قسم إدارة العملات والأداء
        markup.add(InlineKeyboardButton(f"🪙 العملة: {self.current_active_pair.split('USDT')[0]}", callback_data="menu_pairs"),
                   InlineKeyboardButton("🛡️ مستويات المخاطرة", callback_data="menu_risk"))
        
        markup.add(InlineKeyboardButton("📊 إحصائيات الأداء", callback_data="menu_performance"),
                   InlineKeyboardButton("🔮 محرك التوقعات Pre-Move", callback_data="menu_prediction"))
        
        # السطر الأخير: زر الطوارئ الصارم
        markup.add(InlineKeyboardButton("🛑 إغلاق الطوارئ الشامل لكل الصفقات", callback_data="emergency_stop"))
        
        return markup

    def send_dashboard(self, chat_id):
        """إرسال اللوحة الرئيسية المحدثة للمستخدم"""
        text = (
            "👑 **لوحة التحكم المؤسسية الاحترافية V2** 👑\n"
            "-------------------------------------------\n"
            "مرحباً بك في وحدة التحكم المركزية للبوت. استخدم الأزرار أدناه لتوجيه سلوك النظام الحركي وإدارة الصفقات فورياً بدون أوامر نصية.\n\n"
            f"⚡ **الحالة العامة:** {self.bot_status}\n"
            f"🪙 **العملة المراقبة حالياً:** `{self.current_active_pair}`\n"
            f"🧠 **نمط التحليل الحركي:** {self.intelligence_level}\n"
            f"🛡️ **ملف المخاطر النشط:** {self.risk_manager.current_profile}\n"
            f"🔥 **تصفية النخبة (Elite Mode):** {'مفعلة' if self.quality_engine.elite_mode_active else 'معطلة'}"
        )
        self.bot.send_message(chat_id, text, reply_markup=self.get_main_menu_keyboard(), parse_mode="Markdown")

    def _setup_callbacks(self):
        """تفكيك ومعالجة الإشارات القادمة من الأزرار"""
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_query(call):
            chat_id = call.message.chat.id
            data = call.data

            if data == "toggle_bot_status":
                self.bot_status = "STOPPED" if self.bot_status == "RUNNING" else "RUNNING"
                self.bot.answer_callback_query(call.id, f"تم تعديل حالة البوت إلى {self.bot_status}")
                
            elif data == "cycle_intelligence":
                levels = ["NORMAL", "SMART", "INSTITUTIONAL"]
                current_idx = levels.index(self.intelligence_level)
                self.intelligence_level = levels[(current_idx + 1) % len(levels)]
                self.bot.answer_callback_query(call.id, f"تم ترقية مستوى الذكاء لـ {self.intelligence_level}")
                
            elif data == "toggle_news_filter":
                self.news_filter_active = not self.news_filter_active
                self.bot.answer_callback_query(call.id, f"تحديث فلتر الأخبار: {self.news_filter_active}")
                
            elif data == "toggle_elite_mode":
                new_status = not self.quality_engine.elite_mode_active
                self.quality_engine.toggle_elite_mode(new_status)
                self.bot.answer_callback_query(call.id, f"وضع النخبة: {new_status}")
                
            elif data == "toggle_regime":
                self.market_regime = "Risk OFF" if self.market_regime == "Risk ON" else "Risk ON"
                self.bot.answer_callback_query(call.id, f"تحديث حالة السوق لـ {self.market_regime}")
                
            elif data == "menu_risk":
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("📉 منخفض (1%)", callback_data="set_risk_LOW"),
                           InlineKeyboardButton("⚖️ متوسط (2%)", callback_data="set_risk_MEDIUM"))
                markup.add(InlineKeyboardButton("🔥 عالي (3%)", callback_data="set_risk_HIGH"),
                           InlineKeyboardButton("🏦 مؤسسي صارم (0.5%)", callback_data="set_risk_STRICT"))
                markup.add(InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="back_to_main"))
                self.bot.edit_message_text("🛡️ **اختر نمط إدارة المخاطر المؤسسي للمحرك:**", chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
                return

            # 🔥 [تحديث تفاعلي كلي لقسم العملات]: تفعيل لوحة اختيار أزواج التداول
            elif data == "menu_pairs":
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(
                    InlineKeyboardButton("🪙 الذهب الرقمي (PAXGUSDT)", callback_data="select_pair_PAXGUSDT"),
                    InlineKeyboardButton("⚡ البيتكوين (BTCUSDT)", callback_data="select_pair_BTCUSDT"),
                    InlineKeyboardButton("🔷 الإيثيريوم (ETHUSDT)", callback_data="select_pair_ETHUSDT")
                )
                markup.add(InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="back_to_main"))
                self.bot.edit_message_text("🪙 **اختر العملة المؤسسية المراد فحص حركتها اللحظية الآن:**", chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
                return

            elif data.startswith("select_pair_"):
                self.current_active_pair = data.replace("select_pair_", "")
                self.bot.answer_callback_query(call.id, f"🎯 تحويل رادار الفحص إلى: {self.current_active_pair}")

            elif data.startswith("set_risk_"):
                profile = data.replace("set_risk_", "")
                self.risk_manager.set_risk_profile(profile)
                self.bot.answer_callback_query(call.id, f"تم تطبيق نمط المخاطر: {profile}")
                
            elif data == "emergency_stop":
                self.bot_status = "STOPPED"
                self.risk_manager.active_trades.clear()
                self.bot.send_message(chat_id, "⚠️ **إجراء طوارئ إجباري!** تم إيقاف التداول الشامل وتصفير بوابات المخاطر فوراً حماية لرأس المال.", parse_mode="Markdown")
                
            elif data in ["back_to_main", "menu_performance", "menu_prediction"]:
                # معالجة القوائم الإضافية لتعود بأمان للشاشة الرئيسية دون تعطيل الكود
                if data != "back_to_main":
                    self.bot.answer_callback_query(call.id, "📊 النظام يقوم بجمع الإحصائيات في الخلفية...")

            # إعادة تحديث اللوحة الرئيسية لتعكس التغييرات والبيانات اللحظية
            try:
                text = (
                    "👑 **لوحة التحكم المؤسسية الاحترافية V2** 👑\n"
                    "-------------------------------------------\n"
                    f"⚡ **الحالة العامة:** {self.bot_status}\n"
                    f"🪙 **العملة المراقبة حالياً:** `{self.current_active_pair}`\n"
                    f"🧠 **نمط التحليل الحركي:** {self.intelligence_level}\n"
                    f"🛡️ **ملف المخاطر النشط:** {self.risk_manager.current_profile}\n"
                    f"🌍 **حالة السوق الفدرالية والجيوسياسية:** {self.market_regime}\n"
                    f"🔥 **تصفية النخبة (Elite Mode):** {'مفعلة' if self.quality_engine.elite_mode_active else 'معطلة'}"
                )
                self.bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=self.get_main_menu_keyboard(), parse_mode="Markdown")
            except Exception as e:
                logging.error(f"خطأ في تحديث واجهة اللوحة: {e}")

    def start_polling(self):
        """تشغيل محرك استقبال البيانات من تيليغرام"""
        logging.info("📱 لوحة التحكم الاحترافية بدأت العمل واستقبال الأوامر عبر الأزرار...")
        self.bot.infinity_polling()
        
