"""Words by position: the first or last N, the N-th, the leading words up to the middle or within N characters."""

from __future__ import annotations

from collections.abc import Callable

from ...errors import InvalidArguments
from ..base import WordMatcher, whole_number


def _within(words: list[str], limit: int) -> list[bool]:
    """`o·—` (line 1403): the leading words while the phrase so far has `limit` characters at most; the first always."""
    picked: list[bool] = []
    length = -1
    for word in words:
        length += len(word) + 1
        picked.append(not picked or (picked[-1] and length <= limit))
    return picked


def _by_index(test: Callable[[int, int], bool]) -> Callable[[list[str]], list[bool]]:
    """Picks by (index of the word from 0, number of words)."""
    return lambda words: [test(index, len(words)) for index in range(len(words))]


# the words picked, by selector and its N
SELECTORS: dict[str, Callable[[int], Callable[[list[str]], list[bool]]]] = {
    "first": lambda n: _by_index(lambda index, count: index < n),
    "last": lambda n: _by_index(lambda index, count: index >= count - n),
    "nth": lambda n: _by_index(lambda index, count: index == n - 1),
    "to_middle": lambda n: lambda words: _within(words, len(" ".join(words)) // 2),
    "at_most": lambda n: lambda words: _within(words, n),
}


class WordPosition(WordMatcher):
    def __init__(self, given: dict[str, int | bool | None]) -> None:
        chosen = {name: value for name, value in given.items() if value is not None and value is not False}
        if len(chosen) != 1:
            raise InvalidArguments(
                f"word_position: {sorted(chosen) or 'none'} given; allowed: exactly one of {', '.join(SELECTORS)}."
            )
        ((name, value),) = chosen.items()
        self._selects = SELECTORS[name](1 if value is True else whole_number(name, value))

    def picks(self, words: list[str]) -> list[bool]:
        return self._selects(words)


def word_position(
    *,
    first: int | None = None,
    last: int | None = None,
    nth: int | None = None,
    to_middle: bool = False,
    at_most: int | None = None,
) -> WordPosition:
    """Words by their place in the phrase; give exactly one argument, N counts from 1.

    first / last: the first or last N words. nth: the N-th word. to_middle / at_most: the leading words while they
    hold half the characters of the phrase at most, or N characters at most, and always the first word
    («купить диван недорого» with at_most=12 → «купить диван»). remove gives the other words.

    VBA (RibbonCallbacks.vba):
        remove: `ak—k` (line 2081), `ak—o` (line 2659), `ak—–` (line 2485), `ak—a` (line 2939) first;
        `aka—` (line 1940), `ak·o` (line 2270) and the other «Последние» buttons last; nth, to_middle, at_most: no
        VBA handler: derived from `k·k` (line 1851) and `o·—` (line 1403), the words extract would not give.
        extract: `–—a—` (line 1877), `–—·—` (line 1828) first; `–ak–` (line 1778), `–aok` (line 2137) last;
        `–—oo` (line 2847), `–a–k` (line 1850) nth (the 1st word is `–—a—`); `–·—k` (line 1599) to_middle and
        `–·—o` (line 1612) at_most, both with `o·—` (line 1403).
        find: no VBA handler: derived from the extract handlers.
    ADR 0005: split on any whitespace, so empty words never count.
    """
    return WordPosition(
        {"first": first, "last": last, "nth": nth, "to_middle": to_middle, "at_most": at_most},
    )
