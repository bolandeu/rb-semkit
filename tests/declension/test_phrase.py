"""Everything that declines in a phrase: nouns and adjectives change, other words stay."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def _declined(phrases: list[str], case: str, number: str = "singular") -> list[str]:
    return sk.decline(pd.Series(phrases), case, number=number).tolist()


def test_the_verb_stays_and_the_adjective_and_the_noun_go_to_the_genitive() -> None:
    assert _declined(["купить красный диван"], "genitive") == ["купить красного дивана"]


def test_the_plural_and_the_case_of_each_word() -> None:
    assert _declined(["купить красный диван"], "genitive", "plural") == ["купить красных диванов"]
    assert _declined(["Москва"], "dative") == ["Москве"]


def test_a_word_after_a_preposition_and_a_word_already_declined_stay() -> None:
    assert _declined(["чехол для телефон", "диван на дачу", "быстро"], "genitive") == [
        "чехла для телефон",
        "дивана на дачу",
        "быстро",
    ]


def test_a_pronoun_declines_by_the_adjective_tables_only() -> None:
    assert _declined(["этот диван", "он и диван"], "genitive") == ["этого дивана", "он и дивана"]


def test_a_possessive_pronoun_as_the_first_word_does_not_govern() -> None:
    assert _declined(["мой синий стол"], "instrumental") == ["моим синим столом"]
