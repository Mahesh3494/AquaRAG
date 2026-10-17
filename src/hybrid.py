"""Hybrid search: merge ranked result lists with Reciprocal Rank Fusion."""

RRF_K = 60


def chunk_id(result: dict) -> tuple:
    """The (source_doc, page, chunk_index) triple that identifies one chunk.

    Lets us recognise the same chunk when it appears in two lists.
    """
    # 1. Return a tuple of the result's source_doc, page and chunk_index,
    #    in that order.
    return ((result["source_doc"], result["page"], result["chunk_index"]))


def fuse(ranked_lists: list[list[dict]], k: int = 5) -> list[dict]:
    """Merge several best-first result lists into one, by RRF.

    Each chunk earns 1 / (RRF_K + position) from every list it appears in,
    position counting from 1. Points are summed across lists.

    Returns:
        The k chunks with the most points, best first. Each is a dict with
        text, source_doc, page, chunk_index, and "score" = its RRF total.
    """
    # 1. Make two empty dicts:
    #      totals  — chunk_id -> points so far
    #      chunks  — chunk_id -> that chunk's result dict (to rebuild later)
    totals = {}
    chunks = {}
    # 2. For each list in ranked_lists:
    for ranked in ranked_lists:
    #      for position, result in enumerate(that_list, start=1):
        for position, result in enumerate(ranked, start=1):
    #        - get its chunk_id
            cid = chunk_id(result)
    #        - add 1 / (RRF_K + position) to totals for that id
    #          (use totals.get(cid, 0) for "what it has so far, or 0 if new")
            totals[cid] = totals.get(cid, 0) + (1/(RRF_K + position))
    #        - store the result in chunks under that id
            chunks[cid] = result
    # 3. Build (total, cid) pairs from totals, sort highest first, keep k.
    pairs = []
    for cid, total in totals.items():
        pairs.append((total, cid))
    top = sorted(pairs, reverse=True)[:k]
    # 4. For each kept pair, build a result dict: the chunk's four keys
    #    plus "score": total. Return the list.
    results = []
    for total, cid in top:
        chunk = chunks[cid]
        results.append({
            "text": chunk["text"],
            "source_doc": chunk["source_doc"],
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
            "score": total
        })
    return results
    