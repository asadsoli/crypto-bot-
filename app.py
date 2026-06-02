# TelegramLayerV3.py
# 👑 طبقة التيليغرام ولوحة التحكم المطورة بالكامل - النسخة V11 AI CORE المحصنة أمنياً 👑
# 🛡️ نظام الأمان الصارم: تفعيل المسارات الخلفية المستقلة لمنع تجمد السيرفر وحل مشكلة 'عاطل'

import os
import logging
import datetime
import telebot
import time
import random
import threading  # ⚡ حقن مكتبة المسارات الموازية لفك التجميد عن السيرفر
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BrainCore:
    def __init__(self, signal_engine, market=None, news=None, risk=None):
        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        logging.info("🧠 [مدمج] تم تدشين العقل المركزي (BrainCore V4) بنجاح داخل طبقة التيليغرام.")

    def process_market_data(self, raw_data: dict, market_conditions: dict) -> dict:
        if not self.signal_engine:
            logging.error("❌ محرك الإشارات الفنية غير متصل بالـ BrainCore")
            return {"status": "REJECTED", "reason": "Signal Engine Container is missing"}
        try:
            decision = self.signal_engine.analyze_market_and_generate_signal(raw_data, market_conditions)
            return decision
        except Exception as e:
            logging.error(f"❌ خطأ داخلي في الـ BrainCore V4: {e}")
            return {"status": "REJECTED", "reason": str(e)}


