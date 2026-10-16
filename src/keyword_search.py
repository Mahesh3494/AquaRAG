"""Keyword (BM25) search over stored chunks."""
import re


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
    