"""A minimal agent: the LLM decides whether to search again or answer."""

from src.generation import NO_ANSWER

SEARCH = "SEARCH"
ANSWER = "ANSWER"


def parse_action(reply: str) -> tuple[str, str]:
    """Read the LLM's reply and work out what it wants to do.

    "SEARCH: pH for shrimp"      -> ("SEARCH", "pH for shrimp")
    "ANSWER: 7.5 to 8.5 [1]"     -> ("ANSWER", "7.5 to 8.5 [1]")
    "The pH is 7.5"  (no prefix) -> ("ANSWER", "The pH is 7.5")

    The prefix is case-insensitive and surrounding whitespace is ignored.
    A reply with no recognised prefix is treated as a final answer — the
    model forgot the format, but it did reply, so don't throw it away.
    """
    # 1. Strip whitespace from both ends of reply.
    text = reply.strip()
    # 2. If the stripped text, uppercased, starts with "SEARCH:":
    #      return (SEARCH, everything after the "SEARCH:" part, stripped)
    if text.upper().startswith("SEARCH:"):
        return(SEARCH, text[len("SEARCH:"):].strip())
    # 3. Same check for "ANSWER:" → return (ANSWER, the rest, stripped)
    if text.upper().startswith("ANSWER:"):
        return(ANSWER, text[len("ANSWER:"):].strip())
    # 4. Otherwise return (ANSWER, the whole stripped text)
    return (ANSWER, text)

def agent_system_prompt() -> str:
    """The rules the agent works under.

    Must tell the model:
      - it answers aquaculture questions using a search tool over the documents
      - to search, reply with exactly one line: SEARCH: <query>
        (it may reword the query — e.g. expand abbreviations like PLs)
      - when the results are enough, reply: ANSWER: <answer>, using only the
        search results, citing the [n] labels
      - if it has searched and the answer still isn't there, reply:
        ANSWER: <NO_ANSWER>
    """
    return(
        f"you are an assistant that answers shrimp and fish farming questions from aquaculture manuals\n"
        f"for greetings or questions about yourself, you should reply {ANSWER}: with a short introduction, without searching\n"
        f"You are going to answer aquaculture questions using a search tool over the aquaculture documents\n"
        f"to search, reply with exactly one line: {SEARCH}: <query>\n"
        f"you can reword the query (expand abbreviations, use different terms) and search more than once if the results don't answer the question.\n"
        f"when the results are enough, reply: {ANSWER}: <answer>, using only the search results, citing the [n] labels\n"
        f"if you searched already and the answer isn't there, reply: {ANSWER}: {NO_ANSWER}\n"
        f"Every reply must start with {SEARCH}: or {ANSWER}: and contain nothing else before it."
    )

def format_results(results: list[dict], start: int) -> str:
    """Label results [start], [start+1], ... — numbering continues across searches.
    (Tier 2: same as your build_prompt, with a starting number.)"""
    blocks = []
    for n, r in enumerate(results, start=start):
        blocks.append(f"[{n}] ({r['source_doc']}, p. {r['page']})\n{r['text']}")
    return "Search results:\n\n" + "\n\n".join(blocks)


def run_agent(question: str, search, llm, max_steps: int = 3) -> tuple[str, list[dict]]:
    """Let the LLM search (possibly several times) and then answer.

    Args:
        question: The user's question.
        search:   function(query) -> list of result dicts
        llm:      function(messages) -> reply text
        max_steps: most LLM turns before giving up.

    Returns:
        (final answer text, every result shown to the LLM, in label order)
        Label [n] in the answer means gathered[n-1].
        If it never answers within max_steps: (NO_ANSWER, gathered).
    """
    # 1. Start the conversation: a list with two message dicts —
    #      role "system", content agent_system_prompt()
    #      role "user",   content f"Question: {question}"
    messages = [
        {"role": "system", "content": agent_system_prompt()},
        {"role": "user", "content": f"Question: {question}"}
    ]
    # 2. Make an empty list `gathered` for all results seen so far.
    gathered = []
    # 3. Repeat max_steps times:
    for step in range(max_steps):
    #    a. reply = llm(messages)
        reply = llm(messages)
    #    b. kind, content = parse_action(reply)
        kind, content = parse_action(reply)
    #    c. If kind is ANSWER: return (content, gathered)
        if kind == ANSWER:
            return (content, gathered)
    #    d. Otherwise it's a search: results = search(content) 
        results = search(content)
    #    e. observation = format_results(results, start=len(gathered) + 1)
    #       (do this BEFORE adding to gathered, so numbering continues)
        observation = format_results(results, start=len(gathered) + 1)
    #    f. Add results to gathered (gathered.extend(results))
        gathered.extend(results)
    #    g. Append two messages to the conversation:
    #         role "assistant", content reply         ← what the LLM said
    #         role "user",      content observation   ← what the search found
        messages.extend([
            {"role": "assistant", "content": reply},
            {"role": "user", "content": observation}
        ])
    # 4. Out of steps: return (NO_ANSWER, gathered)
    return (NO_ANSWER, gathered)