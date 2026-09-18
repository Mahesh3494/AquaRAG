from pathlib import Path

import pytest

from src.extraction import extract_pages

FIXTURE = Path(__file__).parent / "fixtures" / "three_pages.pdf"


def test_returns_one_string_per_page():
    assert len(extract_pages(FIXTURE)) == 3


def test_pages_are_in_order():
    pages = extract_pages(FIXTURE)
    assert "Page one" in pages[0]
    assert "Page two" in pages[1]
    assert "Page three" in pages[2]


def test_page_text_contains_expected_content():
    pages = extract_pages(FIXTURE)
    assert "5 mg/l" in pages[0]
    assert "6.5 to 8.5" in pages[1]


def test_every_page_is_a_string():
    assert all(isinstance(p, str) for p in extract_pages(FIXTURE))


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_pages(Path("does_not_exist.pdf"))