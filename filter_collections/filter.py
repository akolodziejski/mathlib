def apply_filter(collection, matchers) -> list:
    """Return elements from collection where ALL matchers return True.

    Args:
        collection: Any iterable. Raises TypeError if None.
        matchers: List of Matcher instances. Empty list returns all elements.

    Returns:
        A plain list of elements that passed all matchers.
    """
    if collection is None:
        raise TypeError("collection cannot be None")
    if not matchers:
        return list(collection)
    return [el for el in collection if all(m.match(el) for m in matchers)]
