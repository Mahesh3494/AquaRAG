"""Keyword (BM25) search over stored chunks."""
import re

from rank_bm25 import BM25Okapi

def tokenize(text: str) -> list[str]:
    """Split text into lowercase words for keyword matching.

    "Bleaching Powder"  -> ["bleaching", "powder"]
    "pH (>8.5) high."   -> ["ph", "8", "5", "high"]
    "5-7 days"          -> ["5", "7", "days"]

    Anything that isn't a letter or digit is a separator.
    """
    # 1. Make the text lowercase.
    lower_case = text.lower()
    # 2. Use re.findall with the pattern r"[a-z0-9]+" to pull out
    #    every run of letters/digits as a list.
    words = re.findall(r"[a-z0-9]+", lower_case)
    # 3. Return that list.
    return words
    

def keyword_search(chunks: list[dict], question: str, k: int = 5) -> list[dict]:
    """Rank chunks by BM25 keyword score against the question.

    Args:
        chunks: Chunk dicts, each with text, source_doc, page, chunk_index.
        question: The user's question.
        k: How many results to return.

    Returns:
        The k highest-scoring chunks, best first. Each is a copy of the
        chunk dict with an added "score" key (the BM25 score).
    """
    # 1. Tokenize every chunk's text, giving a list of word-lists.
    tokenized_chunks = []
    for chunk in chunks:
        tokenized_chunks.append(tokenize(chunk["text"]))
    # 2. Build the index: BM25Okapi(that list of word-lists).
    index = BM25Okapi(tokenized_chunks)
    # 3. Tokenize the question.
    question_words = tokenize(question)
    # 4. Get one score per chunk: index.get_scores(question_words).
    #    scores[i] is the score for chunks[i] — same order.
    scores = index.get_scores(question_words)
    # 5. Pair each chunk with its score, sort by score highest first,
    #    keep the first k.
    pairs = []
    for i, score in enumerate(scores):
        pairs.append((score, i))
    top = sorted(pairs, reverse=True)[:k]
    # 6. For each kept pair, build a result dict: the chunk's four keys
    #    plus "score". Return the list.
    results = []
    for score, i in top:
        chunk = chunks[i]
        results.append({
            "text": chunk["text"],
            "source_doc": chunk["source_doc"],
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
            "score": score
        })
    return results
    