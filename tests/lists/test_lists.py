"""sk.compare_lists and sk.edges: the four operations, the kinds, DataFrame columns, bad arguments, speed."""

from __future__ import annotations

import time

import pandas as pd
import pytest

import rb_semkit as sk

FIRST = ["Купить диван", "кресло", "стол"]
SECOND = ["диван купить", "стул"]


class FakeLemmatizer:
    """Knows one fact: «диваны» → «диван»; every other word is its own lemma."""

    def lemma(self, word: str) -> str:
        return {"диваны": "диван"}.get(word, word)

    def pos(self, word: str) -> str:
        raise AssertionError("only lemmas are asked")

    def forms(self, lemma: str) -> list[str]:
        raise AssertionError("only lemmas are asked")


@pytest.mark.parametrize(
    ("op", "expected"),
    [
        ("both", ["Купить диван"]),
        ("first", ["кресло", "стол"]),
        ("second", ["стул"]),
        ("either", ["Купить диван", "кресло", "стол", "стул"]),
    ],
)
def test_operations_by_implicit_kind(op: str, expected: list[str]) -> None:
    result = sk.compare_lists(pd.Series(FIRST), pd.Series(SECOND), op=op, kind="implicit")

    assert result.tolist() == expected


def test_lemmas_kind_matches_wordforms_and_exact_does_not() -> None:
    first, second = pd.Series(["купить диваны"]), pd.Series(["купить диван"])

    assert sk.compare_lists(first, second, kind="lemmas", lemmatizer=FakeLemmatizer()).tolist() == ["купить диваны"]
    assert sk.compare_lists(first, second, kind="exact").tolist() == []


def test_explicit_kind_ignores_case_yo_and_spaces() -> None:
    result = sk.compare_lists(pd.Series(["Ёлка  зелёная"]), pd.Series(["елка зеленая"]), kind="explicit")

    assert result.tolist() == ["Ёлка  зелёная"]


def test_a_phrase_repeated_comes_once_with_its_first_spelling() -> None:
    first = pd.Series(["Диван", "диван", "стол"])

    assert sk.compare_lists(first, pd.Series(["стул", "Стул"]), op="either", kind="explicit").tolist() == [
        "Диван",
        "стол",
        "стул",
    ]


def test_empty_cells_are_never_phrases() -> None:
    first, second = pd.Series(["", None, "стол", "  "]), pd.Series(["", "стол", None])

    assert sk.compare_lists(first, second, op="both").tolist() == ["стол"]
    assert sk.compare_lists(first, second, op="either").tolist() == ["стол"]


def test_dataframe_columns() -> None:
    first = pd.DataFrame({"id": [1, 2], "phrase": ["стол", "стул"]})
    second = pd.DataFrame({"other": ["стул"]})

    assert sk.compare_lists(first, second, column="phrase", second_column="other").tolist() == ["стул"]


def test_wrong_op_and_kind_name_the_allowed_values() -> None:
    phrases = pd.Series(["стол"])

    with pytest.raises(sk.InvalidArguments, match=r"'union'.*both, either, first, second"):
        sk.compare_lists(phrases, phrases, op="union")
    with pytest.raises(sk.InvalidArguments, match=r"'fuzzy'.*exact, explicit, implicit, lemmas"):
        sk.compare_lists(phrases, phrases, kind="fuzzy")


def test_second_column_errors_name_second_column() -> None:
    with pytest.raises(sk.InvalidArguments, match="second_column"):
        sk.compare_lists(pd.Series(["а"]), pd.DataFrame({"p": ["а"]}))


def test_edges_cut_runs_at_word_edges_only() -> None:
    phrases = pd.Series(["+купить !диван? [москва] wi-fi -"])

    result = sk.remove(phrases, sk.edges(start="+-![", end="?!.]"))

    assert result.tolist() == ["купить диван москва wi-fi"]


def test_edges_cut_any_run_and_drop_words_of_only_those_characters() -> None:
    result = sk.remove(pd.Series(['  ++"купить"!!  +"!  диван.. ']), sk.edges(start='+"', end='"!?.'))

    assert result.tolist() == ["купить диван"]


def test_edges_without_characters_only_tidy_spaces() -> None:
    assert sk.remove(pd.Series([" а   б "]), sk.edges()).tolist() == ["а б"]


def test_edges_support_remove_only() -> None:
    with pytest.raises(sk.InvalidArguments, match="allowed: remove"):
        sk.find(pd.Series(["а"]), sk.edges(start="+"))


def test_edges_need_strings() -> None:
    with pytest.raises(sk.InvalidArguments, match="start"):
        sk.edges(start=["+"])


def test_a_million_rows_run_in_seconds() -> None:
    first = pd.Series([f"слово{i % 400_000} фраза" for i in range(1_000_000)])
    second = pd.Series([f"фраза слово{i % 300_000}" for i in range(1_000_000)])
    sk.compare_lists(first.iloc[:10], second.iloc[:10], kind="implicit")

    started = time.perf_counter()
    result = sk.compare_lists(first, second, kind="implicit")

    assert time.perf_counter() - started < 30
    assert len(result) == 300_000
