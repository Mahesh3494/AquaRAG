from pathlib import Path

from src.ingestion import build_chunks

FIXTURE = Path(__file__).parent / "fixtures" / "three_pages.pdf"


def test_one_record_per_page_when_chunk_size_is_large():
    assert len(build_chunks(FIXTURE, chunk_size=1000, overlap=0)) == 3


def test_page_numbers_count_from_one():
    records = build_chunks(FIXTURE, chunk_size=1000, overlap=0)
    assert [r["page"] for r in records] == [1, 2, 3]


def test_source_doc_is_the_filename_only():
    records = build_chunks(FIXTURE, chunk_size=1000, overlap=0)
    assert all(r["source_doc"] == "three_pages.pdf" for r in records)


def test_text_stays_with_its_own_page():
    records = build_chunks(FIXTURE, chunk_size=1000, overlap=0)
    assert "Page one" in records[0]["text"]
    assert "Page three" in records[2]["text"]


def test_chunk_index_restarts_on_each_page():
    records = build_chunks(FIXTURE, chunk_size=15, overlap=0)
    page_one = [r for r in records if r["page"] == 1]
    assert [r["chunk_index"] for r in page_one] == list(range(len(page_one)))


def test_every_record_has_the_four_keys():
    records = build_chunks(FIXTURE, chunk_size=1000, overlap=0)
    assert all(
        set(r) == {"text", "source_doc", "page", "chunk_index"} for r in records
    )