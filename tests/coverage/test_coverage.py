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


def test_lemmas_follow_the_word_order_cross_a_comma_and_stop_at_a_sentence_end() -> None:
    core = pd.Series(["купить диван", "москва диван", "диван кровать", "кресло"])

    table = sk.coverage(core, pd.Series([TEXT]), mode="lemmas")

    assert table["phrase"].tolist() == core.tolist()
    assert table["count"].tolist() == [1, 0, 1, 0]
    assert table["first"].isna().tolist() == [False, True, False, True]


@pytest.mark.parametrize(
    ("text", "count"),
    [
        ("Склад временного хранения — это место", 1),
        ("склад временного хранения, это место", 1),
        ("склад временного хранения. Это место", 0),
        ("склад временного хранения! Это место", 0),
    ],
)
def test_an_exact_occurrence_crosses_a_dash_or_a_comma_not_a_sentence_end(text: str, count: int) -> None:
    table = sk.coverage(pd.Series(["склад временного хранения это"]), pd.Series([text]))

    assert table["count"].tolist() == [count]


def test_an_abbreviation_point_is_no_sentence_end() -> None:
    table = sk.coverage(pd.Series(["склад в г краснознаменск"]), pd.Series(["Склад в г. Краснознаменск."]))

    assert table["count"].tolist() == [1]


def test_density_has_at_most_four_decimals() -> None:
    table = sk.coverage(pd.Series(["диван"]), pd.Series(["диван кровать стол"]))

    assert table["density"].tolist() == [0.3333]


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


def test_counts_shares_have_at_most_four_decimals() -> None:
    df = pd.DataFrame({"phrase": ["диван", "стол", "стул"], "freq": [1, 1, 1]})

    share = sk.counts(df, what="share", weight="freq", column="phrase")["phrase_share"]
    of_total = sk.counts(df, what="share_of_total", weight="freq", column="phrase")["phrase_share_of_total"]

    assert share.tolist() == [0.3333, 0.6667, 1.0]
    assert of_total.tolist() == [0.3333, 0.3333, 0.3333]


def _count(phrase: str, text: str, **options: object) -> int:
    return sk.coverage(pd.Series([phrase]), pd.Series([text]), **options)["count"].tolist()[0]


@pytest.mark.parametrize(
    ("text", "gap", "count"),
    [
        ("Здесь можно купить недорогие пластиковые окна.", 1, 1),
        ("Здесь можно купить недорогие пластиковые окна.", 0, 0),
        ("купить очень недорогие пластиковые окна", 1, 0),
        ("купить очень недорогие пластиковые окна", 2, 1),
        ("купить. Пластиковые окна", 3, 0),
        ("купить пластиковые окна", 2, 1),
    ],
)
def test_gap_allows_inserted_words_between_the_phrase_words(text: str, gap: int, count: int) -> None:
    assert _count("купить пластиковые окна", text, gap=gap) == count


def test_gap_finds_a_later_word_when_the_nearest_is_too_far() -> None:
    assert _count("диван стол кровать", "диван стол стол шкаф кровать", gap=1) == 1


def test_gap_in_lemmas_mode() -> None:
    text = "купили недорогое пластиковое окно"

    assert _count("купить пластиковые окна", text, mode="lemmas", gap=1) == 1
    assert _count("купить пластиковые окна", text, mode="lemmas") == 0


def test_a_negative_gap_names_the_argument() -> None:
    with pytest.raises(sk.InvalidArguments, match="gap"):
        _count("диван стол", "диван стол", gap=-1)


def test_gap_does_not_apply_to_any_order() -> None:
    with pytest.raises(sk.InvalidArguments, match=r"gap.*any_order"):
        _count("диван стол", "диван стол", mode="any_order", gap=2)
