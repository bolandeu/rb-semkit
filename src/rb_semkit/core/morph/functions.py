"""Lemma-dependent functions over phrases: each word is looked up once per call, then mapped back."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..text.base import choice, split_words
from .lemmatizer import FALLBACKS, Lemmatizer, SemtoolsLemmatizer

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
    fallback: str | None = None,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each word of a phrase replaced by its lemma, in lower case: «купила диваны» → «купить диван».

    fallback: None — a word missing from the bundled dictionary goes to pymorphy3 if its dictionary knows the word,
    else to the suffix rule, and often stays as it is («тиктокерами»); "pymorphy" — such a word takes the best
    guess of pymorphy3 («тиктокерами» → «тиктокер»). The fallback is for the bundled lemmatizer.
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
    """The part of speech of each word of a phrase, by space: «купить диван» → «v n» (SemtoolsLemmatizer codes)."""
    return word_by_word(data, lemmatizer.pos, "part_of_speech", column, inplace)


def wordforms(word: str, *, lemmatizer: Lemmatizer = BUNDLED) -> list[str]:
    """Every wordform of the lemma of `word`, alphabetical, each once: «диваны» → [«диван», «дивана», ...].

    As «Генерация всех словоформ»: the forms of the lemma of the word in lower case; the input word is not repeated
    (ADR 0005).
    """
    return sorted(set(lemmatizer.forms(lemmatizer.lemma(word))))
