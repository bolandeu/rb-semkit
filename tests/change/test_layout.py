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
