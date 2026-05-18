from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class FVGSignal:
    """Fair Value Gap Signal"""
    signal_type: str
    zone_low: float
    zone_high: float
    entry: float
    confidence: float
    reason: str
    candle_index: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.signal_type,
            "zone_low": self.zone_low,
            "zone_high": self.zone_high,
            "entry": self.entry,
            "confidence": self.confidence,
            "reason": self.reason,
            "candle_index": self.candle_index
        }


class FVGEngine:
    """
    Fair Value Gap (FVG) Analysis Engine
    يحلل الفجوات السعرية في الشموع اليابانية
    """
    
    MIN_CANDLES = 3  # الحد الأدنى من الشموع المطلوبة
    MIN_CONFIDENCE = 50  # الحد الأدنى من الثقة
    
    def __init__(self, min_gap_percent: float = 0.1):
        """
        Args:
            min_gap_percent: النسبة المئوية الدنيا للفجوة (0.1 = 0.1%)
        """
        self.min_gap_percent = min_gap_percent
    
    def _validate_candle(self, candle: Dict) -> bool:
        """التحقق من صحة الشمعة"""
        required_keys = {"open", "high", "low", "close"}
        if not isinstance(candle, dict):
            return False
        
        if not required_keys.issubset(candle.keys()):
            return False
        
        # التحقق من أن الأسعار منطقية
        try:
            high = float(candle["high"])
            low = float(candle["low"])
            open_price = float(candle["open"])
            close = float(candle["close"])
            
            if high < low or high < open_price or high < close:
                return False
            if low > open_price or low > close:
                return False
                
            return True
        except (ValueError, TypeError):
            return False
    
    def _calculate_confidence(
        self, 
        gap_size: float, 
        zone_range: float,
        volume_ratio: Optional[float] = None
    ) -> float:
        """
        حساب مستوى الثقة بناءً على حجم الفجوة
        
        Args:
            gap_size: حجم الفجوة
            zone_range: نطاق المنطقة
            volume_ratio: نسبة الحجم (اختياري)
        
        Returns:
            مستوى الثقة (0-100)
        """
        gap_ratio = gap_size / zone_range if zone_range > 0 else 0
        
        # النسبة الأساسية من الفجوة
        confidence = min(gap_ratio * 1000, 95)  # أقصى 95%
        
        # إضافة تأثير نسبة الحجم إن وجدت
        if volume_ratio and volume_ratio > 1:
            confidence = min(confidence + (volume_ratio * 5), 99)
        
        return max(confidence, self.MIN_CONFIDENCE)
    
    def _detect_bullish_fvg(
        self, 
        c1: Dict, 
        c3: Dict, 
        index: int
    ) -> Optional[FVGSignal]:
        """
        اكتشاف فجوة صعودية (bullish)
        c1 (low) < c3 (high) لا يوجد تداخل
        """
        c1_high = float(c1["high"])
        c3_low = float(c3["low"])
        
        if c1_high < c3_low:
            gap_size = c3_low - c1_high
            zone_range = c3_low - c1_high
            
            # تطبيق مرشح النسبة المئوية الدنيا للفجوة
            avg_price = (c1_high + c3_low) / 2
            gap_percent = (gap_size / avg_price * 100) if avg_price > 0 else 0
            
            if gap_percent >= self.min_gap_percent:
                confidence = self._calculate_confidence(gap_size, zone_range)
                
                return FVGSignal(
                    signal_type="BULLISH_FVG",
                    zone_low=c1_high,
                    zone_high=c3_low,
                    entry=(c1_high + c3_low) / 2,
                    confidence=confidence,
                    reason=f"Bullish imbalance detected ({gap_percent:.2f}%)",
                    candle_index=index
                )
        
        return None
    
    def _detect_bearish_fvg(
        self, 
        c1: Dict, 
        c3: Dict, 
        index: int
    ) -> Optional[FVGSignal]:
        """
        اكتشاف فجوة هابطة (bearish)
        c1 (low) > c3 (high) لا يوجد تداخل
        """
        c1_low = float(c1["low"])
        c3_high = float(c3["high"])
        
        if c1_low > c3_high:
            gap_size = c1_low - c3_high
            zone_range = c1_low - c3_high
            
            # تطبيق مرشح النسبة المئوية الدنيا للفجوة
            avg_price = (c1_low + c3_high) / 2
            gap_percent = (gap_size / avg_price * 100) if avg_price > 0 else 0
            
            if gap_percent >= self.min_gap_percent:
                confidence = self._calculate_confidence(gap_size, zone_range)
                
                return FVGSignal(
                    signal_type="BEARISH_FVG",
                    zone_low=c3_high,
                    zone_high=c1_low,
                    entry=(c1_low + c3_high) / 2,
                    confidence=confidence,
                    reason=f"Bearish imbalance detected ({gap_percent:.2f}%)",
                    candle_index=index
                )
        
        return None
    
    def analyze(self, candles: List[Dict]) -> Dict[str, Any]:
        """
        تحليل الفجوات العادلة (FVG) في سلسلة من الشموع
        
        Args:
            candles: قائمة الشموع بصيغة {"open", "high", "low", "close"}
        
        Returns:
            قاموس يحتوي على الإشارة والبيانات المرتبطة بها
        """
        # التحقق من صحة البيانات الأساسية
        if not candles or len(candles) < self.MIN_CANDLES:
            return {
                "signal": "NO_FVG",
                "reason": f"Not enough data. Minimum {self.MIN_CANDLES} candles required",
                "confidence": 0
            }
        
        # التحقق من صحة جميع الشموع
        valid_candles = [c for c in candles if self._validate_candle(c)]
        
        if len(valid_candles) < self.MIN_CANDLES:
            return {
                "signal": "NO_FVG",
                "reason": f"Invalid candle data. Found {len(valid_candles)} valid candles",
                "confidence": 0
            }
        
        all_signals = []
        
        # تحليل كل ثلاث شموع متتالية
        for i in range(1, len(valid_candles) - 1):
            c1 = valid_candles[i - 1]
            c3 = valid_candles[i + 1]
            
            try:
                # اكتشاف الفجوات الصعودية
                bullish = self._detect_bullish_fvg(c1, c3, i)
                if bullish and bullish.confidence >= self.MIN_CONFIDENCE:
                    all_signals.append(bullish)
                
                # اكتشاف الفجوات الهابطة
                bearish = self._detect_bearish_fvg(c1, c3, i)
                if bearish and bearish.confidence >= self.MIN_CONFIDENCE:
                    all_signals.append(bearish)
            
            except (ValueError, TypeError, KeyError) as e:
                # تجاهل الأخطاء في الشمعة المحددة والمتابعة
                continue
        
        # إذا تم اكتشاف إشارات
        if all_signals:
            # ترتيب الإشارات حسب الثقة (الأعلى أولاً)
            all_signals.sort(key=lambda x: x.confidence, reverse=True)
            
            # إرجاع أقوى إشارة
            best_signal = all_signals[0]
            result = best_signal.to_dict()
            result["signal"] = best_signal.signal_type
            result["total_signals_found"] = len(all_signals)
            
            return result
        
        # لم يتم اكتشاف فجوات
        return {
            "signal": "NO_FVG",
            "confidence": 0,
            "reason": "No imbalance found matching the criteria"
        }
    
    def analyze_multiple(self, candles: List[Dict]) -> List[Dict[str, Any]]:
        """
        إرجاع جميع الفجوات المكتشفة بدلاً من الأقوى فقط
        
        Returns:
            قائمة بجميع الإشارات المكتشفة مرتبة حسب الثقة
        """
        if not candles or len(candles) < self.MIN_CANDLES:
            return []
        
        valid_candles = [c for c in candles if self._validate_candle(c)]
        
        if len(valid_candles) < self.MIN_CANDLES:
            return []
        
        all_signals = []
        
        for i in range(1, len(valid_candles) - 1):
            c1 = valid_candles[i - 1]
            c3 = valid_candles[i + 1]
            
            try:
                bullish = self._detect_bullish_fvg(c1, c3, i)
                if bullish and bullish.confidence >= self.MIN_CONFIDENCE:
                    all_signals.append(bullish.to_dict())
                
                bearish = self._detect_bearish_fvg(c1, c3, i)
                if bearish and bearish.confidence >= self.MIN_CONFIDENCE:
                    all_signals.append(bearish.to_dict())
            
            except (ValueError, TypeError, KeyError):
                continue
        
        # ترتيب حسب الثقة والفهرس
        all_signals.sort(
            key=lambda x: (x["confidence"], -x["candle_index"]), 
            reverse=True
        )
        
        return all_signals
