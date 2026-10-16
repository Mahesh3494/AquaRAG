from src.keyword_search import tokenize


def test_lowercases():
    assert tokenize("Bleaching Powder") == ["bleaching", "powder"]


def test_punctuation_separates_words():
    assert tokenize("pH (>8.5) high.") == ["ph", "8", "5", "high"]


def test_hyphen_separates():
    assert tokenize("5-7 days") == ["5", "7", "days"]


def test_empty_string_gives_empty_list():
    assert tokenize("") == []


def test_newlines_are_separators():
    assert tokenize("white\nfeces") == ["white", "feces"]