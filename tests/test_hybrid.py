import pytest

from src.hybrid import chunk_id, fuse


def r(doc, page, idx=0):
    return {"text": "...", "source_doc": doc, "page": page, "chunk_index": idx, "score": 0.0}


A = r("a.pdf", 1)
B = r("a.pdf", 2)
C = r("b.pdf", 3)
D = r("b.pdf", 4)
DENSE = [A, B, C]
KEYWORD = [B, D, A]


def test_chunk_id_is_doc_page_index():
    assert chunk_id(A) == ("a.pdf", 1, 0)


def test_worked_example_order():
    # The table from the explanation: B, A, D, C
    pages = [x["page"] for x in fuse([DENSE, KEYWORD], k=4)]
    assert pages == [2, 1, 4, 3]


def test_k_limits_results():
    assert len(fuse([DENSE, KEYWORD], k=2)) == 2


def test_score_is_the_rrf_total():
    top = fuse([DENSE, KEYWORD], k=1)[0]
    assert top["score"] == pytest.approx(1 / 62 + 1 / 61)


def test_same_page_different_chunks_stay_separate():
    x, y = r("a.pdf", 1, 0), r("a.pdf", 1, 1)
    assert len(fuse([[x], [y]], k=5)) == 2


def test_single_list_keeps_its_order():
    pages = [x["page"] for x in fuse([DENSE], k=3)]
    assert pages == [1, 2, 3]