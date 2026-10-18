"""Everything that declines in a phrase: its nouns and adjectives go to the case, the other words stay."""

from __future__ import annotations

import pandas as pd

from ..frame import Frame, map_unique
from ..morph.functions import BUNDLED
from ..morph.lemmatizer import NOUN
from ..normalize import norm_phrase
from ..text.base import split_words
from .forms import (
    Case,
    Number,
    adjective_case,
    adjective_form,
    adjective_index,
    bundled_words,
    cased,
    form_index,
    has_adjective_forms,
    is_abbreviation,
    is_animate,
    noun_form,
    table_key,
)

__all__ = ["decline"]

# The parts of speech that do not decline: verb, adverb, preposition, conjunction, particle.
NOT_DECLINED = frozenset({"v", "advb", "prep", "conj", "prt"})
NOMINATIVE_PLURAL = form_index("nominative", "plural")
# The nominatives of an adjective other than its lemma, the masculine singular.
OTHER_NOMINATIVES = (("feminine", "singular"), ("neuter", "singular"), ("masculine", "plural"))


def _same(word: str, other: str) -> bool:
    return norm_phrase(word) == norm_phrase(other)


class _Words:
    """The declined form of each distinct word, and whether it is a form other than its lemma, found once."""

    def __init__(self, case: str, number: str) -> None:
        self._case = case
        self._number = number
        self._forms: dict[tuple[str, bool], str | None] = {}
        self._inflected: dict[str, bool] = {}

    def inflected(self, word: str) -> bool:
        """The word is not its own lemma: it stands in a case already («дачу»), or in the plural («диваны»)."""
        if word not in self._inflected:
            key = word.lower()
            self._inflected[word] = not _same(BUNDLED.lemma(key), key)
        return self._inflected[word]

    def form(self, word: str, *, animate_noun: bool = False) -> str | None:
        """The word in the case as an adjective, else as a noun in a nominative; None when it stays.

        animate_noun: the noun after the word is animate, so a masculine or plural adjective takes the genitive for
        the accusative («рыжего кота»).
        """
        if (word, animate_noun) not in self._forms:
            self._forms[word, animate_noun] = self._declined(word, animate_noun)
        return self._forms[word, animate_noun]

    def _declined(self, word: str, animate_noun: bool) -> str | None:
        key = word.lower()
        pos = BUNDLED.pos(key)
        if pos in NOT_DECLINED:
            return None
        form = self._adjective(key, animate_noun) if pos != NOUN and not is_abbreviation(key) else None
        if form is None and pos != "prn":
            form = self._noun(key)
        return None if form is None or form == key else cased(word, form)

    def _adjective(self, key: str, animate_noun: bool) -> str | None:
        """The adjective form in its own gender and number («большая» → «большой»); None for no adjective in a
        nominative."""
        lemma = BUNDLED.lemma(key)
        if _same(lemma, key) and has_adjective_forms(key):
            gender, number = "masculine", "singular"
        else:
            found = [
                (gender, number)
                for gender, number in OTHER_NOMINATIVES
                if has_adjective_forms(lemma)
                and _same(adjective_form(lemma, adjective_index("nominative", gender, number)), key)
            ]
            if not found:
                return None
            (gender, number), key = found[0], lemma
        number = "plural" if self._number == "plural" else number
        case = adjective_case(self._case, gender, number, animate=animate_noun)
        return adjective_form(key, adjective_index(case, gender, number))

    def genitive_singular(self, word: str) -> bool:
        """The word is a noun whose form is also the genitive singular of its lemma («продукции»)."""
        key = word.lower()
        lemma = BUNDLED.lemma(key)
        return (
            BUNDLED.pos(key) == NOUN
            and not _same(lemma, key)
            and _same(noun_form(lemma, form_index("genitive", "singular")), key)
        )

    def _noun(self, key: str) -> str | None:
        """The noun form of a word in the nominative, singular or plural; None for a word in another case."""
        lemma = BUNDLED.lemma(key)
        if _same(lemma, key):
            return noun_form(key, form_index(self._case, self._number))
        if _same(noun_form(lemma, NOMINATIVE_PLURAL), key):
            return noun_form(lemma, form_index(self._case, "plural"))
        return None


def _animate_nouns(words: list[str], case: str) -> list[bool]:
    """For each word: in the accusative, the next noun after it is animate."""
    found = [False] * len(words)
    if case != "accusative":
        return found
    animate = False
    for place in range(len(words) - 1, -1, -1):
        found[place] = animate
        if BUNDLED.pos(words[place].lower()) == NOUN:
            animate = is_animate(words[place])
    return found


def _complement(words: list[str], place: int) -> bool:
    """The word follows a noun, with only adjectives between: it is the complement of that noun («импорт продукции»)."""
    for before in reversed(words[:place]):
        pos = BUNDLED.pos(before.lower())
        if pos == NOUN:
            return True
        if pos in NOT_DECLINED:
            return False
    return False


def _phrase(words: list[str], declined: _Words, case: str) -> str:
    result = []
    animate_nouns = _animate_nouns(words, case)
    for place, word in enumerate(words):
        after = words[place + 1] if place + 1 < len(words) else None
        # a preposition or a pronoun governs the case of the next word; but not as the first word of the phrase:
        # «мой синий стол» declines as a whole
        governed = place > 1 and table_key(words[place - 1]) in bundled_words("governing")
        before_inflected = word.lower().endswith("ой") and after is not None and declined.inflected(after)
        complement = declined.genitive_singular(word) and _complement(words, place)
        form = (
            None
            if governed or before_inflected or complement
            else declined.form(word, animate_noun=animate_nouns[place])
        )
        result.append(word if form is None else form)
    return " ".join(result)


def decline(
    data: pd.Series | pd.DataFrame,
    case: Case,
    *,
    number: Number = "singular",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Every word of a phrase that declines, to the case: «купить красный диван» genitive → «купить красного дивана».

    case: "nominative", "genitive", "dative", "accusative", "instrumental" or "prepositional".
    number: "singular" or "plural"; a phrase in the nominative plural declines in the plural anyway («угловые диваны»
    → «угловых диванов»).

    An adjective and a noun in its lemma decline; a verb, an adverb, a preposition, a conjunction, a particle, an
    indeclinable word and a word already in another case («на дачу») stay; a pronoun declines only as an adjective
    («этот» → «этого», «он» stays). A feminine, neuter or plural adjective declines from its lemma («большая скидка» →
    «большой скидки»); a hyphenated noun declines whole («диван-кровать» → «дивана-кровати»). The accusative agrees
    by animacy: an inanimate noun and its adjective keep the nominative («купить кожаный диван»), an animate one takes
    the genitive («купить рыжего кота»). A word right after a preposition or a possessive pronoun that is not the first
    word stays («чехол для телефон» → «чехла для телефон»; «мой синий стол» → «моего синего стола»). A word in «-ой»
    before a word in another case stays too («с большой скидкой»). A word keeps its capitals.
    """
    form_index(case, number)  # the case and the number are checked before any phrase
    declined = _Words(case, number)
    frame = Frame(data, column, inplace)
    return frame.put(map_unique(frame.phrases, lambda phrase: _phrase(split_words(phrase), declined, case)), "decline")
