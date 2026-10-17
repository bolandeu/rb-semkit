"""Irrelevant words: the words that stand before a case preposition and a form of the main word."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments


def test_the_candidate_has_its_uses_and_examples_and_the_input_is_unchanged() -> None:
    phrases = pd.Series(["чехол для телефона", "чехол на телефон", "Купить чехол для телефона"])
    before = phrases.copy()

    table = sk.irrelevant_words(phrases, "телефон")

    assert table.to_dict("records") == [
        {"word": "чехол", "uses": 3, "examples": "чехол для телефона, чехол на телефон"},
    ]
    pd.testing.assert_series_equal(phrases, before)


def test_stopwords_markers_and_a_preposition_of_another_case_give_no_candidate() -> None:
    phrases = pd.Series(["и для телефона", "купить для телефона", "чехол к телефона", "стекло в москве для телефона"])

    table = sk.irrelevant_words(phrases, "телефон")

    assert table.to_dict("records") == [{"word": "стекло", "uses": 1, "examples": "стекло для телефона"}]


def test_the_table_of_a_dataframe_column_and_an_empty_one() -> None:
    table = sk.irrelevant_words(pd.DataFrame({"phrase": ["диван", None]}), "телефон", column="phrase")

    assert list(table.columns) == ["word", "uses", "examples"]
    assert table.empty


def test_the_main_word_is_one_word() -> None:
    with pytest.raises(InvalidArguments, match=r"^word='чехол телефон'; allowed: one word"):
        sk.irrelevant_words(pd.Series(["чехол"]), "чехол телефон")
