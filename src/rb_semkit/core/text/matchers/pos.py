"""Words by part of speech, through a Lemmatizer (the bundled one unless another is given)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal, get_args

from ...morph import Lemmatizer
from ...morph.functions import BUNDLED
from ...morph.lemmatizer import looks_like_adjective
from ..base import WordMatcher, choice

__all__ = ["pos"]

CODES = {"noun": "n", "verb": "v", "adverb": "advb"}
# `··o` (line 1439): a word with one of these codes is no adjective, whatever its lemma looks like
NOT_ADJECTIVES = frozenset({"n", "v", "advb", "p", "prep", "conj", "nv"})
PartOfSpeech = Literal["noun", "adj", "verb", "adverb"]
KINDS = get_args(PartOfSpeech)


class Pos(WordMatcher):
    def __init__(self, kind: PartOfSpeech, lemmatizer: Lemmatizer | None) -> None:
        self._lemmatizer = lemmatizer or BUNDLED
        self._test: Callable[[str], bool] = (
            self._is_adjective if choice("kind", kind, KINDS) == "adj" else self._has_code(CODES[kind])
        )

    def _has_code(self, code: str) -> Callable[[str], bool]:
        return lambda word: self._lemmatizer.pos(word.lower()) == code

    def _is_adjective(self, word: str) -> bool:
        """The code «a»; else, but for the codes of NOT_ADJECTIVES, a lemma that ends like an adjective.

        A word with a capital is looked up in lower case, as for the other parts of speech (the add-in looks it up as
        written, finds no code and takes «Быстро» for an adjective and an adverb at once).
        """
        code = self._lemmatizer.pos(word.lower())
        if code == "a":
            return True
        return code not in NOT_ADJECTIVES and looks_like_adjective(self._lemmatizer.lemma(word.lower()))

    def picks(self, words: list[str]) -> list[bool]:
        return [self._test(word) for word in words]


def pos(kind: PartOfSpeech, *, lemmatizer: Lemmatizer | None = None) -> Pos:
    """Words of one part of speech: "noun", "adj", "verb" or "adverb" (a participle is none of them).

    A word is looked up as written, with its punctuation («диван,» is not a noun). An adjective is a word coded «a»,
    or a word with no code, a pronoun or a particle whose lemma ends like an adjective («какой»); a word with a
    capital is looked up by that rule only («Быстро» is an adjective, as in the add-in).
    lemmatizer: what gives the part of speech and the lemma of a word; None is the bundled !SEMTools dictionary.

    ADR 0005: split on any whitespace; ё = е in the lookup.
    """
    return Pos(kind, lemmatizer)
