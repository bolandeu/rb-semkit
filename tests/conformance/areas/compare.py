"""The compare area: the input is my text (compare_grams, compare_stats) or the texts to rank (bm25).

`show` in the call names the column of the result table to compare; `metric` (compare_stats) names the one row.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..case_files import Case, phrases

NOT_ARGUMENTS = ("show", "metric")


def arguments(case: Case) -> tuple[Any, dict[str, Any]]:
    kwargs = {name: value for name, value in case.kwargs.items() if name not in NOT_ARGUMENTS}
    return (phrases(case) if case.function == "bm25" else case.input), kwargs


def outcome(case: Case, result: pd.DataFrame | pd.Series) -> pd.Series:
    if isinstance(result, pd.Series):
        return result
    table = result.set_index(result.columns[0])
    metric = case.kwargs.get("metric")
    return table[case.kwargs["show"]] if metric is None else table.loc[[metric], case.kwargs["show"]]
