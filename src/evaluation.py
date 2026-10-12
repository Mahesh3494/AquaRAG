"""Metrics for scoring the RAG pipeline against the golden dataset."""
import re


def is_hit(results: list[dict], expected_doc: str, expected_page: int) -> bool:
    """Did retrieval return the expected page anywhere in its results?

    A hit means at least one result came from the expected document AND
    the expected page. Position in the list doesn't matter — that's what
    makes this hit rate rather than precision@1.

    Args:
        results: Search results, each with "source_doc" and "page".
        expected_doc: The golden row's source_doc.
        expected_page: The golden row's page number.

    Returns:
        True if any result matches both, False otherwise.
    """
    # 1. Walk the results.
    for result in results:
    # 2. For each one, check whether its source_doc equals expected_doc
    #    AND its page equals expected_page. If so, return True.
        if result["source_doc"] == expected_doc and result["page"] == expected_page:
            return True
    # 3. If the loop finishes with no match, return False.
    return False

def page_number(source_loc: str) -> int:
    """Pull the page number out of a source_loc string.

    "p. 11"                -> 11
    "p.17"                 -> 17
    "Section 3.1.2, p. 12" -> 12

    Raises:
        ValueError: If no page number can be found.
    """
    # 1. Use re.search with the pattern r"p\.\s*(\d+)" against source_loc.
    # 2. If there is no match, raise ValueError naming the offending string.
    # 3. Otherwise return the captured group, converted to an int.
    m = re.search(r"p\.\s*(\d+)", source_loc)
    if m is None:
        raise ValueError(f"No page number found, the exact data given is {source_loc}")
    return int(m.group(1))    