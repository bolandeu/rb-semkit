"""Ready patterns, the words at the end of a phrase and the prepositional complements, through the three verbs."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments

LETTER = pd.Series(["пишите на info@site.ru до 01022024"])


def test_the_email_and_the_date_are_extracted() -> None:
    assert sk.extract(LETTER, sk.ready_pattern("email")).tolist() == ["info@site.ru"]
    assert sk.extract(LETTER, sk.ready_pattern("date_ddmmyyyy")).tolist() == ["01022024"]


def test_the_ready_patterns_find_remove_and_extract() -> None:
    phrases = pd.Series(["сайт www.example.com и mail.ru", "звоните 8 (999) 123-45-67 или +7 999 111 22 33", "диван"])

    assert sk.find(phrases, sk.ready_pattern("domain")).tolist() == [True, False, False]
    assert sk.extract(phrases, sk.ready_pattern("domain")).tolist() == ["www.example.com mail.ru", "", ""]
    assert sk.extract(phrases, sk.ready_pattern("phone")).tolist()[1] == "8 (999) 123-45-67, +7 999 111 22 33"
    assert sk.remove(phrases, sk.ready_pattern("phone")).tolist()[1] == "звоните или"


def test_the_dates_with_and_without_separators_and_not_inside_a_number() -> None:
    phrases = pd.Series(["заказ от 05.11.2023", "2023-11-05 заказ", "артикул 1201022024", "20231105"])

    assert sk.extract(phrases, sk.ready_pattern("date_ddmmyyyy")).tolist() == ["05.11.2023", "", "", ""]
    assert sk.extract(phrases, sk.ready_pattern("date_yyyymmdd")).tolist() == ["", "2023-11-05", "", "20231105"]


def test_an_unknown_pattern_names_the_argument() -> None:
    with pytest.raises(InvalidArguments, match=r"^kind='url'; allowed: 'domain', "):
        sk.ready_pattern("url")


def test_the_phrase_end_prepositions_go_until_the_last_word_is_clean() -> None:
    phrases = pd.Series(["диван в и", "диван для", "диван по", "в", "диван с подъемным механизмом для"])

    assert sk.remove(phrases, sk.phrase_end("prepositions")).tolist() == [
        "диван",
        "диван",
        "диван",
        "",
        "диван с подъемным механизмом",
    ]


def test_the_buy_markers_at_the_phrase_end_go() -> None:
    phrases = pd.Series(["диван угловой купить", "купить диван", "диван купить недорого"])

    assert sk.remove(phrases, sk.phrase_end("buy_markers")).tolist() == ["диван угловой", "купить диван", "диван"]


def test_the_complements_are_extracted() -> None:
    phrases = pd.Series(["диван для детей с доставкой", "купить диван в москве недорого", "диван В Москве", "диван"])

    assert sk.extract(phrases, sk.complements()).tolist() == ["для детей, с доставкой", "в москве", "В Москве", ""]
