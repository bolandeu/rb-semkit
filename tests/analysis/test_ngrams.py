"""sk.ngrams through the public library seam."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk

PHRASES = ["купить диван", "диван угловой", "купить стол"]


def rows(table: pd.DataFrame) -> list[tuple]:
    """The add-in's columns only: ngram, count and sum."""
    return list(table.drop(columns=["docs", "forms"], errors="ignore").itertuples(index=False, name=None))


def test_unigrams_sorted_by_count_then_ngram() -> None:
    table = sk.ngrams(pd.Series(PHRASES), n=1)

    assert table.columns.tolist() == ["ngram", "count", "docs"]
    assert rows(table) == [("диван", 2), ("купить", 2), ("стол", 1), ("угловой", 1)]


def test_bigrams_of_words_with_the_sum_of_a_weight_column() -> None:
    df = pd.DataFrame({"phrase": PHRASES, "freq": [10, 5, 1]})

    table = sk.ngrams(df, n=2, weight="freq", column="phrase")

    assert table.columns.tolist() == ["ngram", "count", "docs", "sum"]
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

    assert table.columns.tolist() == ["ngram", "count", "docs"]
    assert table.empty


def test_docs_counts_the_phrases_with_the_gram_once_each() -> None:
    table = sk.ngrams(pd.Series(["диван кровать диван", "диван"]), n=1)

    assert table.set_index("ngram").loc["диван", ["count", "docs"]].tolist() == [3, 2]


def test_docs_counts_the_distinct_index_values_when_the_index_repeats() -> None:
    table = sk.ngrams(pd.Series(["диван", "диван", "диван"], index=[0, 0, 1]))

    assert table.set_index("ngram").loc["диван", ["count", "docs"]].tolist() == [3, 2]


def test_docs_of_bigrams_counts_the_texts() -> None:
    table = sk.bigrams(pd.Series(["купить диван", "диван купить", "диван"], index=["a", "a", "b"]))

    assert table.set_index("ngram").loc["диван+купить", ["count", "docs"]].tolist() == [2, 1]


def test_forms_of_a_lemma_are_the_word_forms_most_frequent_first() -> None:
    table = sk.ngrams(pd.Series(["диваны диван", "диваны"]), n=1, lemmas=True)

    assert table.columns.tolist() == ["ngram", "count", "docs", "forms"]
    assert table.set_index("ngram").loc["диван", "forms"] == "диваны, диван"


def test_forms_of_a_longer_gram_are_its_distinct_spellings_at_most_five() -> None:
    phrases = ["купить диваны", "купить диван", "купить диваны"] + [f"купить диван{i}" for i in range(7)]
    table = sk.ngrams(pd.Series(phrases), n=2, lemmas=True, lemmatizer=_Collapse())

    assert table.set_index("ngram").loc["купить диван", "forms"].split(", ")[:2] == ["купить диваны", "купить диван"]
    assert len(table.set_index("ngram").loc["купить диван", "forms"].split(", ")) == 5


def test_forms_of_bigrams_are_spellings_in_the_sorted_order_of_the_pair() -> None:
    table = sk.bigrams(pd.Series(["купить диваны"]), lemmas=True)

    assert table.set_index("ngram").loc["диван+купить", "forms"] == "диваны+купить"


def test_no_forms_without_lemmas() -> None:
    assert "forms" not in sk.ngrams(pd.Series(["диваны"])).columns


class _Collapse:
    """Every «диван…» word is the lemma «диван»."""

    def lemma(self, word: str) -> str:
        return "диван" if word.startswith("диван") else word

    def pos(self, word: str) -> str:
        return ""

    def forms(self, lemma: str) -> list[str]:
        return []
