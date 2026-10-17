"""sk.coverage through the public library seam."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk

TEXT = "Купить диваны в Москве. Диван, кровать!"


def _row(table: pd.DataFrame, phrase: str) -> pd.Series:
    return table.set_index("phrase").loc[phrase]


def test_first_is_the_number_of_the_word_where_the_phrase_starts() -> None:
    table = sk.coverage(pd.Series(["кровать"]), pd.Series(["Диван. Купить кровать"]))

    assert table["first"].tolist() == [3]


def test_lemmas_follow_the_word_order_and_stop_at_punctuation() -> None:
    core = pd.Series(["купить диван", "диван кровать", "кресло"])

    table = sk.coverage(core, pd.Series([TEXT]), mode="lemmas")

    assert table["phrase"].tolist() == core.tolist()
    assert table["count"].tolist() == [1, 0, 0]
    assert table["first"].isna().tolist() == [False, True, True]


def test_any_order_finds_the_lemmas_inside_one_piece_and_exact_does_not() -> None:
    core = pd.Series(["диван купить"])

    assert sk.coverage(core, pd.Series([TEXT]), mode="any_order")["count"].tolist() == [1]
    assert sk.coverage(core, pd.Series([TEXT]), mode="exact")["count"].tolist() == [0]


def test_count_docs_and_density_over_all_texts() -> None:
    texts = pd.Series(["Диван и диван. Кресло", "Мягкий диван"])

    row = _row(sk.coverage(pd.Series(["диван"]), texts), "диван")

    assert (row["count"], row["docs"]) == (3, 2)
    assert row["density"] == pytest.approx(3 / 6)


def test_density_counts_the_words_of_the_phrase() -> None:
    row = _row(sk.coverage(pd.Series(["купить диван"]), pd.Series(["Купить диван в Москве"])), "купить диван")

    assert row["density"] == pytest.approx(2 * 1 / 4)


def test_occurrences_of_one_phrase_do_not_overlap_and_phrases_count_apart() -> None:
    table = sk.coverage(pd.Series(["а а", "а"]), pd.Series(["а а а а а"]))

    assert table["count"].tolist() == [2, 5]


def test_case_and_yo_are_folded_and_repeated_phrases_make_one_row() -> None:
    table = sk.coverage(pd.Series(["Ёлка", "Ёлка", "ель"]), pd.Series(["елка ЁЛКА"]))

    assert table["phrase"].tolist() == ["Ёлка", "ель"]
    assert table["count"].tolist() == [2, 0]


def test_dataframes_with_columns() -> None:
    core = pd.DataFrame({"q": ["диван"]})
    texts = pd.DataFrame({"body": ["Диван"], "id": [7]})

    table = sk.coverage(core, texts, column="q", text_column="body")

    assert table["count"].tolist() == [1]


def test_a_wrong_mode_names_the_argument_and_the_values() -> None:
    with pytest.raises(sk.InvalidArguments, match=r"mode.*'exact', 'lemmas', 'any_order'"):
        sk.coverage(pd.Series(["а"]), pd.Series(["а"]), mode="fuzzy")


def test_a_missing_column_names_the_argument() -> None:
    with pytest.raises(sk.InvalidArguments, match="column"):
        sk.coverage(pd.DataFrame({"q": ["а"]}), pd.Series(["а"]))
    with pytest.raises(sk.InvalidArguments, match="text_column"):
        sk.coverage(pd.Series(["а"]), pd.DataFrame({"body": ["а"]}))
