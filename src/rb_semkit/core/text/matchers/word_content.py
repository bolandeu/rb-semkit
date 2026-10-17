"""Words by content: starts / ends / contains a pattern or a list; only or some latin letters or digits; mixed."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Literal, get_args

from ...errors import InvalidArguments
from ...normalize import norm_phrase
from ..base import WordMatcher, choice, word_key, word_list
from . import classes

__all__ = ["word_content"]

ContentKind = Literal[
    "starts", "ends", "contains", "only_latin", "has_latin", "only_digits", "has_digits", "mixed"
]  # fmt: skip
TYPES: dict[ContentKind, Callable[[str], bool]] = {
    "only_latin": classes.only_latin,
    "has_latin": classes.has_latin,
    "only_digits": classes.is_numeric,
    "has_digits": classes.has_digit,
    "mixed": lambda word: classes.has_digit(word) and classes.has_cased(word),
}
PARTS: dict[ContentKind, Callable[[str, tuple[str, ...]], bool]] = {
    "starts": lambda key, patterns: key.startswith(patterns),
    "ends": lambda key, patterns: key.endswith(patterns),
    "contains": lambda key, patterns: any(pattern in key for pattern in patterns),
}


class WordContent(WordMatcher):
    def __init__(self, kind: ContentKind, pattern: str | Iterable[str] | None) -> None:
        choice("kind", kind, get_args(ContentKind))
        if kind in PARTS:
            if pattern is None:
                raise InvalidArguments(
                    f"pattern: not given for kind={kind!r}; allowed: a word part or a non-empty list of them."
                )
            patterns = tuple(norm_phrase(item) for item in word_list("pattern", pattern))
            self._test: Callable[[str], bool] = lambda word: PARTS[kind](word_key(word), patterns)
        else:
            self._test = TYPES[kind]

    def picks(self, words: list[str]) -> list[bool]:
        return [self._test(word) for word in words]


def word_content(kind: ContentKind, pattern: str | Iterable[str] | None = None) -> WordContent:
    """Words by what they hold; a word is tested as written, with its punctuation («красный,» does not end in «ный»).

    kind: "starts", "ends", "contains" (with `pattern`: a word part or a list of them, any one is enough; case and
    ё do not count); "only_latin" (a latin letter, no digit and no Russian letter: «IKEA», «Wi-Fi»); "has_latin";
    "only_digits" (a number: «2», «1,5», «-5»); "has_digits"; "mixed" (a digit and a letter: «iphone15»).

    ADR 0005: ё = е in the patterns; split on any whitespace; blank list items are refused.
    """
    return WordContent(kind, pattern)
