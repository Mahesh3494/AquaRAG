from pathlib import Path
import psycopg

from src.embeddings import embed_texts
from src.ingestion import build_chunks
from src.store import insert_chunks

def index_pdf(
    conn: psycopg.Connection, pdf_path: Path, chunk_size: int, overlap: int
) -> int:

    """Chunk, embed and store one PDF.

    Returns:
        The number of chunks stored.
    """
    # 1. Build the chunk records with build_chunks.
    records = build_chunks(pdf_path, chunk_size, overlap)
    # 2. Make a list containing just the text of each record.
    texts = []
    for record in records:
        texts.append(record["text"])
    # 3. Embed that list of texts with embed_texts.
    vectors = embed_texts(texts)
    # 4. Store the records and vectors with insert_chunks.
    insert_chunks(conn, records, vectors)
    # 5. Return how many records there were.
    return len(records)