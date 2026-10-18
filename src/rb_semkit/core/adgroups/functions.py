"""`ad_groups`: phrases that are duplicates by meaning of each other share an ad group, taken transitively.

Two phrases are duplicates by meaning by the rule of `dupes_meaning`: the same refining words and close vectors.
"""

from __future__ import annotations

from collections.abc import Collection

import numpy as np
import pandas as pd

from ..dupes.meaning import refining_words
from ..errors import InvalidArguments
from ..frame import Frame
from ..morph.functions import BUNDLED
from ..morph.lemmatizer import Lemmatizer
from ..normalize import norm_phrase
from ..text.base import split_words
from ..vectors.cluster import frequencies
from ..vectors.encoder import Encoder


def _components(vectors: np.ndarray, rows: np.ndarray, threshold: float) -> list[np.ndarray]:
    """The rows of the phrases of the same refining words, split into the groups of phrases close by a chain of pairs."""
    close = vectors[rows] @ vectors[rows].T >= threshold
    seen = np.zeros(len(rows), dtype=bool)
    found = []
    for start in range(len(rows)):
        if seen[start]:
            continue
        members, queue = [], [start]
        seen[start] = True
        while queue:
            current = queue.pop()
            members.append(current)
            fresh = np.flatnonzero(close[current] & ~seen)
            seen[fresh] = True
            queue.extend(fresh)
        found.append(rows[sorted(members)])
    return found


def _parts(vectors: np.ndarray, rows: np.ndarray, max_size: int | None) -> list[np.ndarray]:
    """A group of more than `max_size` rows split: the first row left takes the nearest rows left, and so on."""
    if max_size is None or len(rows) <= max_size:
        return [rows]
    left, parts = rows, []
    while len(left):
        nearest = np.argsort(-(vectors[left] @ vectors[left[0]]), kind="stable")[:max_size]
        parts.append(np.sort(left[nearest]))
        left = np.delete(left, nearest)
    return parts


def _name_rows(groups: list[np.ndarray], counts: np.ndarray | None) -> list[int]:
    """The row of the phrase that names each group: the most frequent, else the first; a tie, the first."""
    if counts is None:
        return [int(rows[0]) for rows in groups]
    return [int(rows[np.argmax(counts[rows])]) for rows in groups]


def ad_groups(
    data: pd.Series,
    *,
    encoder: Encoder,
    threshold: float,
    max_size: int | None = None,
    freq: pd.Series | None = None,
    neutral: Collection[str] = (),
    synonyms: pd.DataFrame | None = None,
    home: str | None = None,
    lemmatizer: Lemmatizer | None = None,
) -> pd.DataFrame:
    """Small ad groups of one intent: phrases that are duplicates by meaning of each other share a group.

    threshold: the similarity from 0 to 1 two phrases need to be one intent.
    max_size: the most phrases in a group; a larger group is split by vector, the nearest phrases together.
    freq: the frequency of each phrase, by the index of `data`; the group is named after its most frequent phrase.
    Without it, after its first phrase.
    neutral: the non-refining words (a phrase of them is read by lemmas).
    synonyms: a table with the columns word and synonyms; a word and its synonyms are the same word.
    home: the home city; its word is non-refining.

    Two phrases of the same refining words and close vectors (the rule of `dupes_meaning`) are one intent, and a chain
    of such pairs makes one group. A group of more than `max_size` phrases is split: the first phrase left takes the
    `max_size` phrases nearest to it, and so on, so the same input gives the same groups. Equal phrases are one phrase.
    The groups are numbered from 1 in the order of their first rows. The columns: ad_group and ad_group_name; every
    phrase gets them, an empty cell gets none.

    Example: {cli} read --text "купить диван" --text "диван купить" --text "кресло" ad-groups write -
    -> купить диван, 1, купить диван; диван купить, 1, купить диван; кресло, 2, кресло
    """
    if max_size is not None and max_size < 1:
        raise InvalidArguments(f"--max-size {max_size}: a group holds at least 1 phrase.", action="Give 1 or more.")
    texts = Frame(data).phrases
    phrases = pd.Index(pd.unique(texts[texts.map(lambda phrase: bool(split_words(norm_phrase(phrase))))]))
    if not len(phrases):
        return _columns(texts, phrases, np.zeros(0, dtype=np.int64), np.empty(0, dtype=object))
    vectors = np.ascontiguousarray(encoder.encode(list(phrases)), dtype=np.float32)
    refining = refining_words(
        pd.Series(phrases), neutral=neutral, synonyms=synonyms, home=home, lemmatizer=lemmatizer or BUNDLED
    )
    groups = [
        part
        for rows in refining.groupby(refining, sort=False).indices.values()
        for group in _components(vectors, rows, threshold)
        for part in _parts(vectors, group, max_size)
    ]
    groups.sort(key=lambda rows: rows[0])
    counts = None if freq is None else frequencies(texts, freq, phrases)
    number = np.zeros(len(phrases), dtype=np.int64)
    name = np.empty(len(phrases), dtype=object)
    for position, (rows, named) in enumerate(zip(groups, _name_rows(groups, counts), strict=True), start=1):
        number[rows], name[rows] = position, phrases[named]
    return _columns(texts, phrases, number, name)


def _columns(texts: pd.Series, phrases: pd.Index, number: np.ndarray, name: np.ndarray) -> pd.DataFrame:
    """The result by row of `texts`; an empty phrase has no group."""
    rows = phrases.get_indexer(texts)
    found = rows >= 0
    table = pd.DataFrame(
        {
            "ad_group": pd.Series(pd.NA, index=texts.index, dtype="Int64"),
            "ad_group_name": pd.Series("", index=texts.index, dtype=object),
        }
    )
    table.loc[found, "ad_group"] = number[rows[found]]
    table.loc[found, "ad_group_name"] = name[rows[found]]
    return table
