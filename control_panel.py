import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalControlPanelV2:
    def __init__(self, token, risk_manager, quality_engine, self_learning_engine):
        self.bot = telebot.TeleBot(token)
        self.risk_manager = risk_manager
        self.quality_engine = quality_engine
        self.self_learning_engine = self_learning_engine
        
        # حالات النظام الافتراضية
        self.bot_status = "RUNNING" 
        self.intelligence_level = "INSTITUTIONAL" 
        self.news_filter_active = True
        self.market_regime = "Risk ON"
        self.tracked_pairs = ["BTCUSDT", "ETHUSDT", "PAXGUSDT"] 
        self.current_active_pair = "PAXGUSDT"

        self.current_menu_state = "MAIN" 
        self._setup_message_handlers()

    def get_main_menu_keyboard(self) -> ReplyKeyboardMarkup:
        """توليد كيبورد تيليغرام الأساسي المدمج أسفل لوحة الكتابة مباشرة"""
        # zero_time_keyboard=False مع resize_keyboard يجعل الأزرار ثابتة وتفتح وتغلق من زر تليجرام نفسه
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        
        status_text = "🟢 تشغيل البوت (نشط)" if self.bot_status == "RUNNING" else "🔴 إيقاف البوت (معطل)"
        markup.row(KeyboardButton(status_text))
        
        intel_text = f"🧠 الذكاء: {self.intelligence_level}"
        elite_text = "🔥 وضع النخبة: ON" if self.quality_engine.elite_mode_active else "🔥 وضع النخبة: OFF"
        markup.row(KeyboardButton(intel_text), KeyboardButton(elite_text))
        
        news_text = "📰 الأخبار: ON" if self.news_filter_active else "📰 الأخبار: OFF"
        regime_text = f"🌍 السوق: {self.market_regime}"
        markup.row(KeyboardButton(news_text), KeyboardButton(regime_text))
        
        pair_short = self.current_active_pair.split('USDT')[0]
        markup.row(KeyboardButton(f"🪙 العملة النشطة: {pair_short}"), KeyboardButton("🛡️ مستويات المخاطرة"))
        
        markup.row(KeyboardButton("📊 إحصائيات الأداء"), KeyboardButton("🔮 محرك التوقعات Pre-Move"))
        markup.row(KeyboardButton("🛑 إغلاق الطوارئ الشامل"))
        return markup

    def get_risk_menu_keyboard(self) -> ReplyKeyboardMarkup:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        markup.row(KeyboardButton("📉 منخفض (1%)"), KeyboardButton("⚖️ متوسط (2%)"))
        markup.row(KeyboardButton("🔥 عالي (3%)"), KeyboardButton("🏦 مؤسسي صارم (0.5%)"))
        markup.row(KeyboardButton("⬅️ العودة للقائمة الرئيسية"))
        return markup

    def get_pairs_menu_keyboard(self) -> ReplyKeyboardMarkup:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        markup.row(KeyboardButton("🪙 الذهب الرقمي (PAXGUSDT)"))
        markup.row(KeyboardButton("⚡ البيتكوين (BTCUSDT)"))
        markup.row(KeyboardButton("🔷 الإيثيريوم (ETHUSDT)"))
        markup.row(KeyboardButton("⬅️ العودة للقائمة الرئيسية"))
        return markup

    def _setup_message_handlers(self):
        """تفكيك الأوامر المدخلة من الكيبورد دون طباعة رسائل مكررة مزعجة"""
        
        @self.bot.message_handler(commands=['start', 'menu'])
        def handle_start_command(message):
            self.current_menu_state = "MAIN"
            # إرسال الرسالة التعريفية لمرة واحدة فقط لتظهر اللوحة بالأسفل
            text = "👑 **تم تفعيل لوحة التحكم المركزية بالأسفل** 👑\nاضغط على زر الكيبورد في تيليغرام لفتحها أو إغلاقها في أي وقت."
            self.bot.send_message(message.chat.id, text, reply_markup=self.get_main_menu_keyboard(), parse_mode="Markdown")

        @self.bot.message_handler(func=lambda msg: True)
        def handle_keyboard_inputs(message):
            chat_id = message.chat.id
            text = message.text

            if text == "⬅️ العودة للقائمة الرئيسية":
                self.current_menu_state = "MAIN"
                self.bot.send_message(chat_id, "🔄 عدنا للقائمة الرئيسية:", reply_markup=self.get_main_menu_keyboard())
                return

            # 🛠️ معالجة القائمة الرئيسية
            if self.current_menu_state == "MAIN":
                if "تشغيل البوت" in text or "إيقاف البوت" in text:
                    self.bot_status = "STOPPED" if self.bot_status == "RUNNING" else "RUNNING"
                    alert = f"⚙️ تم تعديل حالة البوت إلى: {self.bot_status}"
                elif "🧠 الذكاء:" in text:
                    levels = ["NORMAL", "SMART", "INSTITUTIONAL"]
                    current_idx = levels.index(self.intelligence_level)
                    self.intelligence_level = levels[(current_idx + 1) % len(levels)]
                    alert = f"🧠 نمط الذكاء الحالي: {self.intelligence_level}"
                elif "📰 الأخبار:" in text:
                    self.news_filter_active = not self.news_filter_active
                    alert = f"📰 مرشح الأخبار الفدرالية: {'مفعل' if self.news_filter_active else 'معطل'}"
                elif "🔥 وضع النخبة:" in text:
                    new_status = not self.quality_engine.elite_mode_active
                    self.quality_engine.toggle_elite_mode(new_status)
                    alert = f"🔥 وضع النخبة المؤسسي: {'مفعل' if new_status else 'معطل'}"
                elif "🌍 السوق:" in text:
                    self.market_regime = "Risk OFF" if self.market_regime == "Risk ON" else "Risk ON"
                    alert = f"🌍 بيئة السيولة الحالية: {self.market_regime}"
                elif "🛡️ مستويات المخاطرة" in text:
                    self.current_menu_state = "RISK"
                    self.bot.send_message(chat_id, "🛡️ تم فتح قائمة إدارة المخاطر:", reply_markup=self.get_risk_menu_keyboard())
                    return
                elif "🪙 العملة النشطة:" in text:
                    self.current_menu_state = "PAIRS"
                    self.bot.send_message(chat_id, "🪙 تم فتح قائمة اختيار العملات المستهدفة:", reply_markup=self.get_pairs_menu_keyboard())
                    return
                elif text in ["📊 إحصائيات الأداء", "🔮 محرك التوقعات Pre-Move"]:
                    self.bot.send_message(chat_id, "📊 جاري تحديث تحليلات المحرك الحركي في الخلفية...", reply_markup=self.get_main_menu_keyboard())
                    return
                elif text == "🛑 إغلاق الطوارئ الشامل":
                    self.bot_status = "STOPPED"
                    self.risk_manager.active_trades.clear()
                    self.bot.send_message(chat_id, "⚠️ **إغلاق طوارئ صارم!** تم إيقاف كافة المحركات لحماية الحساب.", reply_markup=self.get_main_menu_keyboard(), parse_mode="Markdown")
                    return
                else:
                    return

                # إرسال رسالة تأكيد قصيرة جداً ومحدثة مع إعادة توجيه الكيبورد ليبقى بالأسفل
                self.bot.send_message(chat_id, alert, reply_markup=self.get_main_menu_keyboard())

            # 🛠️ قائمة المخاطر الفرعية
            elif self.current_menu_state == "RISK":
                if "منخفض" in text: self.risk_manager.set_risk_profile("LOW")
                elif "متوسط" in text: self.risk_manager.set_risk_profile("MEDIUM")
                elif "عالي" in text: self.risk_manager.set_risk_profile("HIGH")
                elif "مؤسسي صارم" in text: self.risk_manager.set_risk_profile("STRICT")
                self.current_menu_state = "MAIN"
                self.bot.send_message(chat_id, f"🛡️ تم اعتماد ملف مخاطر: {self.risk_manager.current_profile}", reply_markup=self.get_main_menu_keyboard())

            # 🛠️ قائمة العملات الفرعية
            elif self.current_menu_state == "PAIRS":
                if "PAXGUSDT" in text: self.current_active_pair = "PAXGUSDT"
                elif "BTCUSDT" in text: self.current_active_pair = "BTCUSDT"
                elif "ETHUSDT" in text: self.current_active_pair = "ETHUSDT"
                self.current_menu_state = "MAIN"
                self.bot.send_message(chat_id, f"🎯 تم تثبيت رادار الفحص اللحظي على: {self.current_active_pair}", reply_markup=self.get_main_menu_keyboard())

    def start_polling(self):
        logging.info("📱 تم الانتقال الكامل لنظام كيبورد تيليغرام الأصلي والذكي...")
        self.bot.infinity_polling()
        
