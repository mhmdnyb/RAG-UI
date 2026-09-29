"""Unit tests for Cross-Encoder Reranker and Parent-Document expansion."""

from unittest.mock import MagicMock

from app.common.interfaces import RetrievalResult
from app.retrieval.reranker.reranker import Reranker


def _make_mock_cross_encoder(scores: list[float]):
    model = MagicMock()
    model.predict = MagicMock(return_value=scores)
    return model


async def test_reranker_sorts_descending_by_sigmoid_probability():
    # Logits: c0 -> -3.0 (prob ~0.047), c1 -> 2.5 (prob ~0.924), c2 -> 0.0 (prob 0.5)
    mock_model = _make_mock_cross_encoder([-3.0, 2.5, 0.0])
    reranker = Reranker(model=mock_model, score_threshold=0.0)

    items = [
        RetrievalResult(content="c0", source="doc0", score=0.1),
        RetrievalResult(content="c1", source="doc1", score=0.2),
        RetrievalResult(content="c2", source="doc2", score=0.3),
    ]

    ranked = await reranker.rerank("سوال", items, top_k=3)

    assert len(ranked) == 3
    assert ranked[0].content == "c1"
    assert ranked[1].content == "c2"
    assert ranked[2].content == "c0"
    assert 0.0 < ranked[0].score < 1.0
    assert ranked[0].score > ranked[1].score > ranked[2].score


async def test_reranker_respects_top_k():
    mock_model = _make_mock_cross_encoder([1.0, 2.0, 3.0, 4.0, 5.0])
    reranker = Reranker(model=mock_model)

    items = [RetrievalResult(content=f"item_{i}", source="doc") for i in range(5)]
    ranked = await reranker.rerank("سوال", items, top_k=2)

    assert len(ranked) == 2
    assert ranked[0].content == "item_4"
    assert ranked[1].content == "item_3"


async def test_reranker_filters_by_score_threshold():
    # Logits: -5.0 (prob ~0.006), 2.0 (prob ~0.88), -4.0 (prob ~0.018)
    mock_model = _make_mock_cross_encoder([-5.0, 2.0, -4.0])
    reranker = Reranker(model=mock_model, score_threshold=0.50)

    items = [
        RetrievalResult(content="low_1", source="doc"),
        RetrievalResult(content="high_1", source="doc"),
        RetrievalResult(content="low_2", source="doc"),
    ]
    ranked = await reranker.rerank("سوال", items, top_k=3)

    assert len(ranked) == 1
    assert ranked[0].content == "high_1"
    assert ranked[0].score >= 0.50


async def test_reranker_expands_and_deduplicates_parent_documents():
    # c0 and c1 belong to article_1; c2 belongs to article_2
    mock_model = _make_mock_cross_encoder([3.0, 2.0, 1.0])
    reranker = Reranker(model=mock_model, expand_parent=True)

    items = [
        RetrievalResult(
            content="تبصره ۱ ماده ۱",
            source="آیین‌نامه",
            metadata={
                "parent_id": "art_1",
                "parent_title": "ماده ۱: شرایط عمومی",
                "parent_full_text": "متن کامل و جامع ماده ۱ به همراه تمام تبصره‌ها",
            },
        ),
        RetrievalResult(
            content="تبصره ۲ ماده ۱",
            source="آیین‌نامه",
            metadata={
                "parent_id": "art_1",
                "parent_title": "ماده ۱: شرایط عمومی",
                "parent_full_text": "متن کامل و جامع ماده ۱ به همراه تمام تبصره‌ها",
            },
        ),
        RetrievalResult(
            content="ماده ۲ متن اصلی",
            source="آیین‌نامه",
            metadata={
                "parent_id": "art_2",
                "parent_title": "ماده ۲: ثبت نام",
                "parent_full_text": "متن کامل ماده ۲ ثبت نام",
            },
        ),
    ]

    ranked = await reranker.rerank("سوال", items, top_k=3)

    # Even though 3 chunks were input, the two chunks from article_1 must be merged into one parent
    assert len(ranked) == 2
    assert ranked[0].content == "متن کامل و جامع ماده ۱ به همراه تمام تبصره‌ها"
    assert ranked[0].source == "ماده ۱: شرایط عمومی"
    assert ranked[1].content == "متن کامل ماده ۲ ثبت نام"
    assert ranked[1].source == "ماده ۲: ثبت نام"


async def test_reranker_handles_empty_results_and_blank_query():
    reranker = Reranker()
    assert await reranker.rerank("سوال", []) == []

    items = [RetrievalResult(content="c1", source="doc")]
    assert await reranker.rerank("", items) == items
    assert await reranker.rerank("   ", items) == items


async def test_reranker_fallback_on_model_error():
    broken_model = MagicMock()
    broken_model.predict.side_effect = RuntimeError("GPU memory exhausted")
    reranker = Reranker(model=broken_model)

    items = [
        RetrievalResult(content="c0", source="doc"),
        RetrievalResult(content="c1", source="doc"),
    ]
    # Must not raise an exception; falls back to original results
    ranked = await reranker.rerank("سوال", items, top_k=2)
    assert len(ranked) == 2
    assert ranked[0].content == "c0"
