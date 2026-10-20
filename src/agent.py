"""A minimal agent: the LLM decides whether to search again or answer."""

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