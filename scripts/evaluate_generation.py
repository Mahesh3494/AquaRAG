"""Score the LLM's answers: abstentions and citation accuracy.

Costs one DeepSeek call per golden question (~49 calls, a few cents).

Run:  python -m scripts.evaluate_generation
"""
import csv

from src.evaluation import cited_correct_page, is_hit, page_number, parse_citations
from src.generation import NO_ANSWER, answer, chat_messages
from src.keyword_search import keyword_search
from src.rerank import rerank
from src.store import connect, load_all_chunks
from src.judge import judge
from src.agent import run_agent
from src.pipeline import make_real_search

GOLDEN_PATH = "data/golden.csv"
K = 5
CANDIDATES = 20
MODE = "agent"   # "pipeline" or "agent"


def main() -> None:
    rows = list(csv.DictReader(open(GOLDEN_PATH, encoding="utf-8-sig")))
    conn = connect()
    chunks = load_all_chunks(conn)
    search = make_real_search(chunks, K)
    total_searches = 0

    retrieved = abstained = cited_ok = cited_ok_when_retrieved = judged_correct = 0

    for row in rows:
        question = row["question"]
        if MODE == "pipeline":
            candidates = keyword_search(chunks, question, CANDIDATES)
            results = rerank(question, candidates, K)
            text = answer(question, results)
        else:
            text, results = run_agent(question, search, chat_messages)
            total_searches += len(results) // K
        expected_page = page_number(row["source_loc"])

        # ── YOUR PART: three lines, each using a function or constant you have ──
        hit = is_hit(results, row["source_doc"], expected_page)            # did retrieval get the right page? (is_hit)
        refused = text.strip() == NO_ANSWER        # is the answer exactly NO_ANSWER? (strip it first)
        citations = parse_citations(text)      # the [n] numbers in the answer
        # ────────────────────────────────────────────────────────────────────────
        correct = cited_correct_page(citations, results, row["source_doc"], expected_page)
        if refused:
            right = False                       # a refusal is never a right answer — skip the API call
        else:
            right = judge(question, row["answer"], text)
        judged_correct += right

        retrieved += hit
        abstained += refused
        cited_ok += correct
        cited_ok_when_retrieved += hit and correct

        print(f"{row['id']}  judge={right!s:5}  cited_right={correct!s:5}")
        print(f"    golden: {row['answer']}")
        print(f"    model:  {text[:200]}")

    n = len(rows)
    print()
    print(f"Retrieval hit@{K}:            {retrieved}/{n}")
    print(f"Abstained (wrongly):         {abstained}/{n}")
    print(f"Cited the right page:        {cited_ok}/{n}")
    print(f"  …when retrieval had it:    {cited_ok_when_retrieved}/{retrieved}")
    print(f"Judge says correct:          {judged_correct}/{n}")
    print(f"Searches per question:       {total_searches / n:.1f}")


if __name__ == "__main__":
    main()