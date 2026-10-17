"""Show what retrieval did for the 5 never-retrieved golden questions.

For each miss: what the right page actually contains in the DB,
and what search returned instead.

Run:  python -m scripts.inspect_misses
"""
import csv

from src.embeddings import embed_texts
from src.evaluation import page_number
from src.store import connect, search

GOLDEN_PATH = "data/golden.csv"
MISSES = ["q006", "q009", "q015", "q017"]
K = 5


def chunks_on_page(conn, source_doc: str, page: int) -> list[str]:
    """Return the text of every stored chunk from one page of one document.

    Answers question 1: did extraction produce readable text for the
    page the answer lives on?
    """
    # 1. Run this query with (source_doc, page) as the parameters:
    #    "SELECT text FROM chunks WHERE source_doc = %s AND page = %s "
    #    "ORDER BY chunk_index"
    # 2. Fetch all rows. Each row is a tuple with one item.
    rows = conn.execute("SELECT text FROM chunks WHERE source_doc = %s AND page = %s "
                        "ORDER BY  chunk_index", (source_doc, page),
    ).fetchall()
    # 3. Return a list of just the text strings.
    stored_chunks = []
    for row in rows:
        stored_chunks.append(row[0])
    return stored_chunks


def main() -> None:
    """For each missed question, print the right page's chunks, then what search returned."""
    # 1. Read GOLDEN_PATH into rows (same way as evaluate.py).
    rows = list(csv.DictReader(open(GOLDEN_PATH, encoding="utf-8-sig")))
    # 2. Open a connection.
    conn = connect()
    # 3. For each row whose id is in MISSES:
    for row in rows:
        if row["id"] in MISSES:
            expected_page = page_number(row["source_loc"])
    #    a. Print the id, question, source_doc and expected page.
            print(row["id"], row["question"], row["source_doc"], expected_page)
    #    b. Print every chunk from chunks_on_page for that doc + page.
            print(chunks_on_page(conn, row["source_doc"], expected_page))
    #    c. Embed the question, search with K.
            query_vector = embed_texts([row["question"]])[0]
            results = search(conn, query_vector, K)
    #    d. For each result, print its source_doc, page, score
    #       (2 decimals), and the first 150 characters of its text.
            for result in results:
                print(f"{result['source_doc']} p.{result['page']} | {result['score']:.2f} | {result['text'][:150]}")
    #    e. Print a separator line so questions don't run together.
            print("-" * 60)


if __name__ == "__main__":
    main()