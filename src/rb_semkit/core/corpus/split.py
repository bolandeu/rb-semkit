"""The good / bad split of a semantic core by words: the phrases to keep, to drop, and the rest still to decide."""

from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

import pandas as pd

from ..analysis.frequency import ngrams, word_keys
from ..frame import Frame
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..text.base import split_words, word_list

__all__ = ["split_by_words"]


class Split(NamedTuple):
    """The parts of a split core: the rows of the input (a Series or the table), and the dictionary of the rest."""

    good: pd.Series | pd.DataFrame
    bad: pd.Series | pd.DataFrame
    rest: pd.Series | pd.DataFrame
    frequency: pd.DataFrame


def _keys(argument: str, words: str | Iterable[str], lemmatizer: Lemmatizer | None) -> frozenset[str]:
    listed = [words] if isinstance(words, str) else list(words)
    if not listed:
        return frozenset()
    found = word_keys(pd.Series(word_list(argument, listed)), lemmatizer=lemmatizer, stopwords=True)
    return frozenset(key for key, _, _ in found.values())


def split_by_words(
    data: pd.Series | pd.DataFrame,
    *,
    good: str | Iterable[str] = (),
    bad: str | Iterable[str] = (),
    lemmas: bool = False,
    lemmatizer: Lemmatizer = BUNDLED,
    column: str | None = None,
) -> Split:
    """The core split into good, bad and rest phrases, and the frequency dictionary of the rest.

    bad: a phrase with any of these words is bad.
    good: a phrase that is not bad and has only these words is good.
    lemmas: compare the lemmas of the words of the phrase and of the lists («диваны» is «диван»).
    lemmatizer: what gives the lemmas.

    Every other phrase, an empty one too, is the rest. Words are compared in any case and with ё as е. The parts keep
    the rows of the input in its order. The frequency dictionary is the ngrams table of the rest (of lemmas with
    lemmas), to choose the next good and bad words.

    Example: {cli} read --text "купить диван" --text "купить стол" --text "диван" split-by-words --good "купить,диван" --bad стол --keep good write -
    -> купить диван; диван
    """
    frame = Frame(data, column)
    phrases = frame.phrases
    by = lemmatizer if lemmas else None
    good_keys, bad_keys = _keys("good", good, by), _keys("bad", bad, by)
    keys = word_keys(phrases, lemmatizer=by, stopwords=True)

    def part(phrase: str) -> str:
        words = {keys[word][0] for word in split_words(phrase)}
        if words & bad_keys:
            return "bad"
        return "good" if words and words <= good_keys else "rest"

    parts = phrases.map({phrase: part(phrase) for phrase in phrases.unique()}).to_numpy()
    good_rows, bad_rows, rest = (frame.data[parts == name] for name in ("good", "bad", "rest"))
    return Split(good_rows, bad_rows, rest, ngrams(rest, lemmas=lemmas, lemmatizer=lemmatizer, column=column))
