"""Words repeated in a phrase: equal as written, or equal by lemma. The first occurrence stays (find and remove)."""

from __future__ import annotations

import re
from collections.abc import Callable

from ...morph import Lemmatizer
from ...morph.functions import BUNDLED
from ..base import Matcher, WordMatcher, choice, word_key

MODES = ("exact", "wordforms")
SCOPES: dict[str, Callable[[str], object]] = {
    "all": bool,
    "adjacent": bool,
    "en": re.compile("[a-z]+").fullmatch,
    "ru": re.compile("[а-я]+").fullmatch,
    "numbers": re.compile("[0-9]+").fullmatch,
}


class Repeats(WordMatcher):
    extract = Matcher.extract

    def __init__(self, mode: str, scope: str, lemmatizer: Lemmatizer | None) -> None:
        self._wordforms = choice("mode", mode, MODES) == "wordforms"
        self._scope = choice("scope", scope, tuple(SCOPES))
        self._lemmatizer = lemmatizer or BUNDLED

    def _key(self, word: str) -> str:
        surface = word_key(word, ignore_punct=True)
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

    mode: "exact" — the same word (case, ё and punctuation at the edges do not count); "wordforms" — the same lemma.
    scope: "all" words; only "adjacent" repeats («диван диван»); only latin ("en") or cyrillic ("ru") words;
    only "numbers".
    lemmatizer: for "wordforms"; None is the bundled one.
    """
    return Repeats(mode, scope, lemmatizer)
