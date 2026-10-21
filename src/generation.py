"""Turn retrieved chunks into a cited answer, using the DeepSeek API."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
NO_ANSWER = "Not found in the provided documents."


def build_prompt(question: str, results: list[dict]) -> str:
    """Build the user message: labelled context chunks, then the question.

    Each result is rendered as a numbered block the model can cite:

        [1] (mpeda_2003_shrimp_health_extension.pdf, p. 27)
        Water temperature should be checked morning and evening...

    Args:
        question: The user's question.
        results: Search results, each with "text", "source_doc" and "page".

    Returns:
        One string: every labelled block, then the question.

    Raises:
        ValueError: If results is empty.
    """
    # 1. If results is empty, raise ValueError.
    if not results:
        raise ValueError("No search results to build a prompt from")
    # 2. Make an empty list to collect the rendered blocks.
    blocks = []
    # 3. For each result, with its position (enumerate):
    for position, result in enumerate(results):
        block = f"[{position+1}] ({result['source_doc']}, p. {result['page']})\n{result['text']}"
        blocks.append(block)
    #      - build a block string containing the label number
    #        (position + 1), the source_doc, the page, and the text
    #      - append it to the list
    # 4. Join the blocks together with a blank line between them.
    context = "\n\n".join(blocks)
    # 5. Return the joined blocks, then the question on its own line.
    return f"{context}\n\nQuestion: {question}"
    
    


def system_prompt() -> str:
    """The standing instructions sent with every request.

    Must tell the model to:
      - answer only from the numbered context, never from prior knowledge
      - cite the bracketed label after each claim, e.g. [2]
      - reply with exactly NO_ANSWER when the context doesn't answer it

    Returns:
        The instruction string. Must contain NO_ANSWER verbatim.
    """
    # Write the instructions as one string and return it. The wording is
    # yours; the three requirements above are not.
    return( 
        f"you are an assistant that answers shrimp and fish farming questions from aquaculture manuals\n"
        f"for greetings or questions about yourself, reply with a short introduction instead of {NO_ANSWER}\n"
        f"Answer only from the numbered context, do not use your own knowledge to answer.\n" 
        f"Cite the bracketed label after each claim.\n"
        f"if the answer is not present in the context provided then reply with exactly {NO_ANSWER}"
    )

def answer(question: str, results: list[dict]) -> str:
    """Ask DeepSeek the question, grounded in the retrieved chunks."""
    # 1. Read DEEPSEEK_API_KEY from the environment.
    key = os.getenv("DEEPSEEK_API_KEY")
    # 2. POST to API_URL with
    #      headers: Authorization set to "Bearer " plus the key
    #      json:    model, and messages — a list of two dicts: one with
    #               role "system" holding system_prompt(), one with role
    #               "user" holding build_prompt(question, results)
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt()},
                {"role": "user", "content": build_prompt(question, results)},
            ],
        },
    )
    # 3. Call resp.raise_for_status() so a bad status fails loudly.
    resp.raise_for_status()
    # 4. Return the content, using the expression you worked out.
    return resp.json()["choices"][0]["message"]["content"]

def chat_messages(messages: list[dict]) -> str:
    """Send a whole conversation to DeepSeek, return the reply text."""
    key = os.getenv("DEEPSEEK_API_KEY")
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {key}"},
        json={"model": MODEL, "messages": messages, "temperature": 0},
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def chat(system: str, user: str) -> str:
    """One system + one user message — the common case."""
    return chat_messages([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

def answer(question: str, results: list[dict]) -> str:
    """Ask DeepSeek the question, grounded in the retrieved chunks."""
    return chat(system_prompt(), build_prompt(question, results))