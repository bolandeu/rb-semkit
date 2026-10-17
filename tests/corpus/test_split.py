"""sk.split_by_words through the public library seam."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk

CORE = pd.Series(["диваны бу", "купить диван", "диван", "диваны недорого", "стол бу", "стул"])


def rows(table: pd.DataFrame) -> list[tuple]:
    return list(table.itertuples(index=False, name=None))


def test_by_lemmas_a_bad_word_wins_good_words_only_are_good_and_the_rest_keeps_its_frequency_dictionary() -> None:
    parts = sk.split_by_words(CORE, good=["диван", "купить"], bad="бу", lemmas=True)

    assert parts.bad.tolist() == ["диваны бу", "стол бу"]
    assert parts.good.tolist() == ["купить диван", "диван"]
    assert parts.rest.tolist() == ["диваны недорого", "стул"]
    assert rows(parts.frequency) == [("диван", 1), ("недорогой", 1), ("стул", 1)]


def test_by_words_a_wordform_is_another_word() -> None:
    parts = sk.split_by_words(CORE, good=["диван", "купить"], bad="бу")

    assert parts.good.tolist() == ["купить диван", "диван"]
    assert rows(parts.frequency) == [("диваны", 1), ("недорого", 1), ("стул", 1)]


def test_the_parts_keep_the_rows_of_a_table() -> None:
    table = pd.DataFrame({"phrase": ["купить диван", "стол бу"], "freq": [10, 5]})

    parts = sk.split_by_words(table, good=["купить", "диван"], bad=["бу"], column="phrase")

    assert rows(parts.good) == [("купить диван", 10)]
    assert rows(parts.bad) == [("стол бу", 5)]
    assert parts.rest.empty
    assert parts.frequency.empty


def test_words_are_compared_by_case_and_yo() -> None:
    parts = sk.split_by_words(pd.Series(["Ёлка купить"]), good=["елка", "КУПИТЬ"])

    assert parts.good.tolist() == ["Ёлка купить"]


def test_an_empty_phrase_is_in_the_rest() -> None:
    parts = sk.split_by_words(pd.Series(["", "диван"]), good=["диван"])

    assert parts.rest.tolist() == [""]


def test_a_good_or_bad_item_of_two_words_is_refused() -> None:
    with pytest.raises(sk.InvalidArguments, match="good"):
        sk.split_by_words(CORE, good=["купить диван"])
