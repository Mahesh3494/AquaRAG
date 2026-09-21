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



