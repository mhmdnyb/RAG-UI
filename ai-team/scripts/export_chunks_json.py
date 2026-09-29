"""Export parsed regulation articles and chunks to a JSON file for analysis and verification."""

from __future__ import annotations

import json

try:
    from scripts._common import resolve_data_file
except ImportError:
    from _common import resolve_data_file

from app.retrieval.text_pipeline.parser import (
    ChunkType,
    parse_regulations,
    to_dict_records,
)


def main() -> None:
    data_path = resolve_data_file()

    text = data_path.read_text(encoding="utf-8")
    parsed_articles = parse_regulations(text)
    records = to_dict_records(parsed_articles)

    output_path = data_path.parent / "regulations_chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    total_parents = len(records)
    total_children = sum(len(item["children"]) for item in records)
    total_tabs = sum(
        1 for item in records for c in item["children"] if c["type"] == ChunkType.NOTE
    )
    total_base = sum(
        1 for item in records for c in item["children"] if c["type"] == ChunkType.BASE
    )
    total_defs = sum(
        1
        for item in records
        for c in item["children"]
        if c["type"] == ChunkType.DEFINITION
    )

    print(f"Parsed {total_parents} parent articles successfully.")
    print(
        f"Generated {total_children} child chunks "
        f"({total_base} base + {total_tabs} notes + {total_defs} definitions)."
    )
    print(f"JSON export written to: {output_path}")


if __name__ == "__main__":
    main()
