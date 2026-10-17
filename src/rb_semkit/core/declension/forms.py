"""The forms of one word by the bundled declension tables, and the case, number and gender arguments of the area.

A noun has 12 forms: the nominative it is given in, then the genitive, dative, accusative, instrumental and
prepositional singular, then the six cases of the plural; the tables hold the 11 after the first. A noun form is
the form of the word in the exceptions table, else the word with its last three letters replaced by the endings
table; a word that ends in a consonant and has no ending there takes the usual ending of its consonant group (the
accusative excepted: it comes from the table only). An adjective has the 11 forms of its own gender and four more:
the feminine nominative, genitive (also dative, instrumental and prepositional) and accusative and the neuter
nominative (also accusative); the other neuter cases are the masculine ones. Words are looked up in lower case
with ё as е; a form keeps the capitals of its word.
"""

from __future__ import annotations

import re

from .. import datastore
from ..text.base import choice

TABLES = "declension/tables.json"
CASES = ("nominative", "genitive", "dative", "accusative", "instrumental", "prepositional")
NUMBERS = ("singular", "plural")
GENDERS = ("masculine", "feminine", "neuter")
# The usual endings after a hard consonant, after г к х and after ж ш ч щ, by form index.
HARD_ENDINGS = ("а", "у", "а", "ом", "е", "ы", "ов", "ам", "", "ами", "ах")
USUAL_ENDINGS = {
    **dict.fromkeys("трнсмдзлбпвф", HARD_ENDINGS),
    **dict.fromkeys("гкх", ("а", "у", "а", "ом", "е", "и", "ов", "ам", "", "ами", "ах")),
    **dict.fromkeys("жшчщ", ("а", "у", "а", "ем", "е", "и", "ей", "ам", "", "ами", "ах")),
}
ACCUSATIVES = frozenset({2, 8})  # the accusative singular and plural
FEMININE = {"nominative": 11, "accusative": 13}  # the other feminine cases share form 12
FEMININE_OBLIQUE = 12
NEUTER_DIRECT = 14  # the neuter nominative and accusative
_VOWEL = re.compile("[аоуиыеёэюя]")


def form_index(case: str, number: str = "singular") -> int | None:
    """The index of the form among the 11 of the tables; None for the nominative singular, the word itself."""
    index = CASES.index(choice("case", case, CASES)) + 6 * NUMBERS.index(choice("number", number, NUMBERS))
    return index - 1 if index else None


def adjective_index(case: str, gender: str, number: str) -> int | None:
    """The index of the form among the 15 of the adjective tables; None for the masculine nominative singular."""
    index = form_index(case, number)
    if choice("gender", gender, GENDERS) == "masculine" or number == "plural":
        return index
    if gender == "feminine":
        return FEMININE.get(case, FEMININE_OBLIQUE)
    return NEUTER_DIRECT if case in ("nominative", "accusative") else index


def _tables() -> dict:
    return datastore.table(TABLES)


def table_key(word: str) -> str:
    return word.lower().replace("ё", "е")


def is_abbreviation(word: str) -> bool:
    """Under 5 letters with no vowel in lower case: «МТС», «ссср»."""
    return len(word) < 5 and not _VOWEL.search(word)


def bundled_words(name: str) -> frozenset[str]:
    """A word list of the declension data by name ("indeclinable", "governing", "takes_genitive"…), ё as е."""
    return datastore.once(f"{TABLES}:{name}", lambda: frozenset(_tables()[name]))


def is_indeclinable(word: str) -> bool:
    """An abbreviation or a word of the indeclinable table."""
    return is_abbreviation(word) or table_key(word) in bundled_words("indeclinable")


def cased(word: str, form: str) -> str:
    """`form` with the capitals of `word`: all capitals, a first capital only, or none."""
    if word.isupper():
        return form.upper()
    if word[:1].isupper() and (word[1:].islower() or not word[1:]):
        return form.capitalize()
    return form


def noun_exception(word: str, index: int) -> str | None:
    """The form of the word in the noun exceptions table; None when the table lacks the word."""
    row = _tables()["noun_exceptions"].get(table_key(word))
    return None if row is None else row[index]


def _from_tables(word: str, index: int, exceptions: str, endings: str) -> str | None:
    """The form from the exceptions table, else by the endings table; None when neither holds the word."""
    tables = _tables()
    key = table_key(word)
    if key in tables[exceptions]:
        return tables[exceptions][key][index]
    row = tables[endings].get(key[-3:])
    return None if row is None or not row[index] else word.lower()[: -len(key[-3:])] + row[index]


def noun_form(word: str, index: int | None) -> str:
    """The noun form `index` of `word`; the word as it is when it is indeclinable or the tables lack it."""
    if index is None or is_indeclinable(word):
        return word
    form = _from_tables(word, index, "noun_exceptions", "noun_endings")
    usual = USUAL_ENDINGS.get(word[-1:].lower())
    if form is None and usual is not None and index not in ACCUSATIVES:
        form = word.lower() + usual[index]
    return word if form is None else cased(word, form)


def adjective_form(word: str, index: int | None) -> str:
    """The adjective form `index` of `word`; the word as it is when the tables lack its ending."""
    if index is None:
        return word
    form = _from_tables(word, index, "adjective_exceptions", "adjective_endings")
    return word if form is None else cased(word, form)
