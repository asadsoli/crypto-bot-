# self_learning.py
# 👑 محرك التعلّم الذاتي والذاكرة الرقمية المطور - النسخة V4.2 الكبرى المحصنة 👑
# 🧠 عقل المنظومة الذكي: سحق فخاخ القسمة الصفرية وفصل حركي للأوزان متوافق مع لوحة تحكم القائد

import json
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SelfLearningEngineV1:
    def __init__(self, db_path="bot_memory.json"):
        self.db_path = db_path
        self.memory = self._load_memory()

    def _load_memory(self) -> dict:
        default_structure = {
            'trades_history': [],
            'performance_metrics': {'total_trades': 0, 'winrate': 0.0, 'wins': 0, 'losses': 0},
            'scalp_metrics': {'total_trades': 0, 'winrate': 0.0, 'wins': 0, 'losses': 0},
            'adaptive_weights': {'PAXG_weight': 1.0, 'BTC_weight': 1.0, 'Altcoins_weight': 1.0, 'risk_multiplier': 1.0},
            'scalp_weights': {'risk_multiplier': 1.0}
        }

        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, dict): return default_structure
                    if 'scalp_metrics' not in data: data['scalp_metrics'] = default_structure['scalp_metrics']
                    if 'scalp_weights' not in data: data['scalp_weights'] = default_structure['scalp_weights']
                    return data
            except Exception as e:
                logging.error(f"❌ خطأ في قراءة الذاكرة: {e}")
        
        return default_structure

    def _save_memory(self):
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"❌ خطأ في حفظ ذاكرة البوت: {e}")

    def update_trade_result(self, trade_data: dict, result: str):
        data = trade_data or {}
        history = self.memory.get('trades_history', [])
        
        trade_style = str(data.get('trade_style', ''))
        is_scalp = "SCALPING" in trade_style.upper() or bool(data.get('is_scalping_signal', False))

        trade_entry = {
            'pair': str(data.get('pair', 'UNKNOWN')).upper(),
            'type': str(data.get('type', 'BUY')), 
            'adjusted_score': float(data.get('adjusted_score') or data.get('quality_score', 0.0)),
            'session': str(data.get('session_context') or data.get('session', 'UNKNOWN')),
            'result': str(result), 
            'style': "SCALPING" if is_scalp else "SWING",
            'timestamp': data.get('timestamp')
        }
        history.append(trade_entry)

        pair = str(data.get('pair', '')).upper()
        weight_key = 'PAXG_weight' if 'PAXG' in pair or 'XAU' in pair else ('BTC_weight' if 'BTC' in pair else 'Altcoins_weight')

        if is_scalp:
            metrics = self.memory.get('scalp_metrics', {})
            weights = self.memory.get('scalp_weights', {})

            metrics['total_trades'] = int(metrics.get('total_trades', 0)) + 1
            if result == "Win":
                metrics['wins'] = int(metrics.get('wins', 0)) + 1
                self.memory['adaptive_weights'][weight_key] = min(float(self.memory['adaptive_weights'].get(weight_key, 1.0)) + 0.02, 1.5)
                if float(metrics.get('winrate', 0.0)) > 75:
                    weights['risk_multiplier'] = min(float(weights.get('risk_multiplier', 1.0)) + 0.05, 1.2)
            else:
                metrics['losses'] = int(metrics.get('losses', 0)) + 1
                self.memory['adaptive_weights'][weight_key] = max(float(self.memory['adaptive_weights'].get(weight_key, 1.0)) - 0.04, 0.5)
                weights['risk_multiplier'] = max(float(weights.get('risk_multiplier', 1.0)) - 0.08, 0.4)

            total = int(metrics.get('total_trades', 1))
            metrics['winrate'] = (int(metrics.get('wins', 0)) / total) * 100
            logging.info(f"🧠 [تعلم السكالبينج]: نسبة النجاح {metrics['winrate']:.1f}%. معامل مخاطرة: {weights.get('risk_multiplier', 1.0):.2f}")

        else:
            metrics = self.memory.get('performance_metrics', {})
            weights = self.memory.get('adaptive_weights', {})

            metrics['total_trades'] = int(metrics.get('total_trades', 0)) + 1
            if result == "Win":
                metrics['wins'] = int(metrics.get('wins', 0)) + 1
                weights[weight_key] = min(float(weights.get(weight_key, 1.0)) + 0.05, 1.5)
                if float(metrics.get('winrate', 0.0)) > 70:
                    weights['risk_multiplier'] = min(float(weights.get('risk_multiplier', 1.0)) + 0.1, 1.3)
            else:
                metrics['losses'] = int(metrics.get('losses', 0)) + 1
                weights[weight_key] = max(float(weights.get(weight_key, 1.0)) - 0.1, 0.5)
                weights['risk_multiplier'] = max(float(weights.get('risk_multiplier', 1.0)) - 0.15, 0.5)

            total = int(metrics.get('total_trades', 1))
            metrics['winrate'] = (int(metrics.get('wins', 0)) / total) * 100
            logging.info(f"🧠 [تعلم السوينغ]: نسبة النجاح {metrics['winrate']:.1f}%. معامل مخاطرة: {weights.get('risk_multiplier', 1.0):.2f}")

        self._save_memory()

    def get_adaptive_config(self, is_scalp: bool = None) -> dict:
        is_scalp = bool(is_scalp)
        if is_scalp:
            config = self.memory.get('adaptive_weights', {}).copy()
            config['risk_multiplier'] = self.memory.get('scalp_weights', {}).get('risk_multiplier', 1.0)
            return config
            
        return self.memory.get('adaptive_weights', {})
        
