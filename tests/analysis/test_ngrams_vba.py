"""sk.ngrams(stopwords=False) as «Биграмм без учета стоп-слов» (—k·· L2781 → ka–a L1005) with ADR 0005."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def rows(table: pd.DataFrame) -> list[tuple]:
    return list(table.itertuples(index=False, name=None))


def test_a_stopword_between_two_words_stays_inside_the_gram() -> None:
    table = sk.ngrams(pd.Series(["купить диван в москве"]), n=2, stopwords=False)

    assert rows(table) == [("диван в москве", 1), ("купить диван", 1)]


def test_a_stopword_in_any_case_stays_inside_and_never_starts_or_ends_a_gram() -> None:
    table = sk.ngrams(pd.Series(["В диван В Москве В"]), n=2, stopwords=False)

    assert rows(table) == [("диван в москве", 1)]
