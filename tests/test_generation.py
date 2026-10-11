import pytest

from src.generation import NO_ANSWER, build_prompt, system_prompt

RESULTS = [
    {
        "text": "The optimal pH range for fish is from 6.5 to 8.5.",
        "source_doc": "fao_1993_water_quality_fish_health.pdf",
        "page": 12,
        "chunk_index": 0,
    },
    {
        "text": "Water temperature should be 28 to 32 C.",
        "source_doc": "mpeda_2003_shrimp_health_extension.pdf",
        "page": 27,
        "chunk_index": 3,
    },
]


def test_includes_the_question():
    prompt = build_prompt("What pH for fish?", RESULTS)
    assert "What pH for fish?" in prompt


def test_includes_every_chunk_text():
    prompt = build_prompt("q", RESULTS)
    for result in RESULTS:
        assert result["text"] in prompt


def test_labels_chunks_starting_from_one():
    prompt = build_prompt("q", RESULTS)
    assert "[1]" in prompt
    assert "[2]" in prompt
    assert "[0]" not in prompt


def test_includes_source_and_page_for_each_chunk():
    prompt = build_prompt("q", RESULTS)
    assert "fao_1993_water_quality_fish_health.pdf" in prompt
    assert "12" in prompt
    assert "mpeda_2003_shrimp_health_extension.pdf" in prompt
    assert "27" in prompt


def test_empty_results_raises():
    with pytest.raises(ValueError):
        build_prompt("q", [])


def test_system_prompt_contains_the_refusal_string():
    assert NO_ANSWER in system_prompt()