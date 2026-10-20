from src.agent import ANSWER, SEARCH, parse_action
from src.agent import agent_system_prompt
from src.generation import NO_ANSWER

def test_search():
    assert parse_action("SEARCH: pH for shrimp") == (SEARCH, "pH for shrimp")


def test_answer():
    assert parse_action("ANSWER: 7.5 to 8.5 [1]") == (ANSWER, "7.5 to 8.5 [1]")


def test_whitespace_around_everything():
    assert parse_action("  \nSEARCH:   pH for shrimp  \n") == (SEARCH, "pH for shrimp")


def test_lowercase_prefix():
    assert parse_action("search: pH for shrimp") == (SEARCH, "pH for shrimp")


def test_no_prefix_is_an_answer():
    assert parse_action("The pH is 7.5") == (ANSWER, "The pH is 7.5")


def test_multiline_answer_kept_whole():
    assert parse_action("ANSWER: line one\nline two") == (ANSWER, "line one\nline two")

def test_prompt_explains_both_moves():
    text = agent_system_prompt()
    assert "SEARCH:" in text and "ANSWER:" in text


def test_prompt_contains_no_answer_verbatim():
    assert NO_ANSWER in agent_system_prompt()