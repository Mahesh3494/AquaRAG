"""Score the LLM's answers: abstentions and citation accuracy.

Costs one DeepSeek call per golden question (~49 calls, a few cents).

Run:  python -m scripts.evaluate_generation
"""
import csv

from src.evaluation import cited_correct_page, is_hit, page_number, parse_citations
from src.generation import NO_ANSWER, answer
from src.keyword_search import keyword_search
from src.rerank import rerank
from src.store import connect, load_all_chunks

GOLDEN_PATH = "data/golden.csv"
K = 5
CANDIDATES = 20


def main() -> None:
    rows = list(csv.DictReader(open(GOLDEN_PATH, encoding="utf-8-sig")))
    conn = connect()
    chunks = load_all_chunks(conn)

    retrieved = abstained = cited_ok = cited_ok_when_retrieved = 0

    for row in rows:
        question = row["question"]
        candidates = keyword_search(chunks, question, CANDIDATES)
        results = rerank(question, candidates, K)
        text = answer(question, results)
        expected_page = page_number(row["source_loc"])

        # ── YOUR PART: three lines, each using a function or constant you have ──
        hit = is_hit(results, row["source_doc"], expected_page)            # did retrieval get the right page? (is_hit)
        refused = text.strip() == NO_ANSWER        # is the answer exactly NO_ANSWER? (strip it first)
        citations = parse_citations(text)      # the [n] numbers in the answer
        # ────────────────────────────────────────────────────────────────────────
        correct = cited_correct_page(citations, results, row["source_doc"], expected_page)

        retrieved += hit
        abstained += refused
        cited_ok += correct
        cited_ok_when_retrieved += hit and correct

        print(f"{row['id']}  retrieved={hit!s:5}  refused={refused!s:5}  cited_right={correct!s:5}  cites={citations}")

    n = len(rows)
    print()
    print(f"Retrieval hit@{K}:            {retrieved}/{n}")
    print(f"Abstained (wrongly):         {abstained}/{n}")
    print(f"Cited the right page:        {cited_ok}/{n}")
    print(f"  …when retrieval had it:    {cited_ok_when_retrieved}/{retrieved}")


if __name__ == "__main__":
    main()