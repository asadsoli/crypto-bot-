# InstitutionalRiskManagerV4.py
# ⚡ محرك إدارة المخاطر المؤسسية المطور بالكامل - النسخة V4.0 النخبوية ⚡
# 🛡️ الحارس الذكي: فصل كامل لمعايير صفقات السكالبينج (الخاطفة) عن السوينغ (الموجية بعيدة المدى)

import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalRiskManagerV3:
    def __init__(self, news_engine, self_learning_engine):
        # ربط إدارة المخاطر بمحرك الأخبار ونظام التعلم الذاتي
        self.news_engine = news_engine
        self.self_learning_engine = self_learning_engine
        
        # سجل داخلي لتتبع الصفقات المفتوحة حالياً لمنع التداخل
        self.active_trades = {}
        
        # إعدادات المخاطرة المؤسسية الافتراضية لكل صفقة من حجم الحساب
        self.risk_profiles = {
            'LOW': 0.01,       # 1% مخاطرة لكل صفقة
            'MEDIUM': 0.02,    # 2% مخاطرة لكل صفقة
            'HIGH': 0.03,      # 3% مخاطرة لكل صفقة
            'STRICT': 0.005    # 0.5% مخاطرة مؤسسية صارمة جداً
        }
        
        # الملف الافتراضي الحالي لإدارة المخاطر
        self.current_profile = 'STRICT'

        # 🔥 إضافات حماية المحفظة من نزيف التداولات المتتالية وقت الأخبار
        self.daily_loss_counter = 0
        self.last_loss_date = None
        self.max_daily_losses_allowed = 2  # حد الاستوبات المسموحة يومياً لصفقات السوينغ الافتراضية
        self.emergency_lock_until = None

    def set_risk_profile(self, profile_name: str):
        """تغيير نمط المخاطرة من لوحة التحكم (Low / Medium / High / Strict)"""
        if profile_name.upper() in self.risk_profiles:
            self.current_profile = profile_name.upper()
            logging.info(f"⚙️ تم تعديل نمط إدارة المخاطر إلى: {self.current_profile}")

    def can_open_trade(self, signal_data: dict, current_market_conditions: dict, is_on_demand_scan: bool = False) -> dict:
        """
        🛡️ الفحص النهائي الإجباري قبل تنفيذ أي صفقة.
        يتكيف ديناميكياً 100% بناءً على نوع الصفقة (سكالبينج خاطف أو سوينغ طويل الأمد).
        """
        pair = signal_data.get('pair', 'UNKNOWN').upper()
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')

        current_time = datetime.datetime.utcnow()

        # ⚡ فحص ما إذا كانت الإشارة القادمة من مسار السكالبينج
        is_scalping_signal = signal_data.get('is_scalping_signal', False)

        # 🔥 ميزة حماية المحفظة الرقمية التلقائية من التداولات المتتالية الهابطة
        if self.emergency_lock_until and current_time < self.emergency_lock_until:
            remaining_lock = self.emergency_lock_until - current_time
            return {
                'status': 'BLOCK', 
                'reason': f"❌ حظر المخاطر الصارم V4: النظام مقفل تلقائياً لحماية المحفظة بسبب ضرب الاستوبات المتتالية. متبقي: {remaining_lock.seconds // 3600} ساعة."
            }

        # 🛡️ إذا كان هذا مجرد "طلب فحص مخصص تحت الطلب من الرادار اليدوي"، يتم تجاوز فلاتر الحظر
        if is_on_demand_scan:
            logging.info(f"🔍 طلب فحص فوري مخصص تحت الطلب لزوج {pair}. تجاوز فلاتر الحظر التنفيذي.")
            return {'status': 'ALLOW', 'allocated_risk_percentage': 0.0, 'reason': "✔ فحص مخصص"}

        # 1. فلتر الثقة (Confidence Gate)
        confidence = signal_data.get('confidence_score', signal_data.get('base_confidence', 0.0))
        if confidence < 55.0:
            return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: نسبة الثقة {confidence}% أقل من حد الـ 55%"}
        elif 55.0 <= confidence < 70.0:
            logging.warning(f"⚠️ تنبيه المخاطر: نسبة الثقة {confidence}% في مرحلة المراقبة والحذر")
        
        # 2. فحص كثرة الصفقات المفتوحة وآلية التحرير التلقائي (Dynamic Auto-Healing)
        # تخصيص الحدود والأوقات برمجياً بناءً على النمط المفعل لمنع تجميد البوت
        if is_scalping_signal:
            max_holding_duration = datetime.timedelta(minutes=15) # صفقات السكالب سريعة جداً، تحرير خلال 15 دقيقة لو علقت
            max_concurrent_trades = 6                             # السماح بفتح حتى 6 صفقات سكالب سريعة ومتوازية
        else:
            max_holding_duration = datetime.timedelta(hours=4)    # صفقات السوينغ تحتاج مدة أطول لتتحرك (4 ساعات)
            max_concurrent_trades = 3                             # حد أقصى 3 صفقات متزامنة في السوينغ

        # فحص إجباري لتنظيف وتحرير الصفقات القديمة العالقة قبل اتخاذ القرار
        pairs_to_release = []
        for trade_pair, trade_info in self.active_trades.items():
            opened_at_str = trade_info.get('opened_at')
            if opened_at_str:
                opened_at = datetime.datetime.fromisoformat(opened_at_str)
                if current_time - opened_at > max_holding_duration:
                    pairs_to_release.append(trade_pair)

        # تحرير الأزواج العالقة ذاتياً دون الحاجة لإعادة تشغيل البوت أو حظر الرادار
        for trade_pair in pairs_to_release:
            logging.warning(f"🔄 إصلاح ذاتي آلي V4: تم رصد صفقة قديمة عالقة على زوج {trade_pair}. يتم التحرير برمجياً الآن...")
            if trade_pair in self.active_trades:
                del self.active_trades[trade_pair]

        if len(self.active_trades) >= max_concurrent_trades:
            return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: تم الوصول للحد الأقصى من الصفقات المتزامنة المسموحة لهذا النمط (حد أقصى {max_concurrent_trades})"}
        
        if pair in self.active_trades:
            return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: توجد صفقة مفتوحة بالفعل على زوج {pair}"}

        # 3. فحص حالة السوق العامة (Risk Regime) والظروف الجيوسياسية والأخبار الخطيرة
        news_analysis = current_market_conditions.get('news_analysis', {})
        if news_analysis.get('risk_regime') == 'Risk OFF':
            if pair != 'PAXGUSDT':
                return {'status': 'BLOCK', 'reason': "❌ حظر المخاطر: السوق في حالة Risk OFF (أخبار ماكرو أو جيوسياسية قوية)، يمنع التداول"}

        # 4. فلتر التوقيت للأحداث الاقتصادي (Event Timing Lock)
        event_time_epoch = current_market_conditions.get('next_event_epoch', 0)
        timing_status = self.news_engine.get_event_timing_status(event_time_epoch)
        if timing_status['action'] in ['STOP_TRADING', 'REDUCE_TRADING']:
            if timing_status['action'] == 'STOP_TRADING':
                return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: قفل زمني مفعل بسبب {timing_status['desc']}"}
            else:
                logging.info("⚠️ تقليص المخاطرة إجباريًا بسبب قرب حدث اقتصادي.")

        # 5. فلتر التقلب العشوائي (Volatility Filter)
        if current_market_conditions.get('is_market_choppy', False) and not is_scalping_signal:
            # السكالبينج يمكنه التداول في الأسواق العرضية الحركية السريعة، بينما السوينغ يمنع تماماً
            return {'status': 'BLOCK', 'reason': "❌ حظر المخاطر: السوق يتحرك بشكل عشوائي وبدون اتجاه واضح (Choppy Market)"}

        # 6. حساب إدارة المخاطرة الديناميكية وحجم العقد الموزون (Dynamic Risk Allocation)
        adaptive_weights = self.self_learning_engine.get_adaptive_config()
        learning_multiplier = adaptive_weights.get('risk_multiplier', 1.0)
        
        base_risk_percentage = self.risk_profiles[self.current_profile]
        final_risk_percentage = base_risk_percentage * learning_multiplier
        
        # ⚡ موازنة لوتات السكالبينج: تقليص حجم عقود السكالب بمقدار النصف لحماية تراكمية للمحفظة
        if is_scalping_signal:
            final_risk_percentage *= 0.5
        
        if timing_status['action'] == 'REDUCE_TRADING':
            final_risk_percentage *= 0.5

        return {
            'status': 'ALLOW',
            'reason': "✔ تمت الموافقة من إدارة المخاطر المؤسسية المحدثة V4",
            'allocated_risk_percentage': round(final_risk_percentage, 4),
            'pair': pair
        }

    def register_active_trade(self, pair: str, id: str, risk_amount: float, is_scalping: bool = False):
        """تسجيل الصفقة عند فتحها بنجاح لمنع التداخل وحفظ نوعها"""
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')
        self.active_trades[pair] = {
            'trade_id': id,
            'risk_allocated': risk_amount,
            'is_scalping': is_scalping,
            'opened_at': datetime.datetime.utcnow().isoformat()
        }
        logging.info(f"🔒 تم قفل زوج {pair} في سجل المخاطر. نمط سكالب: {is_scalping}")

    def remove_active_trade(self, pair: str, is_loss: bool = False):
        """إزالة الصفقة من السجل عند إغلاقها وتحديث عداد الخسائر الذكي التكيفي لـ V4"""
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')
        
        is_scalping_trade = False
        if pair in self.active_trades:
            is_scalping_trade = self.active_trades[pair].get('is_scalping', False)
            del self.active_trades[pair]
            logging.info(f"🔓 تم تحرير زوج {pair} وجاهز لاستقبال صفقات جديدة.")

        # 🔥 ميزة حماية V4 التكيفية: مراقبة وتفعيل عداد الخسائر اليومية المتتالية حسب نمط الصفقة
        if is_loss:
            today = datetime.date.today()
            if self.last_loss_date != today:
                self.daily_loss_counter = 0
                self.last_loss_date = today
            
            self.daily_loss_counter += 1
            logging.warning(f"🚨 تنبيه إدارة المخاطر: تم تسجيل صفقة خاسرة. إجمالي خسائر اليوم المتتالية: {self.daily_loss_counter}")
            
            # هندسة سقف الحظر: السكالبينج السريع يعطي مرونة حتى 4 استوبات، بينما السوينغ يقفل المحفظة عند 2
            allowed_losses = 4 if is_scalping_trade else self.max_daily_losses_allowed
            lock_duration_hours = 12 if is_scalping_trade else 24
            
            if self.daily_loss_counter >= allowed_losses:
                self.emergency_lock_until = datetime.datetime.utcnow() + datetime.timedelta(hours=lock_duration_hours)
                logging.error(f"🛑 تم تفعيل قفل الأمان الطارئ لـ V4! حظر التداول بالكامل لمدة {lock_duration_hours} ساعة حماية للمحفظة من تقلبات الجلسة.")
        else:
            # إذا ربحت الصفقة، يتم تصفير العداد فوراً لتأكيد استقرار بيئة التداول والسيولة
            self.daily_loss_counter = 0
        
