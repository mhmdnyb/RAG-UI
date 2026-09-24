# AI-Team — RAG Service

سرویس پاسخ‌گویی دستیار دانشگاه. معماری و قوانین تیم در [ARCHITECTURE.md](./ARCHITECTURE.md).

## شروع سریع

```bash
make install          # نصب وابستگی‌ها
cp .env.example .env  # و مقادیر را پر کن
make infra            # بالا آوردن Postgres و Redis
make dev              # اجرای API روی :8000
make worker           # در ترمینال دوم: اجرای TaskIQ worker
```

بدون Redis هم می‌شود کار کرد: در `.env` مقدار `USE_QUEUE=false` را بگذار.
در این حالت پردازش داخل خود پروسهٔ API انجام می‌شود (فقط برای توسعه؛
با ری‌استارت، کارها از بین می‌روند).

## دستورهای دیگر

| دستور | کار |
|---|---|
| `make test` | اجرای تست‌ها |
| `make lint` | بررسی ruff |
| `make seed` | بارگذاری `data/classes.csv` در Postgres |

## نکات مهم برای توسعه‌دهنده‌ها

- **همیشه از دایرکتوری `ai-team/` اجرا کن.** همهٔ ایمپورت‌ها مطلق‌اند: `from app.common.config import settings`.
- **کار blocking را مستقیم در `async def` صدا نزن.** مدل‌های ML و کتابخانه‌های sync باید داخل `await asyncio.to_thread(...)` اجرا شوند، وگرنه کل worker قفل می‌شود. نمونهٔ درست: `app/embedding/service.py`.
- **برای تست ماژول خودت منتظر بقیه نمان.** از `app/common/fakes.py` استفاده کن.
- **قبل از PR: `make lint && make test`.**

## تست کردن سریع سرویس

```bash
curl -X POST localhost:8000/rag/query \
  -H "Authorization: Bearer $RAG_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversationId":"test-1","question":"چه درس‌هایی یکشنبه کلاس دارند؟"}'
# -> {"status":"OK"}   و پاسخ نهایی با callback به Core می‌رود
```

`GET /health` زنده بودن سرویس و `GET /ready` در دسترس بودن دیتابیس و صف را برمی‌گرداند.
