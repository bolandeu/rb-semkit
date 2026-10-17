"""The data of the markers area: the 18 bundled marker lists, from the xlsx of the !SEMTools add-in.

    <name>.txt.gz   one phrase per line

Source: `markers` (the folder of the xlsx). Each list is column A of the first sheet (so DIY loses its 2nd sheet and
cars its brand table in B..F), stripped and deduped, in the add-in's case.
"""

from __future__ import annotations

import gzip
from pathlib import Path

import openpyxl

from build_parts import REPEAT, Entry, SourceMissing

LIST_NAMES = (
    *("geo", "mosmetro", "districts", "MO", "citiesRu", "questions", "fun", "DIY", "edu"),
    *("game", "sale", "rent", "reviews", "color", "material", "origin", "cars", "names"),
)
OUTSIDE_LIST = "not in column A of the first sheet, which is the list the add-in reads"


def _cells(path: Path) -> list[tuple[int, int, str]]:
    """(sheet, column, phrase) of every filled cell of every sheet, in order; spaces collapsed."""
    if not path.is_file():
        raise SourceMissing(f"source file not found: {path}")
    workbook = openpyxl.load_workbook(path, read_only=True)
    try:
        return [
            (sheet_index, column, " ".join(str(value).split()))
            for sheet_index, sheet in enumerate(workbook.worksheets)
            for row in sheet.iter_rows(values_only=True)
            for column, value in enumerate(row)
            if value is not None and str(value).strip()
        ]
    finally:
        workbook.close()


def read_list(path: Path) -> list[str]:
    """Column A of the first sheet: one phrase per cell, empty cells and repeats dropped."""
    return list(dict.fromkeys(phrase for sheet, column, phrase in _cells(path) if (sheet, column) == (0, 0)))


def _entry(path: Path) -> Entry:
    """Every filled cell of every sheet of a marker list workbook; the list is column A of the first sheet."""
    cells = _cells(path)
    entry = Entry(f"{path.name}: column A of the first sheet", len(cells))
    seen: set[str] = set()
    for sheet, column, phrase in cells:
        if (sheet, column) != (0, 0):
            entry.drop(phrase, OUTSIDE_LIST)
        elif phrase in seen:
            entry.drop(phrase, REPEAT)
        else:
            seen.add(phrase)
    return entry


def manifest(sources: dict[str, Path]) -> dict[str, Entry]:
    return {f"{name}.txt.gz": _entry(sources["markers"] / f"{name}.xlsx") for name in LIST_NAMES}


def build(sources: dict[str, Path], out: Path) -> None:
    lists = {name: read_list(sources["markers"] / f"{name}.xlsx") for name in LIST_NAMES}
    out.mkdir(parents=True, exist_ok=True)
    for name, phrases in lists.items():
        text = "\n".join(phrases) + "\n"
        (out / f"{name}.txt.gz").write_bytes(gzip.compress(text.encode("utf-8"), compresslevel=9, mtime=0))
