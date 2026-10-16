"""sk.counts through the public library seam."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def test_words_and_chars_per_phrase() -> None:
    s = pd.Series(["купить диван в москве", "диван"], index=[7, 9])

    words = sk.counts(s, what="words")
    assert words.tolist() == [4, 1]
    assert words.index.tolist() == [7, 9]
    assert sk.counts(s, what="chars").tolist() == [21, 5]


def test_occurrence_count_and_number() -> None:
    s = pd.Series(["диван", "стол", "диван", "диван"])

    assert sk.counts(s, what="count").tolist() == [3, 1, 3, 3]
    assert sk.counts(s, what="number").tolist() == [1, 1, 2, 3]


def test_share_is_cumulative_and_abc_classes_follow_it() -> None:
    df = pd.DataFrame({"phrase": ["a", "b", "c"], "freq": [70, 20, 10]})

    assert sk.counts(df, what="share", weight="freq", column="phrase")["phrase_share"].tolist() == [0.7, 0.9, 1.0]
    assert sk.counts(df, what="abc", weight="freq", column="phrase")["phrase_abc"].tolist() == ["A", "B", "C"]


def test_share_runs_from_the_heaviest_row_and_lands_on_the_input_order() -> None:
    df = pd.DataFrame({"phrase": ["a", "b", "c"], "freq": [10, 70, 20]})

    assert sk.counts(df, what="share", weight="freq", column="phrase")["phrase_share"].tolist() == [1.0, 0.7, 0.9]


def test_a_dataframe_gets_a_new_column_after_the_phrases() -> None:
    df = pd.DataFrame({"phrase": ["купить диван"], "freq": [1]})

    result = sk.counts(df, what="words", column="phrase")

    assert result.columns.tolist() == ["phrase", "phrase_words", "freq"]
    assert result["phrase_words"].tolist() == [2]
