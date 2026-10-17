"""Change functions on words with punctuation, hyphens and sizes glued to them."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def _one(function, phrase: str, *args, **kwargs) -> str:
    return function(pd.Series([phrase]), *args, **kwargs).iloc[0]


def test_toponyms_capitalise_a_hyphenated_name_and_a_name_before_punctuation() -> None:
    assert _one(sk.change_case, "диван ростов-на-дону", "toponyms") == "диван Ростов-на-Дону"
    assert _one(sk.change_case, "купить диван в москве. отзывы!", "toponyms") == "купить диван в Москве. отзывы!"
    assert _one(sk.change_case, "(санкт-петербург), цены", "toponyms") == "(Санкт-Петербург), цены"


def test_replace_words_replaces_a_word_with_punctuation_and_keeps_the_punctuation() -> None:
    pairs = {"машинка": "машина", "дешево": "недорого"}

    assert _one(sk.replace_words, "швейная машинка, дешево", pairs) == "швейная машина, недорого"
    assert _one(sk.replace_words, "(Машинка)!", {"машинка": "машина"}, case="keep") == "(Машина)!"
    assert _one(sk.replace_words, "стиральная машинка.", {"стиральная машинка": "машина"}) == "машина."


def test_split_digits_keeps_a_size_whole() -> None:
    assert _one(sk.split_digits, "диван 140х200 ps5") == "диван 140х200 ps 5"
    assert _one(sk.split_digits, "диван140x200см 1X2X3") == "диван 140x200 см 1X2X3"
