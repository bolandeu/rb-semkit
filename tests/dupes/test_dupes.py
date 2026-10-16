"""sk.dupes: the four kinds of duplicates, the three actions, `against=`, empty phrases and bad arguments."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk

PHRASES = ["купить диван", "Купить  диван", "диван купить", "купить диваны", "стол"]


class FakeLemmatizer:
    """Knows one fact: «диваны» → «диван»; every other word is its own lemma."""

    def lemma(self, word: str) -> str:
        return {"диваны": "диван"}.get(word, word)

    def pos(self, word: str) -> str:
        raise AssertionError("dupes asks for lemmas only")

    def forms(self, lemma: str) -> list[str]:
        raise AssertionError("dupes asks for lemmas only")


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("exact", [False, False, False, False, False]),
        ("explicit", [False, True, False, False, False]),
        ("implicit", [False, True, True, False, False]),
        ("lemmas", [False, True, True, True, False]),
    ],
)
def test_mark_except_first_by_kind(kind: str, expected: list[bool]) -> None:
    result = sk.dupes(pd.Series(PHRASES), kind=kind, action="mark_except_first")

    assert result.tolist() == expected


def test_mark_all_and_drop() -> None:
    phrases = pd.Series(PHRASES)

    marked = sk.dupes(phrases, kind="implicit", action="mark_all")
    kept = sk.dupes(phrases, kind="implicit", action="drop")

    assert marked.tolist() == [True, True, True, False, False]
    assert kept.index.tolist() == [0, 3, 4]
    assert kept.tolist() == ["купить диван", "купить диваны", "стол"]


def test_against_another_series_marks_a_column_next_to_the_source() -> None:
    table = pd.DataFrame({"phrase": PHRASES, "n": range(5)})

    result = sk.dupes(table, kind="implicit", action="mark_all", against=pd.Series(["диван купить"]), column="phrase")

    assert result.columns.tolist() == ["phrase", "phrase_dupes", "n"]
    assert result["phrase_dupes"].tolist() == [True, True, True, False, False]
    assert result["phrase"].tolist() == PHRASES


def test_against_with_drop_keeps_the_rows_not_in_the_other() -> None:
    kept = sk.dupes(pd.Series(PHRASES), kind="explicit", action="drop", against=pd.Series(["КУПИТЬ диван"]))

    assert kept.index.tolist() == [2, 3, 4]


def test_drop_in_a_table_keeps_the_index_of_kept_rows() -> None:
    table = pd.DataFrame({"phrase": PHRASES})

    kept = sk.dupes(table, kind="explicit", action="drop", column="phrase")

    assert kept.index.tolist() == [0, 2, 3, 4]


def test_yo_equals_ye_in_explicit() -> None:
    result = sk.dupes(pd.Series(["ёлка купить", "елка купить"]), kind="explicit", action="mark_except_first")

    assert result.tolist() == [False, True]


@pytest.mark.parametrize("kind", ["exact", "explicit", "implicit", "lemmas"])
@pytest.mark.parametrize("action", ["mark_except_first", "mark_all"])
def test_empty_phrases_are_never_duplicates(kind: str, action: str) -> None:
    result = sk.dupes(pd.Series(["", None, ""]), kind=kind, action=action, lemmatizer=FakeLemmatizer())

    assert result.tolist() == [False, False, False]


def test_empty_phrases_do_not_match_against() -> None:
    result = sk.dupes(pd.Series(["", "стол"]), kind="exact", action="mark_all", against=pd.Series(["", "стол"]))

    assert result.tolist() == [False, True]


def test_lemmas_use_the_given_lemmatizer_only() -> None:
    result = sk.dupes(
        pd.Series(["купить диван", "купить диваны"]),
        kind="lemmas",
        action="mark_except_first",
        lemmatizer=FakeLemmatizer(),
    )

    assert result.tolist() == [False, True]


def test_unknown_kind_lists_the_allowed_ones() -> None:
    with pytest.raises(sk.InvalidArguments, match=r"exact.*explicit.*implicit.*lemmas"):
        sk.dupes(pd.Series(PHRASES), kind="nope", action="drop")


def test_unknown_action_lists_the_allowed_ones_and_changes_nothing() -> None:
    table = pd.DataFrame({"phrase": PHRASES})

    with pytest.raises(sk.InvalidArguments, match=r"mark_except_first.*mark_all.*drop"):
        sk.dupes(table, kind="exact", action="nope", column="phrase")

    assert table.columns.tolist() == ["phrase"]
