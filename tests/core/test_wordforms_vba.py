"""sk.wordforms as «Генерация всех словоформ» (––aa L380) with ADR 0005."""

from __future__ import annotations

import rb_semkit as sk


def test_forms_come_in_alphabetical_order_each_once() -> None:
    forms = sk.wordforms("диван")

    assert forms == sorted(set(forms))
    assert "диваны" in forms


def test_a_word_that_is_no_lemma_gives_the_forms_of_its_lemma() -> None:
    assert sk.wordforms("диваны") == sk.wordforms("диван")
    assert sk.wordforms("Москва") == sk.wordforms("москва")


def test_the_input_word_is_not_added_to_the_forms() -> None:
    assert sk.wordforms("xyz") == []
