"""Export regulations with precomputed embeddings to JSON for fast import into remote servers."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from _common import PROJECT_ROOT, resolve_data_file

from app.common.config import settings
from app.embedding.service import EmbeddingService
from app.retrieval.text_pipeline.parser import parse_regulations


async def build_embedded_payload() -> dict:
    data_path = resolve_data_file()
    print(f"1. Reading text from: {data_path.name}")
    text = data_path.read_text(encoding="utf-8")

    print("2. Parsing regulations into articles and chunks...")
    articles = parse_regulations(text)

    parent_records = [
        {
            "id": a.id,
            "section": a.section,
            "title": a.title,
            "full_text": a.full_text,
        }
        for a in articles
    ]

    all_chunks_info = []
    for a in articles:
        for c in a.chunks:
            all_chunks_info.append(
                {
                    "id": c.chunk_id,
                    "text": c.context_injected_text,
                    "metadata": {
                        "article_id": a.id,
                        "type": str(c.chunk_type),
                        "title": c.title,
                        "section": a.section,
                    },
                }
            )

    print(f"3. Loading local embedding model ({settings.embedding_model})...")
    embedder = EmbeddingService()

    texts_to_embed = [c["text"] for c in all_chunks_info]
    print(f"4. Generating embeddings locally for {len(texts_to_embed)} chunks...")
    embeddings = await embedder.embed(texts_to_embed)

    chunk_records = []
    for item, emb in zip(all_chunks_info, embeddings, strict=True):
        chunk_records.append(
            {
                "id": item["id"],
                "text": item["text"],
                "metadata": item["metadata"],
                "embedding": emb,
            }
        )

    return {
        "version": "1.0",
        "embedding_model": settings.embedding_model,
        "embedding_dim": settings.embedding_dim,
        "parent_articles": parent_records,
        "chunks": chunk_records,
    }


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Precompute regulations embeddings locally and export to JSON"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(PROJECT_ROOT / "data" / "regulations_with_embeddings.json"),
        help="Output JSON file path",
    )
    parser.add_argument(
        "--server-url",
        "-s",
        default="",
        help="Optional server URL to automatically POST payload (e.g. http://server:8000)",
    )
    parser.add_argument(
        "--token",
        "-t",
        default="",
        help="Optional auth bearer token for server",
    )

    args = parser.parse_args()

    payload = await build_embedded_payload()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"5. Saving JSON to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(
        f"Export complete: {len(payload['parent_articles'])} parents, "
        f"{len(payload['chunks'])} chunks ({size_mb:.2f} MB)."
    )

    if args.server_url:
        import httpx

        target_url = f"{args.server_url.rstrip('/')}/rag/regulations/import-embedded"
        headers = {}
        if args.token:
            headers["Authorization"] = f"Bearer {args.token}"

        print(f"6. Sending payload directly to remote server: {target_url} ...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(target_url, json=payload, headers=headers)
            print(f"   Server response ({resp.status_code}): {resp.text}")


if __name__ == "__main__":
    asyncio.run(main())
