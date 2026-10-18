"""Lemma-dependent functions over phrases: each word is looked up once per call, then mapped back.

word_by_word is the shared walk: it gives each word of a phrase to a lookup and joins the results. The lemmatizer
functions here and the declension of nouns and adjectives use it.
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..normalize import norm_phrase
from ..text.base import choice, split_words
from .lemmatizer import FALLBACKS, Fallback, Lemmatizer, SemtoolsLemmatizer

BUNDLED = SemtoolsLemmatizer()
WITH_PYMORPHY = SemtoolsLemmatizer(fallback="pymorphy")


def word_by_word(
    data: pd.Series | pd.DataFrame,
    lookup: Callable[[str], str],
    operation: str,
    column: str | None,
    inplace: bool,
) -> pd.Series | pd.DataFrame:
    frame = Frame(data, column, inplace)
    phrases = frame.phrases
    words = {word for phrase in phrases.unique() for word in split_words(phrase)}
    found = {word: lookup(word) for word in words}
    return frame.put(
        map_unique(phrases, lambda phrase: " ".join(found[word] for word in split_words(phrase))), operation
    )


def _with_fallback(lemmatizer: Lemmatizer, fallback: str) -> Lemmatizer:
    choice("fallback", fallback, FALLBACKS)
    if lemmatizer is not BUNDLED:
        raise InvalidArguments(
            f"fallback: {fallback!r} is for the bundled lemmatizer; allowed: fallback=None with lemmatizer="
            f"{type(lemmatizer).__name__}(...), or SemtoolsLemmatizer(fallback={fallback!r}) as the lemmatizer."
        )
    return WITH_PYMORPHY


def lemmatize(
    data: pd.Series | pd.DataFrame,
    *,
    lemmatizer: Lemmatizer = BUNDLED,
    fallback: Fallback | None = None,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each word of a phrase replaced by its lemma, in lower case.

    fallback: for a word missing from the bundled dictionary. Not given: the word goes to pymorphy3 if its dictionary
    knows the word, else to the suffix rule, and often stays as it is («тиктокерами»); "pymorphy": such a word takes the
    best guess of pymorphy3 («тиктокерами» → «тиктокер»).
    lemmatizer: what gives the lemmas; the fallback is for the bundled one.

    Example: {cli} read --text "купила диваны" lemmatize write -
    -> купить диван
    """
    if fallback is not None:
        lemmatizer = _with_fallback(lemmatizer, fallback)
    return word_by_word(data, lemmatizer.lemma, "lemmatize", column, inplace)


def part_of_speech(
    data: pd.Series | pd.DataFrame,
    *,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The part of speech of each word of a phrase, joined by a space.

    The codes are those of the bundled dictionary: n (noun), v (verb), a (adjective), p (participle), advb (adverb),
    prn (pronoun), prep (preposition), conj (conjunction), prt (particle), nv (as in the dictionary), and unkn for a
    word no rule gives a part of speech («кляк», «15»), so no code is empty.
    lemmatizer: what gives the parts of speech.

    Example: {cli} read --text "купить диван" part-of-speech write -
    -> купить диван, v n
    """
    return word_by_word(data, lemmatizer.pos, "part_of_speech", column, inplace)


def wordforms(word: str, *, lemmatizer: Lemmatizer = BUNDLED) -> list[str]:
    """Every wordform of the lemma of a word, alphabetical, each once.

    word: the word, in any form. The forms are those of its lemma, in lower case; the word itself is not repeated
    («диван» gives «дивана», «диване», … but not «диван»). A word the dictionary lacks gives no forms.
    lemmatizer: what gives the lemma and the forms.

    Example: {cli} read --text "диваны" wordforms диваны write -
    -> диван; дивана; диванам; диванами; диванах; диване; диванов; диваном; дивану

    ADR 0005: as «Генерация всех словоформ», without the input word the add-in writes twice.
    """
    key = norm_phrase(word)
    return sorted({form for form in lemmatizer.forms(lemmatizer.lemma(word)) if norm_phrase(form) != key})
