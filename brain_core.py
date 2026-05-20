import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BrainCore:
    def __init__(self, signal_engine, market=None, news=None, risk=None):
        """
        🧠 العقل المركزي للنظام (BrainCore)
        يستقبل البيانات من واجهة تيليغرام المحدثة ويغذيها إلى محركات الفلترة الذكية والمخاطر.
        """
        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        
        logging.info("🧠 تم إعادة بناء وتدشين العقل المركزي (BrainCore) بنجاح.")

    def process_market_data(self, raw_data: dict, market_conditions: dict) -> dict:
        """
        معالجة لقطات البيانات القادمة وتمريرها عبر فلاتر الأموال الذكية (SMC) والـ PAXG الصارمة.
        """
        if not self.signal_engine:
            logging.error("❌ محرك الإشارات (Signal Engine) غير متصل بـ BrainCore!")
            return {"status": "REJECTED", "reason": "Signal Engine Container is missing"}

        try:
            # تمرير البيانات الحية إلى محرك الإشارات الشامل لإصدار القرار النهائي
            decision = self.signal_engine.analyze_market_and_generate_signal(raw_data, market_conditions)
            return decision
        except Exception as e:
            logging.error(f"❌ خطأ أثناء معالجة البيانات داخل BrainCore: {e}")
            return {"status": "REJECTED", "reason": f"Internal Brain Error: {str(e)}"}

    def get_system_health(self) -> dict:
        """فحص حالة الاتصال بين العقل المركزي والمحركات الفرعية قبل التشغيل"""
        return {
            "signal_engine_ready": self.signal_engine is not None,
            "risk_manager_ready": self.risk is not None,
            "news_engine_ready": self.news is not None,
            "market_feed_active": True
        }

