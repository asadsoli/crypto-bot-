# 👑 ULTRA V10 AI CORE - Institutional Trading Bot v2

مواصفات المحرك المؤسسي الذكي لإدارة وتحليل أسواق المال الرقمية باستخدام مفاهيم الأموال الذكية (SMC).

## 📊 الأصول المدعومة والمراقبة (Watchlist)
*   **BTCUSDT** (البيتكوين)
*   **ETHUSDT** (الإيثريوم)
*   **BNBUSDT** (بينانس كوين)
*   **PAXGUSDT** (الذهب الرقمي المشفر - المثبت بدلاً من XAU لمنع التداخل)
*   **SOLUSDT** (سولانا)

## 🧠 الهيكل التحليلي والمحركات (Architecture)
1. **BrainCore:** العقل المدبر وموزع البيانات المركزي المدمج.
2. **Signal Engine:** محرك رصد كسر الهيكل (BOS) وتغير السلوك (CHoCH) وسحب السيولة.
3. **Risk Manager:** صمام الأمان المؤسسي لإدارة المخاطر وتحديد أحجام العقود تلقائياً.
4. **Time Engine:** محرك فحص ساعات السيولة وجلسات التداول العالمية.
5. **Federal News Filter:** مصفاة حظر التداول أثناء الأخبار الاقتصادية القوية والسياسات الفدرالية.

## 🛠️ متطلبات التشغيل والبيئة (Environment)
يتم تشغيل البوت عبر منصة **Render** كـ `Background Worker` بالاعتماد على:
* **بايثون:** Python 3.10+
* **المكتبات الأساسية:** `pyTelegramBotAPI`, `scikit-learn`, `numpy`

## 🎛️ أوامر التشغيل السحابي
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `python app.py` (أو `python telegram_layer.py` حسب تسمية ملفك الرئيسي)

---
⚠️ *ملاحظة أمنية: لا تقم بوضع التوكن السرّي (Telegram Token) داخل الأكواد مطلقاً، استخدم دائماً متغيرات البيئة (Environment Variables) في لوحة تحكم Render لحماية الحساب.*
