import pytest
from src.chunking import chunk_text


def test_splits_evenly_with_no_overlap():
    assert chunk_text("abcdefghij", chunk_size=5, overlap=0) == ["abcde", "fghij"]


def test_final_chunk_is_shorter_when_text_does_not_divide_evenly():
    assert chunk_text("abcdefg", chunk_size=3, overlap=0) == ["abc", "def", "g"]


def test_text_shorter_than_chunk_size_returns_one_chunk():
    assert chunk_text("abc", chunk_size=100, overlap=0) == ["abc"]


def test_empty_text_returns_empty_list():
    assert chunk_text("", chunk_size=10, overlap=2) == []


def test_chunks_overlap_by_the_requested_amount():
    chunks = chunk_text("abcdefghij", chunk_size=4, overlap=1)
    assert chunks == ["abcd", "defg", "ghij"]


def test_overlap_equal_to_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_text("abcdefghij", chunk_size=4, overlap=4)


def test_overlap_greater_than_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_text("abcdefghij", chunk_size=4, overlap=5)


def test_zero_chunk_size_raises():
    with pytest.raises(ValueError):
        chunk_text("abcdefghij", chunk_size=0, overlap=0)