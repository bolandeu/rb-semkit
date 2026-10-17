"""sk.split_text through the public library seam."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import rb_semkit as sk

TEXT = "Купить диван в Москве. Диван, кровать и кресло!"


def test_sentences_and_clauses_become_phrases_with_the_source_index() -> None:
    result = sk.split_text(pd.Series([TEXT]))

    assert result.tolist() == ["Купить диван в Москве", "Диван", "кровать и кресло"]
    assert result.index.tolist() == [0, 0, 0]


def test_ngrams_of_split_text_do_not_cross_a_sentence_end() -> None:
    table = sk.ngrams(sk.split_text(pd.Series([TEXT])), 2)

    grams = set(table["ngram"])
    assert "москве диван" not in grams
    assert "купить диван" in grams
    assert not any(char in gram for gram in grams for char in ".,!")


def test_dataframe_rows_repeat_the_source_columns_and_index() -> None:
    df = pd.DataFrame({"phrase": ["Диван, кровать", "Стол. Стул. Шкаф"], "freq": [10, 5]}, index=["a", "b"])

    result = sk.split_text(df, column="phrase")

    assert result["phrase"].tolist() == ["Диван", "кровать", "Стол", "Стул", "Шкаф"]
    assert result["freq"].tolist() == [10, 10, 5, 5, 5]
    assert result.index.tolist() == ["a", "a", "b", "b", "b"]


def test_dataframe_input_is_not_changed() -> None:
    df = pd.DataFrame({"phrase": ["Диван, кровать"], "freq": [10]})

    sk.split_text(df, column="phrase")

    assert df["phrase"].tolist() == ["Диван, кровать"]


@pytest.mark.parametrize(
    "text",
    ["Wi-Fi роутер за 2,5 тысячи", "кто-то купил 2.5 кг", "it's Wi-Fi"],
)
def test_in_word_punctuation_stays_in_one_phrase(text: str) -> None:
    assert sk.split_text(pd.Series([text])).tolist() == [text]


def test_a_dot_at_a_sentence_end_after_a_number_splits() -> None:
    assert sk.split_text(pd.Series(["Цена 5. Скидка 10"])).tolist() == ["Цена 5", "Скидка 10"]


def test_dashes_and_quotes_and_brackets_separate() -> None:
    result = sk.split_text(pd.Series(["диван — это «мебель» (мягкая) - да"]))

    assert result.tolist() == ["диван", "это", "мебель", "мягкая", "да"]


def test_whitespace_is_collapsed_and_case_is_kept() -> None:
    assert sk.split_text(pd.Series(["  Купить \t Диван ;\n  ИКЕА  "])).tolist() == ["Купить Диван", "ИКЕА"]


@pytest.mark.parametrize("cell", [None, np.nan, "", "...", " ?! "])
def test_cells_without_words_give_no_rows(cell: object) -> None:
    assert sk.split_text(pd.Series(["а, б", cell], dtype=object)).tolist() == ["а", "б"]


def test_a_wrong_column_names_it() -> None:
    with pytest.raises(sk.InvalidArguments, match="'nope'"):
        sk.split_text(pd.DataFrame({"phrase": ["а"]}), column="nope")
