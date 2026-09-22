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




from src.store import search


def vec(*positions: int) -> list[float]:
    """A vector with 1.0 at each given position, zeros elsewhere."""
    vector = [0.0] * EMBEDDING_DIM
    for p in positions:
        vector[p] = 1.0
    return vector


def test_search_on_empty_table_returns_empty_list(conn):
    assert search(conn, vec(0)) == []


def test_search_returns_closest_first(conn):
    insert_chunks(
        conn,
        [record("far", 1), record("close", 2), record("middle", 3)],
        [vec(1), vec(0), vec(0, 1)],
    )
    results = search(conn, vec(0), k=3)
    assert [r["text"] for r in results] == ["close", "middle", "far"]


def test_search_returns_at_most_k_results(conn):
    insert_chunks(
        conn,
        [record("a", 1), record("b", 2), record("c", 3)],
        [vec(0), vec(1), vec(2)],
    )
    assert len(search(conn, vec(0), k=2)) == 2


def test_default_k_is_five(conn):
    records = [record(f"chunk {i}", i) for i in range(7)]
    vectors = [vec(i) for i in range(7)]
    insert_chunks(conn, records, vectors)
    assert len(search(conn, vec(0))) == 5


def test_exact_match_scores_one(conn):
    insert_chunks(conn, [record("same", 1)], [vec(0)])
    assert search(conn, vec(0), k=1)[0]["score"] == pytest.approx(1.0)


def test_search_result_carries_its_metadata(conn):
    insert_chunks(conn, [record("optimal pH is 6.5 to 8.5", 12)], [vec(0)])
    result = search(conn, vec(0), k=1)[0]
    assert result["text"] == "optimal pH is 6.5 to 8.5"
    assert result["source_doc"] == "test.pdf"
    assert result["page"] == 12
    assert result["chunk_index"] == 0
    assert set(result) == {"text", "source_doc", "page", "chunk_index", "score"}