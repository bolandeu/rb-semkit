"""`dupes` by meaning: phrases whose vectors are close and whose words differ only by non-refining words, synonyms,
another form of a word, another word order or the home city.

Every phrase gets the lemmas of its words, each synonym changed to its word, without the non-refining words and the
home city: its refining words. Two phrases of the same refining words and close vectors are one intent.
"""

from __future__ import annotations

from collections.abc import Collection

import numpy as np
import pandas as pd

from ..corpus.tables import require_columns
from ..errors import InvalidArguments
from ..frame import Frame
from ..morph.functions import BUNDLED
from ..morph.lemmatizer import Lemmatizer
from ..normalize import norm_phrase
from ..text.base import split_words
from ..vectors.encoder import Encoder
from .functions import ACTIONS, Action

DIGITS = 4
COLUMNS = ["dupes", "dupe_of", "similarity"]


def _lemmas(phrase: str, lemmatizer: Lemmatizer) -> list[str]:
    return [lemmatizer.lemma(word) for word in split_words(norm_phrase(phrase))]


def _same_words(table: pd.DataFrame | None, lemmatizer: Lemmatizer) -> dict[str, str]:
    """Each synonym of a table of word and synonyms mapped to its word, by lemmas."""
    if table is None:
        return {}
    require_columns(table, "synonyms", ["word", "synonyms"])
    found: dict[str, str] = {}
    for word, listed in table[["word", "synonyms"]].fillna("").astype(str).itertuples(index=False):
        for lemma in _lemmas(word, lemmatizer)[:1]:
            found.update({synonym: lemma for synonym in _lemmas(listed, lemmatizer)})
    return found


def refining_words(
    phrases: pd.Series,
    *,
    neutral: Collection[str],
    synonyms: pd.DataFrame | None,
    home: str | None,
    lemmatizer: Lemmatizer,
) -> pd.Series:
    """The refining words of each phrase: its lemmas without the non-refining ones and the home city, sorted, as a text."""
    skipped = {lemma for item in [*neutral, home or ""] for lemma in _lemmas(item, lemmatizer)}
    same = _same_words(synonyms, lemmatizer)
    return phrases.map(
        lambda phrase: " ".join(
            sorted({same.get(lemma, lemma) for lemma in _lemmas(phrase, lemmatizer) if lemma not in skipped})
        )
    )


def _heads(vectors: np.ndarray, groups: pd.Series, threshold: float) -> tuple[np.ndarray, np.ndarray]:
    """For each phrase the row of the head of its group (itself for a head) and the cosine to it.

    The phrases of the same refining words go in order; one close to an earlier head (the first of those) follows it,
    any other starts a group.
    """
    heads = np.arange(len(vectors))
    cosines = np.ones(len(vectors), dtype=np.float32)
    for rows in groups.groupby(groups, sort=False).indices.values():
        started: list[int] = []
        for row in rows:
            close = np.flatnonzero(vectors[started] @ vectors[row] >= threshold) if started else []
            if len(close):
                heads[row] = started[close[0]]
                cosines[row] = vectors[heads[row]] @ vectors[row]
            else:
                started.append(row)
    return heads, cosines


def dupes_meaning(
    data: pd.Series,
    *,
    encoder: Encoder,
    threshold: float,
    action: Action,
    neutral: Collection[str] = (),
    synonyms: pd.DataFrame | None = None,
    home: str | None = None,
    lemmatizer: Lemmatizer | None = None,
) -> pd.DataFrame:
    """The duplicates of the phrases by meaning: the columns dupes, dupe_of and similarity, by the index of `data`.

    threshold: the similarity from 0 to 1 two phrases need to be one intent.
    action: mark_except_first (dupes is true for each duplicate), mark_all (true for every member of a group of 2 or
    more); drop is the caller's: it keeps the rows where dupes is false under mark_except_first.
    neutral: the non-refining words (a phrase of them is read by lemmas).
    synonyms: a table with the columns word and synonyms; a word and its synonyms are the same word.
    home: the home city; its word is non-refining.

    The first row of a group is its head; a duplicate gets in dupe_of the head and in similarity the cosine to it (4
    places). An equal phrase is a duplicate of its first row. An empty phrase is never a duplicate.
    """
    if action not in ACTIONS:
        raise InvalidArguments(f"action: {action!r} is not an action; allowed: {', '.join(ACTIONS)}.")
    texts = Frame(data).phrases
    found = pd.DataFrame({"phrase": texts.to_numpy()})
    found = found[found["phrase"].map(lambda phrase: bool(split_words(norm_phrase(phrase))))].drop_duplicates("phrase")
    vectors = np.ascontiguousarray(encoder.encode(list(found["phrase"])), dtype=np.float32)
    refining = refining_words(
        found["phrase"], neutral=neutral, synonyms=synonyms, home=home, lemmatizer=lemmatizer or BUNDLED
    ).reset_index(drop=True)
    heads, cosines = _heads(vectors, refining, threshold) if len(found) else (np.zeros(0, int), np.zeros(0))
    head_of = pd.Series(found["phrase"].to_numpy()[heads], index=found["phrase"].to_numpy())
    cosine_of = pd.Series(cosines.astype(float).round(DIGITS), index=found["phrase"].to_numpy())
    return _columns(texts, head_of, cosine_of, action)


def _columns(texts: pd.Series, head_of: pd.Series, cosine_of: pd.Series, action: str) -> pd.DataFrame:
    """The result by row: a row that is not the first of its group is a duplicate of the head."""
    known = texts.isin(head_of.index)
    heads = texts.map(head_of)
    first = known & (heads == texts) & ~texts.duplicated()
    duplicate = known & ~first
    marks = duplicate | (first & (heads.map(heads.value_counts()) > 1)) if action == "mark_all" else duplicate
    return pd.DataFrame(
        {"dupes": marks, "dupe_of": heads.where(duplicate, ""), "similarity": texts.map(cosine_of).where(duplicate)}
    )[COLUMNS]
