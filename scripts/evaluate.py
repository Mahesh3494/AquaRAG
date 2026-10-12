"""Score retrieval against the golden dataset.

No LLM calls — this measures retrieval only, so it's free and fast.

Run:  python -m scripts.evaluate
"""
import csv

from src.embeddings import embed_texts
from src.evaluation import is_hit, page_number
from src.store import connect, search

GOLDEN_PATH = "data/golden.csv"
K = 5


def main() -> None:
    """Run every golden question through retrieval and report hit rate."""
    # 1. Read GOLDEN_PATH with csv.DictReader, encoding="utf-8-sig",
    #    into a list of rows.
    rows = list(csv.DictReader(open(GOLDEN_PATH, encoding="utf-8-sig")))
    # 2. Open a database connection with connect().
    conn = connect()
    # 3. Make a counter for hits, starting at 0.
    hits = 0
    # 4. For each row:
    for row in rows:
    #    a. Embed row["question"] and take the single vector out.
        query_vector = embed_texts([row["question"]])[0]
    #    b. Search with that vector and K.
        results = search(conn, query_vector, K)
    #    c. Get the expected page from row["source_loc"] via page_number().
        expected_page = page_number(row["source_loc"])
    #    d. Call is_hit with the results, row["source_doc"] and that page.
        ishit = is_hit(results, row["source_doc"], expected_page)
    #    e. If it's a hit, add one to the counter.
        if ishit == True:
            hits = hits+1
    #    f. Print the row's id and whether it hit, so misses are visible.
        print(row["id"], ishit)
    # 5. After the loop, print the total: how many hits out of how many
    #    rows, and the percentage.
    percentage = (hits/len(rows))*100
    print(f"Hit rate: {hits}/{len(rows)} ({percentage:.1f}%)")

if __name__ == "__main__":
    main()