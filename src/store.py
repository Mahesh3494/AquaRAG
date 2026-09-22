import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from src.embeddings import EMBEDDING_DIM

def connect(dbname: str = "aquarag") -> psycopg.Connection:
    """open a databade connection that understands the vextor type."""
    conn = psycopg.connect(dbname=dbname, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn

def create_table(conn: psycopg.Connection) -> None:
    """Create the chunks table if it doesn't already exist."""
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS chunks (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            source_doc TEXT NOT NULL,
            page INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            embedding vector({EMBEDDING_DIM}) NOT NULL
        )
        """
    )
def insert_chunks(
    conn: psycopg.Connection, records: list[dict], vectors: list[list[float]]) -> None:
    """Store chunk records alongside their embedding vectors.

    records[i] is stored with vectors[i].

    Raises:
        ValueError: If records and vectors differ in length. Nothing is
            inserted in that case.
    """
    # 1. If the two lists differ in length, raise ValueError — BEFORE
    #    inserting anything.
    if len(records) != len(vectors):
        raise ValueError(f"got {len(records)} records but {len(vectors)} vectors")

    # 2. Walk records and vectors together, pairing each record with its
    #    vector (zip). For each pair, run:
    #
    #        conn.execute(
    #            "INSERT INTO chunks (text, source_doc, page, chunk_index, embedding) "
    #            "VALUES (%s, %s, %s, %s, %s)",
    #            ( ...the five values, in that order... ),
    #        )
    #
    #    The embedding must go in as np.array(vector), not a plain list.
    for record, vector in zip(records, vectors):
        conn.execute(
            "INSERT INTO chunks (text, source_doc, page, chunk_index, embedding)"
            "VALUES (%s, %s, %s, %s, %s)",
            (record["text"], record["source_doc"], record["page"], record["chunk_index"], np.array(vector))
        )



def search(conn: psycopg.Connection, query_vector: list[float], k: int = 5) -> list[dict]:
    """Find the k stored chunks closest to query_vector.

    Returns:
        Up to k results, closest first. Each is a dict with text,
        source_doc, page, chunk_index, and score (similarity: 1.0 means
        identical, higher is closer). An empty table gives an empty list.
    """
    # 1. Wrap query_vector in np.array — plain lists crash in <=>.
    q = np.array(query_vector)

    # 2. Run this query, passing (vector, vector, k) for the three %s,
    #    and call .fetchall() on the result to get every row:
    #
    #        "SELECT text, source_doc, page, chunk_index, "
    #        "1 - (embedding <=> %s) AS score "
    #        "FROM chunks ORDER BY embedding <=> %s LIMIT %s"
    #
    #    Each row comes back as a tuple:
    #        (text, source_doc, page, chunk_index, score)
    rows = conn.execute(
        "SELECT text, source_doc, page, chunk_index, "
        "1 - (embedding <=> %s) AS score "
        "FROM chunks ORDER BY embedding <=> %s LIMIT %s",
        (q, q, k),
    ).fetchall()
    
    # 3. Turn each row tuple into a dict with those five keys.
    results = []
    for text, source_doc, page, chunk_index, score in rows:
        results.append({
            "text": text,
            "source_doc": source_doc,
            "page" : page,
            "chunk_index": chunk_index,
            "score": score
        })

    # 4. Return the list of dicts.
    return results