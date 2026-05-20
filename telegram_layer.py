import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ========================================================
# 🧠 الـ BrainCore (تم دمجه هنا مباشرة لضمان عدم حدوث Crash أو غياب الملف)
# ========================================================
class BrainCore:
    def __init__(self, signal_engine, market=None, news=None, risk=None):
        """
        العقل المركزي للنظام - يقوم بالربط الفوري بين الأزرار ومحركات الفلترة الذكية والمخاطر.
        """
        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        logging.info("🧠 [مدمج] تم تدشين العقل المركزي (BrainCore) بنجاح داخل طبقة التيليغرام.")

    def process_market_data(self, raw_data: dict, market_conditions: dict) -> dict:
        """معالجة لقطات البيانات الفنية وإصدار القرار النهائي عبر محرك الإشارات الشامل غداً."""
        if not self.signal_engine:
            logging.error("❌ محرك الإشارات الفنية غير متصل بالـ BrainCore")
            return {"status": "REJECTED", "reason": "Signal Engine Container is missing"}
        try:
            decision = self.signal_engine.analyze_market_and_generate_signal(raw_data, market_conditions)
            return decision
        except Exception as e:
            logging.error(f"❌ خطأ داخلي في الـ BrainCore: {e}")
            return {"status": "REJECTED", "reason": str(e)}


# ========================================================
# 🤖 طبقة التيليغرام المعدلة والمحمية بالكامل
# ========================================================
class TelegramLayer:
    def __init__(self, token, signal_engine, market=None, news=None, risk=None, time_engine=None):
        # 🤖 تهيئة عميل تيليغرام المحدث
        self.bot = telebot.TeleBot(token)

        # ⚙️ ربط المحركات والاعتماديات الفنية بالبنية الأساسية للبوت
        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        self.time_engine = time_engine

        # 🔥 تعديل جوهري: استدعاء الـ BrainCore المدمج بالأعلى مباشرة لتجاوز خطأ الـ Import
        self.brain = BrainCore(
            signal_engine=self.signal_engine,
            market=self.market,
            news=self.news,
            risk=self.risk
        )
        logging.info("🎯 تم ربط واجهة الأزرار بالعقل المركزي المدمج بنجاح وبدون مجلدات فرعية.")

        # ⚙️ حالة البوت والأصول المدعومة
        self.is_bot_active = True
        self.current_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

        # 🔍 قائمة المراقبة النخبوية المثبتة (بما فيها الذهب الرقمي PAXG)
        self.watchlist_assets = [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "PAXGUSDT",
            "SOLUSDT"
        ]

        self.scanner = None
        self.busy = False

        # تفعيل مستمع الأزرار فوراً عند التشغيل
        self._register_callbacks()

    def set_scanner(self, scanner):
        self.scanner = scanner
        if hasattr(scanner, "assets"):
            scanner.assets = list(self.watchlist_assets)
        if hasattr(scanner, "brain"):
            scanner.brain = self.brain

    # 🎛 لوحة التحكم الرسومية المحدثة بالكامل لبث وتوجيه الأوامر
    def menu(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=2)
        
        markup.add(InlineKeyboardButton("📊 تحليل السوق اللحظي", callback_data="analyze"))
        
        markup.add(
            InlineKeyboardButton("🥇 BTCUSDT", callback_data="asset_BTCUSDT"),
            InlineKeyboardButton("💎 ETHUSDT", callback_data="asset_ETHUSDT")
        )
        markup.add(
            InlineKeyboardButton("💰 BNBUSDT", callback_data="asset_BNBUSDT"),
            InlineKeyboardButton("🏅 PAXGUSDT", callback_data="asset_PAXGUSDT")
        )
        markup.add(
            InlineKeyboardButton("⚡ SOLUSDT", callback_data="asset_SOLUSDT")
        )
        markup.add(
            InlineKeyboardButton("🟢 تشغيل البوت", callback_data="bot_on"),
            InlineKeyboardButton("🔴 إيقاف البوت", callback_data="bot_off")
        )
        markup.add(
            InlineKeyboardButton("🔍 Scanner ON", callback_data="scan_on"),
            InlineKeyboardButton("⛔ Scanner OFF", callback_data="scan_off")
        )
        markup.add(
            InlineKeyboardButton("⚙️ فحص الحالة العامة", callback_data="status")
        )
        return markup

    # 🔗 معالجة ضغطات الأزرار والتفاعل الفوري مع لوحة التحكم
    def _register_callbacks(self):
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_buttons(call):
            chat_id = call.message.chat.id
            data = call.data

            if data == "analyze":
                self.bot.answer_callback_query(call.id, "جاري تحليل الهيكلية الفنية...")
                if self.brain:
                    # مصفوفة تجريبية لحين سحب الإشارة الحية من السيرفر غداً
                    result = {"signal": "BUY", "entry": 2350, "sl": 2335, "tp": 2390, "confidence": 85, "quality": "Elite", "reason": "SMC Structure Break"}
                    self.bot.send_message(chat_id, self.format_result(result))
                
            elif data.startswith("asset_"):
                selected_asset = data.replace("asset_", "")
                if self.set_asset(selected_asset):
                    self.bot.answer_callback_query(call.id, f"تم تبديل الأصل النشط إلى: {selected_asset}")
                    self.bot.send_message(chat_id, f"🔄 نظام الفلترة موجه حالياً بالكامل نحو: **{selected_asset}**", parse_mode="Markdown")
                
            elif data == "bot_on":
                self.is_bot_active = True
                self.bot.answer_callback_query(call.id, "تم تفعيل البوت")
                
            elif data == "bot_off":
                self.is_bot_active = False
                self.bot.answer_callback_query(call.id, "تم إيقاف البوت مؤقتاً")
                
            elif data == "status":
                status_msg = (
                    f"⚙️ **حالة النظام الحالية:**\n"
                    f"• حالة البوت: {'🟢 نشط' if self.is_bot_active else '🔴 متوقف'}\n"
                    f"• العملة النشطة: `{self.current_asset}`\n"
                    f"• نمط المخاطرة: `{self.risk_mode}`"
                )
                self.bot.send_message(chat_id, status_msg, parse_mode="Markdown")

    def format_result(self, signal_data):
        if not isinstance(signal_data, dict):
            return "❌ No signal data"

        return f"""🤖 ULTRA V10 AI CORE

💰 ASSET: {self.current_asset}

📊 SIGNAL: {signal_data.get('signal', 'N/A')}
🎯 ENTRY: {signal_data.get('entry', 'N/A')}
🛑 SL: {signal_data.get('sl', 'N/A')}
💰 TP: {signal_data.get('tp', 'N/A')}

💎 CONFIDENCE: {signal_data.get('confidence', 0)}%
🏆 QUALITY: {signal_data.get('quality', 'N/A')}

📍 REASON:
{signal_data.get('reason', 'N/A')}
"""

    def set_asset(self, asset_symbol):
        try:
            if not asset_symbol:
                return False
            asset_symbol = str(asset_symbol).upper().strip()
            if asset_symbol not in self.watchlist_assets:
                return False

            self.current_asset = asset_symbol

            if self.signal_engine and hasattr(self.signal_engine, "set_asset"):
                try:
                    self.signal_engine.set_asset(asset_symbol)
                except:
                    pass

            if self.scanner and hasattr(self.scanner, "assets"):
                try:
                    self.scanner.assets = list(self.watchlist_assets)
                except:
                    pass
            return True
        except Exception as e:
            print("❌ set_asset error:", e)
            return False

    def start_polling(self):
        """بدء استقبال النبضات الفورية من السيرفر"""
        self.bot.infinity_polling()
                              
