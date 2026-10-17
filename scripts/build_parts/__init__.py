"""The build parts of scripts/build_data.py, one per area (`<area>.py`), and what they share.

A part builds the data of its area (ADR 0002) into `rb_semkit/data/<area>/` and describes it for the area's data
manifest. It defines two functions; `sources` are the paths of `[sources]` of the config file:

    manifest(sources) -> dict[str, Entry]   each data file of the area (a JSON file: each of its tables,
                                            «file.json:table»), by its path under the area folder
    build(sources, out) -> None             writes the area's data into `out`; the same sources give byte-identical files

A part raises SourceMissing when a source is not there. A file whose name starts with «_» is not a part.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

REPEAT = "a repeat of an earlier item"
REPEATED_KEY = "a later row of the same key wins"


class SourceMissing(Exception):
    pass


class Sources(dict[str, Path]):
    """The paths of `[sources]` of the config file, by key; a key the config lacks raises SourceMissing."""

    def __missing__(self, key: str) -> Path:
        raise SourceMissing(f"the config has no [sources] {key}")


@dataclass
class Entry:
    """What one data file (or one table of a JSON file) takes from its source."""

    source: str
    source_items: int = 0
    bundled_items: int = 0
    dropped: list[dict[str, str]] = field(default_factory=list)
    added: list[dict[str, str]] = field(default_factory=list)

    def drop(self, item: str, reason: str) -> None:
        self.dropped.append({"item": item, "reason": reason})

    def add(self, item: str, reason: str) -> None:
        self.added.append({"item": item, "reason": reason})


def read_lines(path: Path) -> list[str]:
    if not path.is_file():
        raise SourceMissing(f"source file not found: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def write_json(path: Path, data: dict) -> None:
    """Compact, on one line, keys sorted."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8"
    )


def read_sheet(path: Path) -> list[list[str]]:
    """A sheet exported as TSV: its rows of cells."""
    return [line.split("\t") for line in read_lines(path)]


def cell(address: str) -> tuple[int, int]:
    """A cell address ("AB12") as 0-based (row, column)."""
    letters = address.rstrip("0123456789")
    column = 0
    for letter in letters:
        column = column * 26 + ord(letter) - ord("A") + 1
    return int(address[len(letters) :]) - 1, column - 1


def cell_range(sheet: list[list[str]], address: str) -> list[list[str]]:
    """The rows of `address` ("E50:F305"), fully empty rows dropped."""
    (top, left), (bottom, right) = (cell(end) for end in address.split(":"))
    rows = [(row + [""] * (right + 1))[left : right + 1] for row in sheet[top : bottom + 1]]
    return [row for row in rows if any(row)]


def sheet_table(sheet: list[list[str]], address: str) -> list[str] | dict[str, str]:
    """A one-column range as a list of its non-empty cells; two columns as key → value (the last key wins)."""
    rows = cell_range(sheet, address)
    if len(rows[0]) == 1:
        return [row[0] for row in rows]
    return {key: value for key, value in rows}


def range_entry(sheet: list[list[str]], name: str, address: str) -> Entry:
    """A range of sheet `abc`: one item per filled row; a two-column range is key → value."""
    rows = cell_range(sheet, address)
    entry = Entry(f"sheet abc {address} ({name})", len(rows))
    if len(rows[0]) > 1:
        last_row = {row[0]: index for index, row in enumerate(rows)}
        for index, row in enumerate(rows):
            if last_row[row[0]] != index:
                entry.drop("\t".join(row), REPEATED_KEY)
    return entry
