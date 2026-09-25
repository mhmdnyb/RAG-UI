"""Unit tests for TextRetriever and regulations parser."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.common.exceptions import RetrievalError
from app.common.interfaces import RetrievalResult
from app.retrieval.text_pipeline.parser import (
    ChunkType,
    parse_regulations,
    to_text_nodes,
)
from app.retrieval.text_pipeline.retriever import TextRetriever


@pytest.mark.asyncio
async def test_text_retriever_empty_query():
    retriever = TextRetriever()
    assert await retriever.retrieve("") == []
    assert await retriever.retrieve("   ") == []


@pytest.mark.asyncio
async def test_text_retriever_with_mock_index():
    mock_node_1 = MagicMock()
    mock_node_1.get_content.return_value = "متن ماده ۱۷"
    mock_node_1.metadata = {
        "article_id": "article_17",
        "title": "ماده ۱۷",
        "type": "base",
    }

    mock_node_2 = MagicMock()
    mock_node_2.get_content.return_value = "متن تبصره ۱ ماده ۱۷"
    mock_node_2.metadata = {
        "article_id": "article_17",
        "title": "ماده ۱۷ - تبصره ۱",
        "type": "tabasereh",
    }

    item_1 = MagicMock()
    item_1.node = mock_node_1
    item_1.score = 0.85

    item_2 = MagicMock()
    item_2.node = mock_node_2
    item_2.score = 0.72

    mock_llama_retriever = MagicMock()
    mock_llama_retriever.aretrieve = AsyncMock(return_value=[item_1, item_2])

    mock_index = MagicMock()
    mock_index.as_retriever.return_value = mock_llama_retriever

    retriever = TextRetriever(index=mock_index)
    results = await retriever.retrieve("تست ماده ۱۷", top_k=2)

    assert len(results) == 2
    assert isinstance(results[0], RetrievalResult)
    assert results[0].content == "متن ماده ۱۷"
    assert results[0].source == "ماده ۱۷"
    assert results[0].score == 0.85
    assert results[0].metadata["type"] == "base"

    assert results[1].content == "متن تبصره ۱ ماده ۱۷"
    assert results[1].source == "ماده ۱۷ - تبصره ۱"
    assert results[1].score == 0.72
    assert results[1].metadata["type"] == "tabasereh"


@pytest.mark.asyncio
async def test_text_retriever_respects_top_k():
    items = []
    for i in range(5):
        node = MagicMock()
        node.get_content.return_value = f"content_{i}"
        node.metadata = {"title": f"title_{i}"}
        item = MagicMock()
        item.node = node
        item.score = 1.0 - (i * 0.1)
        items.append(item)

    mock_llama_retriever = MagicMock()
    mock_llama_retriever.aretrieve = AsyncMock(return_value=items)

    mock_index = MagicMock()
    mock_index.as_retriever.return_value = mock_llama_retriever

    retriever = TextRetriever(index=mock_index)
    results = await retriever.retrieve("تست", top_k=3)

    assert len(results) == 3
    assert [r.content for r in results] == ["content_0", "content_1", "content_2"]


@pytest.mark.asyncio
async def test_text_retriever_raises_retrieval_error_on_failure():
    mock_llama_retriever = MagicMock()
    mock_llama_retriever.aretrieve = AsyncMock(
        side_effect=RuntimeError("Vector database unavailable")
    )

    mock_index = MagicMock()
    mock_index.as_retriever.return_value = mock_llama_retriever

    retriever = TextRetriever(index=mock_index)
    with pytest.raises(RetrievalError) as exc_info:
        await retriever.retrieve("پرسش تست")

    assert "Text retrieval failed" in str(exc_info.value)


def test_parser_splits_base_and_tabasereh_with_context():
    sample_text = (
        "بخش دوم - شرایط تحصیلی\n"
        "ماده ۱۰: حداقل نمره قبولی در هر درس ۱۰ است. دانشجویان موظف به کسب این نمره هستند.\n"
        "تبصره ۱: برای دروس پیش‌نیاز نمره ۸ کفایت می‌کند.\n"
        "تبصره ۲: نمرات مردودی در معدل کل محاسبه می‌شود."
    )
    articles = parse_regulations(sample_text)
    assert len(articles) == 1
    art = articles[0]
    assert art.id == "article_10"
    assert art.section == "بخش دوم - شرایط تحصیلی"
    assert len(art.chunks) == 3

    base_chunk = art.chunks[0]
    assert base_chunk.chunk_type == ChunkType.BASE
    assert "حداقل نمره قبولی" in base_chunk.context_injected_text

    tab1_chunk = art.chunks[1]
    assert tab1_chunk.chunk_type == ChunkType.NOTE
    assert tab1_chunk.title == "تبصره ۱"
    assert "حداقل نمره قبولی در هر درس ۱۰ است" in tab1_chunk.context_injected_text
    assert "برای دروس پیش‌نیاز نمره ۸ کفایت می‌کند" in tab1_chunk.context_injected_text


def test_parser_appendix_definitions():
    sample_text = (
        "پیوست شماره ۱: تعاریف و اصطلاحات\n"
        "یک: دانشجو: فردی که پس از قبولی در دانشگاه ثبت‌نام کرده است.\n"
        "دو: استاد: عضو هیئت علمی دانشگاه."
    )
    articles = parse_regulations(sample_text)
    assert len(articles) == 1
    art = articles[0]
    assert art.id == "appendix_1"
    assert len(art.chunks) == 2

    assert art.chunks[0].chunk_type == ChunkType.DEFINITION
    assert "دانشجو" in art.chunks[0].title
    assert "فردی که پس از قبولی" in art.chunks[0].context_injected_text


def test_to_text_nodes():
    pytest.importorskip("llama_index")
    sample_text = (
        "پیوست شماره ۱: تعاریف و اصطلاحات\n"
        "یک: دانشجو: فردی که پس از قبولی در دانشگاه ثبت‌نام کرده است.\n"
        "دو: استاد: عضو هیئت علمی دانشگاه."
    )
    articles = parse_regulations(sample_text)
    nodes = to_text_nodes(articles)
    assert len(nodes) == 2
    assert nodes[0].metadata["type"] == str(ChunkType.DEFINITION)
