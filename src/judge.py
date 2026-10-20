"""LLM-as-judge: does a model answer match the reference answer?"""
from src.generation import chat

CORRECT = "CORRECT"
INCORRECT = "INCORRECT"


def judge_system_prompt() -> str:
    """Instructions for the judge.

    Must tell the model to:
      - compare the candidate answer to the reference answer for the question
      - count it correct if it states the same key facts (wording may differ;
        extra true detail is fine; missing or wrong key facts are not)
      - reply with exactly CORRECT or INCORRECT and nothing else
    """
    # Your wording, like system_prompt() — interpolate CORRECT and INCORRECT.
    return (
        f"compare the candidate answer to the reference answer for the question\n"
        f"Answer {CORRECT} if the candidate states the same key facts as the reference, wording may differ, extra true details is fine but missing or wrong key facts are not fine so mark them as {INCORRECT}\n"
        f"reply with exactly {CORRECT} or {INCORRECT} and nothing else"
    )


def build_judge_prompt(question: str, reference: str, candidate: str) -> str:
    """The user message: the three texts, clearly labelled."""
    # Return one string with three labelled parts, e.g.
    #   Question: ...
    #   Reference answer: ...
    #   Candidate answer: ...
    return (
        f"Question: {question}\n"
        f"Reference answer: {reference}\n"
        f"Candidate answer: {candidate}\n"
    )
    


def parse_verdict(reply: str) -> bool:
    """True only if the judge's reply is CORRECT.

    Tolerate surrounding whitespace, lowercase, and a trailing full stop.
    Anything else — including INCORRECT — is False.
    """
    # 1. Clean the reply: strip whitespace, remove a trailing ".", uppercase.
    cleaned = reply.strip().rstrip(".").upper()
    # 2. Return whether it equals CORRECT.
    return cleaned == CORRECT

def judge(question: str, reference: str, candidate: str) -> bool:
    """Ask the LLM judge; True if it says CORRECT."""
    reply = chat(judge_system_prompt(), build_judge_prompt(question, reference, candidate))
    return parse_verdict(reply)