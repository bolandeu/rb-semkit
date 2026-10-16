"""The weight column of the analysis functions: a numeric column of the table, one weight per phrase."""

from __future__ import annotations

import pandas as pd
from pandas.api import types

from ..errors import InvalidArguments
from ..frame import Frame


def _numeric_columns(data: pd.DataFrame) -> list[str]:
    return [name for name in data.columns if types.is_numeric_dtype(data[name]) and not types.is_bool_dtype(data[name])]


def weights_of(frame: Frame, weight: str | None) -> pd.Series | None:
    """The weight column as numbers, empty cells as 0 and a fresh 0..n-1 index; None when `weight` is None."""
    if weight is None:
        return None
    if not isinstance(frame.data, pd.DataFrame):
        raise InvalidArguments("weight is only for a DataFrame; allowed: weight=None with a Series.")
    numeric = ", ".join(repr(name) for name in _numeric_columns(frame.data)) or "none"
    if weight not in frame.data.columns:
        raise InvalidArguments(f"weight={weight!r} is not in the table; allowed: {numeric}.")
    if weight not in _numeric_columns(frame.data):
        raise InvalidArguments(f"weight={weight!r} holds {frame.data[weight].dtype}, not numeric; allowed: {numeric}.")
    return frame.data[weight].fillna(0).reset_index(drop=True)
