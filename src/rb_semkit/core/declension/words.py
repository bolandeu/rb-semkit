"""Nouns and adjectives declined word by word: each word of a phrase is taken as a noun, or as an adjective."""

from __future__ import annotations

import pandas as pd

from ..morph.functions import word_by_word
from .forms import adjective_form, adjective_index, form_index, noun_form

__all__ = ["decline_adjective", "decline_noun"]


def decline_noun(
    data: pd.Series | pd.DataFrame,
    case: str,
    *,
    number: str = "singular",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each word of a phrase, a noun in the nominative singular, declined: «диван» genitive → «дивана».

    case: "nominative", "genitive", "dative", "accusative", "instrumental" or "prepositional".
    number: "singular" or "plural" (12 forms in all; the nominative singular is the word itself).
    Every word is taken as a noun; for a phrase of mixed words use `decline`. A word with a capital keeps it
    («Москва» → «Москвы»); an indeclinable word («кафе»), an abbreviation («МТС») and a word the tables lack stay.
    The accusative comes from the tables only, by the word or its last three letters: «парк» → «парк», but
    «диван» → «дивана» (as «Иван»).
    """
    index = form_index(case, number)
    return word_by_word(data, lambda word: noun_form(word, index), "decline_noun", column, inplace)


def decline_adjective(
    data: pd.Series | pd.DataFrame,
    case: str,
    *,
    gender: str = "masculine",
    number: str = "singular",
    column: str | None = None,
    inplace: bool = False,
) -> pd.Series | pd.DataFrame:
    """Each word of a phrase, an adjective in the masculine nominative singular, declined: «красный» → «красного».

    case: "nominative", "genitive", "dative", "accusative", "instrumental" or "prepositional".
    gender: "masculine", "feminine" or "neuter", for the singular. number: "singular" or "plural".
    16 forms in all: «красный», «красного», «красному», «красный», «красным», «красном»; «красная», «красной»,
    «красную»; «красное»; «красные», «красных», «красным», «красные», «красными», «красных». The masculine
    accusative is the inanimate one. A word with a capital keeps it; a word whose ending the tables lack stays.
    """
    index = adjective_index(case, gender, number)
    return word_by_word(data, lambda word: adjective_form(word, index), "decline_adjective", column, inplace)
