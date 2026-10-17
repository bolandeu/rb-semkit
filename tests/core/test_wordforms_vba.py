"""sk.wordforms as «Генерация всех словоформ» (––aa L380) with ADR 0005."""

from __future__ import annotations

import rb_semkit as sk


def test_forms_come_in_alphabetical_order_each_once() -> None:
    forms = sk.wordforms("диван")

    assert forms == sorted(set(forms))
    assert "диваны" in forms


def test_a_word_that_is_no_lemma_gives_the_other_forms_of_its_lemma() -> None:
    forms = sk.wordforms("диваны")

    assert "диван" in forms
    assert "диваны" not in forms
    assert sk.wordforms("Москва") == sk.wordforms("москва")


def test_the_input_word_is_not_among_its_forms() -> None:
    assert "диван" not in sk.wordforms("диван")
    assert "елка" not in sk.wordforms("ёлка")


def test_an_unknown_word_or_a_phrase_gives_no_forms() -> None:
    assert sk.wordforms("xyz") == []
    assert sk.wordforms("тиктокер") == []
    assert sk.wordforms("купить диван") == []
