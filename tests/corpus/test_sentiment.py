"""sk.sentiment through the public library seam."""

from __future__ import annotations

import math

import pandas as pd
import pytest

import rb_semkit as sk

SCORES = {"отличный": 5, "плохой": -3}
PHRASES = pd.Series(["Отличный диван", "плохой плохой стол", "стул"])


def values(result: pd.Series) -> list[float | None]:
    return [None if math.isnan(value) else value for value in result]


def test_the_mean_of_the_scores_of_the_words_and_empty_without_one() -> None:
    assert values(sk.sentiment(PHRASES, SCORES)) == [5, -3, None]


def test_the_max_may_be_negative() -> None:
    assert values(sk.sentiment(PHRASES, SCORES, what="max")) == [5, -3, None]


def test_the_min_without_a_scored_word_is_empty() -> None:
    assert values(sk.sentiment(PHRASES, SCORES, what="min")) == [5, -3, None]


def test_mean_min_and_max_of_mixed_words() -> None:
    phrases = pd.Series(["отличный плохой стол"])

    assert [sk.sentiment(phrases, SCORES, what=what).iloc[0] for what in ("mean", "min", "max")] == [1, -3, 5]


def test_the_dictionary_matches_in_any_case_with_e_for_yo() -> None:
    assert values(sk.sentiment(pd.Series(["ЁЖИК", "ежик"]), {"Ёжик": 2})) == [2, 2]


def test_the_first_of_two_same_words_of_the_dictionary_wins() -> None:
    assert values(sk.sentiment(pd.Series(["хороший"]), {"Хороший": 4, "хороший": 1})) == [4]


def test_a_table_gets_the_column_next_to_the_phrases() -> None:
    table = pd.DataFrame({"phrase": ["отличный диван"], "freq": [3]})

    result = sk.sentiment(table, SCORES, column="phrase")

    assert result.columns.tolist() == ["phrase", "phrase_sentiment", "freq"]


@pytest.mark.parametrize("scores", [{"очень плохой": -5}, {"": 1}, {"плохой": "минус"}, {"плохой": True}])
def test_a_dictionary_item_that_is_not_one_word_with_a_number_is_refused(scores: dict) -> None:
    with pytest.raises(sk.InvalidArguments, match="scores"):
        sk.sentiment(PHRASES, scores)


def test_an_unknown_statistic_is_refused() -> None:
    with pytest.raises(sk.InvalidArguments, match="what"):
        sk.sentiment(PHRASES, SCORES, what="median")
