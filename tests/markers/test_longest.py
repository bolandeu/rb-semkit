"""The longest match of a word wins, in markers and phrases; a tie keeps the list order (ADR 0005)."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk


def test_questions_extract_the_longest_marker() -> None:
    phrase = pd.Series(["как сделать диван своими руками"])

    assert sk.extract(phrase, sk.markers("questions")).tolist() == ["как сделать"]


def test_phrases_extract_and_remove_the_longest_item() -> None:
    phrase = pd.Series(["купить диван нижний новгород"])
    matcher = sk.phrases(["нижний", "нижний новгород"])

    assert sk.extract(phrase, matcher).tolist() == ["нижний новгород"]
    assert sk.remove(phrase, matcher).tolist() == ["купить диван"]


def test_find_marks_a_phrase_with_a_longer_item() -> None:
    phrase = pd.Series(["как сделать диван", "диван"])

    assert sk.find(phrase, sk.markers("questions")).tolist() == [True, False]


def test_equal_items_from_one_word_keep_the_list_order() -> None:
    phrase = pd.Series(["купить Диван"])
    matcher = sk.markers(user={"first": ["ДИВАН"], "second": ["диван"]})

    assert sk.extract(phrase, matcher).tolist() == ["ДИВАН"]
