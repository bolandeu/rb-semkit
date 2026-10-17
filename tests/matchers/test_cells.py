"""Cells as units: content, occurrence, empty; remove clears the found cells, the empty ones go."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk

CELLS = pd.Series(["диван", "стол", "диван", ""])


def test_occurrence_and_empty() -> None:
    assert sk.find(CELLS, sk.cells("repeated")).tolist() == [True, False, True, False]
    assert sk.find(CELLS, sk.cells("first")).tolist() == [True, True, False, True]
    assert sk.find(CELLS, sk.cells("empty")).tolist() == [False, False, False, True]
    assert sk.find(CELLS, sk.cells("last")).tolist() == [False, True, True, True]
    assert sk.find(CELLS, sk.cells("unique")).tolist() == [False, True, False, True]


def test_empty_cells_are_never_repeated() -> None:
    twice = pd.Series(["", "", None])

    assert sk.find(twice, sk.cells("repeated")).tolist() == [False, False, False]
    assert sk.find(twice, sk.cells("first")).tolist() == [True, True, True]


def test_remove_drops_the_empty_rows_and_clears_the_other_found_cells() -> None:
    assert sk.remove(CELLS, sk.cells("empty")).to_dict() == {0: "диван", 1: "стол", 2: "диван"}
    assert sk.remove(CELLS, sk.cells("repeated")).to_dict() == {0: "", 1: "стол", 2: "", 3: ""}


def test_extract_keeps_the_cell_where_found() -> None:
    assert sk.extract(CELLS, sk.cells("repeated")).tolist() == ["диван", "", "диван", ""]


def test_remove_drops_the_rows_of_a_table() -> None:
    frame = pd.DataFrame({"phrase": ["диван", "", "стол"], "freq": [1, 2, 3]})

    result = sk.remove(frame, sk.cells("empty"), column="phrase")

    assert result["freq"].tolist() == [1, 3]
    assert result["phrase"].tolist() == ["диван", "стол"]


def test_contains_starts_ends_with_list_items() -> None:
    phrases = pd.Series(["Купить диван", "диван дёшево", "стол"])

    assert sk.find(phrases, sk.cells("contains", items=["ДИВАН"])).tolist() == [True, True, False]
    assert sk.find(phrases, sk.cells("starts", items=["купить", "стол"])).tolist() == [True, False, True]
    assert sk.find(phrases, sk.cells("ends", items=["дешево"])).tolist() == [False, True, False]


def test_starts_and_ends_with_a_preposition() -> None:
    phrases = pd.Series(["в москве", "диван в", "диван"])

    assert sk.find(phrases, sk.cells("starts", prepositions=True)).tolist() == [True, False, False]
    assert sk.find(phrases, sk.cells("ends", prepositions=True)).tolist() == [False, True, False]
    assert sk.find(phrases, sk.cells("contains", prepositions=True)).tolist() == [True, True, False]


def test_regex() -> None:
    phrases = pd.Series(["диван 5", "диван"])

    assert sk.find(phrases, sk.cells("regex", pattern=r"\d")).tolist() == [True, False]
