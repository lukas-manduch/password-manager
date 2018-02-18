def _get_longest_match(search_for: str, search_in: str):
    """Look for SEARCH_FOR in beginning of SEARCH_IN.
    Returns length of match
    """
    search_for = str(search_for).casefold()
    search_in = str(search_in).casefold()
    length = min(len(search_in), len(search_for))
    for i in range(length):
        if search_for[i] != search_in[i]:
            return i
    return length

