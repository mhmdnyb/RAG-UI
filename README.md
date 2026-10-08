# University Assistant - Frontend

رابط کاربری دستیار هوش مصنوعی دانشگاه علم و فرهنگ.

## راه‌اندازی و اجرا (Getting Started)

### ۱. ورود به پوشه فرانت‌اند
```bash
cd frontend
```

### ۲. نصب وابستگی‌ها
```bash
npm install
```

### ۳. تنظیم متغیرهای محیطی
یک فایل `.env` بر اساس `.env.example` بسازید یا مقادیر پیش‌فرض را ویرایش کنید:
```env
VITE_API_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080/ws
```

### ۴. اجرای حالت توسعه (Development Mode)
```bash
npm run dev
```

### ۵. ساخت نسخه نهایی (Production Build)
```bash
npm run build
```
