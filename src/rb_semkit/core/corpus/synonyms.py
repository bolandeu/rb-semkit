"""Synonyms from a search-phrase report of an ad campaign, and the synonyms appended to phrases as minus-words.

In a report row, the condition is the phrase the ad was shown for, the matched phrase is the one the search engine
matched to it («-» when none) and the phrase is what the user searched. When the condition and the matched phrase
differ in one word, that word of the matched phrase is a synonym of the word of the condition.
"""

from __future__ import annotations

import functools
import re
from collections import Counter

import pandas as pd

from ..analysis.frequency import word_keys
from ..frame import Frame, map_unique
from ..morph import Lemmatizer
from ..morph.functions import BUNDLED
from ..normalize import norm_phrase
from ..text.base import split_words
from .tables import require_columns

__all__ = ["add_minus_words", "synonyms"]

REPORT_COLUMNS = ("phrase", "condition", "matched")
SYNONYM_COLUMNS = ["word", "sure", "synonyms"]
NO_MATCH = ("", "-")
_OPERATORS = re.compile(r'[+!"\[\]]')  # the match operators of a search ad: +word, !word, "phrase", [order]
MINUS = " -"
SURE_TEXTS = frozenset({"true", "1", "истина"})  # a `sure` cell of a table read from a file: True, TRUE, ИСТИНА
QUOTE = '"'


def _words(text: str) -> str:
    """The words of a phrase of an ad: without its minus-words and its operators."""
    return _OPERATORS.sub(" ", text.partition(MINUS)[0])


def _pair(initial: list[str], other: list[str]) -> tuple[str, str] | None:
    """The one word of `initial` that `other` has in its place, when they differ in exactly that word."""
    if len(initial) != len(other):
        return None
    only_initial, only_other = Counter(initial) - Counter(other), Counter(other) - Counter(initial)
    if only_initial.total() != 1 or only_other.total() != 1:
        return None
    return next(iter(only_initial)), next(iter(only_other))


def synonyms(report: pd.DataFrame, *, lemmatizer: Lemmatizer = BUNDLED) -> pd.DataFrame:
    """The synonyms in a search-phrase report: a table word, sure, synonyms (joined by a space).

    report: a table with the columns phrase, condition and matched. A row whose condition and matched phrase differ in
    one word gives a sure synonym; a row with no matched phrase («-») compares the condition with the phrase and gives
    a synonym to check, unless it is a sure one already. The word is the one of the condition. Words are compared as
    lemmas (by `lemmatizer`), in any case and with ё = е; minus-words, operators (+ ! " [ ]) and stopwords are left out.
    The sure rows come first, each part in the order of the report.
    """
    require_columns(report, "report", REPORT_COLUMNS)
    texts = report[list(REPORT_COLUMNS)].fillna("").astype(str)
    cleaned = pd.Series(texts.to_numpy().ravel(), dtype=object).map(_words)
    keys = word_keys(cleaned, lemmatizer=lemmatizer, stopwords=False)

    def lemmas(text: str) -> list[str]:
        return [keys[word][0] for word in split_words(_words(text)) if keys[word][1]]

    found: dict[tuple[str, bool], dict[str, None]] = {}
    for phrase, condition, matched in texts.itertuples(index=False):
        sure = matched.strip() not in NO_MATCH
        pair = _pair(lemmas(condition), lemmas(matched if sure else phrase))
        if pair is not None:
            found.setdefault((pair[0], sure), {})[pair[1]] = None
    rows = [
        (word, sure, " ".join(synonym for synonym in listed if sure or synonym not in found.get((word, True), {})))
        for (word, sure), listed in sorted(found.items(), key=lambda item: not item[0][1])
    ]
    return pd.DataFrame([row for row in rows if row[2]], columns=SYNONYM_COLUMNS).astype({"sure": bool})


def _is_sure(value: object) -> bool:
    return value if isinstance(value, bool) else str(value).strip().lower() in SURE_TEXTS


def _taken(table: pd.DataFrame, *, unsure: bool) -> pd.DataFrame:
    """The word and synonyms of the rows to add: the sure ones, and the unsure ones (`sure` False) with `unsure`; a
    table without the column `sure` is all sure."""
    rows = table if unsure or "sure" not in table.columns else table[table["sure"].map(_is_sure).astype(bool)]
    return rows[["word", "synonyms"]].fillna("").astype(str)


def add_minus_words(
    data: pd.Series | pd.DataFrame,
    table: pd.DataFrame,
    *,
    lemmatizer: Lemmatizer = BUNDLED,
    unsure: bool = False,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each phrase with the synonyms of its words appended as minus-words: «купить диван» → «купить диван -софа».

    table: a table with the columns word and synonyms (separated by spaces), as `synonyms` gives. A word of the phrase
    matches by its lemma (by `lemmatizer`), in any case and with ё = е. A synonym that the phrase holds already, as a
    word or a minus-word, is not added again. A phrase in quotes is left as it is.
    """
    require_columns(table, "table", ["word", "synonyms"])

    @functools.cache
    def key(word: str) -> str:
        return norm_phrase(lemmatizer.lemma(norm_phrase(word)))

    by_word: dict[str, list[str]] = {}
    for word, listed in _taken(table, unsure=unsure).itertuples(index=False):
        for initial in split_words(_words(word)):
            by_word.setdefault(key(initial), []).extend(split_words(listed))

    def appended(phrase: str) -> str:
        if phrase.lstrip().startswith(QUOTE):
            return phrase
        held = {key(word) for word in split_words(_OPERATORS.sub(" ", phrase.replace("-", " ")))}
        added = []
        for word in split_words(_words(phrase)):
            for synonym in by_word.get(key(word), ()):
                if key(synonym) not in held:
                    held.add(key(synonym))
                    added.append(f"-{synonym}")
        return " ".join([phrase, *added]) if added else phrase

    frame = Frame(data, column, inplace)
    return frame.put(map_unique(frame.phrases, appended), "minus_words")
