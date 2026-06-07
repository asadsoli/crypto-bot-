# risk_manager.py
# ⚡ محرك إدارة المخاطر المؤسسية المطور بالكامل - النسخة V4.1 النخبوية المحصنة ⚡
# 🛡️ سحق فخ قفل حساب القائد وضبط استنباط صفقات السكالبينج ديناميكياً لتفادي جمود الـ 24 ساعة

import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstitutionalRiskManagerV4:
    def __init__(self, news_engine, self_learning_engine):
        self.news_engine = news_engine
        self.self_learning_engine = self_learning_engine
        self.active_trades = {}
        
        self.risk_profiles = {
            'LOW': 0.01,
            'MEDIUM': 0.02,
            'HIGH': 0.03,
            'STRICT': 0.005
        }
        
        self.current_profile = 'STRICT'
        self.daily_loss_counter = 0
        self.last_loss_date = None
        self.max_daily_losses_allowed = 2
        self.emergency_lock_until = None

    def set_risk_profile(self, profile_name: str):
        if str(profile_name).upper() in self.risk_profiles:
            self.current_profile = str(profile_name).upper()
            logging.info(f"⚙️ تم تعديل نمط إدارة المخاطر إلى: {self.current_profile}")

    def can_open_trade(self, signal_data: dict, current_market_conditions: dict, is_on_demand_scan: bool = False) -> dict:
        data = signal_data or {}
        conditions = current_market_conditions or {}
        
        pair = str(data.get('pair', 'UNKNOWN')).upper()
        if 'XAU' in pair:
            pair = pair.replace('XAU', 'PAXG')

        current_time = datetime.datetime.utcnow()

        # استنباط نمط السكالبينج مع حماية من None
        is_scalping_signal = bool(data.get('is_scalping_signal', False))

        if self.emergency_lock_until and current_time < self.emergency_lock_until:
            remaining_lock = self.emergency_lock_until - current_time
            return {
                'status': 'BLOCK', 
                'reason': f"❌ حظر المخاطر الصارم V4.1: النظام مقفل. متبقي: {remaining_lock.seconds // 3600} ساعة."
            }

        if is_on_demand_scan:
            return {'status': 'ALLOW', 'allocated_risk_percentage': 0.0, 'reason': "✔ فحص مخصص"}

        confidence = float(data.get('confidence_score') or data.get('base_confidence') or 0.0)
        if confidence < 55.0:
            return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: نسبة الثقة {confidence}% أقل من حد الـ 55%"}
        
        # تحرير الصفقات القديمة بذكاء
        max_holding_duration = datetime.timedelta(minutes=5) if is_scalping_signal else datetime.timedelta(hours=2)
        max_concurrent_trades = 6 if is_scalping_signal else 4
        
        pairs_to_release = []
        for trade_pair, trade_info in self.active_trades.items():
            opened_at_str = trade_info.get('opened_at')
            if opened_at_str:
                try:
                    opened_at = datetime.datetime.fromisoformat(opened_at_str)
                    if current_time - opened_at > max_holding_duration:
                        pairs_to_release.append(trade_pair)
                except:
                    pairs_to_release.append(trade_pair)

        for trade_pair in pairs_to_release:
            if trade_pair in self.active_trades:
                del self.active_trades[trade_pair]

        if len(self.active_trades) >= max_concurrent_trades:
            return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: تم الوصول للحد الأقصى ({max_concurrent_trades})"}
        
        if pair in self.active_trades:
            return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: توجد صفقة مفتوحة بالفعل لزوج {pair}"}

        # فحص الأخبار مع حماية من None
        news_analysis = conditions.get('news_analysis') or {}
        if news_analysis.get('risk_regime') == 'Risk OFF':
            if pair != 'PAXGUSDT':
                return {'status': 'BLOCK', 'reason': "❌ حظر المخاطر: السوق في حالة Risk OFF"}

        # فحص التوقيت
        action_status = 'ALLOW'
        action_desc = "طبيعي"
        if self.news_engine:
            try:
                event_time_epoch = float(conditions.get('next_event_epoch', 0))
                timing_status = self.news_engine.get_event_timing_status(event_time_epoch) or {}
                action_status = timing_status.get('action', 'ALLOW')
                action_desc = timing_status.get('desc', 'طبيعي')
            except: pass
                
        if action_status == 'STOP_TRADING':
            return {'status': 'BLOCK', 'reason': f"❌ حظر المخاطر: قفل زمني مفعل بسبب {action_desc}"}

        # حساب المخاطرة الديناميكي
        learning_multiplier = 1.0
        if self.self_learning_engine:
            try:
                adaptive_weights = self.self_learning_engine.get_adaptive_config(is_scalping=is_scalping_signal) or {}
                learning_multiplier = float(adaptive_weights.get('risk_multiplier', 1.0))
            except:
                learning_multiplier = 1.0
        
        base_risk_percentage = self.risk_profiles.get(self.current_profile, 0.005)
        final_risk_percentage = base_risk_percentage * learning_multiplier
        
        if is_scalping_signal: final_risk_percentage *= 0.5
        if action_status == 'REDUCE_TRADING': final_risk_percentage *= 0.5

        return {
            'status': 'ALLOW',
            'reason': "✔ تمت الموافقة من إدارة المخاطر المؤسسية المحدثة V4.1",
            'allocated_risk_percentage': round(float(final_risk_percentage), 4),
            'pair': pair
        }

    def register_active_trade(self, pair: str, id: str, risk_amount: float, is_scalping: bool = None):
        pair_upper = str(pair).upper()
        if 'XAU' in pair_upper:
            pair_upper = pair_upper.replace('XAU', 'PAXG')
            
        if is_scalping is None:
            base_risk = self.risk_profiles.get(self.current_profile, 0.005)
            is_scalping = True if risk_amount < base_risk else False

        self.active_trades[pair_upper] = {
            'trade_id': str(id),
            'risk_allocated': float(risk_amount),
            'is_scalping': bool(is_scalping),
            'opened_at': datetime.datetime.utcnow().isoformat()
        }
        logging.info(f"🔒 [Risk Verification] تم قفل زوج {pair_upper} في السجل.")

    def remove_active_trade(self, pair: str, is_loss: bool = False):
        pair_upper = str(pair).upper()
        if 'XAU' in pair_upper:
            pair_upper = pair_upper.replace('XAU', 'PAXG')
        
        is_scalping_trade = False
        if pair_upper in self.active_trades:
            is_scalping_trade = bool(self.active_trades[pair_upper].get('is_scalping', False))
            del self.active_trades[pair_upper]
            logging.info(f"🔓 تم تحرير زوج {pair_upper}.")

        if is_loss:
            today = datetime.date.today()
            if self.last_loss_date != today:
                self.daily_loss_counter = 0
                self.last_loss_date = today
            
            self.daily_loss_counter += 1
            allowed_losses = 4 if is_scalping_trade else self.max_daily_losses_allowed
            lock_duration_hours = 12 if is_scalping_trade else 24
            
            if self.daily_loss_counter >= allowed_losses:
                self.emergency_lock_until = datetime.datetime.utcnow() + datetime.timedelta(hours=lock_duration_hours)
                logging.error(f"🛑 تم تفعيل قفل الأمان الطارئ لـ V4.1 لمدة {lock_duration_hours} ساعة.")
        else:
            self.daily_loss_counter = 0
    
