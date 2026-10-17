"""sk.ngrams through the public library seam."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk

PHRASES = ["купить диван", "диван угловой", "купить стол"]


def rows(table: pd.DataFrame) -> list[tuple]:
    return list(table.itertuples(index=False, name=None))


def test_unigrams_sorted_by_count_then_ngram() -> None:
    table = sk.ngrams(pd.Series(PHRASES), n=1)

    assert table.columns.tolist() == ["ngram", "count"]
    assert rows(table) == [("диван", 2), ("купить", 2), ("стол", 1), ("угловой", 1)]


def test_bigrams_of_words_with_the_sum_of_a_weight_column() -> None:
    df = pd.DataFrame({"phrase": PHRASES, "freq": [10, 5, 1]})

    table = sk.ngrams(df, n=2, weight="freq", column="phrase")

    assert table.columns.tolist() == ["ngram", "count", "sum"]
    assert rows(table) == [("диван угловой", 1, 5), ("купить диван", 1, 10), ("купить стол", 1, 1)]


def test_lemmas_are_counted_with_the_bundled_lemmatizer() -> None:
    table = sk.ngrams(pd.Series(["купить диваны", "диван купила"]), lemmas=True)

    assert rows(table) == [("диван", 2), ("купить", 2)]


def test_lemmas_use_the_given_lemmatizer_only() -> None:
    class Fake:
        def lemma(self, word: str) -> str:
            return {"диваны": "диван"}.get(word, word)

        def pos(self, word: str) -> str:
            return ""

        def forms(self, lemma: str) -> list[str]:
            return []

    table = sk.ngrams(pd.Series(["диваны", "купила"]), lemmas=True, lemmatizer=Fake())

    assert rows(table) == [("диван", 1), ("купила", 1)]


def test_a_repeated_word_counts_every_occurrence() -> None:
    table = sk.ngrams(pd.Series(["диван диван угловой"]), n=1)

    assert rows(table) == [("диван", 2), ("угловой", 1)]


def test_a_weight_is_added_for_every_occurrence() -> None:
    df = pd.DataFrame({"phrase": ["диван диван"], "freq": [3]})

    assert rows(sk.ngrams(df, weight="freq", column="phrase")) == [("диван", 2, 6)]


def test_stopwords_stay_by_default_and_stay_inside_a_gram_with_stopwords_false() -> None:
    s = pd.Series(["диван в москве"])

    assert rows(sk.ngrams(s, n=2)) == [("в москве", 1), ("диван в", 1)]
    assert rows(sk.ngrams(s, n=2, stopwords=False)) == [("диван в москве", 1)]


def test_words_are_compared_by_case_and_yo() -> None:
    assert rows(sk.ngrams(pd.Series(["Ёлка", "елка", "ЕЛКА"]))) == [("елка", 3)]


def test_empty_phrases_and_phrases_shorter_than_n_give_nothing() -> None:
    table = sk.ngrams(pd.Series(["", None, "диван"]), n=2)

    assert table.columns.tolist() == ["ngram", "count"]
    assert table.empty
