"""Keyboard layout switch and similar chars cyr↔lat."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def test_layout_en_to_ru_turns_every_key_of_the_english_layout() -> None:
    result = sk.switch_layout(pd.Series(["ghbdtn vbh", "z", "Ghbdtn, vbh"]), to="ru")

    assert result.tolist() == ["привет мир", "я", "Приветб мир"]


def test_layout_ru_to_en_gives_the_shifted_key_of_an_upper_case_letter() -> None:
    result = sk.switch_layout(pd.Series(["привет", "яндекс", "Бык Ёж"]), to="en")

    assert result.tolist() == ["ghbdtn", "zyltrc", "<sr ~;"]


def test_similar_chars_swap_the_look_alike_letters_only() -> None:
    assert sk.similar_chars(pd.Series(["Москва"]), to="en").tolist() == ["Mockвa"]
    assert sk.similar_chars(pd.Series(["CTO"]), to="ru").tolist() == ["СТО"]


def test_the_russian_layout_text_comes_back_as_it_was_through_the_english_keys() -> None:
    text = pd.Series(["Хрущёвка, «ж»: Б. ю?", 'Э; э/ "щ" №5 (а)'])

    result = sk.switch_layout(sk.switch_layout(text, to="en"), to="ru")

    assert result.tolist() == text.tolist()


def test_the_punctuation_keys_of_the_russian_layout_are_other_signs_of_the_english_one() -> None:
    assert sk.switch_layout(pd.Series(["а. б, в:"]), to="en").tolist() == ["f/ ,? d^"]
