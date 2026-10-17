"""sk.permutations, sk.ordered_pairs and sk.linear_combinations through the public library seam."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


def rows(table: pd.DataFrame) -> list[tuple]:
    return list(table.itertuples(index=False, name=None))


def test_every_permutation_of_the_words_in_order() -> None:
    result = sk.permutations(pd.Series(["a b c"]))

    assert result.tolist() == ["a b c", "a c b", "b a c", "b c a", "c a b", "c b a"]


def test_the_permutations_of_every_phrase_follow_each_other() -> None:
    result = sk.permutations(pd.Series(["купить диван", "стол"]))

    assert result.tolist() == ["купить диван", "диван купить", "стол"]


def test_a_limit_below_the_result_size_is_refused_naming_the_limit() -> None:
    with pytest.raises(sk.InvalidArguments, match="limit=5"):
        sk.permutations(pd.Series(["a b c"]), limit=5)


def test_a_limit_equal_to_the_result_size_is_enough() -> None:
    assert len(sk.permutations(pd.Series(["a b c"]), limit=6)) == 6


def test_permutations_of_a_table_column() -> None:
    table = pd.DataFrame({"phrase": ["a b"], "freq": [3]})

    assert sk.permutations(table, column="phrase").tolist() == ["a b", "b a"]


def test_ordered_pairs_are_a_two_column_table() -> None:
    table = sk.ordered_pairs(pd.Series(["a", "b", "c"]))

    assert table.columns.tolist() == ["first", "second"]
    assert rows(table) == [("a", "b"), ("a", "c"), ("b", "a"), ("b", "c"), ("c", "a"), ("c", "b")]


def test_ordered_pairs_take_each_item_once_and_skip_empty_cells() -> None:
    table = sk.ordered_pairs(pd.Series(["a", "", "a", "b", None]))

    assert rows(table) == [("a", "b"), ("b", "a")]


def test_ordered_pairs_over_the_limit_are_refused() -> None:
    with pytest.raises(sk.InvalidArguments, match="limit=5"):
        sk.ordered_pairs(pd.Series(["a", "b", "c"]), limit=5)


def test_linear_combinations_are_the_cartesian_product_one_column_per_list() -> None:
    lists = pd.DataFrame({"action": ["купить", "заказать"], "item": ["диван", "стол"]})

    table = sk.linear_combinations(lists)

    assert table.columns.tolist() == ["action", "item"]
    assert rows(table) == [("купить", "диван"), ("купить", "стол"), ("заказать", "диван"), ("заказать", "стол")]


def test_linear_combinations_skip_the_empty_cells_of_a_shorter_list() -> None:
    lists = pd.DataFrame({"action": ["купить", "заказать", None], "item": ["диван", "стол", "стул"]})

    assert len(sk.linear_combinations(lists)) == 6


def test_a_list_with_no_items_is_refused_naming_it() -> None:
    lists = pd.DataFrame({"action": ["купить"], "item": [None]}, dtype=object)

    with pytest.raises(sk.InvalidArguments, match="item"):
        sk.linear_combinations(lists)


def test_linear_combinations_over_the_limit_are_refused() -> None:
    lists = pd.DataFrame({"action": ["купить", "заказать"], "item": ["диван", "стол"]})

    with pytest.raises(sk.InvalidArguments, match="limit=3"):
        sk.linear_combinations(lists, limit=3)


@pytest.mark.parametrize("lists", [pd.DataFrame(), pd.Series(["a"]), [["a"], ["b"]]])
def test_lists_that_are_no_table_with_columns_are_refused(lists: object) -> None:
    with pytest.raises(sk.InvalidArguments, match="lists"):
        sk.linear_combinations(lists)
