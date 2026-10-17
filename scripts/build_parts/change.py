"""The data of the change area: the character tables and the word order lists.

    translit.json   translit_ru_en, translit_en_ru, chpu, layout, similar_chars, phonetic_<kind>_<n> (each a list
                    of [from, to] pairs in the order they apply)
    word_order.json prepositions, and phrase_start_words declined: feminine, feminine_accusative, plural

Sources: `sheet_abc` (sheet `abc` of the add-in as TSV: chpuSym, charsPat and the adjective tables) and `vba`
(RibbonCallbacks.vba, whose string literals hold the other tables).
"""

from __future__ import annotations

import re
from pathlib import Path

from build_parts import (
    REPEATED_KEY,
    Entry,
    SourceMissing,
    cell_range,
    range_entry,
    read_lines,
    read_sheet,
    sheet_table,
    write_json,
)

CHPU = "E10000:F10965"
PHRASE_START_WORDS = "BA1:BA644"
ADJECTIVE_ENDINGS = "AD2:AS90"
ADJECTIVE_EXCLUSIONS = "AD93:AS136"
# The column of each declined form in the adjective tables (1 is the ending itself).
DECLINED_FORMS = {"feminine": 13, "feminine_accusative": 15, "plural": 7}
DIGITS = "0123456789"
DIGITS_ADDED = "the add-in adds the digits to the table in code"
TWO_CHAR_KEY = "a key of two chars: the add-in maps one char at a time, so it never matches"
LAYOUT_KEYS = 33
LAYOUT_FIX = ("·", "z")
LAYOUT_BROKEN = "broken literal: the key of «я» is «·», not «z», so «z» never becomes «я»"
LAYOUT_FIXED = "the key of «я» fixed to «z»"
# The shifted keys of the letters of the Russian layout that sit on punctuation keys of the English one.
SHIFTED_KEYS = (("<", "Б"), (">", "Ю"), (":", "Ж"), ('"', "Э"), ("{", "Х"), ("}", "Ъ"), ("~", "Ё"))
SHIFTED_ADDED = "a shifted key: the add-in maps only the unshifted punctuation keys"
# The letter groups of the latin translit that the add-in lacks, so that «ZHUK», «Tsoy», «shchuka» read back.
TRANSLIT_ADDED = (("Shch", "Щ"), ("shch", "щ"), ("Ts", "Ц"), ("ts", "ц"), ("yy", "ый"))
TRANSLIT_ADDED_WHY = "a letter group of the latin translit that reads back to its cyrillic letters"
# The signs of the Russian layout, by the key of the English layout that types them.
SIGN_KEYS = (("/", "."), ("?", ","), ("^", ":"), ("$", ";"), ("&", "?"), ("@", '"'), ("#", "№"), ("|", "/"))
SIGN_KEYS_ADDED = "a sign of the Russian layout: the add-in maps only the letter keys and the unshifted sign keys"
PHONETIC_WORDS_ADDED = {"f": {"ikea": "икеа"}}
PHONETIC_WORDS_ADDED_WHY = "a brand that the letter groups read wrong («ikea» as «ики»)"
LATIN_C = "a latin «c» in a Russian value: the next table turns it into «к»"
LATIN_C_FIXED = "the latin «c» of the value fixed to «с»"
PHONETIC_TABLES = {
    "words": ("f",),
    "suffixes": ("s5", "s4", "s3", "s2"),
    "prefixes": ("p5", "p4", "p3", "p2"),
    "any": ("a5", "a4", "a3", "a2", "a1"),
}
# String literals of RibbonCallbacks.vba, by table: the pattern captures the «from» and the «to» parts.
VBA_TABLES = {
    "translit_ru_en": r'Function ooa—\$.*?cyr = "([^"]*)": lat = Array\(([^)]*)\)',
    "translit_en_ru": r'Function o·a—\$.*?lat = Split\("([^"]*)"\): cyr = Split\("([^"]*)"\)',
    "layout": r'Function okok\$.*?arr1 = "([^"]*)": arr2 = "([^"]*)"',
    "similar_chars": r"Function ok·a\$.*?lat = Array\(([^)]*)\): cyr = Array\(([^)]*)\)",
}
INIT_DICTS = r"Sub InitDicts\(\)(.*?)End Sub"
WORD_ORDER_PREPOSITIONS = r'Function BKP\$.*?p = "([^"]*)"'


