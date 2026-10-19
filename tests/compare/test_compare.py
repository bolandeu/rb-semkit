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


def test_compare_stats_keeps_integer_metrics_integers() -> None:
    table = sk.compare_stats(MINE, COMPETITORS).set_index("metric")

    chars = table.loc["chars"]
    assert [type(chars[column]) for column in ("mine", "median", "min", "max", "delta")] == [int] * 5
    assert (chars["mine"], chars["median"], chars["min"], chars["max"]) == (18, 10, 9, 22)
    assert isinstance(table.loc["water", "mine"], float)


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


@pytest.mark.speed
def test_one_text_against_twenty_competitors_of_five_thousand_words_runs_fast() -> None:
    words = [f"слово{i}" for i in range(300)]
    texts = [" ".join(words[(i + j) % 300] for j in range(5000)) for i in range(21)]
    sk.compare_grams(texts[0], texts[1:2])  # loads the data

    start = time.perf_counter()
    sk.compare_grams(texts[0], texts[1:])

    assert time.perf_counter() - start < 30


def test_compare_stats_mean_sits_beside_the_median_and_norm_mean_gives_the_verdict() -> None:
    competitors = [" ".join(["слово"] * count) for count in (100, 200, 600)]
    mine = " ".join(["слово"] * 350)

    by_median = sk.compare_stats(mine, competitors).set_index("metric").loc["words"]
    by_mean = sk.compare_stats(mine, competitors, norm="mean").set_index("metric").loc["words"]

    assert (by_median["median"], by_median["mean"], by_median["verdict"]) == (200, 300, "above")
    assert (by_mean["median"], by_mean["mean"], by_mean["delta"], by_mean["verdict"]) == (200, 300, 50, "within")


def test_compare_stats_columns_of_before_stay_and_the_mean_is_added() -> None:
    table = sk.compare_stats(MINE, COMPETITORS)

    assert list(table.columns) == ["metric", "mine", "median", "mean", "min", "max", "delta", "verdict"]


def test_compare_grams_need_have_and_add_come_from_the_mean_density_and_the_size() -> None:
    competitors = ["a" + " я" * 99, "a a" + " я" * 98, "a a a" + " я" * 97]  # a: 0.01, 0.02, 0.03 of 100 words
    mine = "a a a a" + " я" * 496  # 500 words, a four times

    own = gram(sk.compare_grams(mine, competitors, norm="mean", lemmas=False, stopwords=True), "a")
    bigger = gram(sk.compare_grams(mine, competitors, norm="mean", words=1000, lemmas=False, stopwords=True), "a")

    assert (own["need"], own["have"], own["add"]) == (10, 4, 6)
    assert (bigger["need"], bigger["have"], bigger["add"]) == (20, 4, 16)


def test_compare_grams_med_count_is_the_median_of_the_occurrences() -> None:
    competitors = ["диван диван", "диван диван диван", "диван " * 10]

    assert gram(sk.compare_grams("диван", competitors), "диван")["med_count"] == 3


def test_compare_grams_default_columns_are_those_of_before_plus_the_mean_and_the_recommendation() -> None:
    table = sk.compare_grams(MINE, COMPETITORS)

    assert list(table.columns)[:9] == ["ngram", "docs", "docs_share", "median", "mean", "min", "max", "mine", "verdict"]
    assert list(table.columns)[9:] == ["need", "have", "add", "med_count"]


def test_compare_grams_per_text_names_the_columns_by_url_or_by_number() -> None:
    with_url = pd.DataFrame({"url": ["a.ru", "b.ru"], "text": ["диван стол", "диван"]})

    named = sk.compare_grams(MINE, with_url, per_text=True, column="text")
    numbered = sk.compare_grams(MINE, ["диван стол", "диван"], per_text=True)

    assert gram(named, "диван")[["a.ru", "b.ru"]].tolist() == [0.5, 1.0]
    assert gram(numbered, "диван")[["text_1", "text_2"]].tolist() == [0.5, 1.0]


def test_compare_grams_no_digits_and_exclude_leave_words_out_of_the_grams_and_the_density() -> None:
    mine = "диван 2026 года"

    plain = sk.compare_grams(mine, ["диван 2026 года"] * 2, lemmas=False, stopwords=True)
    cleaned = sk.compare_grams(mine, ["диван 2026 года"] * 2, lemmas=False, stopwords=True, no_digits=True)
    excluded = sk.compare_grams(mine, ["диван 2026 года"] * 2, lemmas=False, stopwords=True, exclude=["ГОДА"])

    assert "2026" in set(plain["ngram"])
    assert set(cleaned["ngram"]) == {"диван", "года"}
    assert gram(cleaned, "диван")["median"] == 0.5
    assert set(excluded["ngram"]) == {"диван", "2026"}


@pytest.mark.parametrize(
    ("call", "argument"),
    [
        (lambda: sk.compare_grams(MINE, COMPETITORS, norm="mode"), "norm"),
        (lambda: sk.compare_stats(MINE, COMPETITORS, norm="mode"), "norm"),
        (lambda: sk.compare_grams(MINE, COMPETITORS, words=-1), "words"),
        (lambda: sk.compare_grams(MINE, COMPETITORS, exclude="года"), "exclude"),
    ],
)
def test_wrong_new_arguments_raise_invalid_arguments_naming_the_argument(call, argument: str) -> None:
    with pytest.raises(sk.InvalidArguments, match=argument):
        call()
