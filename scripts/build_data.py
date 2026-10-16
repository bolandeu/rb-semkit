#!/usr/bin/env python3
"""Build the bundled reference data (ADR 0002) from the !SEMTools sources.

    uv run scripts/build_data.py [--config scripts/build_data.toml] [--out src/rb_semkit/data]

The source paths come from the config file (docs/brief.md «Materials»). The same sources give
byte-identical files, so the script is safe to re-run; the built files are committed. It writes:

    morph/lemmas.marisa   wordform → "lemma<TAB>pos" (BytesTrie), plus a ё→е key for every wordform with ё
    morph/forms.marisa    lemma → each of its wordforms (BytesTrie, one value per wordform)
    morph/morph.json      lemma_suffixes (lemmSuf), nouns_like_adjectives (nounsLikeAdj),
                          adjective_endings (the first column of adjSuffixes)
    lists/lists.json      stopwords, three preposition lists, abbreviations, phrase_start_words (charsPat)

JSON is written compact, on one line. Marker lists are built by build_markers.py; the declension tables (v2) are not built.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

import marisa_trie  # ty: ignore[unresolved-import]  # a compiled extension without type stubs

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = Path(__file__).with_suffix(".toml")
DEFAULT_OUT = ROOT / "src" / "rb_semkit" / "data"

# A wordform is letters, maybe joined by hyphens («камне-на-оби»); this drops «0,0000001» and «од?оклассники».
WORDFORM = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")
# Named ranges of sheet `abc` (the add-in's `xl/workbook.xml`), by output name.
TABLES = {
    "morph": {
        "lemma_suffixes": "E50:F305",  # lemmSuf is E50:G305; G (a POS guess) is not used by the add-in
        "nouns_like_adjectives": "J1:J417",
        "adjective_endings": "AD2:AD90",  # adjSuffixes is AD2:AS90; the other columns are declension (v2)
    },
    "lists": {"abbreviations": "M1:M1016", "phrase_start_words": "BA1:BA644"},
}
# String literals of RibbonCallbacks.vba, by output name: the pattern captures the list.
VBA_LISTS = {
    "stopwords": r"Function stopwords\$\(\)\s*stopwords = (.*?)\nEnd Function",
    "prepositions": r"Function prps\$\(\): prps = (\"[^\"]*\")",
    "complement_prepositions": r"Function collocs\$.*?preps = (\"[^\"]*\")",
    "toponym_prepositions_ru": r"Sub udalit_toponimy_s_pryedlogami.*?Case Else: b = Array\(([^)]*)\)",
    "toponym_prepositions_en": r"Sub udalit_toponimy_s_pryedlogami.*?Case True: b = Array\(([^)]*)\)",
}
# Junk in the VBA literals: «пo» has a latin «o»; a stray latin «g» sits among the Russian words.
JUNK_FIXES = {"пo": "по", "g": None}


class SourceMissing(Exception):
    pass


def read_lines(path: Path) -> list[str]:
    if not path.is_file():
        raise SourceMissing(f"source file not found: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def yo_to_ye(text: str) -> str:
    return text.replace("ё", "е")


def lemma_rows(path: Path) -> list[tuple[str, str, str]]:
    """(wordform, lemma, pos) in source order: header and junk rows dropped, lower case."""
    rows = []
    for line in read_lines(path)[1:]:
        wordform, lemma, pos = line.split("\t")
        if pos and WORDFORM.fullmatch(wordform):
            rows.append((wordform.lower(), lemma.lower(), pos))
    return rows


def lemma_trie(rows: list[tuple[str, str, str]]) -> marisa_trie.BytesTrie:
    found: dict[str, str] = {}
    for wordform, lemma, pos in rows:  # a repeated wordform: the last row wins, as the add-in's sorted VLOOKUP
        found[wordform] = f"{lemma}\t{pos}"
    for wordform, value in list(found.items()):
        found.setdefault(yo_to_ye(wordform), value)
    return marisa_trie.BytesTrie((key, value.encode()) for key, value in sorted(found.items()))


def forms_trie(rows: list[tuple[str, str, str]]) -> marisa_trie.BytesTrie:
    pairs = {(key, wordform) for wordform, lemma, _ in rows for key in (lemma, yo_to_ye(lemma))}
    return marisa_trie.BytesTrie((lemma, wordform.encode()) for lemma, wordform in sorted(pairs))


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


def vba_list(source: str, name: str) -> list[str]:
    match = re.search(VBA_LISTS[name], source, re.DOTALL)
    if match is None:
        raise SourceMissing(f"the VBA list {name!r} was not found: the VBA source changed")
    words = " ".join(re.findall(r'"([^"]*)"', match.group(1))).split()
    fixed = (JUNK_FIXES.get(word, word) for word in words)
    return list(dict.fromkeys(word.lower() for word in fixed if word))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8"
    )


def build(sources: dict[str, Path], out: Path) -> None:
    rows = lemma_rows(sources["lemmas"])
    sheet = [line.split("\t") for line in read_lines(sources["sheet_abc"])]
    vba = "\n".join(read_lines(sources["vba"]))
    tables = {
        name: {key: sheet_table(sheet, address) for key, address in group.items()} for name, group in TABLES.items()
    }
    lists = tables["lists"] | {name: vba_list(vba, name) for name in VBA_LISTS}

    (out / "morph").mkdir(parents=True, exist_ok=True)
    lemma_trie(rows).save(str(out / "morph" / "lemmas.marisa"))
    forms_trie(rows).save(str(out / "morph" / "forms.marisa"))
    write_json(out / "morph" / "morph.json", tables["morph"])
    write_json(out / "lists" / "lists.json", lists)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the bundled reference data from the !SEMTools sources.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="TOML with a [sources] table")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="the package data directory")
    args = parser.parse_args(argv)
    sources = {key: Path(value) for key, value in tomllib.loads(args.config.read_text())["sources"].items()}
    try:
        build(sources, args.out)
    except SourceMissing as error:
        print(f"build_data: {error}", file=sys.stderr)
        return 1
    print(f"build_data: built {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
