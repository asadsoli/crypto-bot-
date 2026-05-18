from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging


@dataclass
class SwingPoint:
    """تمثيل نقطة تأرجح في السعر"""
    price: float
    timestamp: Optional[Any] = None
    index: Optional[int] = None


@dataclass
class LiquidityZone:
    """تمثيل منطقة السيولة"""
    type: str
    zone: float
    strength: str
    reason: str
    proximity: Optional[float] = None


@dataclass
class SweepSignal:
    """تمثيل إشارة الاختراق"""
    signal_hint: str
    type: Optional[str] = None
    swept_level: Optional[float] = None
    reason: str = ""


@dataclass
class AnalysisResult:
    """نتيجة التحليل الكاملة"""
    signal_hint: str
    zones: List[LiquidityZone] = field(default_factory=list)
    sweep: Optional[SweepSignal] = None
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class LiquidityEngine:
    """
    محرك الكشف عن السيولة في الأسواق المالية
    
    يقوم بـ:
    - كشف مناطق السيولة من نقاط التأرجح
    - اكتشاف اختراقات السيولة (Sweeps)
    - تحليل شامل للسوق
    """

    def __init__(
        self,
        debug: bool = False,
        liquidity_threshold: float = 0.0005,
        max_swing_history: int = 10,
        logger: Optional[logging.Logger] = None
    ):
        """
        تهيئة محرك السيولة
        
        Args:
            debug: تفعيل وضع التصحيح
            liquidity_threshold: حد الفارق النسبي لاعتبار السعرين متطابقين
            max_swing_history: عدد نقاط التأرجح المحفوظة
            logger: مسجل أحداث مخصص
        """
        self.recent_swing_highs: List[Dict[str, Any]] = []
        self.recent_swing_lows: List[Dict[str, Any]] = []
        self.debug = debug
        self.liquidity_threshold = liquidity_threshold
        self.max_swing_history = max_swing_history
        self.logger = logger or self._setup_logger()
        
        # السجل المخزن مؤقتاً للتحليل الأخير
        self.last_analysis: Optional[AnalysisResult] = None
        
        # إحصائيات الأداء
        self.analysis_count = 0
        self.sweep_detections = 0

    def _setup_logger(self) -> logging.Logger:
        """إعداد مسجل الأحداث"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _validate_candle(self, candle: Dict[str, Any]) -> bool:
        """
        التحقق من صحة بيانات الشمعة
        
        Args:
            candle: بيانات الشمعة
            
        Returns:
            True إذا كانت البيانات صحيحة
        """
        required_fields = {"open", "high", "low", "close"}
        if not all(field in candle for field in required_fields):
            return False
        
        # التحقق من القيم
        try:
            high = float(candle["high"])
            low = float(candle["low"])
            close = float(candle["close"])
            open_ = float(candle["open"])
            
            # يجب أن يكون high >= low
            if not (high >= low > 0 and open_ > 0 and close > 0):
                return False
            
            return True
        except (ValueError, TypeError):
            return False

    def _validate_swing(self, swing: Dict[str, Any]) -> bool:
        """
        التحقق من صحة نقطة التأرجح
        
        Args:
            swing: بيانات نقطة التأرجح
            
        Returns:
            True إذا كانت البيانات صحيحة
        """
        if not isinstance(swing, dict) or "price" not in swing:
            return False
        
        try:
            price = float(swing["price"])
            return price > 0
        except (ValueError, TypeError):
            return False

    # =========================
    # 📊 تحديث نقاط التأرجح
    # =========================

    def update_swings(
        self,
        swing_highs: Optional[List[Dict[str, Any]]] = None,
        swing_lows: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        تحديث نقاط التأرجح العليا والدنيا
        
        Args:
            swing_highs: قائمة نقاط التأرجح العليا
            swing_lows: قائمة نقاط التأرجح الدنيا
        """
        # تصفية البيانات غير الصحيحة
        valid_highs = [s for s in (swing_highs or []) if self._validate_swing(s)]
        valid_lows = [s for s in (swing_lows or []) if self._validate_swing(s)]
        
        self.recent_swing_highs = valid_highs[-self.max_swing_history:]
        self.recent_swing_lows = valid_lows[-self.max_swing_history:]

        if self.debug:
            self.logger.debug(f"📊 تم تحديث التأرجحات")
            self.logger.debug(f"🔼 نقاط عليا: {len(self.recent_swing_highs)}")
            self.logger.debug(f"🔽 نقاط دنيا: {len(self.recent_swing_lows)}")

    # =========================
    # 💧 كشف مناطق السيولة
    # =========================

    def detect_liquidity_zones(self) -> List[LiquidityZone]:
        """
        كشف مناطق السيولة من نقاط التأرجح المتشابهة
        
        Returns:
            قائمة مناطق السيولة المكتشفة
        """
        liquidity_zones: List[LiquidityZone] = []

        # فحص النقاط العليا المتشابهة
        for i in range(1, len(self.recent_swing_highs)):
            prev = self.recent_swing_highs[i - 1]
            curr = self.recent_swing_highs[i]

            prev_price = float(prev["price"])
            curr_price = float(curr["price"])
            
            price_diff = abs(curr_price - prev_price)
            threshold = self.liquidity_threshold * curr_price

            if price_diff <= threshold:
                proximity = (price_diff / threshold) * 100 if threshold > 0 else 0
                
                zone = LiquidityZone(
                    type="BUY_SIDE_LIQUIDITY",
                    zone=curr_price,
                    strength="HIGH",
                    reason="مناطق متساوية من السيولة العليا",
                    proximity=proximity
                )
                liquidity_zones.append(zone)

        # فحص النقاط الدنيا المتشابهة
        for i in range(1, len(self.recent_swing_lows)):
            prev = self.recent_swing_lows[i - 1]
            curr = self.recent_swing_lows[i]

            prev_price = float(prev["price"])
            curr_price = float(curr["price"])
            
            price_diff = abs(curr_price - prev_price)
            threshold = self.liquidity_threshold * curr_price

            if price_diff <= threshold:
                proximity = (price_diff / threshold) * 100 if threshold > 0 else 0
                
                zone = LiquidityZone(
                    type="SELL_SIDE_LIQUIDITY",
                    zone=curr_price,
                    strength="HIGH",
                    reason="مناطق متساوية من السيولة الدنيا",
                    proximity=proximity
                )
                liquidity_zones.append(zone)

        if self.debug:
            self.logger.debug(f"📍 تم العثور على {len(liquidity_zones)} منطقة سيولة")

        return liquidity_zones

    # =========================
    # 🔥 كشف الاختراقات
    # =========================

    def detect_sweep(self, candles: Optional[List[Dict[str, Any]]]) -> SweepSignal:
        """
        كشف اختراقات السيولة (حيث يتم الضغط على أوامر الوقف)
        
        Args:
            candles: قائمة بيانات الشموع
            
        Returns:
            إشارة الاختراق المكتشفة
        """
        if not candles:
            return SweepSignal(
                signal_hint="NO_DATA",
                reason="لا توجد بيانات شموع"
            )

        # التحقق من صحة الشمعة الأخيرة
        last = candles[-1]
        if not self._validate_candle(last):
            return SweepSignal(
                signal_hint="INVALID_DATA",
                reason="بيانات الشمعة الأخيرة غير صحيحة"
            )

        last_close = float(last["close"])
        last_high = float(last["high"])
        last_low = float(last["low"])

        # فحص الاختراقات العليا
        for swing in self.recent_swing_highs:
            swing_price = float(swing["price"])
            
            if last_high > swing_price and last_close < swing_price:
                signal = SweepSignal(
                    signal_hint="WAIT_SELL_CONFIRMATION",
                    type="BUY_SIDE_SWEEP",
                    swept_level=swing_price,
                    reason="تم سحب السيولة فوق النقاط العليا"
                )

                if self.debug:
                    self.logger.debug(f"⚡ تم كشف اختراق: {signal}")

                self.sweep_detections += 1
                return signal

        # فحص الاختراقات الدنيا
        for swing in self.recent_swing_lows:
            swing_price = float(swing["price"])
            
            if last_low < swing_price and last_close > swing_price:
                signal = SweepSignal(
                    signal_hint="WAIT_BUY_CONFIRMATION",
                    type="SELL_SIDE_SWEEP",
                    swept_level=swing_price,
                    reason="تم سحب السيولة تحت النقاط الدنيا"
                )

                if self.debug:
                    self.logger.debug(f"⚡ تم كشف اختراق: {signal}")

                self.sweep_detections += 1
                return signal

        return SweepSignal(
            signal_hint="NO_SWEEP",
            reason="لم يتم كشف اختراقات سيولة"
        )

    # =========================
    # 🧠 التحليل الرئيسي
    # =========================

    def analyze(
        self,
        candles: Optional[List[Dict[str, Any]]] = None,
        swing_highs: Optional[List[Dict[str, Any]]] = None,
        swing_lows: Optional[List[Dict[str, Any]]] = None
    ) -> AnalysisResult:
        """
        تحليل شامل للسوق والسيولة
        
        Args:
            candles: قائمة بيانات الشموع
            swing_highs: نقاط التأرجح العليا
            swing_lows: نقاط التأرجح الدنيا
            
        Returns:
            نتيجة التحليل الكاملة
        """
        self.analysis_count += 1

        # تحديث نقاط التأرجح إذا تم توفيرها
        if swing_highs or swing_lows:
            self.update_swings(swing_highs, swing_lows)

        # كشف السيولة والاختراقات
        liquidity_zones = self.detect_liquidity_zones()
        sweep = self.detect_sweep(candles)

        # =========================
        # محرك اتخاذ القرار
        # =========================

        if sweep.signal_hint in ["WAIT_BUY_CONFIRMATION", "WAIT_SELL_CONFIRMATION"]:
            result = AnalysisResult(
                signal_hint="WAIT_SWEEP",
                sweep=sweep,
                zones=liquidity_zones,
                reason=sweep.reason,
                metadata={
                    "sweep_type": sweep.type,
                    "swept_level": sweep.swept_level
                }
            )

        elif liquidity_zones:
            result = AnalysisResult(
                signal_hint="LIQUIDITY_PRESENT",
                zones=liquidity_zones,
                reason="تم كشف مناطق سيولة",
                metadata={
                    "zone_count": len(liquidity_zones),
                    "avg_proximity": sum(z.proximity for z in liquidity_zones if z.proximity) / len(liquidity_zones) if liquidity_zones else 0
                }
            )

        else:
            result = AnalysisResult(
                signal_hint="NO_LIQUIDITY",
                zones=[],
                reason="لم يتم كشف مناطق سيولة ذات معنى",
                metadata={}
            )

        # تخزين النتيجة مؤقتاً
        self.last_analysis = result

        if self.debug:
            self.logger.debug(f"💧 نتيجة السيولة: {result}")

        return result

    # =========================
    # 🔥 دعم الماسح الضوئي
    # =========================

    def get_last(self) -> Optional[AnalysisResult]:
        """
        الحصول على آخر تحليل بدون إعادة الحساب
        
        مفيد للماسح الضوئي للحصول على النتائج المخزنة مؤقتاً
        
        Returns:
            نتيجة التحليل الأخيرة أو None إذا لم يتم إجراء تحليل بعد
        """
        return self.last_analysis

    def clear_cache(self) -> None:
        """مسح السجل المخزن مؤقتاً"""
        self.last_analysis = None
        if self.debug:
            self.logger.debug("🧹 تم مسح السجل المخزن مؤقتاً")

    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات محرك السيولة
        
        Returns:
            قاموس بالإحصائيات
        """
        return {
            "total_analyses": self.analysis_count,
            "total_sweeps_detected": self.sweep_detections,
            "current_swing_highs": len(self.recent_swing_highs),
            "current_swing_lows": len(self.recent_swing_lows),
            "liquidity_threshold": self.liquidity_threshold
        }

    def reset(self) -> None:
        """إعادة تعيين محرك السيولة إلى الحالة الأولية"""
        self.recent_swing_highs = []
        self.recent_swing_lows = []
        self.last_analysis = None
        self.analysis_count = 0
        self.sweep_detections = 0
        
        if self.debug:
            self.logger.debug("🔄 تم إعادة تعيين محرك السيولة")
