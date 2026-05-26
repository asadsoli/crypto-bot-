# InstitutionalRiskManagerV3.py
# ⚡ محرك إدارة المخاطر المؤسسية المطور بالكامل - النسخة V3 ⚡
# 🛡️ يحافظ على طبقات الأمان والشفاء الذاتي القديمة ويضيف: قفل الخسائر المتتالية، ودعم الرادار والخلفي

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

        # 🔥 إضافات ترقية V3 لحماية الحساب من نزيف التداولات المتتالية وقت الأخبار
        self.daily_loss_counter = 0
        self.last_loss_date = None
        self.max_daily_losses_allowed = 2  # حد الاستوبات المتتالية المسموحة يومياً
        self.emergency_lock_until = None

    def set_risk_profile(self, profile_name: str):
        """تغيير نمط المخاطرة من لوحة التحكم (Low / Medium / High / Strict)"""
        if profile_name.upper() in self.risk_profiles:
            self.current_profile = profile_name.upper()
            logging.info(f"⚙️ تم تعديل نمط إدارة المخاطر إلى: {self.current_profile}")

    def can_open_trade(self, signal_data: dict, current_market_conditions: dict, is_on_demand_scan: bool = False) -> dict:
        """
        🛡️ الفحص النهائي الإجباري قبل تنفيذ أي صفقة.
        يرجع إما موافقة بالدخول وحجم العقد أو حظر تام للصفقة (مع آلية الشفاء الذاتي للتعليق وقفل الخسائر المتتالية لـ V3).
        """
        pair = signal_data.get('pair', 'UNKNOWN').upper()
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')

        current_time = datetime.datetime.utcnow()

        # 🔥 ميزة V3: فحص القفل الرقمي لحماية المحفظة من التداولات المتتالية الهابطة
        if self.emergency_lock_until and current_time < self.emergency_lock_until:
            remaining_lock = self.emergency_lock_until - current_time
            return {
                'status': 'BLOCK', 
                'reason': f"❌ حظر المخاطر الصارم V3: النظام مقفل تلقائياً لحماية المحفظة بسبب تلقي {self.max_daily_losses_allowed} استوبات متتالية اليوم. متبقي: {remaining_lock.seconds // 3600} ساعة."
            }

        # 🛡️ ميزة V3: إذا كان هذا مجرد "طلب فحص مخصص تحت الطلب"، يتم تجاوز فلاتر الحظر التداولي
        if is_on_demand_scan:
            logging.info(f"🔍 طلب فحص فوري مخصص تحت الطلب لزوج {pair}. تجاوز فلاتر الحظر التنفيذي.")
            return {'status': 'ALLOW', 'allocated_risk_percentage': 0.0, 'reason': "✔ فحص مخصص"}

        # 1. فلتر الثقة (Confidence Gate)
        confidence = signal_data.get('confidence_score', 0.0)
        if confidence < 55.0:
            return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: نسبة الثقة {confidence}% أقل من حد الـ 55%"}
        elif 55.0 <= confidence < 70.0:
            logging.warning(f"⚠️ تنبيه المخاطر: نسبة الثقة {confidence}% في مرحلة المراقبة والحذر")
        
        # 2. فحص كثرة الصفقات المفتومة ومنع التداخل وآلية التحرير التلقائي (Auto-Healing المثبتة)
        max_holding_duration = datetime.timedelta(hours=4) # حد الأمان الزمني لتصفير الصفقات العالقة

        # فحص إجباري لتنظيف الصفقات القديمة العالقة قبل اتخاذ القرار
        pairs_to_release = []
        for trade_pair, trade_info in self.active_trades.items():
            opened_at_str = trade_info.get('opened_at')
            if opened_at_str:
                opened_at = datetime.datetime.fromisoformat(opened_at_str)
                if current_time - opened_at > max_holding_duration:
                    pairs_to_release.append(trade_pair)

        # تحرير الأزواج العالقة ذاتياً دون الحاجة لإعادة تشغيل البوت
        for trade_pair in pairs_to_release:
            logging.warning(f"🔄 إصلاح ذاتي آلي V3: تم رصد صفقة قديمة عالقة على زوج {trade_pair}. يتم التحرير برمجياً الآن...")
            del self.active_trades[trade_pair]

        if len(self.active_trades) >= 3:
            return {'status': 'BLOCK', 'reason': "❌ حظر المخاطر: تم الوصول للحد الأقصى من الصفقات المتزامنة (حد أقصى 3)"}
        
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
        if current_market_conditions.get('is_market_choppy', False):
            return {'status': 'BLOCK', 'reason': "❌ حظر المخاطر: السوق يتحرك بشكل عشوائي وبدون اتجاه واضح (Choppy Market)"}

        # 6. حساب إدارة المخاطرة الديناميكية (Dynamic Risk Management)
        adaptive_weights = self.self_learning_engine.get_adaptive_config()
        learning_multiplier = adaptive_weights.get('risk_multiplier', 1.0)
        
        base_risk_percentage = self.risk_profiles[self.current_profile]
        final_risk_percentage = base_risk_percentage * learning_multiplier
        
        if timing_status['action'] == 'REDUCE_TRADING':
            final_risk_percentage *= 0.5

        return {
            'status': 'ALLOW',
            'reason': "✔ تمت الموافقة من إدارة المخاطر المؤسسية V3",
            'allocated_risk_percentage': round(final_risk_percentage, 4),
            'pair': pair
        }

    def register_active_trade(self, pair: str, id: str, risk_amount: float):
        """تسجيل الصفقة عند فتحها بنجاح لمنع التداخل"""
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')
        self.active_trades[pair] = {
            'trade_id': id,
            'risk_allocated': risk_amount,
            'opened_at': datetime.datetime.utcnow().isoformat()
        }
        logging.info(f"🔒 تم قفل زوج {pair} في سجل المخاطر المفتوحة.")

    def remove_active_trade(self, pair: str, is_loss: bool = False):
        """إزالة الصفقة من السجل عند إغلاقها وتحديث عداد الخسائر لـ V3"""
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')
        if pair in self.active_trades:
            del self.active_trades[pair]
            logging.info(f"🔓 تم تحرير زوج {pair} وجاهز لاستقبال صفقات جديدة.")

        # 🔥 ميزة حماية V3: مراقبة وتفعيل عداد الخسائر اليومية المتتالية
        if is_loss:
            today = datetime.date.today()
            if self.last_loss_date != today:
                self.daily_loss_counter = 0
                self.last_loss_date = today
            
            self.daily_loss_counter += 1
            logging.warning(f"🚨 تنبيه إدارة المخاطر: تم تسجيل صفقة خاسرة. إجمالي خسائر اليوم المتتالية: {self.daily_loss_counter}")
            
            if self.daily_loss_counter >= self.max_daily_losses_allowed:
                self.emergency_lock_until = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                logging.error(f"🛑 تم تفعيل قفل الأمان الطارئ لـ V3! حظر التداول بالكامل لمدة 24 ساعة حماية للمحفظة.")
        else:
            # إذا ربحت الصفقة، يتم تصفير العداد لتأكيد استقرار السوق
            self.daily_loss_counter = 0
        
