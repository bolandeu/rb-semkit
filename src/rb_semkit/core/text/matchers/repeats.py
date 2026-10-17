"""Words repeated in a phrase: equal as written, or equal by lemma. The first occurrence stays (find and remove)."""

from __future__ import annotations

from collections.abc import Callable

from ...morph import Lemmatizer
from ...morph.functions import BUNDLED
from ..base import Matcher, WordMatcher, choice, word_key
from . import classes

__all__ = ["repeats"]

MODES = ("exact", "wordforms")
# Which words can repeat: the VBA tests the earlier word of a pair, which equals the later one.
SCOPES: dict[str, Callable[[str], object]] = {
    "all": bool,
    "adjacent": bool,
    "en": classes.has_latin,
    "ru": classes.has_cyrillic,
    "numbers": classes.is_numeric,
}


class Repeats(WordMatcher):
    extract = Matcher.extract

    def __init__(self, mode: str, scope: str, lemmatizer: Lemmatizer | None) -> None:
        self._wordforms = choice("mode", mode, MODES) == "wordforms"
        self._scope = choice("scope", scope, tuple(SCOPES))
        self._lemmatizer = lemmatizer or BUNDLED

    def _key(self, word: str) -> str:
        surface = word_key(word)
        if not surface or not SCOPES[self._scope](surface):
            return ""
        return self._lemmatizer.lemma(surface) if self._wordforms else surface

    def picks(self, words: list[str]) -> list[bool]:
        keys = [self._key(word) for word in words]
        if self._scope == "adjacent":
            return [bool(key) and index > 0 and keys[index - 1] == key for index, key in enumerate(keys)]
        seen: set[str] = set()
        picks = []
        for key in keys:
            picks.append(bool(key) and key in seen)
            seen.add(key)
        return picks


def repeats(mode: str = "exact", *, scope: str = "all", lemmatizer: Lemmatizer | None = None) -> Repeats:
    """Words that repeat an earlier word of the phrase (find and remove; remove keeps the first one).

    mode: "exact" — the same word (case and ё do not count, punctuation does: «диван, диван» has no repeat);
    "wordforms" — the same lemma.
    scope: "all" words; only "adjacent" repeats («диван диван»); only words with a latin ("en") or a cyrillic ("ru")
    letter («iphone13», «wi-fi-роутер»); only "numbers" («2», «1,5»).
    lemmatizer: for "wordforms"; None is the bundled one.

    ADR 0005: ё = е; split on any whitespace; lemmas in lower case.
    """
    return Repeats(mode, scope, lemmatizer)
