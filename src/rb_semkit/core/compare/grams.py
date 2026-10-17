"""compare_grams: the density of each gram of the competitors' texts against mine."""

from __future__ import annotations

from functools import partial

import pandas as pd

from ..analysis.frequency import _checked_n
from .shared import DECIMALS, TextCounts, checked_number, checked_text, texts_of, verdicts

COLUMNS = ["ngram", "docs", "docs_share", "median", "min", "max", "mine", "verdict"]


def compare_grams(
    mine: str,
    competitors: pd.Series | pd.DataFrame | list[str],
    *,
    n: int = 1,
    lemmas: bool = True,
    stopwords: bool = False,
    tolerance: float = 0.3,
    column: str | None = None,
) -> pd.DataFrame:
    """How the grams of my text differ from the competitors' texts: a row per gram met in any competitor.

    mine: one text (a str). competitors: texts one per row (a Series, or a DataFrame with `column`).
    The density of a gram in a text is its count / the words of that text; a competitor without the gram counts as 0.
    Grams are those of sk.ngrams (`n`, `lemmas`, `stopwords`).
    Columns: ngram. docs: competitors that hold it. docs_share: docs / competitors, 0..1. median, min, max: the density
    in the competitors. mine: its density in my text. verdict: 'below', 'within' or 'above', mine against
    median x (1 ± tolerance); when the median is 0, 'within' if mine is 0, else 'above'.
    Densities are rounded to 4 decimals. Sorted by median, biggest first, then ngram. The only norm is the median.
    """
    text, others = checked_text(mine), texts_of(competitors, column, "competitors")
    counts = partial(TextCounts, n=_checked_n(n), lemmas=lemmas, stopwords=stopwords)
    limit = checked_number(tolerance, "tolerance")
    density = pd.concat([counts(other).density for other in others], axis=1).fillna(0)
    own = counts(text).density.reindex(density.index, fill_value=0)
    median = density.median(axis=1)
    docs = (density > 0).sum(axis=1)
    table = pd.DataFrame(
        {
            "ngram": density.index,
            "docs": docs.to_numpy(),
            "docs_share": (docs / len(others)).round(DECIMALS).to_numpy(),
            "median": median.round(DECIMALS).to_numpy(),
            "min": density.min(axis=1).round(DECIMALS).to_numpy(),
            "max": density.max(axis=1).round(DECIMALS).to_numpy(),
            "mine": own.round(DECIMALS).to_numpy(),
            "verdict": verdicts(own, median, limit).to_numpy(),
        },
        columns=COLUMNS,
    )
    return table.sort_values(["median", "ngram"], ascending=[False, True]).reset_index(drop=True)
