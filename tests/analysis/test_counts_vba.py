"""sk.counts where it follows the VBA (––k— L1875, –kko L2166, –koo L2489, –kok L1607) with the ADR 0005 deviations."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def weighted(weights: list[int]) -> pd.DataFrame:
    return pd.DataFrame({"phrase": list("abc"), "freq": weights})


def test_count_keys_a_phrase_by_case() -> None:
    assert sk.counts(pd.Series(["диван", "Диван", "стол"]), what="count").tolist() == [2, 2, 1]


def test_count_and_number_compare_yo_as_ye() -> None:
    s = pd.Series(["ёж", "еж"])

    assert sk.counts(s, what="count").tolist() == [2, 2]
    assert sk.counts(s, what="number").tolist() == [1, 2]


def test_an_empty_cell_gets_no_count_and_no_number() -> None:
    s = pd.Series(["диван", "", None])

    assert sk.counts(s, what="count").tolist() == [1, pd.NA, pd.NA]
    assert sk.counts(s, what="number").tolist() == [1, pd.NA, pd.NA]


def test_share_is_cumulative_in_row_order() -> None:
    result = sk.counts(weighted([20, 50, 30]), what="share", weight="freq", column="phrase")

    assert result["phrase_share"].tolist() == [0.2, 0.7, 1.0]


def test_share_of_total_is_the_value_over_the_sum() -> None:
    result = sk.counts(weighted([20, 50, 30]), what="share_of_total", weight="freq", column="phrase")

    assert result["phrase_share_of_total"].tolist() == [0.2, 0.5, 0.3]


def test_a_zero_sum_gives_empty_shares() -> None:
    for what in ("share", "share_of_total"):
        result = sk.counts(weighted([0, 0, 0]), what=what, weight="freq", column="phrase")

        assert result[f"phrase_{what}"].isna().all()
