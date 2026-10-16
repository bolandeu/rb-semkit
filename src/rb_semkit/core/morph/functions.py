"""Lemma-dependent functions over phrases: each word is looked up once per call, then mapped back."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from ..frame import Frame, map_unique
from ..text.base import split_words
from .lemmatizer import Lemmatizer, SemtoolsLemmatizer

BUNDLED = SemtoolsLemmatizer()


def _word_by_word(
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


def lemmatize(
    data: pd.Series | pd.DataFrame,
    *,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each word of a phrase replaced by its lemma, in lower case: «купила диваны» → «купить диван»."""
    return _word_by_word(data, lemmatizer.lemma, "lemmatize", column, inplace)


def part_of_speech(
    data: pd.Series | pd.DataFrame,
    *,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """The part of speech of each word of a phrase, by space: «купить диван» → «v n» (SemtoolsLemmatizer codes)."""
    return _word_by_word(data, lemmatizer.pos, "part_of_speech", column, inplace)


def wordforms(lemma: str, *, lemmatizer: Lemmatizer = BUNDLED) -> list[str]:
    """Every wordform of `lemma`: «москва» → [..., «москве», ...]."""
    return lemmatizer.forms(lemma)
