"""Words by content: starts / ends / contains a pattern or a list; only or some latin letters or digits; mixed."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from ...errors import InvalidArguments
from ...normalize import norm_phrase
from ..base import WordMatcher, choice, word_key, word_list
from . import classes

TYPES: dict[str, Callable[[str], bool]] = {
    "only_latin": classes.only_latin,
    "has_latin": classes.has_latin,
    "only_digits": classes.is_numeric,
    "has_digits": classes.has_digit,
    "mixed": lambda word: classes.has_digit(word) and classes.has_cased(word),
}
PARTS: dict[str, Callable[[str, tuple[str, ...]], bool]] = {
    "starts": lambda key, patterns: key.startswith(patterns),
    "ends": lambda key, patterns: key.endswith(patterns),
    "contains": lambda key, patterns: any(pattern in key for pattern in patterns),
}


class WordContent(WordMatcher):
    def __init__(self, kind: str, pattern: str | Iterable[str] | None) -> None:
        choice("kind", kind, (*PARTS, *TYPES))
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


def word_content(kind: str, pattern: str | Iterable[str] | None = None) -> WordContent:
    """Words by what they hold; a word is tested as written, with its punctuation («красный,» does not end in «ный»).

    kind: "starts", "ends", "contains" (with `pattern`: a word part or a list of them, any one is enough; case and
    ё do not count); "only_latin" (a latin letter, no digit and no Russian letter: «IKEA», «Wi-Fi»); "has_latin";
    "only_digits" (a number: «2», «1,5», «-5»); "has_digits"; "mixed" (a digit and a letter: «iphone15»).

    VBA (RibbonCallbacks.vba):
        find: `—ka—` (line 2082) starts, `—kaa` (line 2225) starts a list, `—kao` (line 2670) ends, `—ka–`
        (line 2759) ends a list, `—kk—` (line 2556) contains a list; contains one pattern: no VBA handler
        (`SEM_findCellsContainingPattern` is missing): derived from `—kk—` (line 2556); the kinds of characters:
        no VBA handler: derived from their remove and extract handlers.
        remove: `aoaa` (line 2653) starts, `aoa·` (line 1762) starts a list, `aoa–` (line 1887) ends, `aoa—`
        (line 2706) ends a list, `aoak` (line 2901) contains, `aoao` (lines 2183–2185) contains a list, `a·—–`
        (line 2456) only_latin, `a·a–` (line 2336) has_latin, `a·——` (line 2780) only_digits, `a·a—` (line 1864)
        has_digits; mixed: no VBA handler: derived from `a·o–` (line 2916).
        extract: `–·–a` (line 1903) starts, `–·–·` (line 2513) starts a list, `–·––` (line 1816) ends, `–·–—`
        (line 2330) ends a list, `–·k·` (line 2156) contains a list, `——·–` (line 2107) only_latin, `–—k—`
        (line 2442) has_latin, `——·—` (line 2127) only_digits, `–—k–` (line 2416) has_digits, `a·o–` (line 2916)
        mixed; contains one pattern: no VBA handler: derived from `–·k·` (line 2156).
    ADR 0005: ё = е in the patterns; split on any whitespace; blank list items are refused.
    """
    return WordContent(kind, pattern)
