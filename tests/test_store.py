import pytest

from src.embeddings import EMBEDDING_DIM
from src.store import connect, create_table, insert_chunks


def unit_vector(position: int) -> list[float]:
    """A vector of zeros with a single 1.0 — cheap, distinct, no model needed."""
    vector = [0.0] * EMBEDDING_DIM
    vector[position] = 1.0
    return vector


def record(text: str, page: int) -> dict:
    return {"text": text, "source_doc": "test.pdf", "page": page, "chunk_index": 0}


@pytest.fixture
def conn():
    conn = connect("aquarag_test")
    conn.execute("DROP TABLE IF EXISTS chunks")
    create_table(conn)
    yield conn
    conn.close()


def count_rows(conn) -> int:
    return conn.execute("SELECT count(*) FROM chunks").fetchone()[0]


def test_table_starts_empty(conn):
    assert count_rows(conn) == 0


def test_inserts_one_row_per_record(conn):
    insert_chunks(
        conn,
        [record("first", 1), record("second", 2)],
        [unit_vector(0), unit_vector(1)],
    )
    assert count_rows(conn) == 2


def test_metadata_is_stored_with_the_text(conn):
    insert_chunks(conn, [record("optimal pH is 6.5 to 8.5", 12)], [unit_vector(0)])
    row = conn.execute("SELECT text, source_doc, page, chunk_index FROM chunks").fetchone()
    assert row == ("optimal pH is 6.5 to 8.5", "test.pdf", 12, 0)


def test_empty_input_inserts_nothing(conn):
    insert_chunks(conn, [], [])
    assert count_rows(conn) == 0


def test_mismatched_lengths_raise(conn):
    with pytest.raises(ValueError):
        insert_chunks(conn, [record("a", 1), record("b", 2)], [unit_vector(0)])


def test_mismatched_lengths_insert_nothing(conn):
    with pytest.raises(ValueError):
        insert_chunks(conn, [record("a", 1), record("b", 2)], [unit_vector(0)])
    assert count_rows(conn) == 0