def _match(source: str, pattern: str, name: str) -> re.Match[str]:
    match = re.search(pattern, source, re.DOTALL)
    if match is None:
        raise SourceMissing(f"the VBA table {name!r} was not found: the VBA source changed")
    return match


def _items(literal: str) -> list[str]:
    """The items of an `Array("a", "b")` body, or the chars of a plain string."""
    quoted = re.findall(r'"([^"]*)"', literal)
    return quoted if quoted else list(literal)


def _vba_pairs(source: str, name: str) -> list[list[str]]:
    """The [from, to] pairs of a VBA table, as the add-in reads them."""
    match = _match(source, VBA_TABLES[name], name)
    if name == "translit_en_ru":
        sources, targets = match[1].split(" "), match[2].split(" ")
    else:
        sources, targets = _items(match[1]), _items(match[2])
    if name == "layout":
        sources = sources[:LAYOUT_KEYS]
    return [list(pair) for pair in zip(sources, targets, strict=True)]


def _phonetic_literals(source: str) -> dict[str, tuple[list[str], list[str]]]:
    """Each table of the phonetic literals («s5»: the En words and the Ru words), split on single spaces."""
    body = _match(source, INIT_DICTS, "phonetic")[1]
    literals = dict(re.findall(r'(\w+) = "([^"]*)"', body))
    keys = [key for keys in PHONETIC_TABLES.values() for key in keys]
    return {
        key: (literals[f"{key[0]}En{key[1:]}"].split(" "), literals[f"{key[0]}Ru{key[1:]}"].split(" ")) for key in keys
    }


def _phonetic_name(key: str) -> str:
    kind = next(kind for kind, keys in PHONETIC_TABLES.items() if key in keys)
    return f"phonetic_{kind}" if kind == "words" else f"phonetic_{kind}_{key[1:]}"


def _phonetic_pairs(key: str, english: list[str], russian: list[str]) -> list[list[str]]:
    """A key keeps its first place and its last value, as a dictionary filled in order; a latin «c» is fixed; the
    added words follow."""
    values: dict[str, str] = {}
    for word, value in zip(english, russian, strict=True):
        values[word] = value.replace("c", "с")
    values |= PHONETIC_WORDS_ADDED.get(key, {})
    return [[word, value] for word, value in values.items()]


def _phonetic_entry(path: Path, key: str, english: list[str], russian: list[str]) -> Entry:
    entry = Entry(f"{path.name} InitDicts: the literals {key[0]}En{key[1:]} / {key[0]}Ru{key[1:]}", len(english))
    last = {word: index for index, word in enumerate(english)}
    for index, (word, value) in enumerate(zip(english, russian, strict=True)):
        if last[word] != index:
            entry.drop(f"{word}\t{value}", REPEATED_KEY)
        elif "c" in value:
            entry.drop(f"{word}\t{value}", LATIN_C)
            entry.add(f"{word}\t{value.replace('c', 'с')}", LATIN_C_FIXED)
    for word, value in PHONETIC_WORDS_ADDED.get(key, {}).items():
        entry.add(f"{word}\t{value}", PHONETIC_WORDS_ADDED_WHY)
    return entry


def _chpu(sheet: list[list[str]]) -> list[list[str]]:
    rows = cell_range(sheet, CHPU)
    return [[key, value] for key, value in rows if len(key) == 1] + [[digit, digit] for digit in DIGITS]


def _chpu_entry(sheet: list[list[str]]) -> Entry:
    rows = cell_range(sheet, CHPU)
    entry = Entry(f"sheet abc {CHPU} (chpuSym)", len(rows))
    for key, value in rows:
        if len(key) != 1:
            entry.drop(f"{key}\t{value}", TWO_CHAR_KEY)
    for digit in DIGITS:
        entry.add(f"{digit}\t{digit}", DIGITS_ADDED)
    return entry


def _layout(source: str) -> list[list[str]]:
    pairs = [[LAYOUT_FIX[1] if key == LAYOUT_FIX[0] else key, value] for key, value in _vba_pairs(source, "layout")]
    return pairs + [list(pair) for pair in (*SHIFTED_KEYS, *SIGN_KEYS)]


