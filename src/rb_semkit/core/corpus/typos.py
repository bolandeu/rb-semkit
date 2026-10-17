"""Typos: is a phrase misspelt, and its most likely correction, by a spelling provider (CoreSpelling by default)."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Iterator
from itertools import combinations

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame
from ..normalize import norm_phrase
from ..text.base import whole_number
from .spelling import Misspelling, SpellingProvider

__all__ = ["CoreSpelling", "is_typo", "levenshtein", "typo_correction"]

_WORD = re.compile(r"\S+")
_DIGIT = re.compile(r"\d")


def levenshtein(first: str, second: str) -> int:
    """The fewest one-character edits (insert, delete, replace) that turn `first` into `second`; «а» and «0» differ."""
    if len(first) < len(second):
        first, second = second, first
    previous = list(range(len(second) + 1))
    for row, char in enumerate(first, start=1):
        current = [row]
        for column, other in enumerate(second, start=1):
            current.append(min(previous[column] + 1, current[-1] + 1, previous[column - 1] + (char != other)))
        previous = current
    return previous[-1]


def _deletes(word: str, distance: int) -> Iterator[str]:
    """The word with up to `distance` of its characters left out, the word itself too."""
    for count in range(min(distance, len(word)) + 1):
        for left_out in combinations(range(len(word)), count):
            yield "".join(char for place, char in enumerate(word) if place not in left_out)


class CoreSpelling:
    """A spelling provider that needs no network: the phrases it checks are the core whose words it learns.

    A word is misspelt when another word stands in at least `ratio` times as many phrases and differs from it by a
    few edits (Levenshtein): up to `distance`, and fewer for a short word, one per two letters after the first
    («диавн» → «диван» is 2 edits, «кит» → «кот» 1). A word with a digit is never misspelt. The correction is the
    nearest such word, then the most frequent, then the first alphabetically; words are compared by case and ё, and
    the correction is in lower case, spelt as it first stands in the phrases.
    """

    name = "core"

    def __init__(self, *, distance: int = 2, ratio: float = 10) -> None:
        self.distance = whole_number("distance", distance)
        if isinstance(ratio, bool) or not isinstance(ratio, int | float) or ratio < 1:
            raise InvalidArguments(f"ratio={ratio!r}; allowed: a number of 1 or more.")
        self.ratio = ratio

    def _allowed(self, word: str) -> int:
        return 0 if _DIGIT.search(word) else min(self.distance, (len(word) - 1) // 2)

    def check(self, phrases: list[str]) -> list[list[Misspelling]]:
        words = [[(match.start(), match.group()) for match in _WORD.finditer(phrase)] for phrase in phrases]
        spelling = {norm_phrase(word): word.lower() for phrase in reversed(words) for _, word in reversed(phrase)}
        frequency = Counter(key for phrase in words for key in {norm_phrase(word) for _, word in phrase})
        corrections = self._corrections(frequency)
        return [
            [
                Misspelling(start, len(word), (spelling[corrections[key]],))
                for start, word in phrase
                if (key := norm_phrase(word)) in corrections
            ]
            for phrase in words
        ]

    def _corrections(self, frequency: Counter[str]) -> dict[str, str]:
        """The correction of each misspelt word."""
        most = max(frequency.values(), default=0)
        by_delete: dict[str, list[str]] = defaultdict(list)
        for key, count in frequency.items():
            if count >= self.ratio:
                for variant in set(_deletes(key, self.distance)):
                    by_delete[variant].append(key)
        found = {}
        for key, count in frequency.items():
            allowed = self._allowed(key)
            if not allowed or count * self.ratio > most:
                continue
            near = {other for variant in set(_deletes(key, allowed)) for other in by_delete.get(variant, ())}
            ranked = [
                (edits, -frequency[other], other)
                for other in near
                if frequency[other] >= count * self.ratio and (edits := levenshtein(key, other)) <= allowed
            ]
            if ranked:
                found[key] = min(ranked)[2]
        return found


CORE = CoreSpelling()


def _misspellings(frame: Frame, provider: SpellingProvider) -> tuple[pd.Series, dict[str, list[Misspelling]]]:
    phrases = frame.phrases
    unique = list(phrases.unique())
    return phrases, dict(zip(unique, provider.check(unique), strict=True))


def is_typo(
    data: pd.Series | pd.DataFrame,
    *,
    provider: SpellingProvider = CORE,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """TRUE for a phrase with a misspelt word, FALSE for the others.

    provider: what finds the misspelt words. CoreSpelling (the default) learns the words from the phrases given, so
    give it the whole core; sk.LanguageTool asks a spelling server.
    """
    frame = Frame(data, column, inplace)
    phrases, found = _misspellings(frame, provider)
    return frame.put(phrases.map(lambda phrase: bool(found[phrase])).astype(bool), "is_typo")


def typo_correction(
    data: pd.Series | pd.DataFrame,
    *,
    provider: SpellingProvider = CORE,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each phrase with its misspelt words replaced by their most likely corrections («купить диавн» → «купить диван»).

    A phrase with no misspelt word, or none the provider can correct, stays as it is. provider: as for `is_typo`.
    """
    frame = Frame(data, column, inplace)
    phrases, found = _misspellings(frame, provider)

    def corrected(phrase: str) -> str:
        for misspelling in sorted(found[phrase], reverse=True):
            if misspelling.replacements:
                end = misspelling.offset + misspelling.length
                phrase = phrase[: misspelling.offset] + misspelling.replacements[0] + phrase[end:]
        return phrase

    return frame.put(phrases.map({phrase: corrected(phrase) for phrase in found}), "typo_correction")
