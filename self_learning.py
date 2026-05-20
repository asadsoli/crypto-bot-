import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SelfLearningEngineV1:
    def __init__(self, db_path="bot_memory.json"):
        self.db_path = db_path
        self.memory = self._load_memory()

    def _load_memory(self) -> dict:
        """تحميل الذاكرة التاريخية للصفقات والأوزان من ملف JSON"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"خطأ في قراءة ذاكرة البوت: {e}")
        
        # البنية الافتراضية للتعلم الذاتي عند التشغيل لأول مرة
        return {
            'trades_history': [],
            'performance_metrics': {
                'total_trades': 0,
                'winrate': 0.0,
                'wins': 0,
                'losses': 0
            },
            'adaptive_weights': {
                'PAXG_weight': 1.0,
                'BTC_weight': 1.0,
                'Altcoins_weight': 1.0,
                'risk_multiplier': 1.0  # معامل تعديل حجم المخاطرة تلقائياً
            }
        }

    def _save_memory(self):
        """حفظ الذاكرة المحدثة فوراً"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"خطأ في حفظ ذاكرة البوت: {e}")

    def update_trade_result(self, trade_data: dict, result: str):
        """
        📥 استقبال نتيجة الصفقة (Win أو Loss) وتحديث الأداء
        وتعديل الأوزان والمخاطر تلقائياً بناءً على التجربة.
        """
        history = self.memory['trades_history']
        metrics = self.memory['performance_metrics']
        weights = self.memory['adaptive_weights']

        # تسجيل تفاصيل الصفقة بالكامل
        trade_entry = {
            'pair': trade_data.get('pair'),
            'type': trade_data.get('type'), # BUY or SELL
            'adjusted_score': trade_data.get('adjusted_score', 0),
            'session': trade_data.get('session_context'),
            'result': result, # Win / Loss
            'timestamp': trade_data.get('timestamp')
        }
        history.append(trade_entry)

        # تحديث الحسابات الرقمية
        metrics['total_trades'] += 1
        if result == "Win":
            metrics['wins'] += 1
        else:
            metrics['losses'] += 1

        metrics['winrate'] = (metrics['wins'] / metrics['total_trades']) * 100

        # محرك التكيف الذاتي (Adaptive Mechanism)
        pair = trade_data.get('pair', '')
        weight_key = 'PAXG_weight' if 'PAXG' in pair else ('BTC_weight' if 'BTC' in pair else 'Altcoins_weight')

        if result == "Win":
            # إذا ربحت الصفقة، نكافئ هذا النوع من العملات برفع وزنه تدريجياً لزيادة التركيز عليه
            weights[weight_key] = min(weights[weight_key] + 0.05, 1.5)
            # رفع جرأة التداول تدريجياً لأن السوق متوافق مع الاستراتيجية
            if metrics['winrate'] > 70:
                weights['risk_multiplier'] = min(weights['risk_multiplier'] + 0.1, 1.3)
        else:
            # إذا خسرت الصفقة، يتم معاقبة هذا الوزن لتقليص دخوله مستقبلاً لحين تغير ظروف السوق
            weights[weight_key] = max(weights[weight_key] - 0.1, 0.5)
            # تقليص وإخماد حجم المخاطرة فوراً عند رصد خسائر متتالية لحماية الحساب
            weights['risk_multiplier'] = max(weights['risk_multiplier'] - 0.15, 0.5)

        logging.info(f"🧠 تحديث نظام التعلم الذاتي: نسبة النجاح الحالية {metrics['winrate']:.1f}%. معامل المخاطرة الجديد: {weights['risk_multiplier']:.2f}")
        self._save_memory()

    def get_adaptive_config(self) -> dict:
        """توفير الأوزان الحالية والمحدثة لباقي فلاتر النظام والمخاطر"""
        return self.memory['adaptive_weights']
      
