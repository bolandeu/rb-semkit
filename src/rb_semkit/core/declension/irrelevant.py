"""Irrelevant words: the words of a core that stand before a case preposition and a form of the main word."""

from __future__ import annotations

from collections.abc import Iterator

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame
from ..markers.matcher import markers
from ..normalize import norm_phrase
from ..text.base import bundled_list, split_words
from .forms import CASES, NUMBERS, bundled_words, form_index, noun_form

__all__ = ["irrelevant_words"]

COLUMNS = ["word", "uses", "examples"]
Governed = list[tuple[frozenset[str], frozenset[str]]]  # for each case: the words that take it, the forms in it


def _main_word(word: str) -> str:
    if not isinstance(word, str) or len(split_words(word)) != 1:
        raise InvalidArguments(f"word={word!r}; allowed: one word, a noun in the nominative singular.")
    return word.strip()


def _governed_forms(word: str) -> Governed:
    """For each case: the words that take it and the forms of `word` in it, singular and plural."""
    return [
        (
            bundled_words(f"takes_{case}"),
            frozenset(norm_phrase(noun_form(word, form_index(case, number))) for number in NUMBERS),
        )
        for case in CASES
    ]


def _cleaned(phrases: pd.Series) -> pd.Series:
    """The phrases without toponyms (with their prepositions) and buy markers, in lower case."""
    without_toponyms = markers("geo", with_prepositions=True).remove(phrases)
    return markers(["geo", "sale"]).remove(without_toponyms).str.lower()


def _candidates(words: list[str], governed: Governed, stopwords: frozenset[str]) -> Iterator[tuple[str, str]]:
    """Each candidate of the words of a phrase, with its example «word preposition form»."""
    for candidate, preposition, form in zip(words, words[1:], words[2:], strict=False):
        keys = norm_phrase(preposition), norm_phrase(form)
        if norm_phrase(candidate) not in stopwords and any(
            keys[0] in takes and keys[1] in forms for takes, forms in governed
        ):
            yield candidate, f"{candidate} {preposition} {form}"


def irrelevant_words(data: pd.Series | pd.DataFrame, word: str, *, column: str | None = None) -> pd.DataFrame:
    """The candidates for minus-words around a main word: «чехол» in «чехол для телефона» for «телефон».

    word: the main word, a noun in the nominative singular. A candidate is a word right before a preposition (or a
    pronoun) and a form of the main word in the case the preposition takes («для телефона», «на телефон»), when it
    is no stopword. Toponyms with their prepositions and buy markers are cut first («купить чехол для телефона в
    москве» → «чехол для телефона»). A table with a row per candidate in the order of first use: `word` (lower
    case), `uses` (every phrase counts, repeats too) and `examples` (each distinct «word preposition form», joined
    by ", "). The input is not changed.
    """
    governed = _governed_forms(_main_word(word))
    phrases = Frame(data, column).phrases
    counts = phrases.value_counts()
    distinct = pd.Series(phrases.unique(), dtype=object)
    stopwords = frozenset(norm_phrase(stopword) for stopword in bundled_list("stopwords"))
    uses: dict[str, int] = {}
    examples: dict[str, dict[str, None]] = {}
    for phrase, cleaned in zip(distinct, _cleaned(distinct), strict=True):
        for candidate, example in _candidates(split_words(cleaned), governed, stopwords):
            uses[candidate] = uses.get(candidate, 0) + int(counts[phrase])
            examples.setdefault(candidate, {})[example] = None
    rows = [(candidate, count, ", ".join(examples[candidate])) for candidate, count in uses.items()]
    return pd.DataFrame(rows, columns=COLUMNS).astype({"uses": int})
