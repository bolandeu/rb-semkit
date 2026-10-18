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


def test_the_accusative_of_an_inanimate_noun_is_its_nominative_and_the_adjective_agrees() -> None:
    assert _declined(["купить кожаный диван", "угловой диван", "купить кота"], "accusative") == [
        "купить кожаный диван",
        "угловой диван",
        "купить кота",
    ]


def test_a_plural_phrase_declines_in_the_plural() -> None:
    assert _declined(["угловые диваны", "дизайнерские диваны"], "instrumental") == [
        "угловыми диванами",
        "дизайнерскими диванами",
    ]


def test_a_compound_a_feminine_adjective_and_an_adjective_in_ne() -> None:
    phrases = ["диван-кровать угловой", "большая скидка", "нераскладной диван"]

    assert _declined(phrases, "genitive") == ["дивана-кровати углового", "большой скидки", "нераскладного дивана"]
    assert _declined(phrases, "prepositional") == ["диване-кровати угловом", "большой скидке", "нераскладном диване"]


def test_a_noun_in_the_genitive_after_the_head_noun_stays() -> None:
    assert _declined(
        [
            "импорт продукции",
            "ввоз на территорию российской федерации",
            "импорт товаров",
            "таможенное оформление товаров",
        ],
        "genitive",
    ) == [
        "импорта продукции",
        "ввоза на территорию российской федерации",
        "импорта товаров",
        "таможенного оформления товаров",
    ]


def test_a_noun_in_the_nominative_plural_after_an_adjective_still_declines() -> None:
    assert _declined(["красные платья"], "genitive") == ["красных платьев"]
