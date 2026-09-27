"""
Interactive Smoke Test for the full RAG pipeline.

Run with:
    python -m scripts.test_rag_flow "سوال شما اینجا"
"""

from __future__ import annotations

import asyncio
import sys

from app.common.config import settings
from app.composition import build_orchestrator


async def test_flow(question: str) -> None:
    print("\n" + "=" * 70)
    print("🚀 شروع تست فلو RAG برای پرسش:")
    print(f"   «{question}»")
    print("=" * 70)

    # 1. ساخت Orchestrator
    print("\n⏳ در حال بارگذاری ارکستریتور و ماژول‌ها...")
    try:
        orchestrator = build_orchestrator()
    except Exception as e:
        print(f"❌ خطا در ایجاد Orchestrator: {e}")
        return

    # 2. بررسی کلید LLM
    api_key = settings.resolved_llm_api_key
    if not api_key:
        print("⚠️ هشدار: هیچ کلید API برای LLM تنظیم نشده است.")
        print(
            "   سیستم در حالت فال‌بک امن اجرا می‌شود (متن کانتکست خام برگردانده خواهد شد)."
        )
    else:
        print(f"🔑 کلید API شناسایی شد (مدل: {settings.resolved_llm_model})")

    # 3. اجرای خط لوله کامل
    print(
        "\n⚙️ در حال پردازش سوال در خط لوله RAG (مسیربندی -> بازیابی -> بازرتبه‌بندی -> تولید پاسخ)..."
    )
    try:
        answer, sources = await orchestrator.process_query(
            conversation_id="smoke-test-1",
            question=question,
        )

        print("\n" + "=" * 70)
        print("🎯 نتایج نهایی:")
        print("=" * 70)

        print(f"\n📚 مستندات و مراجع استخراج‌شده ({len(sources)} مورد):")
        for i, src in enumerate(sources, 1):
            doc = src.get("document", "نامشخص")
            page = src.get("page")
            page_info = f" (صفحه {page})" if page else ""
            print(f"   [{i}] {doc}{page_info}")

        print("\n📝 پاسخ تولیدشده توسط مدل زبانی:")
        print("-" * 70)
        print(answer)
        print("-" * 70)

    except Exception as exc:
        print(f"\n❌ خطا در حین اجرای پایپ‌لاین: {exc}")
        print("💡 نکات احتمالی عیب‌یابی:")
        print("   ۱. آیا دیتابیس در دسترس است؟ (تنظیم DATABASE_URL در .env)")
        print(
            "   ۲. آیا داده‌ها سید شده‌اند؟ (دستور python -m scripts.seed_classes یا ingest_regulations)"
        )


def main():
    default_q = "مدت مجاز تحصیل در دوره کارشناسی ارشد چقدر است؟"
    question = sys.argv[1] if len(sys.argv) > 1 else default_q
    asyncio.run(test_flow(question))


if __name__ == "__main__":
    main()
