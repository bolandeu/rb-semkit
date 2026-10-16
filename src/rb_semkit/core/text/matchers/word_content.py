"""Words by content: starts / ends / contains a pattern or a list; only or some latin letters or digits; mixed."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable

from ...errors import InvalidArguments
from ...normalize import norm_phrase
from ..base import WordMatcher, choice, word_key, word_list

LATIN = re.compile("[a-z]")
DIGIT = re.compile("[0-9]")
LETTER = re.compile(r"[^\W\d_]")
TYPES: dict[str, Callable[[str], object]] = {
    "only_latin": re.compile("[a-z]+").fullmatch,
    "has_latin": LATIN.search,
    "only_digits": re.compile("[0-9]+").fullmatch,
    "has_digits": DIGIT.search,
    "mixed": lambda key: bool(LETTER.search(key) and DIGIT.search(key)),
}
PARTS: dict[str, Callable[[str, tuple[str, ...]], bool]] = {
    "starts": lambda key, patterns: key.startswith(patterns),
    "ends": lambda key, patterns: key.endswith(patterns),
    "contains": lambda key, patterns: any(pattern in key for pattern in patterns),
}


class WordContent(WordMatcher):
    def __init__(self, kind: str, pattern: str | Iterable[str] | None) -> None:
        choice("kind", kind, (*PARTS, *TYPES))
        self._patterns: tuple[str, ...] = ()
        if kind in PARTS:
            if pattern is None:
                raise InvalidArguments(
                    f"pattern: not given for kind={kind!r}; allowed: a word part or a non-empty list of them."
                )
            self._patterns = tuple(norm_phrase(item) for item in word_list("pattern", pattern))
            self._test = lambda key: PARTS[kind](key, self._patterns)
        else:
            self._test = TYPES[kind]

    def picks(self, words: list[str]) -> list[bool]:
        return [bool(self._test(word_key(word, ignore_punct=True))) for word in words]


def word_content(kind: str, pattern: str | Iterable[str] | None = None) -> WordContent:
    """Words by what they hold; case and ё do not count.

    kind: "starts", "ends", "contains" (with `pattern`: a word part or a list of them, any one is enough);
    "only_latin", "has_latin", "only_digits", "has_digits"; "mixed" (letters and digits in one word, «iphone15»).
    """
    return WordContent(kind, pattern)
