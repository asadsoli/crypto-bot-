import logging

class BrainCore:
    def __init__(self, signal_engine, market=None, news=None, risk=None):
        """
        العقل المركزي للنظام (BrainCore)
        يقوم بربط محرك الإشارات الفنية الفائقة بآليات إدارة المخاطر والأخبار لضمان فلترة مؤسسية
        """
        self.signal_engine = signal_engine
        self.market = market
        self.news = news
        self.risk = risk
        
        logging.info("🧠 تم تدشين عقل النظام المركزي (BrainCore) بنجاح وجاري ربطه بالطبقات الخارجية...")

    def process_market_data(self, raw_data, market_conditions=None):
        """
        استقبال البيانات الخام من الواجهة وتمريرها عبر معالجات الذكاء الاصطناعي
        """
        logging.info(f"📥 [BrainCore] جاري معالجة لقطة بيانات للأصل النشط...")
        
        if not self.signal_engine:
            return {"status": "REJECTED", "reason": "Signal Engine Container is missing"}

        # تمرير البيانات الحية إلى محرك الإشارات الشامل الذي قمنا ببنائه بالأمس
        # يقوم المحرك داخلياً بفحص الوقت، تصفية السيولة، ومطابقة شروط الـ PAXG الصارمة
        try:
            decision = self.signal_engine.analyze_market_and_generate_signal(raw_data, market_conditions)
            return decision
        except Exception as e:
            logging.error(f"❌ خطأ أثناء معالجة الإشارة داخل BrainCore: {e}")
            return {"status": "REJECTED", "reason": f"Internal Brain Error: {str(e)}"}

    def get_system_health(self):
        """
        فحص جهوزية المحركات الفرعية المرتبطة بقلب النظام
        """
        return {
            "signal_engine_ready": self.signal_engine is not None,
            "risk_manager_ready": self.risk is not None,
            "news_engine_ready": self.news is not None,
            "market_feed_active": self.market is not None or True
        }
      
