"""Translit of phrases: ЧПУ (a URL slug), ru→en and en→ru by letters, and the phonetic en→ru."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


def _one(function, phrase: str, **kwargs) -> str:
    return function(pd.Series([phrase]), **kwargs).iloc[0]


def test_chpu_is_lower_case_with_one_dash_between_words() -> None:
    assert _one(sk.chpu, "Диван-кровать 2 м!") == "divan-krovat-2-m"
    assert _one(sk.chpu, "Щётка  ёж") == "schetka-ezh"


def test_chpu_drops_dashes_at_the_edges_and_folds_accents() -> None:
    assert _one(sk.chpu, " «Café» — №1 ") == "cafe-1"


def test_translit_to_latin_keeps_an_all_caps_word_in_caps() -> None:
    assert _one(sk.translit, "Щука жёлтая", to="en") == "Schuka zheltaya"
    assert _one(sk.translit, "ЖУК и Жук", to="en") == "ZHUK i Zhuk"


def test_translit_to_cyrillic_goes_by_letter_groups() -> None:
    assert _one(sk.translit, "Yandex Fyva", to="ru") == "Яндекс Фыва"
    assert _one(sk.translit, "ob'em Jeep", to="ru") == "обэм Джееп"


def test_phonetic_reads_english_words_in_russian_and_keeps_their_case() -> None:
    assert _one(sk.phonetic, "Dreamline iphone XIAOMI") == "Дримлайн айфон СЯОМИ"


@pytest.mark.parametrize("word", ["ЖУК", "ЖКХ", "Цой", "Чайка", "щука", "Жук", "диван"])
def test_translit_to_cyrillic_reverses_translit_to_latin(word: str) -> None:
    latin = _one(sk.translit, word, to="en")

    assert _one(sk.translit, latin, to="ru") == word


def test_translit_to_cyrillic_reads_a_word_in_capitals_by_its_letter_groups() -> None:
    assert _one(sk.translit, "ZHUK SHCHUKA", to="ru") == "ЖУК ЩУКА"


def test_translit_to_cyrillic_cannot_restore_the_signs() -> None:
    assert _one(sk.translit, _one(sk.translit, "съёмный", to="en"), to="ru") == "сыемный"


def test_phonetic_reads_a_brand_by_its_word() -> None:
    assert _one(sk.phonetic, "IKEA Ikea") == "ИКЕА Икеа"
