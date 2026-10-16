#!/usr/bin/env python3
"""Build the bundled marker lists (ADR 0002) from the 18 xlsx of the !SEMTools add-in.

    uv run scripts/build_markers.py [--config scripts/build_data.toml] [--out src/rb_semkit/data]

The folder comes from `[sources] markers` of the config file (docs/brief.md «Materials»). Each list is column A of
the first sheet (so DIY loses its 2nd sheet and cars its brand table in B..F), stripped and deduped, in the
add-in's case. It writes `markers/<name>.txt.gz`, one phrase per line; the same sources give byte-identical files.
"""

from __future__ import annotations

import argparse
import gzip
import sys
import tomllib
from pathlib import Path

import openpyxl
from build_data import DEFAULT_CONFIG, DEFAULT_OUT, SourceMissing

LIST_NAMES = (
    *("geo", "mosmetro", "districts", "MO", "citiesRu", "questions", "fun", "DIY", "edu"),
    *("game", "sale", "rent", "reviews", "color", "material", "origin", "cars", "names"),
)


def read_list(path: Path) -> list[str]:
    """Column A of the first sheet: one phrase per cell, spaces collapsed, empty cells and repeats dropped."""
    if not path.is_file():
        raise SourceMissing(f"source file not found: {path}")
    workbook = openpyxl.load_workbook(path, read_only=True)
    try:
        cells = (row[0] for row in workbook.worksheets[0].iter_rows(min_col=1, max_col=1, values_only=True))
        phrases = (" ".join(str(value).split()) for value in cells if value is not None)
        return list(dict.fromkeys(phrase for phrase in phrases if phrase))
    finally:
        workbook.close()


def write_list(path: Path, phrases: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(("\n".join(phrases) + "\n").encode("utf-8"), compresslevel=9, mtime=0))


def build(source: Path, out: Path) -> None:
    lists = {name: read_list(source / f"{name}.xlsx") for name in LIST_NAMES}  # all read before any is written
    for name, phrases in lists.items():
        write_list(out / "markers" / f"{name}.txt.gz", phrases)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the bundled marker lists from the !SEMTools xlsx.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="TOML with a [sources] table")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="the package data directory")
    args = parser.parse_args(argv)
    source = Path(tomllib.loads(args.config.read_text())["sources"]["markers"])
    try:
        build(source, args.out)
    except SourceMissing as error:
        print(f"build_markers: {error}", file=sys.stderr)
        return 1
    print(f"build_markers: built {args.out / 'markers'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
