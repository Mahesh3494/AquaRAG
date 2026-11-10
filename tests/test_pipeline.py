from pathlib import Path

import pytest

import src.pipeline
from src.embeddings import embed_texts
from src.pipeline import EmptyIndexError, ask, index_pdf
from src.store import connect, create_table, search

FIXTURE = Path(__file__).parent / "fixtures" / "three_pages.pdf"


@pytest.fixture
def conn():
    conn = connect("aquarag_test")
    conn.execute("DROP TABLE IF EXISTS chunks")
    create_table(conn)
    yield conn
    conn.close()


def count_rows(conn) -> int:
    return conn.execute("SELECT count(*) FROM chunks").fetchone()[0]


def test_returns_the_number_of_chunks_stored(conn):
    assert index_pdf(conn, FIXTURE, chunk_size=1000, overlap=0) == 3


def test_every_chunk_ends_up_in_the_database(conn):
    stored = index_pdf(conn, FIXTURE, chunk_size=15, overlap=0)
    assert count_rows(conn) == stored


def test_page_numbers_survive_into_the_database(conn):
    index_pdf(conn, FIXTURE, chunk_size=1000, overlap=0)
    pages = [row[0] for row in conn.execute("SELECT page FROM chunks ORDER BY page")]
    assert pages == [1, 2, 3]


def test_a_question_finds_the_page_that_answers_it(conn):
    index_pdf(conn, FIXTURE, chunk_size=1000, overlap=0)
    question = embed_texts(["What pH should the water be?"])[0]
    best = search(conn, question, k=1)[0]
    assert best["page"] == 2


def test_ask_on_an_empty_index_raises(conn):
    with pytest.raises(EmptyIndexError):
        ask(conn, "What pH should the water be?")


def test_ask_before_the_table_exists_raises(conn):
    # A fresh database where scripts.index_corpus was never run.
    conn.execute("DROP TABLE chunks")
    with pytest.raises(EmptyIndexError):
        ask(conn, "What pH should the water be?")


def test_ask_returns_the_results_its_answer_was_built_from(conn, monkeypatch):
    index_pdf(conn, FIXTURE, chunk_size=1000, overlap=0)
    seen = []

    def fake_answer(question, results):
        seen.append(results)
        return "7.5 to 8.5 [1]"

    # No cross-encoder and no DeepSeek call: keep the BM25 order, fake the LLM.
    monkeypatch.setattr(src.pipeline, "rerank", lambda q, candidates, k: candidates[:k])
    monkeypatch.setattr(src.pipeline, "answer", fake_answer)

    text, results = ask(conn, "What pH should the water be?", k=2)

    assert text == "7.5 to 8.5 [1]"
    assert results == seen[0]
    assert len(results) == 2
