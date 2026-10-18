"""Typos: is a phrase misspelt, and its most likely correction, by a spelling provider (CoreSpelling by default)."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Iterator
from itertools import combinations

import pandas as pd
import pymorphy3

from .. import datastore
from ..analysis.frequency import bundled_stopwords
from ..errors import InvalidArguments
from ..frame import Frame
from ..morph.lemmatizer import LEMMAS
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


def _known(key: str) -> bool:
    """A stopword, or a wordform the lemmatizer's dictionaries hold («москве», «угловые», «пружинном»)."""
    analyzer = datastore.once("pymorphy3", pymorphy3.MorphAnalyzer)
    return key in bundled_stopwords() or key in datastore.trie(LEMMAS) or analyzer.word_is_known(key)


def _deletes(word: str, distance: int) -> Iterator[str]:
    """The word with up to `distance` of its characters left out, the word itself too."""
    for count in range(min(distance, len(word)) + 1):
        for left_out in combinations(range(len(word)), count):
            yield "".join(char for place, char in enumerate(word) if place not in left_out)


class CoreSpelling:
    """A spelling provider that needs no network: the phrases it checks are the core whose words it learns.

    A word is misspelt when another word stands in at least `ratio` times as many phrases and differs from it by a
    few edits (Levenshtein): up to `distance`, and fewer for a short word, one per two letters after the first
    («диавн» → «диван» is 2 edits, «кит» → «кот» 1). A word with a digit, a stopword and a wordform the bundled
    dictionary or pymorphy3 knows are never misspelt. The correction starts with the same letter as the word; it is
    the nearest such word, then the most frequent, then the first alphabetically; words are compared by case and ё,
    and the correction is in lower case, spelt as it first stands in the phrases.
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
        corrections = {key: spelling[correction] for key, correction in self._corrections(frequency).items()}
        return [_misspelt(phrase, corrections) for phrase in words]

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
            if allowed and count * self.ratio <= most and not _known(key):
                near = {other for variant in set(_deletes(key, allowed)) for other in by_delete.get(variant, ())}
                correction = self._nearest(key, near, frequency, allowed)
                if correction is not None:
                    found[key] = correction
        return found

    def _nearest(self, key: str, near: set[str], frequency: Counter[str], allowed: int) -> str | None:
        """The nearest of the frequent words `near` the word, then the most frequent, then the first alphabetically.

        A correction starts with the letter of the word: a typo seldom hits the first letter, an abbreviation does not
        become another one («нпб» is not «спб»)."""
        least = frequency[key] * self.ratio
        ranked = [
            (edits, -frequency[other], other)
            for other in near
            if other[0] == key[0] and frequency[other] >= least and (edits := levenshtein(key, other)) <= allowed
        ]
        return min(ranked)[2] if ranked else None


def _misspelt(words: list[tuple[int, str]], corrections: dict[str, str]) -> list[Misspelling]:
    """The misspelt words of a phrase (its words with their offsets), each with its correction."""
    return [
        Misspelling(start, len(word), (corrections[key],))
        for start, word in words
        if (key := norm_phrase(word)) in corrections
    ]


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
    """true for a phrase with a misspelt word, false for the others.

    By default the words are learnt from the phrases given, so give the whole core: a word is misspelt when another word
    stands in at least 10 times as many phrases and differs from it by a few edits (up to 2, and one per two letters
    after the first for a short word: «диавн» → «диван»). A word with a digit, a stopword and a wordform the bundled
    dictionary or pymorphy3 knows («москве», «угловые») are never misspelt; a correction starts with the same letter
    as the word.
    provider: what finds the misspelt words: the core itself (the default), or a spelling server (LanguageTool).

    Example: {cli} read core.csv is-typo write -
    -> Диван-кровать 2 м!, false, 5; купить диван, false, 4; Диван купить, false, 3; купить   диван в москве!, false, 2; углы, false, 1; диван бесплатно, false, 6; диван www.sofa.ru диван, false, 7; отличный диван "Лион", false, 3; диван120см, false, 2; чехол на диван, false, 1; купить диван в москве, false, 2; диавн купить, true, 1; угловой диван, false, 2; диван недорого, false, 1
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

    The misspelt words are those of is-typo; the correction is the nearest such word, then the most frequent, starting
    with the same letter. A phrase with no misspelt word, or none that can be corrected, stays as it is.
    provider: what finds the misspelt words, as for is_typo.

    Example: {cli} read core.csv typo-correction write -
    -> Диван-кровать 2 м!, 5; купить диван, 4; Диван купить, 3; купить   диван в москве!, 2; углы, 1; диван бесплатно, 6; диван www.sofa.ru диван, 7; отличный диван "Лион", 3; диван120см, 2; чехол на диван, 1; купить диван в москве, 2; диван купить, 1; угловой диван, 2; диван недорого, 1
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
