"""compare_stats: the metrics of my text against the competitors' median or mean."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from ..textstats import text_stats
from .shared import DECIMALS, Norm, checked_norm, checked_number, checked_text, texts_of, verdicts, wholes_kept

COLUMNS = ["metric", "mine", "median", "mean", "min", "max", "delta", "verdict"]
NUMBERS = ["mine", "median", "mean", "min", "max", "delta"]


def _integers_kept(table: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    """The numbers of an integer metric (chars, words…) as integers where they are whole."""
    counted = table["metric"].isin(metrics.select_dtypes("integer").columns).to_numpy()
    return table.assign(**wholes_kept(table[NUMBERS], counted))


def compare_stats(
    mine: str,
    competitors: pd.Series | pd.DataFrame | list[str],
    *,
    tolerance: float = 0.3,
    column: str | None = None,
    norm: Norm = "median",
    no_digits: bool = False,
    exclude: Iterable[str] = (),
) -> pd.DataFrame:
    """The metrics of text-stats, mine against the competitors: a row per metric.

    mine: my text, one text.
    competitors: the texts of the competitors, one per row.
    tolerance: how far from the norm a metric is still within, a share of the norm (0.3 is ±30 %).
    norm: «median» (the default) or «mean»: what delta and the verdict are against.
    no_digits: leave out the words with a digit of every count, as text-stats does.
    exclude: words to leave out of every count, as text-stats does.

    The columns: metric; mine; median, mean, min, max, the metric over the competitors; delta, mine - the norm;
    verdict, «below», «within» or «above», mine against norm x (1 ± tolerance), and when the norm is 0, «within» if
    mine is 0, else «above». Numbers are rounded to 4 decimals; the counts (chars, chars_no_spaces, words, unique) stay
    whole numbers where they are whole.

    Example: {cli} read --whole mine.txt compare-stats competitors.csv write -
    -> chars, 46, 44, 34.6667, 14, 46, 2, within; chars_no_spaces, 40, 38, 30.3333, 13, 40, 2, within; words, 6, 7, 5.3333, 2, 7, -1, within; unique, 5, 4, 3.6667, 2, 5, 1, within; water, 0.0, 0.1429, 0.0952, 0.0, 0.1429, -0.1429, below; nausea_classic, 1.41, 1.41, 1.38, 1.0, 1.73, 0.0, within; nausea_academic, 0.3333, 0.4286, 0.4048, 0.2857, 0.5, -0.0952, within; ttr, 0.8333, 0.8333, 0.8333, 0.6667, 1.0, 0.0, within; mtld, 10.08, 6.0, 5.36, 0.0, 10.08, 4.08, above; zipf, 70.9, 0.0, 23.6333, 0.0, 70.9, 70.9, above
    """
    text, others = checked_text(mine), texts_of(competitors, column, "competitors")
    limit, chosen = checked_number(tolerance, "tolerance"), checked_norm(norm)
    texts = pd.Series([text, *others], dtype=object)
    metrics = text_stats(texts, no_digits=no_digits, exclude=exclude).select_dtypes("number")
    own, rest = metrics.iloc[0], metrics.iloc[1:]
    median, mean = rest.median(), rest.mean()
    target = median if chosen == "median" else mean
    table = pd.DataFrame(
        {
            "metric": metrics.columns,
            "mine": own.round(DECIMALS).to_numpy(),
            "median": median.round(DECIMALS).to_numpy(),
            "mean": mean.round(DECIMALS).to_numpy(),
            "min": rest.min().round(DECIMALS).to_numpy(),
            "max": rest.max().round(DECIMALS).to_numpy(),
            "delta": (own - target).round(DECIMALS).to_numpy(),
            "verdict": verdicts(own, target, limit).to_numpy(),
        },
        columns=COLUMNS,
    )
    return _integers_kept(table, metrics)
