"""`fix_word_order`: the words of a phrase in the order of a search query: definitions first, the main word, then the
complements («для гостиной»)."""

from __future__ import annotations

import re

import pandas as pd

from .. import datastore
from ..morph.functions import BUNDLED
from ..morph.lemmatizer import Lemmatizer, looks_like_adjective
from ..text.base import bundled_list, choice, collapse, split_words, word_key
from .common import WORD_ORDER, changed, one_word
from .insert import WordMover

__all__ = ["fix_word_order"]

# The form of the main word and the last letter of an adjective that agrees with it.
FORMS = {"masculine": "й", "feminine": "я", "feminine_accusative": "ю", "plural": "е"}
NOT_ADJECTIVES = frozenset({"n", "v", "advb", "p", "prep", "conj", "nv"})
NOUN = "n"
ADJECTIVE = "a"
COMPLEMENT_WORDS = 5  # a complement is a preposition and up to this many words after it, up to its last noun
_SIGNS = re.compile(r"[^\w\s]|_")


def _start_words(form: str) -> list[str]:
    if form == "masculine":
        return bundled_list("phrase_start_words")
    return datastore.table(WORD_ORDER)[f"phrase_start_words_{form}"]


def _is_noun(word: str, lemmatizer: Lemmatizer) -> bool:
    return any(lemmatizer.pos(part) == NOUN for part in _SIGNS.sub(" ", word).split())


def _is_adjective(word: str, lemmatizer: Lemmatizer) -> bool:
    pos = lemmatizer.pos(word)
    if pos == ADJECTIVE or pos in NOT_ADJECTIVES:
        return pos == ADJECTIVE
    return looks_like_adjective(lemmatizer.lemma(word))


class _Order:
    def __init__(self, form: str, main_word: str | None, complements: bool, lemmatizer: Lemmatizer) -> None:
        self._ending = FORMS[form]
        self._main = None if main_word is None else word_key(one_word("main_word", main_word))
        self._complements = complements
        self._lemmatizer = lemmatizer
        self._mover = WordMover(_start_words(form))
        self._prepositions = frozenset(map(word_key, datastore.table(WORD_ORDER)["prepositions"]))

    def _last_noun(self, words: list[str], start: int) -> int | None:
        """The last noun of the words after the preposition at `start`, up to the next preposition or the main word."""
        found = None
        for index in range(start + 1, min(start + COMPLEMENT_WORDS + 1, len(words))):
            if word_key(words[index]) in self._prepositions or word_key(words[index]) == self._main:
                break
            if _is_noun(words[index], self._lemmatizer):
                found = index
        return found

    def _split(self, words: list[str]) -> tuple[list[str], list[str]]:
        """The words of the phrase and its complements: each preposition with the words up to the last noun after it."""
        rest: list[str] = []
        complements: list[str] = []
        index = 0
        while index < len(words):
            last_noun = self._last_noun(words, index) if word_key(words[index]) in self._prepositions else None
            if last_noun is None:
                rest.append(words[index])
                index += 1
            else:
                complements += words[index : last_noun + 1]
                index = last_noun + 1
        return rest, complements

    def _adjectives_first(self, words: list[str]) -> list[str]:
        agree = [word.lower().endswith(self._ending) and _is_adjective(word, self._lemmatizer) for word in words]
        return [word for word, first in zip(words, agree, strict=True) if first] + [
            word for word, first in zip(words, agree, strict=True) if not first
        ]

    def __call__(self, phrase: str) -> str:
        words = split_words(phrase)
        if not self._complements:
            return " ".join(self._mover.moved(words, "start"))
        rest, complements = self._split(words)
        return collapse(" ".join([*self._mover.moved(self._adjectives_first(rest), "start"), *complements]))


def fix_word_order(
    data: pd.Series | pd.DataFrame,
    *,
    form: str = "masculine",
    main_word: str | None = None,
    complements: bool = True,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The words of the phrase in the order of a search query: «диван для гостиной раскладной кожаный» → «кожаный
    раскладной диван для гостиной».

    1. The complements go to the end: a preposition (для, с, без, в, из, на…) with the words after it up to the last
       noun among the next 5, stopping at the next preposition or at `main_word`.
    2. The adjectives that agree with the main word in `form` go first: masculine («кожаный»), feminine
       («кожаная»), feminine_accusative («кожаную»), plural («кожаные»).
    3. The words of the bundled list of words that start a query (где, купить, недорогой, кожаный…, in that form)
       go first, in the order of the list.

    main_word: the object of the query, one word (case and ё do not count): a complement never takes it.
    complements=False: only step 3. The words are joined by one space.
    """
    choice("form", form, tuple(FORMS))
    order = _Order(form, main_word, complements, lemmatizer)
    return changed(data, order, "fix_word_order", column, inplace)
