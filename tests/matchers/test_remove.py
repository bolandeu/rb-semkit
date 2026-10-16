"""The remove verb: cleaned text, no double spaces, index kept."""

from __future__ import annotations

import pandas as pd

import rb_semkit as sk

MESSY = pd.Series(["  купить  диван  в  москве "], index=[3])


def test_spaces_stopwords_and_around() -> None:
    assert sk.remove(MESSY, sk.spaces("extra")).tolist() == ["купить диван в москве"]
    assert sk.remove(MESSY, sk.stopwords()).tolist() == ["купить диван москве"]
    assert sk.remove(MESSY, sk.around("в", after=True, include=True)).tolist() == ["купить ди"]
    assert sk.remove(MESSY, sk.stopwords()).index.tolist() == [3]


def test_spaces_kinds() -> None:
    phrases = pd.Series(["  a  b  "])

    assert sk.remove(phrases, sk.spaces("all")).tolist() == ["ab"]
    assert sk.remove(phrases, sk.spaces("left")).tolist() == ["a  b  "]
    assert sk.remove(phrases, sk.spaces("right")).tolist() == ["  a  b"]
    assert sk.remove(phrases, sk.spaces("both")).tolist() == ["a  b"]


def test_chars_remove_leaves_single_spaces() -> None:
    phrases = pd.Series(["Купить iPhone 15 в Москве"])

    assert sk.remove(phrases, sk.chars("digits")).tolist() == ["Купить iPhone в Москве"]
    assert sk.remove(phrases, sk.chars("latin")).tolist() == ["Купить 15 в Москве"]
    assert sk.remove(phrases, sk.chars("cyrillic")).tolist() == ["iPhone 15"]


def test_positions_around_and_regex_remove() -> None:
    phrases = pd.Series(["купить диван в москве"])

    assert sk.remove(phrases, sk.positions(7)).tolist() == ["диван в москве"]
    assert sk.remove(phrases, sk.positions(7, last=True)).tolist() == ["купить диван в"]
    assert sk.remove(phrases, sk.around("диван")).tolist() == ["диван в москве"]
    assert sk.remove(phrases, sk.around("диван", include=True)).tolist() == ["в москве"]
    assert sk.remove(phrases, sk.around("нет", after=True)).tolist() == ["купить диван в москве"]
    assert sk.remove(phrases, sk.regex(r"\bв\b")).tolist() == ["купить диван москве"]


def test_regex_not_match_keeps_only_the_matches() -> None:
    phrases = pd.Series(["a1", "abc"])

    assert sk.remove(phrases, sk.regex(r"\d", invert=True)).tolist() == ["1", ""]


def test_words_by_content_and_position() -> None:
    phrases = pd.Series(["купить iPhone15 в 2024 году"])

    assert sk.remove(phrases, sk.word_content("has_digits")).tolist() == ["купить в году"]
    assert sk.remove(phrases, sk.word_position(first=2)).tolist() == ["в 2024 году"]
    assert sk.remove(phrases, sk.word_position(at_most=3)).tolist() == ["iPhone15 в 2024 году"]


def test_stopwords_with_a_user_list_and_case_and_yo() -> None:
    phrases = pd.Series(["Купить В ёлку недорого"])

    assert sk.remove(phrases, sk.stopwords(["ЕЛКУ", "недорого"])).tolist() == ["Купить"]


def test_phrases_remove_whole_words_only() -> None:
    phrases = pd.Series(["купить угловой диван сегодня", "угловойдиван"])

    assert sk.remove(phrases, sk.phrases(["угловой диван"])).tolist() == ["купить сегодня", "угловойдиван"]
    assert sk.find(phrases, sk.phrases(["угловой диван"])).tolist() == [True, False]


def test_dataframe_gets_the_result_in_a_new_column() -> None:
    frame = pd.DataFrame({"phrase": ["купить диван в москве"], "freq": [5]})

    result = sk.remove(frame, sk.stopwords(), column="phrase")

    assert result.columns.tolist() == ["phrase", "phrase_remove", "freq"]
    assert result["phrase_remove"].tolist() == ["купить диван москве"]
