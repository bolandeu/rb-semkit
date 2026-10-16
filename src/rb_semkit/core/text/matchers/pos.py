"""Words by part of speech, through a Lemmatizer (the bundled one unless another is given)."""

from __future__ import annotations

from ...morph import Lemmatizer
from ...morph.functions import BUNDLED
from ..base import WordMatcher, choice, word_key

CODES = {"noun": "n", "adj": "a", "verb": "v", "adverb": "advb"}


class Pos(WordMatcher):
    def __init__(self, kind: str, lemmatizer: Lemmatizer | None) -> None:
        self._code = CODES[choice("kind", kind, tuple(CODES))]
        self._lemmatizer = lemmatizer or BUNDLED

    def picks(self, words: list[str]) -> list[bool]:
        keys = [word_key(word, ignore_punct=True) for word in words]
        return [bool(key) and self._lemmatizer.pos(key) == self._code for key in keys]


def pos(kind: str, *, lemmatizer: Lemmatizer | None = None) -> Pos:
    """Words of one part of speech: "noun", "adj", "verb" or "adverb" (a participle is none of them).

    lemmatizer: what gives the part of speech of a word; None is the bundled !SEMTools dictionary.
    """
    return Pos(kind, lemmatizer)