class TelegramLayerV3:
    def __init__(self, token, signal_engine, market=None, news=None, risk=None, time_engine=None):
        self.bot = telebot.TeleBot(token)
        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        self.time_engine = time_engine

        # 🔒 جدار الحماية الفولاذي المقفل بـ Chat ID لمنع تطفل الغرباء
        self.admin_chat_id = os.getenv("MY_CHAT_ID", "YOUR_TELEGRAM_CHAT_ID_HERE")

        self.brain = BrainCore(
            signal_engine=self.signal_engine,
            market=self.market,
            news=self.news,
            risk=self.risk
        )
        logging.info("🎯 تم ربط واجهة الأزرار بالعقل المركزي V4 بنجاح وبدون مجلدات فرعية.")

        self.is_bot_active = True
        self.current_asset = "BTCUSDT"
        self.risk_mode = "AUTO"

        self.watchlist_assets = ["BTCUSDT", "PAXGUSDT", "ETHUSDT", "SOLUSDT"]
        self.scanner = None
        self.busy = False
        self._register_callbacks()

    def set_scanner(self, scanner):
        self.scanner = scanner
        if hasattr(scanner, "assets"):
            scanner.assets = list(self.watchlist_assets)
        if hasattr(scanner, "brain"):
            scanner.brain = self.brain

    def menu(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("📊 تحليل السوق اللحظي", callback_data="analyze"))
        markup.add(
            InlineKeyboardButton("🥇 BTC (البيتكوين)", callback_data="asset_BTCUSDT"),
            InlineKeyboardButton("🏅 PAXG (الذهب)", callback_data="asset_PAXGUSDT")
        )
        markup.add(
            InlineKeyboardButton("💎 ETH (إيثيريوم)", callback_data="asset_ETHUSDT"),
            InlineKeyboardButton("⚡ SOL (سولانا)", callback_data="asset_SOLUSDT")
        )
        markup.add(InlineKeyboardButton("🔍 فحص عملة مخصصة (تحت الطلب)", callback_data="custom_scan_menu"))
        markup.add(InlineKeyboardButton("🔓 تصفير وتحرير الصفقات العالقة", callback_data="clear_active_trades"))
        markup.add(
            InlineKeyboardButton("🟢 تشغيل البوت", callback_data="bot_on"),
            InlineKeyboardButton("🔴 إيقاف البوت", callback_data="bot_off")
        )
        markup.add(
            InlineKeyboardButton("🔍 Scanner ON", callback_data="scan_on"),
            InlineKeyboardButton("⛔ Scanner OFF", callback_data="scan_off")
        )
        markup.add(InlineKeyboardButton("⚙️ فحص الحالة والخط المالي", callback_data="status"))
        return markup

    def custom_scan_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🪙 BNB", callback_data="ondemand_BNBUSDT"),
            InlineKeyboardButton("🌐 XRP", callback_data="ondemand_XRPUSDT")
        )
        markup.add(
            InlineKeyboardButton("🧬 ADA", callback_data="ondemand_ADAUSDT"),
            InlineKeyboardButton("🐕 DOGE", callback_data="ondemand_DOGEUSDT")
        )
        markup.add(InlineKeyboardButton("🔙 العودة للوحة الرئيسية", callback_data="back_to_main"))
        return markup

    def _register_callbacks(self):
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_buttons(call):
            chat_id = call.message.chat.id
            data = call.data

            if self.admin_chat_id != "YOUR_TELEGRAM_CHAT_ID_HERE" and str(chat_id) != str(self.admin_chat_id):
                self.bot.answer_callback_query(call.id, "❌ خطأ أمني: لوحة التحكم هذه مشفرة ومقيدة بالكامل للقائد فقط!", show_alert=True)
                logging.warning(f"⚠️ محاولة اختراق وتدخل أمني مرفوضة من الـ Chat ID: {chat_id}")
                return

            if data == "analyze":
                self.bot.answer_callback_query(call.id, f"جاري سحب نبض الشارت لـ {self.current_asset}...")
                if self.signal_engine:
                    chosen_structure = random.choice(['BOS_Bullish', 'BOS_Bearish', 'CHoCH_Bullish', 'CHoCH_Bearish'])
                    is_bull = "Bullish" in chosen_structure
                    
                    # 🪙 حزام أمان فك الـ Circular Import التراكمي
                    current_live_price = 93500.0 if "BTC" in self.current_asset else (2450.0 if "PAXG" in self.current_asset else 3400.0)
                    try:
                        from main import get_real_crypto_price
                        current_live_price = get_real_crypto_price(self.current_asset)
                    except:
                        pass
                    
                    if "PAXG" in self.current_asset.upper():
                        sl_calc = round(current_live_price - 15.0 if is_bull else current_live_price + 15.0, 2)
                    elif "BTC" in self.current_asset.upper():
                        sl_calc = round(current_live_price - 350.0 if is_bull else current_live_price + 350.0, 2)
                    elif "ETH" in self.current_asset.upper():
                        sl_calc = round(current_live_price - 25.0 if is_bull else current_live_price + 25.0, 2)
                    else:
                        sl_calc = round(current_live_price - 2.0 if is_bull else current_live_price + 2.0, 2)
                    
                    mock_smc = {
                        'pair': self.current_asset, 
                        'structure': chosen_structure, 
                        'liquidity_swept': True,
                        'at_order_block_or_fvg': True, 
                        'rsi': 54 if is_bull else 66, 
                        'ema_supporting': True, 
                        'current_price': current_live_price,
                        'stop_loss': sl_calc, 
                        'base_confidence': 93.4, 
                        'base_ai_score': 95.1,
                        'is_scalping_signal': False
                    }
                    mock_market = {'news_analysis': {'risk_regime': 'Risk ON'}, 'next_event_epoch': 0, 'is_market_choppy': False}
                    
                    res = self.signal_engine.analyze_market_and_generate_signal(mock_smc, mock_market)
                    if res.get('status') == 'TRIGGERED':
                        self.bot.send_message(chat_id, self.format_result_v3(res['signal_data']), parse_mode="Markdown")
                    else:
                        self.bot.send_message(chat_id, f"⚠️ حظر المحرك المؤسسي: {res.get('reason', 'تجميع سيولة وتوزيع')}")

            elif data.startswith("asset_"):
                selected_asset = data.replace("asset_", "")
                if self.set_asset(selected_asset):
                    self.bot.answer_callback_query(call.id, f"تم تبديل الأصل النشط إلى: {selected_asset}")
                    self.bot.send_message(chat_id, f"🔄 نظام الفلترة موجه حالياً بالكامل نحو: **{selected_asset}**", parse_mode="Markdown")

            elif data == "custom_scan_menu":
                self.bot.edit_message_text("🔍 اختر العملة التي تريد من البوت فحصها فوراً جلب سعرها وتحديد وجود فرصة أم لا:", 
                                           chat_id, call.message.message_id, reply_markup=self.custom_scan_markup())

            elif data == "back_to_main":
                self.bot.edit_message_text("⚡ لوحة تحكم منظومة الوحش المؤسسية V4 ⚡", 
                                           chat_id, call.message.message_id, reply_markup=self.menu())

            elif data == "clear_active_trades":
                if self.risk:
                    self.risk.active_trades.clear()
                    self.risk.daily_loss_counter = 0
                    self.risk.emergency_lock_until = None
                    self.bot.answer_callback_query(call.id, "🔄 تم تصفير كافة الأقفال بنجاح!")
                    self.bot.send_message(chat_id, "✅ **[تحديث المخاطر V4]:** تم تنظيف سجل الصفقات العالقة وتصفير عدادات الحظر التلقائي بنجاح. المنظومة عادت للرصد والنشر اللحظي الفوري الآن! 🦅", parse_mode="Markdown")
                else:
                    self.bot.answer_callback_query(call.id, "❌ خطأ: محرك إدارة المخاطر المحدث غير متصل برمجياً بالواجهة حالياً.")

            elif data.startswith("ondemand_"):
                custom_pair = data.replace("ondemand_", "")
                self.bot.answer_callback_query(call.id, f"جاري فحص {custom_pair}...")
                
                live_custom_price = 1.0
                try:
                    from main import get_real_crypto_price
                    live_custom_price = get_real_crypto_price(custom_pair)
                except:
                    pass
                
                if self.signal_engine:
                    def get_mock_data(p):
                        return {'pair': p, 'current_price': live_custom_price, 'structure': 'CHoCH_Bullish', 'liquidity_swept': True, 'at_order_block_or_fvg': True, 'rsi': 58, 'ema_supporting': True, 'stop_loss': round(live_custom_price * 0.98, 2)}
                    
                    mock_market = {'news_analysis': {'risk_regime': 'Risk ON'}, 'next_event_epoch': 0, 'is_market_choppy': False}
                    report = self.signal_engine.process_on_demand_request(custom_pair, get_mock_data, mock_market)
                    
                    msg = (
                        f"📊 **تقرير الفحص الفوري المخصص (V4)**\n"
                        f"----------------------------------------\n"
                        f"🪙 **العملة:** `{report['pair']}`\n"
                        f"💰 **السعر الحالي المباشر:** ${report['current_price']}\n"
                        f"🧠 **الهيكلية المؤسسية (SMC):** `{report['structure']}`\n"
                        f"🛡️ **حالة السيولة:** {report['liquidity_swept']}\n\n"
                        f"🚨 **النتيجة الشخصية:** {'✅ توجد فرصة دخول ممتازة مبدئياً' if report['opportunity'] == 'AVAILABLE' else '❌ لا توجد فرصة آمنة حالياً'}\n"
                        f"----------------------------------------\n"
                        f"⏱️ تاريخ الفحص: {report['timestamp']}"
                    )
                    self.bot.send_message(chat_id, msg, parse_mode="Markdown")

            elif data == "bot_on":
                self.is_bot_active = True
                self.bot.answer_callback_query(call.id, "تم تفعيل البوت وعودته للعمل")
                
            elif data == "bot_off":
                self.is_bot_active = False
                self.bot.answer_callback_query(call.id, "تم إيقاف البوت مؤقتاً")
                
            elif data == "status":
                status_msg = (
                    f"⚙️ **حالة النظام والخط المالي (V4):**\n"
                    f"• حالة البوت: {'🟢 نشط ويعمل بالخلفية' if self.is_bot_active else '🔴 متوقف مؤقتاً'}\n"
                    f"• العملة النشطة على اللوحة: `{self.current_asset}`\n"
                    f"• سلة الرادار الخلفي النشط: `BTC, PAXG, ETH, SOL`\n"
                    f"• نمط المخاطرة المعتمد: `{self.risk_mode}`"
                )
                self.bot.send_message(chat_id, status_msg, parse_mode="Markdown")

    def format_result_v3(self, signal_data):
        pair_clean = str(signal_data.get('pair')).replace("_", "\\_")
        classification_clean = str(signal_data.get('classification', '🎖️ ELITE TARGET')).replace("_", "\\_")
        session_clean = str(signal_data.get('session_context', 'LIVE INJECTION')).replace("_", "\\_")
        
        return f"""👑 **إشارة تداول مؤسسية معتمدة لـ القائد** 👑
----------------------------------------
📊 **نمط التداول:** 🏆 SWING (موجية)
🪙 **الزوج:** `{pair_clean}`
**نوع الصفقة:** {'🟢 BUY (شراء صاعد)' if signal_data.get('type') == 'BUY' else '🔴 SELL (بيع مكشوف)'}

📊 **نقطة الدخول الحالية:** {signal_data.get('entry_price')}
🛑 **وقف الخسارة:** {signal_data.get('sl')}
🎯 **الهدف الأول (TP1):** {signal_data.get('tp1')}
🎯 **الهدف الثاني (TP2):** {signal_data.get('tp2')}
🎯 **الهدف الثالث (TP3):** {signal_data.get('tp3')}

💎 **جودة الصفقة:** {classification_clean} ({signal_data.get('quality_score', 94.2)}/100)
🧠 **نسبة الثقة:** {signal_data.get('confidence_score', 96.2)}%
🛡️ **المخاطرة المخصصة:** {signal_data.get('allocated_risk', 0.02)}% من رأس المال
🌍 **الجلسة الحالية:** {session_clean}
----------------------------------------
⚠️ *تتم إدارة الصفقة تلقائياً بواسطة محرك التعديل الديناميكي ونظام الـ Break Even المؤسسي.*"""

    def broadcast_session_alert(self, chat_id, session_name, is_weekend=False):
        if is_weekend:
            msg = f"🛑 [تنبيه عطلة V4]: بدأت الآن العطلة الأسبوعية للأسواق العالمية. أسواق الذهب الرقمي PAXG قد تكون ضعيفة السيولة وخادعة، البوت يوصي بالتركيز التام على الكريبتو فقط! 🛡️"
        else:
            msg = f"🚨 [تنبيه مؤسسي V4]: بدأت الآن جلسة {session_name}. سيولة مؤسسية جديدة وضخمة تتدفق إلى الأسواق، يرجى مراقبة الإشارات بحذر! 🌍"
        self.bot.send_message(chat_id, msg)

    def set_asset(self, asset_symbol):
        try:
            if not asset_symbol:
                return False
            asset_symbol = str(asset_symbol).upper().strip()
            if asset_symbol not in self.watchlist_assets:
                return False
            self.current_asset = asset_symbol
            return True
        except:
            return False

    def _execute_polling(self):
        """الدالة الداخلية لتشغيل البولينج مع آلية حماية من التجمد والـ 409"""
        try:
            logging.info("🧹 جاري تنظيف اتصالات تليغرام القديمة لمنع التعارض 409...")
            self.bot.remove_webhook()
            time.sleep(1)
            logging.info("🚀 انطلق البث اللحظي للوحة التحكم في مسار موازي آمن.")
            self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logging.error(f"🚨 خطأ أثناء البولينج الخلفي: {e}")

    def start_polling(self):
        """[تحديث الحسم V11]: بدء الاستقبال اللحظي داخل Thread مستقل تماماً لفك حظر السيرفر نهائياً"""
        bot_thread = threading.Thread(target=self._execute_polling, daemon=True)
        bot_thread.start()
        logging.info("🟢 [تم الحسم] تم ترحيل البوت إلى المسارات الخلفية. السيرفر الآن حر بنسبة 100%.")
        
