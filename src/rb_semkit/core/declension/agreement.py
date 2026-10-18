"""Agreement: the words of a phrase put in agreement by rules on neighbouring words, with no syntax parser.

A phrase is read as units: a verb, a preposition, or a noun group (its adjectives, then its noun). The unit before a
noun group gives its case: none (the first group) the nominative, a verb the accusative, a noun group the genitive, a
preposition the case of PREPOSITION_CASES. The adjectives of a group take the gender, the number and the case of its
noun. A noun that is in that case already stays; one in the nominative declines; any other keeps the phrase. Each
phrase is kept as it is, with a note, when a word has no rule or a rule is unsure.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from pymorphy3.analyzer import Parse

from ..frame import Frame, map_unique, put_columns
from ..markers.matcher import markers
from ..morph.functions import BUNDLED
from ..morph.lemmatizer import NOUN, noun_parses
from ..text.base import split_words
from .forms import (
    CASES,
    PYMORPHY_CASES,
    Case,
    adjective_case,
    adjective_form,
    adjective_index,
    cased,
    form_index,
    has_adjective_forms,
    is_abbreviation,
    is_indeclinable,
    noun_form,
)

__all__ = ["agree"]

AGREED, NOTE = "agreed", "agree_note"
VERB, PREPOSITION, ADJECTIVE = "v", "prep", "a"
# The role of a word in a unit by its part of speech: a participle is an adjective.
ROLES = {VERB: VERB, PREPOSITION: PREPOSITION, NOUN: NOUN, ADJECTIVE: ADJECTIVE, "p": ADJECTIVE}
# The cases a preposition takes; of two, the second is for a place («в москве»), the first for any other noun.
PREPOSITION_CASES: dict[str, tuple[Case, ...]] = {
    **dict.fromkeys(("из", "для", "без", "до", "от", "у"), ("genitive",)),
    "к": ("dative",),
    "с": ("instrumental",),
    **dict.fromkeys(("в", "на"), ("accusative", "prepositional")),
}
GENDERS = {"masc": "masculine", "femn": "feminine", "neut": "neuter"}
NUMBERS = {"sing": "singular", "plur": "plural"}


class _Kept(Exception):
    """The phrase stays as it is; the message is the note."""


@dataclass(frozen=True)
class _Unit:
    """A verb, a preposition or a noun group (NOUN): its words, the adjectives of a group before its noun."""

    role: str
    words: tuple[str, ...]


@dataclass(frozen=True)
class _Noun:
    """The noun of a group as it agrees: its form, and the case, number, gender and animacy its adjectives take."""

    form: str
    case: Case
    number: str
    gender: str | None
    animate: bool


def _role(word: str) -> str:
    """The role by the part of speech; an abbreviation is a noun («BMW»), any other word keeps the phrase."""
    role = ROLES.get(BUNDLED.pos(word.lower())) or (NOUN if is_abbreviation(word) else None)
    if role is None:
        raise _Kept(f"no rule for «{word}»")
    return role


def _units(words: list[str]) -> list[_Unit]:
    """The units of the words; an adjective with no noun after it keeps the phrase."""
    units: list[_Unit] = []
    adjectives: list[str] = []
    for word in words:
        role = _role(word)
        if adjectives and role not in (ADJECTIVE, NOUN):
            break
        if role == ADJECTIVE:
            adjectives.append(word)
            continue
        units.append(_Unit(role, (*adjectives, word)))
        adjectives = []
    if adjectives:
        raise _Kept(f"«{adjectives[-1]}» has no noun after it")
    return units


def _cases(before: _Unit | None, unit: _Unit) -> tuple[Case, ...]:
    """The cases the unit before a noun group gives it; a unit after a preposition that is no group keeps the phrase."""
    if before is not None and before.role == PREPOSITION and unit.role != NOUN:
        raise _Kept(f"«{before.words[0]}» has no noun after it")
    if unit.role == VERB and before is not None:
        raise _Kept(f"no rule for «{before.words[-1]} {unit.words[0]}»")
    if before is None:
        return ("nominative",)
    if before.role == PREPOSITION:
        cases = PREPOSITION_CASES.get(before.words[0].lower())
        if cases is None:
            raise _Kept(f"no case for the preposition «{before.words[0]}»")
        return cases
    return ("accusative",) if before.role == VERB else ("genitive",)


def _case_of(parse: Parse) -> Case | None:
    found = parse.tag.case
    return CASES[PYMORPHY_CASES.index(found)] if found in PYMORPHY_CASES else None


def _noun(parse: Parse, form: str, case: Case) -> _Noun:
    tag = parse.tag
    return _Noun(form, case, NUMBERS.get(tag.number, "singular"), GENDERS.get(tag.gender), tag.animacy == "anim")


def _declined_case(cases: tuple[Case, ...], group: _Unit, before: _Unit | None) -> Case:
    """The case a noun in the nominative declines to; of two, the place one for a toponym, else unsure."""
    if len(cases) == 1:
        return cases[0]
    if markers("geo").find(pd.Series([" ".join(group.words)]))[0]:
        return cases[-1]
    preposition = "" if before is None else before.words[0]
    raise _Kept(f"the case after «{preposition}» is unsure: «{group.words[-1]}» is no toponym")


def _in_cases(parses: list[Parse]) -> list[tuple[Parse, Case]]:
    """The parses with the lemma of the likeliest one («машина» is no genitive of «Машин»), each with its case."""
    found = [(parse, _case_of(parse)) for parse in parses if parse.normal_form == parses[0].normal_form]
    return [(parse, case) for parse, case in found if case is not None]


def _declined(word: str, nominative: Parse, case: Case) -> _Noun:
    """The noun in the nominative declined to the case, in its own number."""
    noun = _noun(nominative, word, case)
    base = word if noun.number == "singular" else nominative.normal_form
    return _noun(nominative, cased(word, noun_form(base, form_index(case, noun.number))), case)


def _agreed_noun(group: _Unit, cases: tuple[Case, ...], before: _Unit | None) -> _Noun:
    """The noun of the group: as it is when indeclinable or in one of `cases`, else declined from the nominative."""
    word = group.words[-1]
    parses = noun_parses(word.lower())
    if not parses:
        return _Noun(word, cases[0], "singular", None, animate=False)
    if is_indeclinable(word) or "Fixd" in parses[0].tag:
        return _noun(parses[0], word, cases[0])
    in_cases = _in_cases(parses)
    found = next(((parse, case) for parse, case in in_cases if case in cases), None)
    if found is not None:
        return _noun(found[0], word, found[1])
    nominative = next((parse for parse, case in in_cases if case == "nominative"), None)
    if nominative is None:
        raise _Kept(f"«{word}» is in another case")
    return _declined(word, nominative, _declined_case(cases, group, before))


def _agreed_adjective(word: str, noun: _Noun) -> str:
    lemma = BUNDLED.lemma(word.lower())
    if not has_adjective_forms(lemma):
        raise _Kept(f"the tables lack the adjective «{word}»")
    if noun.gender is None and noun.number == "singular":
        raise _Kept(f"the gender of «{noun.form}» is unknown")
    gender = noun.gender or "masculine"
    case = adjective_case(noun.case, gender, noun.number, animate=noun.animate)
    return cased(word, adjective_form(lemma, adjective_index(case, gender, noun.number)))


def _agreed_words(words: list[str]) -> list[str]:
    found: list[str] = []
    before = None
    for unit in _units(words):
        cases = _cases(before, unit)
        if unit.role == NOUN:
            noun = _agreed_noun(unit, cases, before)
            found += [*(_agreed_adjective(word, noun) for word in unit.words[:-1]), noun.form]
        else:
            found += unit.words
        before = unit
    if before is not None and before.role == PREPOSITION:
        raise _Kept(f"«{before.words[0]}» has no noun after it")
    return found


def _agreement(phrase: str) -> tuple[str, str]:
    """The phrase with its words in agreement and an empty note; else the phrase as it is and the reason."""
    try:
        return " ".join(_agreed_words(split_words(phrase))) if phrase.strip() else phrase, ""
    except _Kept as kept:
        return phrase, str(kept)


def agree(data: pd.Series | pd.DataFrame, *, column: str | None = None) -> pd.DataFrame:
    """The words of each phrase put in agreement.

    The phrase «растаможить машина» becomes «растаможить машину».

    The rules go by neighbouring words, with no syntax parser:
    - a verb, then a noun group: the group in the accusative, by animacy as decline does («купить рыжий кот» →
      «купить рыжего кота»);
    - a noun, then a noun group with no preposition: the group in the genitive («растаможка автомобиль» →
      «растаможка автомобиля», «таможенное оформление автомобиль» → «таможенное оформление автомобиля»);
    - an adjective, then a noun: the adjective in the gender, number and case of the noun («легковой машина» →
      «легковая машина»);
    - a preposition, then a noun group: из, для, без, до, от, у the genitive («растаможка авто из германия» →
      «растаможка авто из германии»); к the dative; с the instrumental; в, на the prepositional for a toponym
      («в москве»), and a word in the accusative or the prepositional already stays («в кредит»);
    - an indeclinable word («авто», «такси») stays.

    A phrase whose words agree already stays («купить диван»). A phrase stays as it is when a word has no rule
    («быстро», «машина купить», «по» and other prepositions), an adjective has no noun after it, a noun is in another
    case («купить машиной»), or в, на stand before a noun that is no toponym («в аптека»).

    The result is a table, a row per phrase: agreed, the phrase with its words in agreement, and agree_note, the
    reason a phrase stays as it is (empty when it agrees); the two columns go right after the column of the phrases.
    A core from word variants: linear-combinations, then agree, then a step by meaning (`semkit read variants.csv
    linear-combinations agree nearest --against page_texts.csv`).

    Example: {cli} read --text "купить рыжий кот" --text "машина купить" agree write -
    -> купить рыжего кота, ; машина купить, no rule for «машина купить»
    """
    frame = Frame(data, column)
    found = map_unique(frame.phrases, _agreement)
    table = pd.DataFrame(found.tolist(), index=found.index, columns=[AGREED, NOTE], dtype=object)
    return put_columns(data, table, column)
