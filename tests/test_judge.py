from src.judge import CORRECT, INCORRECT, build_judge_prompt, judge_system_prompt, parse_verdict


def test_system_prompt_names_both_verdicts():
    text = judge_system_prompt()
    assert CORRECT in text and INCORRECT in text


def test_judge_prompt_contains_all_three_texts():
    p = build_judge_prompt("What pH?", "7.5 to 8.5", "Keep it at 7.5-8.5 [1]")
    assert "What pH?" in p and "7.5 to 8.5" in p and "Keep it at 7.5-8.5 [1]" in p


def test_parse_correct():
    assert parse_verdict("CORRECT") is True


def test_parse_tolerates_case_space_and_period():
    assert parse_verdict("  correct.\n") is True


def test_parse_incorrect_is_false():
    assert parse_verdict("INCORRECT") is False


def test_parse_garbage_is_false():
    assert parse_verdict("I think it's mostly right") is False