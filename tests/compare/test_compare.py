"""sk.compare_grams, sk.compare_stats and sk.bm25 through the public library seam."""

from __future__ import annotations

import time

import pandas as pd
import pytest

import rb_semkit as sk

MINE = "диван диван кресло"
COMPETITORS = ["диван стол", "стол стул", "диван диван диван стол"]


def gram(table: pd.DataFrame, name: str) -> pd.Series:
    return table.set_index("ngram").loc[name]


def test_a_gram_denser_than_the_median_is_above() -> None:
    row = gram(sk.compare_grams(MINE, COMPETITORS), "диван")

    assert (row["docs"], row["median"], row["min"], row["max"]) == (2, 0.5, 0.0, 0.75)
    assert (row["docs_share"], row["mine"], row["verdict"]) == (0.6667, 0.6667, "above")


def test_a_gram_missing_in_my_text_is_below_and_a_gram_of_no_competitor_is_absent() -> None:
    table = sk.compare_grams(MINE, pd.Series(COMPETITORS))

    row = gram(table, "стол")
    assert (row["docs"], row["mine"], row["verdict"]) == (3, 0.0, "below")
    assert "кресло" not in set(table["ngram"])


def test_rows_are_sorted_by_median_then_ngram() -> None:
    table = sk.compare_grams(MINE, COMPETITORS)

    assert list(table["ngram"]) == ["диван", "стол", "стул"]
    assert list(table.columns) == ["ngram", "docs", "docs_share", "median", "min", "max", "mine", "verdict"]


def test_a_gram_within_the_tolerance_is_within() -> None:
    row = gram(sk.compare_grams("диван стол", ["диван стол"] * 2), "диван")

    assert row["verdict"] == "within"


def test_a_zero_median_is_above_for_any_presence_of_mine() -> None:
    row = gram(sk.compare_grams("диван кресло", ["диван стол", "стол", "стол"]), "диван")
    assert (row["median"], row["verdict"]) == (0.0, "above")


def test_a_zero_median_with_mine_zero_is_within() -> None:
    row = gram(sk.compare_grams("кресло", ["диван стол", "стол", "стол"]), "диван")

    assert (row["median"], row["mine"], row["verdict"]) == (0.0, 0.0, "within")


def test_competitors_from_a_dataframe_column() -> None:
    frame = pd.DataFrame({"text": COMPETITORS, "other": [1, 2, 3]})

    table = sk.compare_grams(MINE, frame, column="text")

    assert gram(table, "диван")["docs"] == 2


def test_bigrams_are_counted_per_text_words() -> None:
    row = gram(
        sk.compare_grams("диван купить", ["купить диван", "купить диван сегодня"], n=2, lemmas=False), "купить диван"
    )

    assert (row["docs"], row["mine"]) == (2, 0.0)
    assert row["median"] == 0.4167


def test_compare_stats_gives_a_row_per_numeric_metric() -> None:
    table = sk.compare_stats(MINE, COMPETITORS)
    stats = sk.text_stats(pd.Series([MINE])).select_dtypes("number")

    assert list(table["metric"]) == list(stats.columns)
    assert "top" not in set(table["metric"])
    words = table.set_index("metric").loc["words"]
    assert (words["mine"], words["median"], words["min"], words["max"]) == (3, 2, 2, 4)
    assert (words["delta"], words["verdict"]) == (1, "above")


def test_compare_stats_verdict_below_and_within() -> None:
    table = sk.compare_stats("а б", ["а б в г", "а б в г", "а б в г"]).set_index("metric")

    assert table.loc["words", "verdict"] == "below"
    assert sk.compare_stats("а б в г", ["а б в г"]).set_index("metric").loc["words", "verdict"] == "within"


BM25_TEXTS = pd.Series(["диван стол", "стол стул", "диван диван диван кресло"], index=["a", "b", "c"])


def test_bm25_matches_a_hand_computation() -> None:
    scores = sk.bm25(BM25_TEXTS, "диван")

    assert list(scores.index) == ["a", "b", "c"]
    assert list(scores) == [0.5296, 0.0, 0.6963]


def test_bm25_text_without_the_term_scores_zero_and_the_densest_scores_highest() -> None:
    scores = sk.bm25(BM25_TEXTS, "диван")

    assert scores["b"] == 0
    assert scores.idxmax() == "c"


def test_bm25_ignores_stopwords_of_the_query() -> None:
    assert list(sk.bm25(BM25_TEXTS, "и диван")) == list(sk.bm25(BM25_TEXTS, "диван"))


@pytest.mark.parametrize(
    ("call", "argument"),
    [
        (lambda: sk.compare_grams(MINE, []), "competitors"),
        (lambda: sk.compare_grams(MINE, COMPETITORS, tolerance=-0.1), "tolerance"),
        (lambda: sk.compare_grams(MINE, COMPETITORS, n=0), "n"),
        (lambda: sk.compare_stats(MINE, pd.Series([], dtype=object)), "competitors"),
        (lambda: sk.compare_stats(MINE, COMPETITORS, tolerance=-1), "tolerance"),
        (lambda: sk.bm25(BM25_TEXTS, "диван", k1=-1), "k1"),
        (lambda: sk.bm25(BM25_TEXTS, "диван", b=2), "b"),
        (lambda: sk.compare_grams(5, COMPETITORS), "mine"),
    ],
)
def test_wrong_arguments_raise_invalid_arguments_naming_the_argument(call, argument: str) -> None:
    with pytest.raises(sk.InvalidArguments, match=argument):
        call()


def test_one_text_against_twenty_competitors_of_five_thousand_words_runs_fast() -> None:
    words = [f"слово{i}" for i in range(300)]
    texts = [" ".join(words[(i + j) % 300] for j in range(5000)) for i in range(21)]
    sk.compare_grams(texts[0], texts[1:2])  # loads the data

    start = time.perf_counter()
    sk.compare_grams(texts[0], texts[1:])

    assert time.perf_counter() - start < 30
