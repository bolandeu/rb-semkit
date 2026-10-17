"""The data of the declension area: the add-in's declension tables and the words that govern a case.

    tables.json     noun_endings (nounSuffixes: a 3-letter ending → 11 endings), noun_exceptions (nounExclusions:
                    a word → its 11 forms), indeclinable (nonDecl), adjective_endings (adjSuffixes: a 3-letter
                    ending → 15 endings), adjective_exceptions (adjExclusions: a word → its 15 forms);
                    governing (arrPron: a word after one of them keeps its case) and takes_<case> (the words that
                    take each case right before the main word of the irrelevant-words search)

The 11 forms are the genitive, dative, accusative, instrumental and prepositional singular, then the 6 cases of the
plural; the 15 of an adjective are the 11 of its own gender, then the feminine nominative, the feminine genitive
(also the dative, instrumental and prepositional), the feminine accusative and the neuter nominative. Keys and
words are lower case with ё as е. Sources: `sheet_abc` (sheet `abc` of the add-in as TSV), `vba`
(RibbonCallbacks.vba) and `find_irrelevant` (findIrr.frm), whose string literals hold the word lists. The corrections
of the tables are declension.toml next to this part: a row there replaces the row of its key, or is added.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from build_parts import Entry, SourceMissing, cell_range, read_lines, read_sheet, write_json

# Named ranges of sheet `abc` (the add-in's `xl/workbook.xml`), by table name.
TABLES = {
    "noun_endings": "Q1:AB3331",
    "noun_exceptions": "Q3380:AB11089",
    "adjective_endings": "AD2:AS90",
    "adjective_exceptions": "AD93:AS136",
}
INDECLINABLE = ("indeclinable", "B1:B1205")
# Row 1 of nounSuffixes holds the column titles (РОД, ДАТ, ...) over the cells of the ending «ааз».
HEADER_ROWS = {"noun_endings": 1}
HEADER = "the column titles, not an ending"
REPEATED_KEY = "a later row of the same key wins (ё as е)"
REPEATED_WORD = "a repeat of an earlier item (ё as е)"
CORRECTIONS = Path(__file__).with_suffix(".toml")
CORRECTED = "a corrected row: its line of declension.toml replaces it"
# Array literals of the VBA sources, by list name: (source key, the array variable).
WORD_LISTS = {
    "governing": ("vba", "arrPron"),
    "takes_nominative": ("find_irrelevant", "arrImenit"),
    "takes_genitive": ("find_irrelevant", "arrRodit"),
    "takes_dative": ("find_irrelevant", "arrDat"),
    "takes_accusative": ("find_irrelevant", "arrVinit"),
    "takes_instrumental": ("find_irrelevant", "arrTvorit"),
    "takes_prepositional": ("find_irrelevant", "arrPredl"),
}


def table_key(word: str) -> str:
    return word.lower().replace("ё", "е")


def _rows(sheet: list[list[str]], name: str) -> list[list[str]]:
    return cell_range(sheet, TABLES[name])[HEADER_ROWS.get(name, 0) :]


def corrections(name: str, path: Path = CORRECTIONS) -> list[dict]:
    """The lines of declension.toml for the table `name`."""
    return [line for line in tomllib.loads(path.read_text(encoding="utf-8"))["corrections"] if line["table"] == name]


def _forms(sheet: list[list[str]], name: str) -> dict[str, list[str]]:
    forms = {table_key(row[0]): row[1:] for row in _rows(sheet, name)}
    return forms | {line["key"]: line["forms"] for line in corrections(name)}


def _table_entry(sheet: list[list[str]], name: str) -> Entry:
    """One item per filled row; the header row and the earlier rows of a repeated key are dropped."""
    rows = cell_range(sheet, TABLES[name])
    entry = Entry(f"sheet abc {TABLES[name]} ({name})", len(rows))
    for row in rows[: HEADER_ROWS.get(name, 0)]:
        entry.drop("\t".join(row), HEADER)
    kept = _rows(sheet, name)
    last_row = {table_key(row[0]): index for index, row in enumerate(kept)}
    for index, row in enumerate(kept):
        if last_row[table_key(row[0])] != index:
            entry.drop("\t".join(row), REPEATED_KEY)
    for line in corrections(name):
        if line["key"] in last_row:
            entry.drop("\t".join(kept[last_row[line["key"]]]), CORRECTED)
        entry.add("\t".join([line["key"], *line["forms"]]), line["why"])
    return entry


def _distinct_entry(source: str, words: list[str]) -> Entry:
    """One item per word; a repeat of an earlier word (ё as е) is dropped."""
    entry = Entry(source, len(words))
    seen: set[str] = set()
    for word in words:
        if table_key(word) in seen:
            entry.drop(word, REPEATED_WORD)
        seen.add(table_key(word))
    return entry


def _distinct(words: list[str]) -> list[str]:
    return list(dict.fromkeys(table_key(word) for word in words))


def _indeclinable(sheet: list[list[str]]) -> list[str]:
    return [row[0] for row in cell_range(sheet, INDECLINABLE[1])]


def _array(sources: dict[str, Path], name: str) -> tuple[list[str], str]:
    """The words of an array literal of a VBA source, and where it stands."""
    key, variable = WORD_LISTS[name]
    text = "\n".join(read_lines(sources[key]))
    match = re.search(rf"{variable} = Array\(([^)]*)\)", text)
    if match is None:
        raise SourceMissing(f"the VBA array {variable!r} was not found: the VBA source changed")
    line = text.count("\n", 0, match.start()) + 1
    return re.findall(r'"([^"]*)"', match.group(1)), f"{sources[key].name} L{line}: the literal of {variable}"


def manifest(sources: dict[str, Path]) -> dict[str, Entry]:
    sheet = read_sheet(sources["sheet_abc"])
    entries = {f"tables.json:{name}": _table_entry(sheet, name) for name in TABLES}
    source = f"sheet abc {INDECLINABLE[1]} ({INDECLINABLE[0]})"
    entries[f"tables.json:{INDECLINABLE[0]}"] = _distinct_entry(source, _indeclinable(sheet))
    for name in WORD_LISTS:
        words, where = _array(sources, name)
        entries[f"tables.json:{name}"] = _distinct_entry(where, words)
    return entries


def build(sources: dict[str, Path], out: Path) -> None:
    sheet = read_sheet(sources["sheet_abc"])
    tables: dict = {name: _forms(sheet, name) for name in TABLES}
    tables[INDECLINABLE[0]] = _distinct(_indeclinable(sheet))
    tables |= {name: _distinct(_array(sources, name)[0]) for name in WORD_LISTS}
    write_json(out / "tables.json", tables)
