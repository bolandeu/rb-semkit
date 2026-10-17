"""The data of the text area: the word lists.

    lists.json      stopwords, three preposition lists, abbreviations, phrase_start_words (charsPat)

Sources: `sheet_abc` (sheet `abc` of the add-in as TSV) and `vba` (RibbonCallbacks.vba, whose string literals hold the
stopwords and the prepositions).
"""

from __future__ import annotations

import re
from pathlib import Path

from build_parts import REPEAT, Entry, SourceMissing, range_entry, read_lines, read_sheet, sheet_table, write_json

# Named ranges of sheet `abc` (the add-in's `xl/workbook.xml`), by list name.
TABLES = {"abbreviations": "M1:M1016", "phrase_start_words": "BA1:BA644"}
# String literals of RibbonCallbacks.vba, by list name: the pattern captures the list.
VBA_LISTS = {
    "stopwords": r"Function stopwords\$\(\)\s*stopwords = (.*?)\nEnd Function",
    "prepositions": r"Function prps\$\(\): prps = (\"[^\"]*\")",
    "complement_prepositions": r"Function collocs\$.*?preps = (\"[^\"]*\")",
    "toponym_prepositions_ru": r"Sub udalit_toponimy_s_pryedlogami.*?Case Else: b = Array\(([^)]*)\)",
    "toponym_prepositions_en": r"Sub udalit_toponimy_s_pryedlogami.*?Case True: b = Array\(([^)]*)\)",
}
# Junk in the VBA literals: «пo» has a latin «o»; a stray latin «g» sits among the Russian words.
JUNK_FIXES = {"пo": "по", "g": None}
JUNK_WORD = "junk in the VBA literal: a stray latin letter among the Russian words"


def _literal(source: str, name: str) -> re.Match[str]:
    match = re.search(VBA_LISTS[name], source, re.DOTALL)
    if match is None:
        raise SourceMissing(f"the VBA list {name!r} was not found: the VBA source changed")
    return match


def _words(match: re.Match[str]) -> list[str]:
    return " ".join(re.findall(r'"([^"]*)"', match.group(1))).split()


def vba_list(source: str, name: str) -> list[str]:
    fixed = (JUNK_FIXES.get(word, word) for word in _words(_literal(source, name)))
    return list(dict.fromkeys(word.lower() for word in fixed if word))


def _vba_entry(source: str, path: Path, name: str) -> Entry:
    """A string literal of RibbonCallbacks.vba: one item per word; «пo» is fixed to «по», a stray «g» dropped."""
    match = _literal(source, name)
    words = _words(match)
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


def manifest(sources: dict[str, Path]) -> dict[str, Entry]:
    sheet = read_sheet(sources["sheet_abc"])
    vba = "\n".join(read_lines(sources["vba"]))
    entries = {f"lists.json:{name}": range_entry(sheet, name, address) for name, address in TABLES.items()}
    return entries | {f"lists.json:{name}": _vba_entry(vba, sources["vba"], name) for name in VBA_LISTS}


def build(sources: dict[str, Path], out: Path) -> None:
    sheet = read_sheet(sources["sheet_abc"])
    vba = "\n".join(read_lines(sources["vba"]))
    lists = {name: sheet_table(sheet, address) for name, address in TABLES.items()}
    write_json(out / "lists.json", lists | {name: vba_list(vba, name) for name in VBA_LISTS})
