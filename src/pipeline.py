from pathlib import Path
import psycopg

from src.embeddings import embed_texts
from src.ingestion import build_chunks
from src.store import insert_chunks, search
from src.generation import answer

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

def ask(conn: psycopg.Connection, question: str, k: int = 5) -> str:
    """Answer a question from the indexed corpus, with citations.

    Args:
        conn: An open database connection.
        question: The user's question.
        k: How many chunks to retrieve.

    Returns:
        The model's answer, citing retrieved chunks by their label.

    Raises:
        ValueError: If nothing was retrieved — an empty index.
    """
    # 1. Embed the question. embed_texts takes a LIST of strings and
    #    returns a LIST of vectors, so wrap the question going in and
    #    take the first vector back out.
    query_vector = embed_texts([question])[0]
    # 2. Call search with the connection, that vector, and k.
    results = search(conn, query_vector, k)
    # 3. Pass question and results to answer(), and return the result.
    return answer(question, results)