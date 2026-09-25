"""Parser and hierarchical chunker for university regulations."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from llama_index.core.schema import TextNode

    from app.retrieval.text_pipeline.schema import RegulationArticle

FA_TO_EN = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

NUMBER_WORDS = (
    "یک|دو|سه|چهار|پنج|شش|هفت|هشت|نه|ده|"
    "یازده|دوازده|سیزده|چهارده|پانزده|شانزده|هفده|هجده|نوزده|بیست|"
    "بیست و یک|بیست و دو|بیست و سه|بیست و چهار|بیست و پنج|بیست و شش|بیست و هفت|بیست و هشت|بیست و نه|سی|"
    "سی و یک|سی و دو|سی و سه|سی و چهار|سی و پنج|سی و شش|سی و هفت|سی و هشت|سی و نه|چهل"
)

FINAL_ARTICLES_START = 51
DEFAULT_SECTION = "کلیات"
FINAL_SECTION = "مواد پایانی / نظارت و اجرا"
APPENDIX_SECTION = "پیوست‌ها"


class ChunkType(StrEnum):
    BASE = "base"
    NOTE = "note"
    DEFINITION = "definition"


@dataclass
class RegulationChunk:
    chunk_id: str
    chunk_type: ChunkType | str
    title: str
    context_injected_text: str
    raw_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedRegulationArticle:
    id: str
    section: str
    title: str
    full_text: str
    chunks: list[RegulationChunk] = field(default_factory=list)


def _extract_topic_sentence(text: str) -> str:
    cleaned = text.replace("\n", " ").strip()
    if not cleaned:
        return ""
    topic = cleaned.split(".")[0].strip()
    if len(topic) < 40 and "." in cleaned:
        topic = ".".join(cleaned.split(".")[:2]).strip()
    if len(topic) > 250:
        topic = topic[:250].rsplit(" ", 1)[0] + "..."
    return topic


def parse_regulations(text: str) -> list[ParsedRegulationArticle]:
    """Parse regulation document text into structured parent articles and context-rich child chunks."""
    lines = text.split("\n")
    results: list[ParsedRegulationArticle] = []

    current_section = DEFAULT_SECTION
    current_part = ""
    current_article = "شناسه تصویب و امضاکنندگان"
    current_article_lines: list[str] = []

    def get_full_section_name() -> str:
        if current_part:
            return f"{current_section} - {current_part}"
        return current_section

    def finalize_article() -> None:
        nonlocal current_article_lines
        if not current_article_lines:
            return

        full_text = "\n".join(current_article_lines).strip()
        if not full_text:
            return

        if current_article.startswith("پیوست"):
            m_num = re.search(r"[۰-۹\d]+", current_article)
            num_str = m_num.group().translate(FA_TO_EN) if m_num else "1"
            article_id = f"appendix_{num_str}"
        elif current_article.startswith("شناسه"):
            article_id = "article_metadata"
        elif current_article.startswith("مقدمه"):
            article_id = "article_intro"
        else:
            m_num = re.search(r"[۰-۹\d]+", current_article)
            if m_num:
                article_id = f"article_{m_num.group().translate(FA_TO_EN)}"
            else:
                article_id = f"item_{len(results) + 1}"

        section_name = get_full_section_name()
        chunks: list[RegulationChunk] = []

        if current_article.startswith("پیوست"):
            tokens = re.split(rf"((?:^|\s)(?:{NUMBER_WORDS}):\s*)", full_text)
            def_counter = 1
            for i in range(1, len(tokens), 2):
                num_word = tokens[i].strip().rstrip(":")
                content = tokens[i + 1].strip() if i + 1 < len(tokens) else ""
                if not content:
                    continue

                term_match = re.match(r"^([^:]+):", content)
                term_title = term_match.group(1).strip() if term_match else num_word
                title = f"تعریف {def_counter}: {term_title}"

                context_injected = (
                    f"[{section_name}] [پیوست شماره ۱: تعاریف] [{title}]:\n{content}"
                )

                chunks.append(
                    RegulationChunk(
                        chunk_id=f"{article_id}_def_{def_counter}",
                        chunk_type=ChunkType.DEFINITION,
                        title=title,
                        context_injected_text=context_injected,
                        raw_text=f"{num_word}: {content}",
                    )
                )
                def_counter += 1
        else:
            parts = re.split(r"(\s*تبصره\s+[۰-۹\d]+:)", full_text)
            base_text = parts[0].strip()

            if base_text:
                chunks.append(
                    RegulationChunk(
                        chunk_id=f"{article_id}_base",
                        chunk_type=ChunkType.BASE,
                        title="متن اصلی",
                        context_injected_text=f"[{section_name}] [{current_article}] [متن اصلی]:\n{base_text}",
                        raw_text=base_text,
                    )
                )

            topic_sentence = _extract_topic_sentence(base_text)

            tab_counter = 1
            for i in range(1, len(parts), 2):
                tab_header = parts[i].strip()
                tab_body = parts[i + 1].strip() if i + 1 < len(parts) else ""
                if tab_body:
                    tab_title = tab_header.rstrip(":").strip()
                    context_injected = (
                        f"[{section_name}] [{current_article}] [{tab_title}]\n"
                        f"موضوع ماده: {topic_sentence}\n"
                        f"متن تبصره:\n{tab_body}"
                    )
                    chunks.append(
                        RegulationChunk(
                            chunk_id=f"{article_id}_tab_{tab_counter}",
                            chunk_type=ChunkType.NOTE,
                            title=tab_title,
                            context_injected_text=context_injected,
                            raw_text=f"{tab_header} {tab_body}",
                        )
                    )
                    tab_counter += 1

        results.append(
            ParsedRegulationArticle(
                id=article_id,
                section=section_name,
                title=current_article,
                full_text=full_text,
                chunks=chunks,
            )
        )
        current_article_lines = []

    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue

        if line_s.startswith("بخش ") or line_s.startswith("بخش نخست"):
            finalize_article()
            current_section = line_s
            current_part = ""
            continue

        if line_s.startswith("قسمت "):
            finalize_article()
            current_part = line_s
            continue

        if line_s.startswith("مقدمه"):
            finalize_article()
            current_section = DEFAULT_SECTION
            current_part = ""
            current_article = "مقدمه آیین‌نامه"
            current_article_lines = [line_s]
            continue

        if line_s.startswith("پیوست"):
            finalize_article()
            current_section = APPENDIX_SECTION
            current_part = ""
            current_article = line_s
            current_article_lines = [line_s]
            continue

        m_article = re.match(r"^(ماده\s+[۰-۹\d]+)\s*:", line_s)
        if m_article:
            finalize_article()
            art_raw = m_article.group(1)
            num_match = re.search(r"[۰-۹\d]+", art_raw)
            if num_match:
                art_num = int(num_match.group().translate(FA_TO_EN))
                if art_num >= FINAL_ARTICLES_START:
                    current_section = FINAL_SECTION
                    current_part = ""

            current_article = art_raw
            current_article_lines = [line_s]
        else:
            current_article_lines.append(line_s)

    finalize_article()
    return results


def to_text_nodes(articles: list[ParsedRegulationArticle]) -> list[TextNode]:
    """Convert parsed articles and chunks into LlamaIndex TextNode objects."""
    from llama_index.core.schema import TextNode

    nodes: list[TextNode] = []
    for article in articles:
        for chunk in article.chunks:
            node = TextNode(
                id_=chunk.chunk_id,
                text=chunk.context_injected_text,
                metadata={
                    "article_id": article.id,
                    "section": article.section,
                    "type": str(chunk.chunk_type),
                    "title": chunk.title,
                    **chunk.metadata,
                },
            )
            nodes.append(node)
    return nodes


def to_article_models(
    articles: list[ParsedRegulationArticle],
) -> list[RegulationArticle]:
    """Convert parsed articles to SQLAlchemy RegulationArticle models."""
    from app.retrieval.text_pipeline.schema import RegulationArticle

    return [
        RegulationArticle(
            id=a.id,
            section=a.section,
            title=a.title,
            full_text=a.full_text,
        )
        for a in articles
    ]


def to_dict_records(articles: list[ParsedRegulationArticle]) -> list[dict[str, Any]]:
    """Convert parsed articles to dictionary records for JSON export."""
    return [
        {
            "parent": {
                "id": a.id,
                "section": a.section,
                "title": a.title,
                "full_text": a.full_text,
                "children_count": len(a.chunks),
            },
            "children": [
                {
                    "child_id": c.chunk_id,
                    "type": str(c.chunk_type),
                    "title": c.title,
                    "context_injected_text": c.context_injected_text,
                    "raw_text": c.raw_text,
                }
                for c in a.chunks
            ],
        }
        for a in articles
    ]
