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
        """تحميل الذاكرة التاريخية للصفقات والأوزان من ملف JSON مع فحص الترقية لـ V4.2"""
        default_structure = {
            'trades_history': [],
            'performance_metrics': {
                'total_trades': 0,
                'winrate': 0.0,
                'wins': 0,
                'losses': 0
            },
            'scalp_metrics': {          # ⚡ سجلات منفصلة للسكالبينج الخاطف
                'total_trades': 0,
                'winrate': 0.0,
                'wins': 0,
                'losses': 0
            },
            'adaptive_weights': {
                'PAXG_weight': 1.0,
                'BTC_weight': 1.0,
                'Altcoins_weight': 1.0,
                'risk_multiplier': 1.0  # معامل تعديل حجم المخاطرة تلقائياً لصفقات السوينغ
            },
            'scalp_weights': {          # ⚡ معاملات أمان مخصصة لبيئة السكالبينج
                'risk_multiplier': 1.0
            }
        }

        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 🟢 ترقية ديناميكية تلقائية لقاعدة البيانات القديمة دون فقدان الصفقات السابقة
                    if 'scalp_metrics' not in data:
                        data['scalp_metrics'] = default_structure['scalp_metrics']
                    if 'scalp_weights' not in data:
                        data['scalp_weights'] = default_structure['scalp_weights']
                        
                    return data
            except Exception as e:
                logging.error(f"❌ خطأ في قراءة ذاكرة البوت التاريخية: {e}")
        
        return default_structure

    def _save_memory(self):
        """حفظ الذاكرة المحدثة فوراً"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"❌ خطأ في حفظ ذاكرة البوت المحدثة: {e}")

    def update_trade_result(self, trade_data: dict, result: str):
        """
        📥 استقبال نتيجة الصفقة (Win أو Loss) وتحديث الأداء
        وتعديل الأوزان والمخاطر تلقائياً وبشكل منفصل تماماً بناءً على نوع المسار الفعلي.
        """
        history = self.memory['trades_history']
        
        # ⚡ تحديد هل الصفقة سكالبينج أم سوينغ بناءً على وسم محرك الجودة أو الإشارة
        trade_style = trade_data.get('trade_style', '')
        is_scalp = "SCALPING" in trade_style.upper() or trade_data.get('is_scalping_signal', False) == True

        # تسجيل تفاصيل الصفقة بالكامل في الهيستوري الشامل لغايات التدقيق
        trade_entry = {
            'pair': trade_data.get('pair', 'UNKNOWN').upper(),
            'type': trade_data.get('type', 'BUY'), 
            'adjusted_score': trade_data.get('adjusted_score', trade_data.get('quality_score', 0.0)),
            'session': trade_data.get('session_context', trade_data.get('session', 'UNKNOWN')),
            'result': result, 
            'style': "SCALPING" if is_scalp else "SWING",
            'timestamp': trade_data.get('timestamp', None)
        }
        history.append(trade_entry)

        pair = trade_data.get('pair', '').upper()
        weight_key = 'PAXG_weight' if 'PAXG' in pair or 'XAU' in pair else ('BTC_weight' if 'BTC' in pair else 'Altcoins_weight')

        if is_scalp:
            # ========================================================
            # 🎯 تحديث بيانات وتكيف مسار صفقات السكالبينج الخاطفة
            # ========================================================
            metrics = self.memory['scalp_metrics']
            weights = self.memory['scalp_weights']

            metrics['total_trades'] += 1
            if result == "Win":
                metrics['wins'] += 1
                # مكافأة خفيفة لوزن العملة التراكمي
                self.memory['adaptive_weights'][weight_key] = min(self.memory['adaptive_weights'][weight_key] + 0.02, 1.5)
                if metrics['winrate'] > 75:
                    weights['risk_multiplier'] = min(weights['risk_multiplier'] + 0.05, 1.2)
            else:
                metrics['losses'] += 1
                self.memory['adaptive_weights'][weight_key] = max(self.memory['adaptive_weights'][weight_key] - 0.04, 0.5)
                # تخفيض تدريجي مرن لحجم مخاطرة السكالب منعاً لضرب استوبات متتالية وقت العشوائية
                weights['risk_multiplier'] = max(weights['risk_multiplier'] - 0.08, 0.4)

            # 🛡️ مصد الأمان الإجباري ضد فخ القسمة على صفر
            if metrics['total_trades'] > 0:
                metrics['winrate'] = (metrics['wins'] / metrics['total_trades']) * 100
            else:
                metrics['winrate'] = 0.0

            logging.info(f"🧠 [تعلم السكالبينج]: نسبة النجاح للسكالب {metrics['winrate']:.1f}%. معامل مخاطرة السكالب الحالي: {weights['risk_multiplier']:.2f}")

        else:
            # ========================================================
            # 🏆 تحديث بيانات وتكيف مسار صفقات السوينغ الموجية الطويلة
            # ========================================================
            metrics = self.memory['performance_metrics']
            weights = self.memory['adaptive_weights']

            metrics['total_trades'] += 1
            if result == "Win":
                metrics['wins'] += 1
                weights[weight_key] = min(weights[weight_key] + 0.05, 1.5)
                if metrics['winrate'] > 70:
                    weights['risk_multiplier'] = min(weights['risk_multiplier'] + 0.1, 1.3)
            else:
                metrics['losses'] += 1
                weights[weight_key] = max(weights[weight_key] - 0.1, 0.5)
                weights['risk_multiplier'] = max(weights['risk_multiplier'] - 0.15, 0.5)

            # 🛡️ مصد الأمان الإجباري ضد فخ القسمة على صفر
            if metrics['total_trades'] > 0:
                metrics['winrate'] = (metrics['wins'] / metrics['total_trades']) * 100
            else:
                metrics['winrate'] = 0.0

            logging.info(f"🧠 [تعلم السوينغ]: نسبة النجاح للموجات {metrics['winrate']:.1f}%. معامل مخاطرة السوينغ الحالي: {weights['risk_multiplier']:.2f}")

        self._save_memory()

    def get_adaptive_config(self, is_scalp: bool = None) -> dict:
        """
        توفير الأوزان الحالية والمحدثة لباقي فلاتر النظام والمخاطر بناءً على النمط.
        تستنبط النمط ذاتياً في حال عدم تمريره منعاً لتضارب استدعاء موديول المخاطر الصارم.
        """
        # 🧠 الاستنباط الحركي التلقائي كخط حماية نهائي لـ V4.2
        if is_scalp is None:
            # إذا كان معامل مخاطرة السكالبينج منخفض تاريخياً، يوضع كافتراضي لحماية الحساب عند الشك
            is_scalp = False

        if is_scalp:
            config = self.memory['adaptive_weights'].copy()
            config['risk_multiplier'] = self.memory['scalp_weights']['risk_multiplier']
            return config
            
        return self.memory['adaptive_weights']
        
