"""Marker lists through the public seam: names, several lists in one pass, user lists, prepositions."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments

PHRASES = pd.Series(["диван в москве у метро таганская", "диван купить"], index=[10, 20])


def test_extract_gives_the_markers_as_the_list_spells_them_in_phrase_order() -> None:
    result = sk.extract(PHRASES, sk.markers(["geo", "mosmetro"]))

    assert result.tolist() == ["Москве, Таганская", ""]
    assert result.index.tolist() == [10, 20]


def test_sep_changes_the_separator() -> None:
    assert sk.extract(PHRASES, sk.markers(["geo", "mosmetro"], sep=" | ")).tolist() == ["Москве | Таганская", ""]


def test_matching_is_case_insensitive_and_the_list_spelling_wins() -> None:
    phrases = pd.Series(["Диван СПБ", "диван спб"])

    assert sk.extract(phrases, sk.markers(["geo"])).tolist() == ["СПб", "СПб"]


def test_find_and_remove() -> None:
    matcher = sk.markers(["geo", "mosmetro"])

    assert sk.find(PHRASES, matcher).tolist() == [True, False]
    assert sk.remove(PHRASES, matcher).tolist() == ["диван в у метро", "диван купить"]


def test_remove_with_prepositions_takes_the_toponym_preposition() -> None:
    matcher = sk.markers(["geo", "mosmetro"], with_prepositions=True)

    assert sk.remove(PHRASES, matcher).tolist() == ["диван у метро", "диван купить"]
    assert sk.extract(PHRASES, matcher).tolist() == ["в Москве, Таганская", ""]


def test_a_marker_of_several_words_is_one_marker() -> None:
    phrases = pd.Series(["авиамоторная и автозаводская"])

    assert sk.extract(phrases, sk.markers(["mosmetro"])).tolist() == ["Авиамоторная, Автозаводская"]


def test_user_list_matches_whole_words_only() -> None:
    phrases = pd.Series(["купить угловой диван", "угловойдиван", "угловой диванчик"])
    matcher = sk.markers(user={"mine": ["угловой диван"]})

    assert sk.find(phrases, matcher).tolist() == [True, False, False]
    assert sk.extract(phrases, matcher).tolist() == ["угловой диван", "", ""]


def test_a_user_list_beside_a_bundled_one() -> None:
    phrases = pd.Series(["диван в Москве"])

    matcher = sk.markers(["geo"], user={"mine": ["диван"]})

    assert sk.extract(phrases, matcher).tolist() == ["диван, Москве"]


def test_phrases_match_whole_words_only() -> None:
    phrases = pd.Series(["купить угловой диван", "угловойдиван"])

    assert sk.find(phrases, sk.phrases(["угловой диван"])).tolist() == [True, False]


def test_an_unknown_list_name_lists_the_18_names() -> None:
    with pytest.raises(InvalidArguments) as error:
        sk.markers(["nope"])

    message = str(error.value)
    assert "lists='nope'" in message
    for name in ("geo", "mosmetro", "districts", "MO", "citiesRu", "questions", "fun", "DIY", "edu", "game"):
        assert repr(name) in message
    for name in ("sale", "rent", "reviews", "color", "material", "origin", "cars", "names"):
        assert repr(name) in message


def test_no_list_at_all_is_refused() -> None:
    with pytest.raises(InvalidArguments, match="lists"):
        sk.markers([])
