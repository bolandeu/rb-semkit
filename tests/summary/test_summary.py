"""sk.summary through the public library seam."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


def test_a_numeric_column_gives_its_count_mean_median_min_and_max() -> None:
    table = sk.summary(pd.DataFrame({"words": [100, 200, 600], "title": ["a", "b", "c"]}))

    assert table.to_dict("records") == [
        {"column": "words", "count": 3, "mean": 300, "median": 200, "min": 100, "max": 600}
    ]


def test_a_fractional_column_is_rounded_to_four_decimals_and_empty_cells_are_not_counted() -> None:
    table = sk.summary(pd.DataFrame({"water": [0.1, 0.2, 0.5, None]}))

    row = table.iloc[0]
    assert (row["count"], row["mean"], row["median"], row["min"], row["max"]) == (3, 0.2667, 0.2, 0.1, 0.5)


def test_every_numeric_column_is_a_row_in_the_order_of_the_table() -> None:
    table = sk.summary(pd.DataFrame({"a": [1, 2], "text": ["x", "y"], "b": [0.5, 1.5], "flag": [True, False]}))

    assert table["column"].tolist() == ["a", "b"]
    assert table["mean"].tolist() == [1.5, 1.0]


@pytest.mark.parametrize("data", [pd.DataFrame({"title": ["a", "b"]}), pd.DataFrame({"flag": [True, False]})])
def test_a_table_without_a_numeric_column_is_refused(data: pd.DataFrame) -> None:
    with pytest.raises(sk.InvalidArguments, match="no numeric column"):
        sk.summary(data)
