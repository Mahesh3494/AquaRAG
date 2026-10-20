from pathlib import Path
import psycopg

from src.embeddings import embed_texts
from src.ingestion import build_chunks
from src.store import insert_chunks, search, load_all_chunks
from src.generation import answer, chat_messages
from src.keyword_search import keyword_search
from src.rerank import rerank
from src.agent import run_agent

CANDIDATES = 20

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
    # 1.Load every chunk
    chunks = load_all_chunks(conn)
    # 2. Keyword search for CANDIDATES chunks
    candidates = keyword_search(chunks, question, CANDIDATES)
    # Rerank them, keep the top k
    results = rerank(question, candidates, k)
    # 3. Pass question and results to answer(), and return the result.
    return answer(question, results)

def make_real_search(chunks: list[dict], k: int):
    """Build a search(query) function with chunks and k already fixed.

    The agent only ever calls search(query); this bakes in the rest.
    """
    def search(query: str) -> list[dict]:
        # Keyword search for CANDIDATES chunks, then rerank to the top k.
        # Same two lines as in ask(), but using `query`.
        candidates = keyword_search(chunks, query, CANDIDATES)
        results = rerank(query, candidates, k)
        return results
    return search


def ask_agent(conn, question: str, k: int = 5) -> tuple[str, list[dict]]:
    """Answer with the agent: it may reword and search more than once.

    Returns (answer text, every result the agent saw — [n] means item n-1).
    """
    # 1. Load all chunks.
    chunks = load_all_chunks(conn)
    # 2. Build the search function with make_real_search(chunks, k).
    search = make_real_search(chunks, k)
    # 3. Call run_agent with the question, that search function, and
    #    chat_messages as the llm. Return what it returns.
    return run_agent(question, search, chat_messages)
