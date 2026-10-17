"""The input tables of the corpus area: a table must hold the columns a function reads."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from ..errors import InvalidArguments


def require_columns(table: pd.DataFrame, argument: str, columns: Sequence[str]) -> None:
    """InvalidArguments naming `argument` and the missing columns, unless `table` is a DataFrame with all `columns`."""
    missing = [name for name in columns if not isinstance(table, pd.DataFrame) or name not in table.columns]
    if missing:
        raise InvalidArguments(
            f"{argument}: no columns {missing!r}; allowed: a table with the columns {list(columns)}."
        )
