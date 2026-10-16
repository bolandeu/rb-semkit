"""sk.bigrams through the public library seam."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def rows(table: pd.DataFrame) -> list[tuple]:
    return list(table.itertuples(index=False, name=None))


def test_pairs_ignore_word_order_and_keep_stopwords() -> None:
    table = sk.bigrams(pd.Series(["диван в москве", "москве диван"]))

    assert table.columns.tolist() == ["ngram", "count"]
    assert rows(table) == [("диван+москве", 2), ("в+диван", 1), ("в+москве", 1)]


def test_stopwords_false_drops_them_first() -> None:
    table = sk.bigrams(pd.Series(["диван в москве", "москве диван"]), stopwords=False)

    assert rows(table) == [("диван+москве", 2)]


def test_both_orders_of_a_pair_are_one_ngram() -> None:
    assert rows(sk.bigrams(pd.Series(["купить диван", "Диван купить"]))) == [("диван+купить", 2)]


def test_repeated_words_of_a_phrase_are_dropped() -> None:
    assert rows(sk.bigrams(pd.Series(["диван диван угловой"]))) == [("диван+угловой", 1)]


def test_lemmas_and_the_sum_of_a_weight_column() -> None:
    df = pd.DataFrame({"phrase": ["купить диваны", "диван купила"], "freq": [4, 6]})

    table = sk.bigrams(df, lemmas=True, weight="freq", column="phrase")

    assert table.columns.tolist() == ["ngram", "count", "sum"]
    assert rows(table) == [("диван+купить", 2, 10)]
