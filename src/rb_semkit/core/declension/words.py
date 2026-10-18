"""Nouns and adjectives declined word by word: each word of a phrase is taken as a noun, or as an adjective."""

from __future__ import annotations

import pandas as pd

from ..morph.functions import word_by_word
from .forms import Case, Gender, Number, adjective_form, adjective_index, form_index, noun_form

__all__ = ["decline_adjective", "decline_noun"]


def decline_noun(
    data: pd.Series | pd.DataFrame,
    case: Case,
    *,
    number: Number = "singular",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each word of a phrase, taken as a noun in the nominative singular, put in the given case.

    The word «диван» in the genitive is «дивана».

    case: "nominative", "genitive", "dative", "accusative", "instrumental" or "prepositional".
    number: "singular" or "plural" (12 forms in all; the nominative singular is the word itself).

    Every word is taken as a noun; for a phrase of mixed words use decline. A word with a capital keeps it
    («Москва» → «Москвы»); an indeclinable word («кафе»), an abbreviation («МТС») and a word the tables lack stay.
    The accusative goes by animacy: an inanimate noun takes its nominative («диван» → «диван»), an animate one its
    genitive («кот» → «кота»), a singular in «-а» or «-я» the form of the tables («книга» → «книгу»). A hyphenated noun
    declines whole («диван-кровать» instrumental → «диваном-кроватью»).

    Example: {cli} read --text "диван" --text "кот" decline-noun genitive write -
    -> дивана; кота
    """
    index = form_index(case, number)
    return word_by_word(data, lambda word: noun_form(word, index), "decline_noun", column, inplace)


def decline_adjective(
    data: pd.Series | pd.DataFrame,
    case: Case,
    *,
    gender: Gender = "masculine",
    number: Number = "singular",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each word of a phrase, taken as an adjective in the masculine nominative singular, put in the given case.

    The word «красный» in the genitive is «красного».

    case: "nominative", "genitive", "dative", "accusative", "instrumental" or "prepositional".
    gender: "masculine", "feminine" or "neuter", for the singular.
    number: "singular" or "plural".

    16 forms in all: «красный», «красного», «красному», «красный», «красным», «красном»; «красная», «красной»,
    «красную»; «красное»; «красные», «красных», «красным», «красные», «красными», «красных». The masculine
    accusative is the inanimate one. A word with a capital keeps it; a word whose ending the tables lack stays.

    Example: {cli} read --text "красный" --text "новый" decline-adjective genitive write -
    -> красного; нового
    Example: {cli} read --text "красный" decline-adjective dative --number plural write -
    -> красным
    """
    index = adjective_index(case, gender, number)
    return word_by_word(data, lambda word: adjective_form(word, index), "decline_adjective", column, inplace)
