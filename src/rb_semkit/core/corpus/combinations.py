"""Combinations: the permutations of the words of a phrase, the ordered pairs of a list, the linear combinations of
several lists. Each refuses a result larger than its `limit`."""

from __future__ import annotations

import math
from itertools import permutations as orders
from itertools import product

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame
from ..text.base import split_words, whole_number

__all__ = ["linear_combinations", "ordered_pairs", "permutations"]

LIMIT = 1_048_576  # the rows of a spreadsheet


def _within(size: int, limit: int) -> None:
    if size > whole_number("limit", limit):
        raise InvalidArguments(f"limit={limit}: the result has {size} rows; allowed: a limit of {size} or more.")


def permutations(data: pd.Series | pd.DataFrame, *, limit: int = LIMIT, column: str | None = None) -> pd.Series:
    """Every order of the words of each phrase, the phrases one after another: «a b c» → «a b c», «a c b», «b a c»…

    A phrase of n words gives n! phrases, a repeated word too; an empty phrase gives one empty phrase.
    limit: the most phrases the result may hold; a larger result is refused before any is made.
    """
    words = [split_words(phrase) for phrase in Frame(data, column).phrases]
    _within(sum(math.factorial(len(phrase)) for phrase in words), limit)
    return pd.Series([" ".join(order) for phrase in words for order in orders(phrase)], dtype=object)


def ordered_pairs(data: pd.Series | pd.DataFrame, *, limit: int = LIMIT, column: str | None = None) -> pd.DataFrame:
    """Every ordered pair of two different items of a list: a table first, second («a», «b» → a b, b a).

    Each item counts once, in the order of its first row; empty cells are no items. n items give n x (n - 1) pairs.
    limit: the most pairs the result may hold; a larger result is refused before any is made.
    """
    items = [item for item in dict.fromkeys(Frame(data, column).phrases) if item]
    _within(len(items) * (len(items) - 1), limit)
    pairs = [(first, second) for first in items for second in items if first != second]
    return pd.DataFrame(pairs, columns=["first", "second"], dtype=object)


def linear_combinations(lists: pd.DataFrame, *, limit: int = LIMIT) -> pd.DataFrame:
    """Every combination of one item from each column of the table, one column per list (the Cartesian product).

    The first column changes slowest: купить, заказать × диван, стол → купить диван, купить стол, заказать диван…
    The empty cells of a column are skipped, so the lists may differ in length; a column with no items is refused.
    limit: the most rows the result may hold; a larger result is refused before any is made.
    """
    if not isinstance(lists, pd.DataFrame) or lists.columns.empty:
        raise InvalidArguments("lists: no table with columns; allowed: a DataFrame, one column per list.")
    items = {name: [item for item in values.fillna("").astype(str) if item] for name, values in lists.items()}
    empty = [name for name, values in items.items() if not values]
    if empty:
        raise InvalidArguments(f"lists: the columns {empty!r} hold no items; allowed: columns with at least one item.")
    _within(math.prod(len(values) for values in items.values()), limit)
    return pd.DataFrame(list(product(*items.values())), columns=list(items), dtype=object)
