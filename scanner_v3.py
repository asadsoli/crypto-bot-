import time
import threading
import logging
from typing import Dict, List, Optional, Any

# إعداد نظام التسجيل
logger = logging.getLogger(__name__)


class ScannerV3:
    """
    ماسح التحليلات الفائق V3 لتحليل الأصول المشفرة
    يوفر مراقبة مستمرة للإشارات التجارية عبر Telegram
    """

    def __init__(
        self,
        signal_engine,
        telegram_layer,
        chat_id: str,
        scan_assets: Optional[List[str]] = None,
        cooldown: int = 300,
        confidence_threshold: int = 75,
        scan_interval: int = 60
    ):
        """
        تهيئة الماسح
        
        Args:
            signal_engine: محرك تحليل الإشارات
            telegram_layer: طبقة التواصل مع Telegram
            chat_id: معرّف الدردشة لإرسال الرسائل
            scan_assets: قائمة الأصول المراد مسحها
            cooldown: وقت الانتظار بين الإشارات (ثانية)
            confidence_threshold: حد الثقة الأدنى (%)
            scan_interval: فترة المسح (ثانية)
        """
        self.signal_engine = signal_engine
        self.telegram = telegram_layer
        self.chat_id = chat_id

        # التحقق من المدخلات الأساسية
        if not self.signal_engine:
            raise ValueError("❌ Signal Engine مطلوب")
        if not self.telegram:
            raise ValueError("❌ Telegram Layer مطلوب")
        if not self.chat_id:
            raise ValueError("❌ Chat ID مطلوب")

        # 🔥 FIX: الأصول الموحدة (بدون تضارب XAUUSD)
        self.scan_assets = scan_assets or [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "PAXGUSDT",
            "SOLUSDT"
        ]

        # معايير الماسح
        self.confidence_threshold = confidence_threshold
        self.cooldown = cooldown
        self.scan_interval = scan_interval

        # حالة الماسح
        self.stop_event = threading.Event()
        self.stop_event.set()  # بدء متوقف
        self.thread: Optional[threading.Thread] = None

        # تتبع آخر الإشارات
        self.last_signal: Dict[str, float] = {}
        self.signal_count: int = 0

        logger.info("🟢 تم تهيئة Scanner V3 بنجاح")

    def _validate_result(self, result: Any, asset: str) -> bool:
        """
        التحقق من صحة نتيجة التحليل
        
        Args:
            result: نتيجة التحليل
            asset: الأصل المحلل
            
        Returns:
            True إذا كانت النتيجة صحيحة، False خلاف ذلك
        """
        if not result:
            return False

        if not isinstance(result, dict):
            logger.warning(f"⚠️ تنسيق نتيجة غير صحيح لـ {asset}: {type(result)}")
            return False

        required_fields = ["signal", "confidence"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"⚠️ حقل مفقود في {asset}: {field}")
                return False

        return True

    def _should_send_signal(self, asset: str, confidence: float) -> bool:
        """
        التحقق من إمكانية إرسال الإشارة
        
        Args:
            asset: الأصل
            confidence: درجة الثقة
            
        Returns:
            True إذا كان يجب إرسال الإشارة
        """
        # التحقق من حد الثقة
        if confidence < self.confidence_threshold:
            logger.debug(f"📊 {asset}: ثقة منخفضة ({confidence}% < {self.confidence_threshold}%)")
            return False

        # التحقق من فترة الانتظار (Cooldown)
        now = time.time()
        last_time = self.last_signal.get(asset, 0)

        if now - last_time < self.cooldown:
            remaining = self.cooldown - (now - last_time)
            logger.debug(f"⏱️ {asset}: في فترة انتظار ({remaining:.0f}ث المتبقية)")
            return False

        return True

    def _send_telegram_message(self, message: str) -> bool:
        """
        إرسال رسالة عبر Telegram
        
        Args:
            message: محتوى الرسالة
            
        Returns:
            True إذا تم الإرسال بنجاح
        """
        if not self.telegram:
            logger.error("❌ Telegram Layer غير متاح")
            return False

        try:
            # محاولة الطريقة الأولى
            if hasattr(self.telegram, 'bot') and hasattr(self.telegram.bot, 'sendMessage'):
                self.telegram.bot.sendMessage(self.chat_id, message)
                logger.info("✅ تم إرسال الرسالة عبر telegram.bot.sendMessage")
                return True
        except (AttributeError, TypeError) as e:
            logger.debug(f"⚠️ طريقة bot.sendMessage فشلت: {e}")
        except Exception as e:
            logger.error(f"❌ خطأ في bot.sendMessage: {e}")

        try:
            # محاولة الطريقة الثانية
            if hasattr(self.telegram, 'send_message'):
                self.telegram.send_message(self.chat_id, message)
                logger.info("✅ تم إرسال الرسالة عبر telegram.send_message")
                return True
        except (AttributeError, TypeError) as e:
            logger.debug(f"⚠️ طريقة send_message فشلت: {e}")
        except Exception as e:
            logger.error(f"❌ خطأ في send_message: {e}")

        logger.error("❌ فشل إرسال الرسالة عبر جميع الطرق المتاحة")
        return False

    def _format_signal_message(self, asset: str, result: Dict) -> str:
        """
        تنسيق رسالة الإشارة
        
        Args:
            asset: الأصل
            result: بيانات النتيجة
            
        Returns:
            الرسالة المنسقة
        """
        signal = result.get("signal", "UNKNOWN")
        confidence = result.get("confidence", 0)
        entry = result.get("entry", "N/A")
        sl = result.get("sl", "N/A")
        tp = result.get("tp", "N/A")
        quality = result.get("quality", "N/A")
        reason = result.get("reason", "لا توجد تفاصيل")

        message = f"""🔍 ULTRA SCANNER V3

💰 ASSET: {asset}
📊 SIGNAL: {signal}

🎯 ENTRY: {entry}
🛑 SL: {sl}
💰 TP: {tp}

💎 CONFIDENCE: {confidence}%
🏆 QUALITY: {quality}

📍 REASON:
{reason}
"""
        return message

    def scan_loop(self):
        """حلقة المسح الرئيسية"""
        logger.info("🟢 بدء حلقة المسح الرئيسية")

        while not self.stop_event.is_set():
            try:
                for asset in self.scan_assets:
                    try:
                        # تحليل الأصل
                        result = self.signal_engine.analyze_asset(asset)

                        # التحقق من صحة النتيجة
                        if not self._validate_result(result, asset):
                            continue

                        signal = result.get("signal")
                        confidence = result.get("confidence", 0)

                        # تخطي إذا لم تكن هناك تجارة
                        if signal == "NO TRADE":
                            logger.debug(f"⏭️ {asset}: لا توجد إشارة تجارية")
                            continue

                        # التحقق من شروط الإرسال
                        if not self._should_send_signal(asset, confidence):
                            continue

                        # تنسيق وإرسال الرسالة
                        message = self._format_signal_message(asset, result)
                        
                        if self._send_telegram_message(message):
                            self.last_signal[asset] = time.time()
                            self.signal_count += 1
                            logger.info(f"✅ إشارة جديدة مرسلة: {asset} | الإجمالي: {self.signal_count}")
                        else:
                            logger.error(f"❌ فشل إرسال إشارة: {asset}")

                    except Exception as e:
                        logger.error(f"❌ خطأ في تحليل {asset}: {type(e).__name__} - {e}")
                        continue

                # الانتظار حتى الفحص التالي
                time.sleep(self.scan_interval)

            except Exception as e:
                logger.critical(f"❌ خطأ حرج في حلقة المسح: {type(e).__name__} - {e}")
                time.sleep(self.scan_interval)

        logger.info("🔴 تم إيقاف حلقة المسح")

    def start(self) -> bool:
        """
        بدء الماسح
        
        Returns:
            True إذا تم البدء بنجاح
        """
        if self.thread and self.thread.is_alive():
            logger.warning("⚠️ الماسح قيد التشغيل بالفعل")
            return False

        try:
            self.stop_event.clear()
            self.thread = threading.Thread(
                target=self.scan_loop,
                name="ScannerV3-Thread",
                daemon=False
            )
            self.thread.start()
            logger.info("🟢 تم تشغيل Scanner V3 بنجاح")
            return True
        except Exception as e:
            logger.error(f"❌ فشل تشغيل الماسح: {e}")
            return False

    def stop(self, timeout: int = 5) -> bool:
        """
        إيقاف الماسح
        
        Args:
            timeout: مهلة الانتظار لإيقاف الخيط (ثانية)
            
        Returns:
            True إذا تم الإيقاف بنجاح
        """
        if not self.thread or not self.thread.is_alive():
            logger.warning("⚠️ الماسح غير مشغل حالياً")
            return False

        try:
            logger.info("🔴 إيقاف الماسح...")
            self.stop_event.set()
            self.thread.join(timeout=timeout)

            if self.thread.is_alive():
                logger.warning(f"⚠️ لم يتم إيقاف الخيط خلال {timeout} ثانية")
                return False

            logger.info(f"🔴 تم إيقاف Scanner V3 | عدد الإشارات: {self.signal_count}")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ عند إيقاف الماسح: {e}")
            return False

    def is_running(self) -> bool:
        """
        التحقق من حالة الماسح
        
        Returns:
            True إذا كان الماسح مشغلاً
        """
        return self.thread is not None and self.thread.is_alive()

    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الماسح
        
        Returns:
            قاموس يحتوي على الإحصائيات
        """
        return {
            "running": self.is_running(),
            "signal_count": self.signal_count,
            "scanned_assets": self.scan_assets,
            "last_signals": self.last_signal.copy(),
            "confidence_threshold": self.confidence_threshold,
            "cooldown": self.cooldown,
            "scan_interval": self.scan_interval
        }
