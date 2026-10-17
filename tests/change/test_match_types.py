"""Match types of the search engines: operators on the words of a phrase, minus-words kept apart."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk

PHRASE = "купить диван в москве"


def _one(phrase: str, kind: str, **kwargs) -> str:
    return sk.match_type(pd.Series([phrase]), kind, **kwargs).iloc[0]


def test_the_broad_match_modifier_leaves_the_stopwords_plain() -> None:
    assert _one(PHRASE, "broad_modifier") == "+купить +диван в +москве"
    assert _one("Купить В Москве", "broad_modifier") == "+Купить В +Москве"


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("broad", "купить диван в москве -бесплатно"),
        ("plus_every_word", "+купить +диван +в +москве -бесплатно"),
        ("fixed_forms", "!купить !диван !в !москве -бесплатно"),
        ("quoted_fixed_forms", '"!купить !диван !в !москве" -бесплатно'),
        ("quoted_fixed_order", '"[!купить !диван !в !москве]" -бесплатно'),
        ("brackets", "[купить диван в москве] -бесплатно"),
        ("quotes", '"купить диван в москве" -бесплатно'),
        ("antisemantic", "[купить] [диван] в [москве] -бесплатно"),
    ],
)
def test_each_kind_keeps_the_minus_words_out_of_its_operators(kind: str, expected: str) -> None:
    assert _one(f"{PHRASE} -бесплатно", kind) == expected


def test_a_word_with_an_operator_keeps_it_and_an_empty_phrase_stays_empty() -> None:
    assert _one("!купить +в москве", "fixed_forms") == "!купить +в !москве"
    assert _one("", "fixed_forms") == ""


def test_the_stopword_modifier_goes_on_the_stopwords_only() -> None:
    assert _one("диван в москве для дачи", "stopword_modifier", modifier="!") == "диван !в москве !для дачи"


def test_drop_modifiers_takes_them_off_the_stopwords_in_any_case() -> None:
    result = sk.drop_modifiers(pd.Series(["+купить +В !москве +для дачи"]))

    assert result.tolist() == ["+купить В !москве для дачи"]


def test_drop_minus_words_keeps_a_dash_between_words() -> None:
    result = sk.drop_minus_words(pd.Series(["купить диван -бесплатно -скачать", "диван - кровать"]))

    assert result.tolist() == ["купить диван", "диван - кровать"]


@pytest.mark.parametrize(
    ("phrase", "kind", "expected"),
    [
        ('"купить диван" -бесплатно', "plus_every_word", '"+купить +диван" -бесплатно'),
        ('"купить диван" -бесплатно', "fixed_forms", '"!купить !диван" -бесплатно'),
        ('"купить диван" -бесплатно', "quotes", '"купить диван" -бесплатно'),
        ('"купить диван" -бесплатно', "brackets", "[купить диван] -бесплатно"),
        ("[диван в икеа] -бу", "plus_every_word", "[+диван +в +икеа] -бу"),
        ("[диван в икеа] -бу", "fixed_forms", "[!диван !в !икеа] -бу"),
        ("[диван в икеа] -бу", "brackets", "[диван в икеа] -бу"),
        ("[диван в икеа] -бу", "quotes", '"диван в икеа" -бу'),
        ('"[!диван !в]" -бу', "quoted_fixed_order", '"[!диван !в]" -бу'),
        ("[диван в икеа] -бу", "antisemantic", "[диван] в [икеа] -бу"),
    ],
)
def test_a_phrase_with_quotes_or_brackets_is_not_wrapped_again(phrase: str, kind: str, expected: str) -> None:
    assert _one(phrase, kind) == expected
