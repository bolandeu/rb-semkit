"""Full names «Фамилия Имя Отчество» declined: the surname and the name by their endings, the patronymic as a noun."""

from __future__ import annotations

import pandas as pd

from ..errors import InvalidArguments
from ..frame import Frame, map_unique
from ..text.base import choice, split_words
from .forms import CASES, HARD_ENDINGS, noun_exception, noun_form

__all__ = ["decline_full_name"]

NAME_CASES = CASES[1:]
Forms = tuple[str, str, str, str, str]  # the genitive, dative, accusative, instrumental and prepositional
# Endings of a surname and their forms; the first ending the surname has wins.
WOMAN_SURNAMES: dict[str, Forms] = {
    "ая": ("ой", "ой", "ую", "ой", "ой"),
    "ина": ("иной", "иной", "ину", "иной", "иной"),
    "ева": ("евой", "евой", "еву", "евой", "евой"),
    "ова": ("овой", "овой", "ову", "овой", "овой"),
}
MAN_SURNAMES: dict[str, Forms] = {
    "ев": ("ева", "еву", "ева", "евым", "еве"),
    "ов": ("ова", "ову", "ова", "овым", "ове"),
    "ый": ("ого", "ому", "ого", "ым", "ом"),
    "ин": ("ина", "ину", "ина", "иным", "ине"),
    "кий": ("кого", "кому", "кого", "ким", "ком"),
    "ой": ("ого", "ому", "ого", "ым", "ом"),
    "а": ("а", "а", "а", "а", "а"),
    "о": ("о", "о", "о", "о", "о"),
}
WOMAN_NAMES: dict[str, Forms] = {"ая": ("аи", "ае", "аю", "аей", "ае")}
MAN_NAMES: dict[str, Forms] = {"ий": ("ия", "ию", "ия", "ием", "ии")}
FIXED_NAMES: dict[str, Forms] = {"любовь": ("любови", "любови", "любовь", "любовью", "любови")}
CONSONANTS = "трнсмдзлбпвфгкхжшчщ"
WOMAN_ENDINGS = ("зы", "на")  # a full name of a woman ends so: «Ивановна», «Мамедовна», «кызы»


def _by_ending(word: str, endings: dict[str, Forms], case: int) -> str | None:
    for ending, forms in endings.items():
        if word.endswith(ending):
            return word[: -len(ending)] + forms[case]
    return None


def _man_name(name: str, case: int) -> str:
    """By «-ий», else by the noun exceptions; a name in a consonant takes the hard ending, any other declines as a noun."""
    found = _by_ending(name, MAN_NAMES, case) or noun_exception(name, case)
    if found is None and name.endswith(tuple(CONSONANTS)):
        found = name + HARD_ENDINGS[case]
    return found or noun_form(name, case)


def _woman_name(name: str, case: int) -> str:
    """A fixed name, by «-ая», as a noun in «-а», «-я»; any other stays."""
    if name in FIXED_NAMES:
        return FIXED_NAMES[name][case]
    found = _by_ending(name, WOMAN_NAMES, case)
    if found is not None:
        return found
    return noun_form(name, case) if name.endswith(("а", "я")) else name


def _declined(full_name: str, case: int) -> str:
    surname, name, patronymic = words = full_name.lower().split()
    if " ".join(words).endswith(WOMAN_ENDINGS):
        surname = _by_ending(surname, WOMAN_SURNAMES, case) or surname
        name = _woman_name(name, case)
    else:
        surname = _by_ending(surname, MAN_SURNAMES, case) or _man_name(surname, case)
        name = _man_name(name, case)
    return f"{surname} {name} {noun_form(patronymic, case)}".title()


def _checked(phrases: pd.Series, argument: str) -> None:
    wrong = [phrase for phrase in phrases.unique() if phrase.strip() and len(split_words(phrase)) != 3]
    if wrong:
        raise InvalidArguments(f"{argument}: {wrong[0]!r} is not three words; allowed: «Фамилия Имя Отчество».")


def decline_full_name(
    data: pd.Series | pd.DataFrame,
    case: str,
    *,
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """A full name «Фамилия Имя Отчество» declined: «Иванов Сергей Петрович» genitive → «Иванова Сергея Петровича».

    case: "genitive", "dative", "accusative", "instrumental" or "prepositional".
    A full name that ends in «-на» or «-зы» is a woman's («Петрова Анна Ивановна» → «Петровой Анны Ивановны»).
    The surname declines by its ending («-ов», «-ин», «-ой», «-ская»…), the name and the patronymic as nouns; the
    result has a capital in each word. An empty cell stays empty; any other value that is not three words raises
    InvalidArguments.
    """
    index = NAME_CASES.index(choice("case", case, NAME_CASES))
    frame = Frame(data, column, inplace)
    phrases = frame.phrases
    _checked(phrases, "data" if column is None else f"column {column!r}")
    declined = map_unique(phrases, lambda phrase: _declined(phrase, index) if phrase.strip() else "")
    return frame.put(declined, "decline_full_name")
