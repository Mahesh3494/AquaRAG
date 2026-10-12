from src.evaluation import is_hit

RESULTS = [
    {"text": "...", "source_doc": "fao.pdf", "page": 11, "score": 0.75},
    {"text": "...", "source_doc": "mpeda.pdf", "page": 27, "score": 0.73},
    {"text": "...", "source_doc": "fao.pdf", "page": 23, "score": 0.72},
]


def test_hit_when_doc_and_page_both_match():
    assert is_hit(RESULTS, "mpeda.pdf", 27) is True


def test_hit_anywhere_in_the_list_not_just_first():
    assert is_hit(RESULTS, "fao.pdf", 23) is True


def test_miss_when_page_matches_but_doc_does_not():
    assert is_hit(RESULTS, "ciba.pdf", 27) is False


def test_miss_when_doc_matches_but_page_does_not():
    assert is_hit(RESULTS, "fao.pdf", 99) is False


def test_miss_on_empty_results():
    assert is_hit([], "fao.pdf", 11) is False