from src.keyword_search import tokenize, keyword_search


def test_lowercases():
    assert tokenize("Bleaching Powder") == ["bleaching", "powder"]


def test_punctuation_separates_words():
    assert tokenize("pH (>8.5) high.") == ["ph", "8", "5", "high"]


def test_hyphen_separates():
    assert tokenize("5-7 days") == ["5", "7", "days"]


def test_empty_string_gives_empty_list():
    assert tokenize("") == []


def test_newlines_are_separators():
    assert tokenize("white\nfeces") == ["white", "feces"]


CHUNKS = [
    {"text": "Treat pond water with bleaching powder before discharge",
     "source_doc": "a.pdf", "page": 1, "chunk_index": 0},
    {"text": "Pond water should be green. Keep pond water deep.",
     "source_doc": "a.pdf", "page": 2, "chunk_index": 0},
    {"text": "Feed shrimp twice daily",
     "source_doc": "b.pdf", "page": 3, "chunk_index": 0},
]


def test_returns_k_results():
    assert len(keyword_search(CHUNKS, "pond water", k=2)) == 2


def test_rare_word_wins_over_repeated_common_words():
    results = keyword_search(CHUNKS, "bleaching powder pond", k=3)
    assert results[0]["page"] == 1


def test_results_keep_metadata_and_add_score():
    result = keyword_search(CHUNKS, "shrimp feed", k=1)[0]
    assert result["source_doc"] == "b.pdf"
    assert result["page"] == 3
    assert "score" in result


def test_results_sorted_best_first():
    results = keyword_search(CHUNKS, "pond water bleaching", k=3)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)