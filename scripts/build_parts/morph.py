"""The data of the morph area: the lemma dictionary and the tables of the lemma rules.

    lemmas.marisa   wordform → "lemma<TAB>pos" (BytesTrie), plus a ё→е key for every wordform with ё
    forms.marisa    lemma → each of its wordforms (BytesTrie, one value per wordform)
    morph.json      lemma_suffixes (lemmSuf), nouns_like_adjectives (nounsLikeAdj),
                    adjective_endings (the first column of adjSuffixes)

Sources: `lemmas` (lemms.tsv) and `sheet_abc` (sheet `abc` of the add-in as TSV). The corrections of lemms.tsv are
morph.toml next to this part: a corrected wordform takes the lemma and the part of speech written there instead of its
rows (ADR 0003). The declension tables are the declension part's (scripts/build_parts/declension.py).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import marisa_trie  # ty: ignore[unresolved-import]  # a compiled extension without type stubs

from build_parts import Entry, range_entry, read_lines, read_sheet, sheet_table, write_json

# A wordform is letters, maybe joined by hyphens («камне-на-оби»); this drops «0,0000001» and «од?оклассники».
WORDFORM = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")
# Named ranges of sheet `abc` (the add-in's `xl/workbook.xml`), by table name.
TABLES = {
    "lemma_suffixes": "E50:F305",  # lemmSuf is E50:G305; G (a POS guess) is not used by the add-in
    "nouns_like_adjectives": "J1:J417",
    "adjective_endings": "AD2:AD90",  # adjSuffixes is AD2:AS90; the declension part builds it whole
}
JUNK_ROW = "junk row: the wordform is not letters (maybe joined by hyphens) or the part of speech is empty"
REPEATED_WORDFORM = "a later row of the same wordform wins, as the add-in's sorted VLOOKUP"
SAME_PAIR = "the same lemma and wordform as an earlier row once the lemma is lower case"
YO_KEY = "a ё→е key for a word with ё"
CORRECTIONS = Path(__file__).with_suffix(".toml")
CORRECTED = "a corrected wordform: its line of morph.toml replaces it"

Row = tuple[str, str, str]  # wordform, lemma, pos


def yo_to_ye(text: str) -> str:
    return text.replace("ё", "е")


def _is_kept(wordform: str, pos: str) -> bool:
    return bool(pos) and WORDFORM.fullmatch(wordform) is not None


def lemma_rows(path: Path) -> list[Row]:
    """(wordform, lemma, pos) in source order: header and junk rows dropped, lower case."""
    rows = (line.split("\t") for line in read_lines(path)[1:])
    return [(wordform.lower(), lemma.lower(), pos) for wordform, lemma, pos in rows if _is_kept(wordform, pos)]


def corrections(path: Path = CORRECTIONS) -> dict[str, tuple[Row, str]]:
    """Each corrected wordform: its row and the reason, from the lines of morph.toml."""
    lines = tomllib.loads(path.read_text(encoding="utf-8"))["corrections"]
    return {
        wordform: ((wordform, line["lemma"], line["pos"]), line["why"])
        for line in lines
        for wordform in line["wordforms"]
    }


def corrected(rows: list[Row]) -> list[Row]:
    """The rows of lemms.tsv without those of a corrected wordform, then a row per corrected wordform."""
    found = corrections()
    return [row for row in rows if row[0] not in found] + [row for row, _ in found.values()]


def lemma_trie(rows: list[Row]) -> marisa_trie.BytesTrie:
    found: dict[str, str] = {}
    for wordform, lemma, pos in rows:  # a repeated wordform: the last row wins, as the add-in's sorted VLOOKUP
        found[wordform] = f"{lemma}\t{pos}"
    for wordform, value in list(found.items()):
        found.setdefault(yo_to_ye(wordform), value)
    return marisa_trie.BytesTrie((key, value.encode()) for key, value in sorted(found.items()))


def forms_trie(rows: list[Row]) -> marisa_trie.BytesTrie:
    pairs = {(key, wordform) for wordform, lemma, _ in rows for key in (lemma, yo_to_ye(lemma))}
    return marisa_trie.BytesTrie((lemma, wordform.encode()) for lemma, wordform in sorted(pairs))


def _lemma_entries(path: Path) -> dict[str, Entry]:
    """lemmas.marisa (wordform → lemma, pos) and forms.marisa (lemma → wordforms) from lemms.tsv."""
    rows = [line.split("\t") for line in read_lines(path)[1:]]
    lemmas = Entry(f"{path.name}: every row", len(rows))
    forms = Entry(f"{path.name}: every row as a lemma and its wordform", len(rows))
    for wordform, lemma, pos in rows:
        if not _is_kept(wordform, pos):
            lemmas.drop(f"{wordform}\t{lemma}\t{pos}", JUNK_ROW)
            forms.drop(f"{wordform}\t{lemma}\t{pos}", JUNK_ROW)
    kept = lemma_rows(path)
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
    _corrections_entries(kept, lemmas, forms)
    return {"lemmas.marisa": lemmas, "forms.marisa": forms}


def _corrections_entries(kept: list[Row], lemmas: Entry, forms: Entry) -> None:
    """The rows and the pairs a correction replaces, as dropped, and those it brings, as added."""
    winner = {wordform: (wordform, lemma, pos) for wordform, lemma, pos in kept}
    pairs = {(wordform, lemma) for wordform, lemma, _ in kept}
    for wordform, (row, why) in sorted(corrections().items()):
        if winner.get(wordform) != row:
            if wordform in winner:
                lemmas.drop("\t".join(winner[wordform]), CORRECTED)
            lemmas.add("\t".join(row), why)
        for _, lemma in sorted(pair for pair in pairs if pair[0] == wordform and pair[1] != row[1]):
            forms.drop(f"{lemma}\t{wordform}", CORRECTED)
        if (wordform, row[1]) not in pairs:
            forms.add(f"{row[1]}\t{wordform}", why)


def manifest(sources: dict[str, Path]) -> dict[str, Entry]:
    sheet = read_sheet(sources["sheet_abc"])
    tables = {f"morph.json:{name}": range_entry(sheet, name, address) for name, address in TABLES.items()}
    return _lemma_entries(sources["lemmas"]) | tables


def build(sources: dict[str, Path], out: Path) -> None:
    rows = corrected(lemma_rows(sources["lemmas"]))
    sheet = read_sheet(sources["sheet_abc"])
    out.mkdir(parents=True, exist_ok=True)
    lemma_trie(rows).save(str(out / "lemmas.marisa"))
    forms_trie(rows).save(str(out / "forms.marisa"))
    write_json(out / "morph.json", {name: sheet_table(sheet, address) for name, address in TABLES.items()})
