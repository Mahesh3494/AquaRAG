from src.agent import ANSWER, SEARCH, agent_system_prompt, parse_action, run_agent
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

def r(text, page):
    return {"text": text, "source_doc": "a.pdf", "page": page, "chunk_index": 0, "score": 0.0}


def make_llm(replies, seen):
    """A fake LLM that gives scripted replies in order, recording what it was sent."""
    def llm(messages):
        seen.append(list(messages))
        return replies.pop(0)
    return llm


def make_search(queries):
    """A fake search that records each query and returns one result."""
    def search(query):
        queries.append(query)
        return [r(f"text about {query}", len(queries))]
    return search


def test_answers_without_searching():
    answer, gathered = run_agent("hi", make_search([]), make_llm(["ANSWER: hello"], []))
    assert answer == "hello"
    assert gathered == []


def test_one_search_then_answer():
    queries = []
    answer, gathered = run_agent("pH?", make_search(queries),
                                 make_llm(["SEARCH: shrimp pH", "ANSWER: 7.5 [1]"], []))
    assert answer == "7.5 [1]"
    assert queries == ["shrimp pH"]          # searched with the LLM's own wording
    assert len(gathered) == 1


def test_second_search_continues_numbering():
    seen = []
    run_agent("q", make_search([]),
              make_llm(["SEARCH: a", "SEARCH: b", "ANSWER: done"], seen))
    last_message = seen[2][-1]["content"]    # what the LLM saw before its 3rd reply
    assert "[2]" in last_message
    assert "[1]" not in last_message


def test_conversation_grows():
    seen = []
    run_agent("q", make_search([]), make_llm(["SEARCH: a", "ANSWER: done"], seen))
    roles = [m["role"] for m in seen[1]]     # messages sent on the 2nd call
    assert roles == ["system", "user", "assistant", "user"]


def test_gives_up_after_max_steps():
    answer, gathered = run_agent("q", make_search([]),
                                 make_llm(["SEARCH: a", "SEARCH: b"], []), max_steps=2)
    assert answer == NO_ANSWER
    assert len(gathered) == 2