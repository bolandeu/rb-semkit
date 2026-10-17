#!/usr/bin/env python3
"""Rebuild tests/conformance/data_manifest.json: what each bundled data file takes from its !SEMTools source.

    uv run scripts/data_manifest.py [--config scripts/build_data.toml] [--out tests/conformance/data_manifest.json]

For each bundled file (a JSON file: each of its tables) the manifest holds its source, the number of items in the
source, the number the build keeps, and every item the build drops, with the reason. The items are read from the
sources named in the config file, as build_data.py and build_markers.py read them, and counted by the rules those
scripts apply; tests/conformance/test_data.py checks the committed data against the manifest, offline.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import openpyxl
from build_data import (
    DEFAULT_CONFIG,
    JUNK_FIXES,
    ROOT,
    TABLES,
    VBA_LISTS,
    WORDFORM,
    SourceMissing,
    cell,
    read_lines,
    yo_to_ye,
)
from build_markers import LIST_NAMES

DEFAULT_OUT = ROOT / "tests" / "conformance" / "data_manifest.json"
JUNK_ROW = "junk row: the wordform is not letters (maybe joined by hyphens) or the part of speech is empty"
REPEATED_WORDFORM = "a later row of the same wordform wins, as the add-in's sorted VLOOKUP"
SAME_PAIR = "the same lemma and wordform as an earlier row once the lemma is lower case"
YO_KEY = "a ё→е key for a word with ё"
REPEATED_KEY = "a later row of the same key wins"
REPEAT = "a repeat of an earlier item"
JUNK_WORD = "junk in the VBA literal: a stray latin letter among the Russian words"
OUTSIDE_LIST = "not in column A of the first sheet, which is the list the add-in reads"


@dataclass
class Entry:
    source: str
    source_items: int = 0
    bundled_items: int = 0
    dropped: list[dict[str, str]] = field(default_factory=list)
    added: list[dict[str, str]] = field(default_factory=list)

    def drop(self, item: str, reason: str) -> None:
        self.dropped.append({"item": item, "reason": reason})

    def add(self, item: str, reason: str) -> None:
        self.added.append({"item": item, "reason": reason})


def lemma_entries(path: Path) -> dict[str, Entry]:
    """morph/lemmas.marisa (wordform → lemma, pos) and morph/forms.marisa (lemma → wordforms) from lemms.tsv."""
    rows = [line.split("\t") for line in read_lines(path)[1:]]
    lemmas = Entry(f"{path.name}: every row", len(rows))
    forms = Entry(f"{path.name}: every row as a lemma and its wordform", len(rows))
    kept = []
    for wordform, lemma, pos in rows:
        if pos and WORDFORM.fullmatch(wordform):
            kept.append((wordform.lower(), lemma.lower(), pos))
        else:
            lemmas.drop(f"{wordform}\t{lemma}\t{pos}", JUNK_ROW)
            forms.drop(f"{wordform}\t{lemma}\t{pos}", JUNK_ROW)
    last_row = {wordform: index for index, (wordform, _, _) in enumerate(kept)}
    for index, (wordform, lemma, pos) in enumerate(kept):
        if last_row[wordform] != index:
            lemmas.drop(f"{wordform}\t{lemma}\t{pos}", REPEATED_WORDFORM)
    for wordform in sorted({yo_to_ye(wordform) for wordform in last_row} - set(last_row)):
        lemmas.add(wordform, YO_KEY)
    seen: set[tuple[str, str]] = set()
    for wordform, lemma, _ in kept:
        if (lemma, wordform) in seen:
            forms.drop(f"{lemma}\t{wordform}", SAME_PAIR)
        seen.add((lemma, wordform))
    for lemma, wordform in sorted({(yo_to_ye(lemma), wordform) for lemma, wordform in seen} - seen):
        forms.add(f"{lemma}\t{wordform}", YO_KEY)
    return {"morph/lemmas.marisa": lemmas, "morph/forms.marisa": forms}


def range_entry(sheet: list[list[str]], name: str, address: str) -> Entry:
    """A range of sheet `abc`: one item per filled row; a two-column range is key → value."""
    (top, left), (bottom, right) = (cell(end) for end in address.split(":"))
    rows = [(row + [""] * (right + 1))[left : right + 1] for row in sheet[top : bottom + 1]]
    rows = [row for row in rows if any(row)]
    entry = Entry(f"sheet abc {address} ({name})", len(rows))
    if right > left:
        last_row = {row[0]: index for index, row in enumerate(rows)}
        for index, row in enumerate(rows):
            if last_row[row[0]] != index:
                entry.drop("\t".join(row), REPEATED_KEY)
    return entry


def vba_entry(source: str, path: Path, name: str) -> Entry:
    """A string literal of RibbonCallbacks.vba: one item per word; «пo» is fixed to «по», a stray «g» dropped."""
    match = re.search(VBA_LISTS[name], source, re.DOTALL)
    if match is None:
        raise SourceMissing(f"the VBA list {name!r} was not found: the VBA source changed")
    words = " ".join(re.findall(r'"([^"]*)"', match.group(1))).split()
    line = source.count("\n", 0, match.start()) + 1
    entry = Entry(f"{path.name} L{line}: the literal of {name}", len(words))
    seen: set[str] = set()
    for word in words:
        fixed = JUNK_FIXES.get(word, word)
        if fixed is None:
            entry.drop(word, JUNK_WORD)
        elif fixed.lower() in seen:
            entry.drop(word, REPEAT)
        else:
            seen.add(fixed.lower())
    return entry


def marker_entry(path: Path) -> Entry:
    """Every filled cell of every sheet of a marker list workbook; the list is column A of the first sheet."""
    if not path.is_file():
        raise SourceMissing(f"source file not found: {path}")
    workbook = openpyxl.load_workbook(path, read_only=True)
    try:
        cells = [
            (sheet_index, column, " ".join(str(value).split()))
            for sheet_index, sheet in enumerate(workbook.worksheets)
            for row in sheet.iter_rows(values_only=True)
            for column, value in enumerate(row)
            if value is not None and str(value).strip()
        ]
    finally:
        workbook.close()
    entry = Entry(f"{path.name}: column A of the first sheet", len(cells))
    seen: set[str] = set()
    for sheet_index, column, phrase in cells:
        if (sheet_index, column) != (0, 0):
            entry.drop(phrase, OUTSIDE_LIST)
        elif phrase in seen:
            entry.drop(phrase, REPEAT)
        else:
            seen.add(phrase)
    return entry


def manifest(sources: dict[str, Path]) -> dict[str, dict]:
    entries = lemma_entries(sources["lemmas"])
    sheet = [line.split("\t") for line in read_lines(sources["sheet_abc"])]
    for group, tables in TABLES.items():
        for name, address in tables.items():
            entries[f"{group}/{group}.json:{name}"] = range_entry(sheet, name, address)
    vba = "\n".join(read_lines(sources["vba"]))
    for name in VBA_LISTS:
        entries[f"lists/lists.json:{name}"] = vba_entry(vba, sources["vba"], name)
    for name in LIST_NAMES:
        entries[f"markers/{name}.txt.gz"] = marker_entry(sources["markers"] / f"{name}.xlsx")
    for entry in entries.values():
        entry.bundled_items = entry.source_items - len(entry.dropped) + len(entry.added)
    return {name: vars(entry) for name, entry in sorted(entries.items())}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rebuild the manifest of the bundled data from the !SEMTools sources.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="TOML with a [sources] table")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="the manifest file")
    args = parser.parse_args(argv)
    sources = {key: Path(value) for key, value in tomllib.loads(args.config.read_text())["sources"].items()}
    try:
        data = manifest(sources)
    except SourceMissing as error:
        print(f"data_manifest: {error}", file=sys.stderr)
        return 1
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"data_manifest: wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
