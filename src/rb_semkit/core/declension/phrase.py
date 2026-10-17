"""Everything that declines in a phrase: its nouns and adjectives go to the case, the other words stay."""

from __future__ import annotations

import pandas as pd

from ..frame import Frame, map_unique
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..text.base import split_words
from .forms import adjective_form, bundled_words, cased, form_index, is_abbreviation, noun_form, table_key

__all__ = ["decline"]

# The parts of speech that do not decline: verb, adverb, preposition, conjunction, particle.
NOT_DECLINED = frozenset({"v", "advb", "prep", "conj", "prt"})


class _Words:
    """The declined form of each distinct word, and whether it is a form other than its lemma, found once."""

    def __init__(self, index: int | None) -> None:
        self._index = index
        self._forms: dict[str, str | None] = {}
        self._inflected: dict[str, bool] = {}

    def inflected(self, word: str) -> bool:
        """The word is not its own lemma: it stands in a case already («дачу»)."""
        if word not in self._inflected:
            key = word.lower()
            self._inflected[word] = norm_phrase(BUNDLED.lemma(key)) != norm_phrase(key)
        return self._inflected[word]

    def form(self, word: str) -> str | None:
        """The word in the case as an adjective, else as a noun in its lemma; None when it stays."""
        if word not in self._forms:
            self._forms[word] = self._declined(word)
        return self._forms[word]

    def _declined(self, word: str) -> str | None:
        key = word.lower()
        pos = BUNDLED.pos(key)
        if pos in NOT_DECLINED:
            return None
        if pos != "n" and not is_abbreviation(key) and (form := adjective_form(key, self._index)) != key:
            return cased(word, form)
        if pos == "prn" or self.inflected(word):
            return None
        form = noun_form(key, self._index)
        return None if form == key else cased(word, form)


def _phrase(words: list[str], declined: _Words) -> str:
    result = []
    for place, word in enumerate(words):
        after = words[place + 1] if place + 1 < len(words) else None
        # a preposition or a pronoun governs the case of the next word; but not as the first word of the phrase:
        # «мой синий стол» declines as a whole
        governed = place > 1 and table_key(words[place - 1]) in bundled_words("governing")
        before_inflected = word.lower().endswith("ой") and after is not None and declined.inflected(after)
        form = None if governed or before_inflected else declined.form(word)
        result.append(word if form is None else form)
    return " ".join(result)


def decline(
    data: pd.Series | pd.DataFrame,
    case: str,
    *,
    number: str = "singular",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Every word of a phrase that declines, to the case: «купить красный диван» genitive → «купить красного дивана».

    case: "nominative", "genitive", "dative", "accusative", "instrumental" or "prepositional".
    number: "singular" or "plural".
    An adjective and a noun in its lemma decline; a verb, an adverb, a preposition, a conjunction, a particle, an
    indeclinable word and a word already in another case («на дачу») stay; a pronoun declines only as an adjective
    («этот» → «этого», «он» stays). A word right after a preposition or a possessive pronoun that is not the first
    word stays («чехол для телефон» → «чехла для телефон»; «мой синий стол» → «моего синего стола»). A word in «-ой»
    before a word in another case stays too («с большой скидкой»). A word keeps its capitals.
    """
    declined = _Words(form_index(case, number))
    frame = Frame(data, column, inplace)
    return frame.put(map_unique(frame.phrases, lambda phrase: _phrase(split_words(phrase), declined)), "decline")
