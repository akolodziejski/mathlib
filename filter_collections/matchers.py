import re
import random
import operator
from abc import ABC, abstractmethod

_OPS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


class Matcher(ABC):
    @abstractmethod
    def match(self, element) -> bool: ...


class SizeMatcher(Matcher):
    """Matches elements where len(element) <op> size.

    Args:
        op: Comparison operator string: '>', '>=', '<', '<=', '==', '!='
        size: Integer threshold to compare against len(element)
    """

    def __init__(self, op: str, size: int):
        if op not in _OPS:
            raise ValueError(f"Unsupported operator '{op}'. Use one of {list(_OPS)}")
        if not isinstance(size, int):
            raise TypeError("size must be an int")
        self._op = _OPS[op]
        self._size = size

    def match(self, element) -> bool:
        if element is None:
            return False
        try:
            return self._op(len(element), self._size)
        except TypeError:
            return False


class PatternMatcher(Matcher):
    """Matches string elements against a regex pattern.

    Args:
        pattern: Regular expression string. Raises re.error if invalid.
    """

    def __init__(self, pattern: str):
        self._regex = re.compile(pattern)

    def match(self, element) -> bool:
        if not isinstance(element, str):
            return False
        return bool(self._regex.search(element))


class RandomMatcher(Matcher):
    """Randomly passes or rejects elements based on a probability.

    Args:
        probability: Integer or float in range [0, 100].
                     0 = always True (pass all), 100 = always False (reject all).
                     Higher values increase the chance of rejection.
    """

    def __init__(self, probability):
        if not isinstance(probability, (int, float)):
            raise TypeError("probability must be a number")
        if not (0 <= probability <= 100):
            raise ValueError("probability must be between 0 and 100")
        self._probability = probability

    def match(self, element) -> bool:
        return random.random() >= self._probability / 100
