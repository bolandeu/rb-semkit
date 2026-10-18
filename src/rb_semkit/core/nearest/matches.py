"""nearest: for each row of a table, the nearest rows of another table by meaning, in a long report."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..compare.grams import URL
from ..errors import InvalidArguments
from ..frame import Frame
from ..relevance.page import PageEncoder
from ..relevance.vectors import DIGITS
from ..relevance.vectors import nearest as nearest_targets


def check_top(top: int) -> None:
    """Refuse a number of matches below 1."""
    if top < 1:
        raise InvalidArguments(f"top={top}; allowed: a whole number from 1.")


def nearest(
    data: pd.DataFrame,
    *,
    column: str,
    against: pd.DataFrame,
    against_column: str,
    encoder: PageEncoder,
    top: int = 1,
    threshold: float | None = None,
) -> pd.DataFrame:
    """For each row of the table, the rows of another table nearest it by meaning, in a long report.

    against: the table of the matches; against_column: its column of the texts.
    top: the matches of each row, the nearest first: a whole number from 1.
    threshold: the similarity from 0 to 1 a match needs to stay; without it every match stays.

    The texts of both tables get the page vector. The report has a row for each match of each row: the text of the row
    (in a column named as the working one), match, rank (1 for the nearest), similarity (4 places), and url (of the
    match) when the against table has a url column. A row with no match left (an empty cell, or every match below the
    threshold) keeps one row with an empty match.
    """
    check_top(top)
    texts = Frame(against, against_column, argument="against_column").phrases
    targets, has_text = encoder.encode(texts, against)
    if not has_text.any():
        raise InvalidArguments("against: the table has no texts.", action="Give a table with a column of texts.")
    kept = np.flatnonzero(has_text)
    phrases = Frame(data, column).phrases
    vectors, found = encoder.encode(phrases, data)
    ids, similarities = nearest_targets(vectors, targets[kept], top)
    matched = (ids >= 0) & found[:, None]
    if threshold is not None:
        matched &= similarities >= threshold
    shown = matched | (~matched.any(axis=1, keepdims=True) & (np.arange(ids.shape[1]) == 0))
    rows, places = np.nonzero(shown)
    hit = matched[rows, places]
    match_rows = kept[np.where(hit, ids[rows, places], 0)]
    report = pd.DataFrame(
        {
            column: phrases.to_numpy()[rows],
            "match": np.where(hit, texts.to_numpy()[match_rows], ""),
            "rank": pd.Series(places + 1, dtype="Int64").where(hit),
            "similarity": np.where(hit, similarities[rows, places].astype(float).round(DIGITS), np.nan),
        }
    )
    if URL in against.columns:
        report[URL] = np.where(hit, against[URL].fillna("").astype(str).to_numpy()[match_rows], "")
    return report
