"""compare_stats: the metrics of my text against the competitors' median."""

from __future__ import annotations

import pandas as pd

from ..textstats import text_stats
from .shared import DECIMALS, checked_number, checked_text, texts_of, verdicts

COLUMNS = ["metric", "mine", "median", "min", "max", "delta", "verdict"]
NUMBERS = ["mine", "median", "min", "max", "delta"]


def _whole(value: float) -> int | float:
    return int(value) if float(value).is_integer() else float(value)


def _integers_kept(table: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    """The numbers of an integer metric (chars, words…) as integers where they are whole; the median of an even
    number of competitors may be a half."""
    counted = table["metric"].isin(metrics.select_dtypes("integer").columns).to_numpy()
    numbers = table[NUMBERS].astype(object)
    numbers.loc[counted] = numbers.loc[counted].map(_whole)
    return table.assign(**numbers)


def compare_stats(
    mine: str,
    competitors: pd.Series | pd.DataFrame | list[str],
    *,
    tolerance: float = 0.3,
    column: str | None = None,
) -> pd.DataFrame:
    """The numeric metrics of sk.text_stats, mine against the competitors: a row per metric.

    mine: one text (a str). competitors: texts one per row (a Series, or a DataFrame with `column`).
    Columns: metric. mine. median, min, max: the metric over the competitors. delta: mine - median.
    verdict: 'below', 'within' or 'above', mine against median x (1 ± tolerance); when the median is 0, 'within' if
    mine is 0, else 'above'. Numbers are rounded to 4 decimals. The only norm is the median.
    """
    text, others = checked_text(mine), texts_of(competitors, column, "competitors")
    limit = checked_number(tolerance, "tolerance")
    metrics = text_stats(pd.Series([text, *others], dtype=object)).select_dtypes("number")
    own, rest = metrics.iloc[0], metrics.iloc[1:]
    median = rest.median()
    table = pd.DataFrame(
        {
            "metric": metrics.columns,
            "mine": own.round(DECIMALS).to_numpy(),
            "median": median.round(DECIMALS).to_numpy(),
            "min": rest.min().round(DECIMALS).to_numpy(),
            "max": rest.max().round(DECIMALS).to_numpy(),
            "delta": (own - median).round(DECIMALS).to_numpy(),
            "verdict": verdicts(own, median, limit).to_numpy(),
        },
        columns=COLUMNS,
    )
    return _integers_kept(table, metrics)
