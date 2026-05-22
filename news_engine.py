import datetime
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FederalNewsEngine: # تم تعديل الاسم هنا ليتوافق مع ملف main.py
    def __init__(self):
        # الكلمات المفتاحية الحساسة لأخبار الماكرو الاقتصادي
        self.macro_keywords = {
            'FOMC': r'\bfomc\b',
            'Powell': r'\b(powell|jerome powell)\b',
            'CPI': r'\b(cpi|inflation|consumer price index)\b',
            'Interest Rates': r'\b(interest rate|rates hike|fed rate|interest rates)\b'
        }
        
        # الكلمات المفتاحية للأخبار الجيوسياسية الخطيرة
        self.geo_political_keywords = r'\b(war|wars|geopolitical|sanctions|strike|military|escalation|conflict|tension|missile)\b'

        # الكلمات المفتاحية لتحديد اتجاه الخبر (Sentiment)
        self.bullish_keywords = r'\b(bullish|surge|growth|adoption|upgrade|success|gain|pump|green|breakout)\b'
        self.bearish_keywords = r'\b(bearish|dump|crash|ban|hack|scam|lawsuit|fud|red|liquidation|drop)\b'

    def analyze_news_text(self, title: str, body: str = "") -> dict:
        """
        تحليل نص الخبر وتحديد المشاعر، رصد الماكرو، وحساب الـ Impact Score رقمياً.
        """
        full_text = f"{title} {body}".lower()
        
        # 1. رصد أخبار الماكرو (Macro Detection)
        detected_macro = []
        for key, pattern in self.macro_keywords.items():
            if re.search(pattern, full_text):
                detected_macro.append(key)
                
        # 2. رصد الأخبار الجيوسياسية (Geo-Political)
        is_geo_political = bool(re.search(self.geo_political_keywords, full_text))
        
        # 3. تحليل المشاعر (Sentiment Analysis)
        bullish_count = len(re.findall(self.bullish_keywords, full_text))
        bearish_count = len(re.findall(self.bearish_keywords, full_text))
        
        if bullish_count > bearish_count:
            sentiment = "Bullish"
        elif bearish_count > bullish_count:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"

        # 4. حساب قوة الخبر رقمياً (Impact Score من 1 إلى 5)
        # القيمة الافتراضية بناءً على المشاعر
        impact_score = 1 if sentiment == "Neutral" else 2
        
        # زيادة النقاط بناءً على خطورة الماكرو أو الوضع الجيوسياسي
        if detected_macro:
            impact_score += 2  # أخبار الفيدرالي والتضخم ثقيلة جداً
        if is_geo_political:
            impact_score += 2  # الحروب والتوترات تهز الأسواق
            
        # سقف الـ Impact Score هو 5
        impact_score = min(impact_score, 5)

        return {
            'sentiment': sentiment,
            'impact_score': impact_score,
            'macro_detected': detected_macro,
            'is_geo_political': is_geo_political,
            'risk_regime': 'Risk OFF' if (is_geo_political or impact_score >= 4) else 'Risk ON'
        }

    def get_event_timing_status(self, event_time_epoch: float) -> dict:
        """
        ⏰ تحديد حالة التداول بناءً على توقيت الحدث الاقتصادي (Event Timing)
        قبل الحدث بـ 30 دقيقة -> تقليل التداول
        أثناء الحدث (نافذة 15 دقيقة) -> إيقاف التداول تماماً
        بعد الحدث بـ 30 دقيقة -> استعداد ومراقبة الحركة
        """
        now = datetime.datetime.utcnow().timestamp()
        time_diff_mins = (event_time_epoch - now) / 60

        # إذا كان الحدث في المستقبل وقريب (خلال 30 دقيقة)
        if 0 < time_diff_mins <= 30:
            return {'status': '⚠️ WARNING', 'action': 'REDUCE_TRADING', 'desc': 'اقتراب حدث اقتصادي هام - تقليل المخاطر'}
        
        # إذا كنا في وقت الحدث تماماً (قبل بـ 5 دقائق إلى بعد بـ 10 دقائق)
        elif -10 <= time_diff_mins <= 0:
            return {'status': '❌ LOCKED', 'action': 'STOP_TRADING', 'desc': 'صدور الحدث الآن - إيقاف التداول منعاً للانزلاقات'}
        
        # بعد صدور الحدث (خلال 30 دقيقة الأولى من صدوره)
        elif -40 < time_diff_mins < -10:
            return {'status': '🔥 READY', 'action': 'PREPARE_FOR_MOMENTUM', 'desc': 'انتهى الحدث الاقتصادي - مراقبة اتجاه السيولة الجديد'}
        
        else:
            return {'status': '🟢 NORMAL', 'action': 'ALLOW_TRADING', 'desc': 'الوضع مستقر برمجياً'}

    def process_crypto_panic_feed(self, news_list: list) -> list:
        """
        دمج ومعالجة قائمة الأخبار القادمة من المصادر (مثل CryptoPanic)
        لتصفيتها وضخها للـ Score والـ Risk Manager.
        """
        processed_news = []
        for news in news_list:
            # نتأكد أن الرموز تتبع شرطك (تبديل أي ذكر لـ XAU بالذهب المشفر PAXG تلقائياً)
            title = news.get('title', '').replace('XAU', 'PAXG')
            body = news.get('body', '').replace('XAU', 'PAXG')
            
            analysis = self.analyze_news_text(title, body)
            
            processed_news.append({
                'title': title,
                'analysis': analysis,
                'timestamp': news.get('timestamp', datetime.datetime.utcnow().timestamp())
            })
        return processed_news
        
