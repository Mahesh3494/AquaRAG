from src.evaluation import is_hit, parse_citations, cited_correct_page

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

def test_parse_finds_all_citations_in_order():
    assert parse_citations("pH 7.5-8.5 [2]. Lime below 7.5 [1][3].") == [2, 1, 3]


def test_parse_no_citations():
    assert parse_citations("No citations here.") == []


def test_parse_two_digit_citation():
    assert parse_citations("see [12]") == [12]


def test_cited_correct_page_true():
    # [2] -> RESULTS[1], which is mpeda.pdf p.27
    assert cited_correct_page([2], RESULTS, "mpeda.pdf", 27) is True


def test_cited_wrong_page_false():
    # [1] -> fao.pdf p.11, not mpeda p.27
    assert cited_correct_page([1], RESULTS, "mpeda.pdf", 27) is False


def test_out_of_range_citation_ignored():
    # [9] doesn't exist (only 3 results) — must not crash
    assert cited_correct_page([9], RESULTS, "mpeda.pdf", 27) is False


def test_no_citations_false():
    assert cited_correct_page([], RESULTS, "mpeda.pdf", 27) is False