def _layout_entry(source: str, path: Path) -> Entry:
    pairs = _vba_pairs(source, "layout")
    entry = _vba_entry(source, path, "layout", len(pairs))
    for key, value in pairs:
        if key == LAYOUT_FIX[0]:
            entry.drop(f"{key}\t{value}", LAYOUT_BROKEN)
            entry.add(f"{LAYOUT_FIX[1]}\t{value}", LAYOUT_FIXED)
    for key, value in SHIFTED_KEYS:
        entry.add(f"{key}\t{value}", SHIFTED_ADDED)
    for key, value in SIGN_KEYS:
        entry.add(f"{key}\t{value}", SIGN_KEYS_ADDED)
    return entry


def _vba_entry(source: str, path: Path, name: str, items: int) -> Entry:
    match = _match(source, VBA_TABLES[name], name)
    line = source.count("\n", 0, match.start()) + 1
    return Entry(f"{path.name} L{line}: the literals of {name}", items)


def _prepositions(source: str) -> list[str]:
    return _match(source, WORD_ORDER_PREPOSITIONS, "prepositions")[1].split()


def _declined(word: str, column: int, endings: dict[str, list[str]], exclusions: dict[str, list[str]]) -> str:
    """The form of an adjective by the adjective tables; a word they do not know stays as it is."""
    if word.lower() in exclusions:
        return exclusions[word.lower()][column - 1]
    ending = word[-3:].lower()
    return word[: len(word) - len(word[-3:])] + (endings[ending][column - 1] if ending in endings else word[-3:])


def _declined_lists(sheet: list[list[str]]) -> dict[str, list[str]]:
    endings = {row[0]: row for row in cell_range(sheet, ADJECTIVE_ENDINGS)}
    exclusions = {row[0]: row for row in cell_range(sheet, ADJECTIVE_EXCLUSIONS)}
    words = sheet_table(sheet, PHRASE_START_WORDS)
    return {
        f"phrase_start_words_{form}": [
            " ".join(_declined(word, column, endings, exclusions) for word in item.split()) for item in words
        ]
        for form, column in DECLINED_FORMS.items()
    }


def manifest(sources: dict[str, Path]) -> dict[str, Entry]:
    sheet = read_sheet(sources["sheet_abc"])
    vba_path = sources["vba"]
    vba = "\n".join(read_lines(vba_path))
    entries = {
        f"translit.json:{name}": _vba_entry(vba, vba_path, name, len(_vba_pairs(vba, name)))
        for name in ("translit_ru_en", "translit_en_ru", "similar_chars")
    }
    for source, target in TRANSLIT_ADDED:
        entries["translit.json:translit_en_ru"].add(f"{source}\t{target}", TRANSLIT_ADDED_WHY)
    entries["translit.json:layout"] = _layout_entry(vba, vba_path)
    entries["translit.json:chpu"] = _chpu_entry(sheet)
    for key, (english, russian) in _phonetic_literals(vba).items():
        entries[f"translit.json:{_phonetic_name(key)}"] = _phonetic_entry(vba_path, key, english, russian)
    match = _match(vba, WORD_ORDER_PREPOSITIONS, "prepositions")
    line = vba.count("\n", 0, match.start()) + 1
    entries["word_order.json:prepositions"] = Entry(
        f"{vba_path.name} L{line}: the literal p of BKP", len(_prepositions(vba))
    )
    for form in DECLINED_FORMS:
        entry = range_entry(sheet, "charsPat", PHRASE_START_WORDS)
        entry.source += f", declined by {ADJECTIVE_ENDINGS} (adjSuffixes) and {ADJECTIVE_EXCLUSIONS} (adjExclusions)"
        entries[f"word_order.json:phrase_start_words_{form}"] = entry
    return entries


def build(sources: dict[str, Path], out: Path) -> None:
    sheet = read_sheet(sources["sheet_abc"])
    vba = "\n".join(read_lines(sources["vba"]))
    translit = {name: _vba_pairs(vba, name) for name in ("translit_ru_en", "translit_en_ru", "similar_chars")}
    translit["translit_en_ru"] = [list(pair) for pair in TRANSLIT_ADDED] + translit["translit_en_ru"]
    translit |= {"layout": _layout(vba), "chpu": _chpu(sheet)}
    translit |= {_phonetic_name(key): _phonetic_pairs(key, *pair) for key, pair in _phonetic_literals(vba).items()}
    write_json(out / "translit.json", translit)
    write_json(out / "word_order.json", {"prepositions": _prepositions(vba), **_declined_lists(sheet)})
