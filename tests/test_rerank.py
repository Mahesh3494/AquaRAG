from src.rerank import rerank


def r(text, page):
    return {"text": text, "source_doc": "a.pdf", "page": page, "chunk_index": 0, "score": 0.0}


def fake_scorer(question, texts):
    """Pretend relevance = how many times 'pH' appears. No model needed."""
    scores = []
    for text in texts:
        scores.append(text.count("pH"))
    return scores


RESULTS = [r("pond water", 1), r("pH pH pH", 2), r("pH", 3)]


def test_reorders_by_scorer():
    pages = [x["page"] for x in rerank("q", RESULTS, k=3, scorer=fake_scorer)]
    assert pages == [2, 3, 1]


def test_keeps_only_k():
    assert len(rerank("q", RESULTS, k=2, scorer=fake_scorer)) == 2


def test_score_comes_from_scorer():
    assert rerank("q", RESULTS, k=1, scorer=fake_scorer)[0]["score"] == 3


def test_metadata_survives():
    top = rerank("q", RESULTS, k=1, scorer=fake_scorer)[0]
    assert top["text"] == "pH pH pH"
    assert top["source_doc"] == "a.pdf"
    assert top["chunk_index"] == 0


def test_empty_results_give_empty_list():
    assert rerank("q", [], k=5, scorer=fake_scorer) == []