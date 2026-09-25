"""Ingest regulations document into PostgreSQL (parent articles) and PGVector (child chunks)."""

from __future__ import annotations

import asyncio

from _common import resolve_data_file

from app.retrieval.text_pipeline.ingest import ingest_regulations_text


async def main() -> None:
    data_path = resolve_data_file()
    print(f"Reading from: {data_path.name}")
    text = data_path.read_text(encoding="utf-8")

    print("Ingesting regulations into PostgreSQL and PGVector...")
    result = await ingest_regulations_text(text, clear_existing=True)

    print(f"Saved {result.parent_articles_count} parent articles to PostgreSQL.")
    print(f"Indexed {result.child_chunks_count} child chunks into PGVector.")
    print("Ingestion completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
