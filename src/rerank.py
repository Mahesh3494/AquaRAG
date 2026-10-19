"""Rerank retrieved chunks with a cross-encoder."""
from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_model = None


def cross_encoder_scores(question: str, texts: list[str]) -> list[float]:
    """Score how well each text answers the question. Higher = better.

    Loads the model on first use (same lazy-loading idea as embeddings.py).
    """
    # ── Tier 2: given ──────────────────────────────────────────
    global _model
    if _model is None:
        _model = CrossEncoder(MODEL_NAME)
    pairs = []
    for text in texts:
        pairs.append((question, text))
    return list(_model.predict(pairs))
    # ───────────────────────────────────────────────────────────


def rerank(question: str, results: list[dict], k: int = 5,
           scorer=cross_encoder_scores) -> list[dict]:
    """Re-sort search results by a careful relevance score; keep the top k.

    Args:
        question: The user's question.
        results: Chunk dicts from a search (text, source_doc, page, chunk_index, score).
        k: How many to keep.
        scorer: Function (question, texts) -> one score per text.
                Defaults to the real cross-encoder; tests pass a fake.

    Returns:
        The k best results by scorer, best first. Each keeps its four
        metadata keys; "score" is replaced by the scorer's score.
    """
    # 1. Make a list of just the text of each result.
    texts = []
    for result in results:
        texts.append(result["text"])
    # 2. Call scorer(question, that list) to get one score per text.
    #    scores[i] belongs to results[i] — same order.
    scores = scorer(question, texts)
    # 3. Pair (score, i), sort highest first, keep the first k.
    pairs = []
    for i, score in enumerate(scores):
        pairs.append((score, i))
    top = sorted(pairs, reverse=True)[:k]
    # 4. For each kept pair, build a result dict: the four keys from
    #    results[i] plus "score". Return the list.
    reranked = []
    for score, i in top:
        result = results[i]
        reranked.append({
            "text": result["text"],
            "source_doc": result["source_doc"],
            "page": result["page"],
            "chunk_index": result["chunk_index"],
            "score": score,
        })
    return reranked
    