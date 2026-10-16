"""Input and output of every library function: a Series of phrases, or a DataFrame plus `column=`.

In: NaN and None become empty strings. Out: a Series with the input index, or the input DataFrame with the
result in a new column `<column>_<operation>` right after `column` (`inplace=True` replaces `column`).
Wrong input raises InvalidArguments before anything changes.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pandas as pd
from pandas.api import types

from .errors import InvalidArguments


def _is_text(values: pd.Series) -> bool:
    return types.is_object_dtype(values) or types.is_string_dtype(values)


def _listed(names: list) -> str:
    return ", ".join(repr(name) for name in names) or "none"


@dataclass(frozen=True)
class Frame:
    data: pd.Series | pd.DataFrame
    column: str | None = None
    inplace: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.data, pd.DataFrame):
            self._check_column(self.data)
        elif isinstance(self.data, pd.Series):
            self._check_series(self.data)
        else:
            raise InvalidArguments(
                f"data is a {type(self.data).__name__}; allowed: a pandas Series, DataFrame (with column=)."
            )

    def _check_column(self, data: pd.DataFrame) -> None:
        text_columns = [name for name in data.columns if _is_text(data[name])]
        if self.column not in data.columns:
            given = "not given" if self.column is None else f"{self.column!r} is not in the table"
            raise InvalidArguments(f"column: {given}; allowed: {_listed(list(data.columns))}.")
        if self.column not in text_columns:
            raise InvalidArguments(
                f"column {self.column!r} holds {data[self.column].dtype}, not text; allowed: {_listed(text_columns)}."
            )

    def _check_series(self, data: pd.Series) -> None:
        if self.column is not None:
            raise InvalidArguments("column is only for a DataFrame; allowed: column=None with a Series.")
        if self.inplace:
            raise InvalidArguments("inplace is only for a DataFrame; allowed: inplace=False with a Series.")
        if not _is_text(data):
            raise InvalidArguments(f"data holds {data.dtype}, not text; allowed: a Series of text.")

    @property
    def phrases(self) -> pd.Series:
        """The input text as `str`, NaN and None as empty strings, with the input index."""
        values = self.data if isinstance(self.data, pd.Series) else self.data[self.column]
        return values.fillna("").astype(str)

    def put(self, result: pd.Series, operation: str) -> pd.Series | pd.DataFrame:
        """A Series for a Series. A DataFrame gets the result in its own object, also with inplace=False, and is returned.

        A result with fewer rows than the input is a row filter: a DataFrame then comes back as a new table
        without the dropped rows (its index labels must be unique).
        """
        if isinstance(self.data, pd.Series):
            return result.rename(self.data.name)
        data = self._kept_rows(self.data, result)
        column = str(self.column)
        if self.inplace:
            data[column] = result
        else:
            target = f"{column}_{operation}"
            if target in data.columns:
                data[target] = result
            else:
                data.insert(data.columns.get_loc(column) + 1, target, result)
        return data

    @staticmethod
    def _kept_rows(data: pd.DataFrame, result: pd.Series) -> pd.DataFrame:
        if len(result) == len(data):
            return data
        if not data.index.is_unique:
            raise InvalidArguments("index: has repeated labels; allowed: a unique index to drop rows.")
        return data.loc[result.index].copy()


def map_unique(phrases: pd.Series, transform: Callable[[str], Any]) -> pd.Series:
    """`transform` each distinct phrase once and map the results back, input index kept."""
    return phrases.map({phrase: transform(phrase) for phrase in phrases.unique()})
