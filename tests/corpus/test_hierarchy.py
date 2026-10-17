"""sk.nearest_parents, sk.first_parents, sk.first_children and sk.basis_phrases through the public library seam."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


def test_the_nearest_parent_is_the_one_with_most_words_and_a_phrase_is_not_its_own_parent() -> None:
    children = pd.Series(["купить стол недорого", "стол"])

    result = sk.nearest_parents(children, ["стол", "купить стол"])

    assert result.tolist() == ["купить стол", ""]


def test_a_phrase_in_another_word_order_is_not_a_parent() -> None:
    assert sk.nearest_parents(pd.Series(["стол купить"]), ["купить стол", "стол"]).tolist() == ["стол"]


def test_parents_are_found_in_any_case_and_with_e_for_yo() -> None:
    assert sk.nearest_parents(pd.Series(["Купить ёлку"]), ["елку"]).tolist() == ["елку"]


def test_a_parent_of_more_than_six_words_is_found() -> None:
    parent = "a b c d e f g"

    assert sk.nearest_parents(pd.Series([f"{parent} h"]), [parent, "a"]).tolist() == [parent]


def test_between_parents_of_the_same_size_the_one_with_later_words_wins() -> None:
    assert sk.nearest_parents(pd.Series(["a b c"]), ["a b", "b c", "a c"]).tolist() == ["b c"]


def test_the_first_parent_is_the_first_of_the_list() -> None:
    result = sk.first_parents(pd.Series(["купить стол недорого", "стул"]), ["купить стол", "стол"])

    assert result.tolist() == ["купить стол", ""]


def test_the_first_child_is_the_first_of_the_list_that_holds_all_the_words() -> None:
    children = ["стол", "купить стол недорого", "купить стол"]

    result = sk.first_children(pd.Series(["стол купить", "стол", "", "диван"]), children)

    assert result.tolist() == ["купить стол недорого", "купить стол недорого", "", ""]


def test_a_table_gets_the_parent_column_next_to_the_phrases() -> None:
    table = pd.DataFrame({"phrase": ["купить стол"], "freq": [5]})

    result = sk.first_parents(table, ["стол"], column="phrase")

    assert result.columns.tolist() == ["phrase", "phrase_first_parents", "freq"]
    assert result["phrase_first_parents"].tolist() == ["стол"]


def test_basis_phrases_keep_the_phrases_with_no_smaller_phrase_inside() -> None:
    core = pd.Series(["купить диван", "диван", "купить диван недорого", "стол", "диван купить"])

    assert sk.basis_phrases(core).tolist() == ["", "диван", "", "стол", ""]


def test_basis_phrases_by_lemmas() -> None:
    core = pd.Series(["купить диваны", "диван"])

    assert sk.basis_phrases(core).tolist() == ["купить диваны", "диван"]
    assert sk.basis_phrases(core, lemmas=True).tolist() == ["", "диван"]


def test_basis_phrases_without_stopwords() -> None:
    core = pd.Series(["диван в москве", "диван москве"])

    assert sk.basis_phrases(core).tolist() == ["", "диван москве"]
    assert sk.basis_phrases(core, stopwords=False).tolist() == ["диван в москве", ""]


def test_a_phrase_of_stopwords_only_keeps_its_words() -> None:
    assert sk.basis_phrases(pd.Series(["в", "в на"]), stopwords=False).tolist() == ["в", ""]


def test_parents_of_a_phrase_of_many_words_are_found_too() -> None:
    words = [f"w{number}" for number in range(14)]
    phrase = " ".join(words)

    result = sk.nearest_parents(pd.Series([phrase, " ".join(words[:13])]), [" ".join(words[:13]), "w1", phrase])

    assert result.tolist() == [" ".join(words[:13]), "w1"]


def test_a_list_of_parents_with_a_value_that_is_not_text_is_refused() -> None:
    with pytest.raises(sk.InvalidArguments, match="parents"):
        sk.first_parents(pd.Series(["стол"]), ["стол", 5])
