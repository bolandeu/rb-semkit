"""Every row of the 7 sheets of the reference workbook is a case, with `vba` equal to the workbook value.

The workbook (`[conformance] reference` of scripts/build_data.toml) holds the add-in's output on 20 phrases; its sheet
README names the handler of each sheet. A per-phrase sheet gives one case per row: `ref-<sheet>-<row>`. Sheet dupes
gives one case per row and kind, `ref-dupes-<kind>-<row>`: the input is the column down to that row, because a
duplicate depends on the rows above it. An n-gram sheet holds one table for the whole column: one case, `ref-<sheet>`,
its rows in workbook order. The test is skipped where the workbook is not on the machine.
"""

from __future__ import annotations

import tomllib
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import openpyxl
import pytest

from .case_files import SEP, Case, all_cases, render_value

ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = Path(tomllib.loads((ROOT / "scripts" / "build_data.toml").read_text())["conformance"]["reference"])
FIRST_ROW = 2  # row 1 is the header
# Sheet dupes: the column of each kind (README: exact —kka, explicit ako—, implicit akoa, implicit_wordforms ako·).
DUPE_KINDS = {"exact": "exact", "explicit": "explicit", "implicit": "implicit", "implicit_wordforms": "lemmas"}

pytestmark = pytest.mark.skipif(not WORKBOOK.is_file(), reason="the reference workbook is not on this machine")

Reference = tuple[str, str, dict[str, Any], str, str]  # case_id, function, call, input, vba
Rows = list[tuple[Any, ...]]
Builder = Callable[[str, tuple[Any, ...], Rows], Iterator[Reference]]


def _phrases(rows: Rows) -> list[str]:
    """Column A down to its last filled cell; an empty cell inside it is an empty phrase."""
    filled = [index for index, row in enumerate(rows) if row[0] is not None]
    return [render_value(row[0]) for row in rows[: filled[-1] + 1]]


def _per_phrase(function: str, call: dict[str, Any]) -> Builder:
    def cases(sheet: str, _header: tuple[Any, ...], rows: Rows) -> Iterator[Reference]:
        for number, row in enumerate(rows, FIRST_ROW):
            yield f"ref-{sheet}-{number:02d}", function, call, render_value(row[0]), render_value(row[1])

    return cases


def _table(function: str, call: dict[str, Any]) -> Builder:
    """Columns C:D hold the table the handler wrote for column A."""

    def cases(sheet: str, _header: tuple[Any, ...], rows: Rows) -> Iterator[Reference]:
        table = SEP.join(f"{render_value(row[2])}={render_value(row[3])}" for row in rows if row[2] is not None)
        yield f"ref-{sheet}", function, call, SEP.join(_phrases(rows)), table

    return cases


def _dupes(sheet: str, header: tuple[Any, ...], rows: Rows) -> Iterator[Reference]:
    phrases = _phrases(rows)
    for column, name in enumerate(header[1:], 1):
        kind = DUPE_KINDS[name]
        marks = [render_value(row[column]) for row in rows]
        for index in range(len(phrases)):
            yield (
                f"ref-{sheet}-{kind}-{index + FIRST_ROW:02d}",
                "dupes",
                {"kind": kind, "action": "mark_except_first"},
                SEP.join(phrases[: index + 1]),
                SEP.join(marks[: index + 1]),
            )


SHEETS: dict[str, Builder] = {
    "dupes": _dupes,
    "ngrams_1": _table("ngrams", {"n": 1}),
    "ngrams_2": _table("ngrams", {"n": 2}),
    "bigrams": _table("bigrams", {}),
    "lemmas": _per_phrase("lemmatize", {}),
    "markers_geo": _per_phrase("markers.extract", {"lists": "geo"}),
    "stopwords": _per_phrase("stopwords.remove", {}),
}


def _references() -> list[Reference]:
    workbook = openpyxl.load_workbook(WORKBOOK, read_only=True)
    try:
        references = []
        for sheet in workbook.worksheets[1:]:  # the first sheet is README
            header, *rows = sheet.iter_rows(values_only=True)
            references += SHEETS[sheet.title](sheet.title, header, rows)
        return references
    finally:
        workbook.close()


@pytest.fixture(scope="module")
def cases() -> dict[str, Case]:
    return {case.case_id: case for case in all_cases()}


def test_the_workbook_has_the_seven_sheets_the_cases_map() -> None:
    sheets = {reference[0].split("-")[1] for reference in _references()}

    assert sheets == set(SHEETS)


@pytest.mark.parametrize("reference", _references() if WORKBOOK.is_file() else [], ids=lambda ref: ref[0])
def test_a_workbook_row_is_a_case_with_its_value_as_vba(reference: Reference, cases: dict[str, Case]) -> None:
    case_id, function, call, phrases, vba = reference

    case = cases.get(case_id)

    assert case is not None, f"no case {case_id}"
    assert (case.function, case.kwargs, case.input, case.vba) == (function, call, phrases, vba)
