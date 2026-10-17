"""The frequency steps: n-grams and bigrams, reports whose table becomes the current one."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from ..core.analysis.frequency import bigrams, ngrams
from ..core.errors import InvalidArguments
from . import Prepared, Report, Step


def _numeric_weight(table: pd.DataFrame, weight: str | None) -> pd.DataFrame:
    """The table with the weight column as numbers: the pipeline reads every column as text; an empty cell stays empty."""
    if weight is None or weight not in table.columns:
        return table
    values = table[weight]
    try:
        numbers = pd.to_numeric(values.mask(values == ""))
    except (TypeError, ValueError):
        raise InvalidArguments(
            f"weight: {weight!r} holds text that is not a number; allowed: a column of numbers."
        ) from None
    return table.assign(**{weight: numbers})


def _report(function: Callable[..., pd.DataFrame]) -> Callable[[dict], Prepared]:
    def prepare(options: dict) -> Prepared:
        return lambda table, column: Report(
            function(_numeric_weight(table, options["weight"]), column=column, **options)
        )

    return prepare


NOTE = "The step counts the working column; the table replaces the current one, its column ngram is the working one."
STEPS = [
    Step("ngrams", ngrams, "report", _report(ngrams), NOTE),
    Step("bigrams", bigrams, "report", _report(bigrams), NOTE),
]
