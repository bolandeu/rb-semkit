"""The matchers through sk.find / sk.extract: small Series in, exact Series out, index kept."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk

PHRASE = pd.Series(["Купить iPhone 15 в Москве"], index=[7])


@pytest.mark.parametrize(
    ("matcher", "expected"),
    [
        (sk.chars("latin"), "iPhone"),
        (sk.chars("digits"), "15"),
        (sk.regex(r"\d+"), "15"),
        (sk.word_case("Capital"), "Купить Москве"),
        (sk.word_position(first=1), "Купить"),
    ],
)
def test_extract_and_find_on_one_phrase(matcher: sk.Matcher, expected: str) -> None:
    extracted = sk.extract(PHRASE, matcher)

    assert extracted.tolist() == [expected]
    assert extracted.index.tolist() == [7]
    assert sk.find(PHRASE, matcher).tolist() == [True]


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("cyrillic", "Купить в Москве"),
        ("letters_digits", "Купить iPhone 15 в Москве"),
        ("upper", "К P М"),
        ("punctuation", ""),
        ("ua", ""),
    ],
)
def test_char_kinds_extract_runs_joined_by_a_space(kind: str, expected: str) -> None:
    assert sk.extract(PHRASE, sk.chars(kind)).tolist() == [expected]


def test_ua_letters_and_punctuation() -> None:
    phrases = pd.Series(["їжак, ґанок!", "ёж"])

    assert sk.extract(phrases, sk.chars("ua")).tolist() == ["ї ґ", ""]
    assert sk.extract(phrases, sk.chars("punctuation")).tolist() == [", !", ""]
    assert sk.find(phrases, sk.chars("ua")).tolist() == [True, False]


def test_find_is_false_and_extract_empty_where_nothing_is_found() -> None:
    phrases = pd.Series(["диван", "", None])

    assert sk.find(phrases, sk.chars("latin")).tolist() == [False, False, False]
    assert sk.extract(phrases, sk.chars("latin")).tolist() == ["", "", ""]


def test_regex_all_matches_and_not_match() -> None:
    phrases = pd.Series(["a1 b22 c", "abc"])

    assert sk.extract(phrases, sk.regex(r"\d+", all_matches=True)).tolist() == ["1 22", ""]
    assert sk.find(phrases, sk.regex(r"\d+", invert=True)).tolist() == [True, True]
    assert sk.extract(phrases, sk.regex(r"\d+", invert=True)).tolist() == ["a b c", "abc"]


def test_positions_extract_first_and_last_chars() -> None:
    phrases = pd.Series(["купить диван"])

    assert sk.extract(phrases, sk.positions(3)).tolist() == ["куп"]
    assert sk.extract(phrases, sk.positions(5, last=True)).tolist() == ["диван"]


def test_around_extract_before_and_after_the_occurrence() -> None:
    phrases = pd.Series(["купить диван в москве и в спб", "диван"])

    assert sk.extract(phrases, sk.around("в")).tolist() == ["купить ди", "ди"]
    assert sk.extract(phrases, sk.around("в", after=True)).tolist() == ["ан в москве и в спб", "ан"]
    assert sk.extract(phrases, sk.around("в", after=True, last=True)).tolist() == ["спб", "ан"]
    assert sk.extract(phrases, sk.around("в", last=True, include=True)).tolist() == ["купить диван в москве и в", "див"]


def test_word_content_kinds() -> None:
    phrases = pd.Series(["купить iPhone15 в 2024 году", "диван Samsung"])

    assert sk.extract(phrases, sk.word_content("only_latin")).tolist() == ["", "Samsung"]
    assert sk.extract(phrases, sk.word_content("has_latin")).tolist() == ["iPhone15", "Samsung"]
    assert sk.extract(phrases, sk.word_content("only_digits")).tolist() == ["2024", ""]
    assert sk.extract(phrases, sk.word_content("has_digits")).tolist() == ["iPhone15 2024", ""]
    assert sk.extract(phrases, sk.word_content("mixed")).tolist() == ["iPhone15", ""]


def test_word_content_starts_ends_contains_a_pattern_or_a_list() -> None:
    phrases = pd.Series(["Диванчик угловой диван", "стол"])

    assert sk.extract(phrases, sk.word_content("starts", "див")).tolist() == ["Диванчик диван", ""]
    assert sk.extract(phrases, sk.word_content("ends", ["ван", "ол"])).tolist() == ["диван", "стол"]
    assert sk.extract(phrases, sk.word_content("contains", "ГЛО")).tolist() == ["угловой", ""]


def test_word_case_lower_and_caps() -> None:
    phrases = pd.Series(["Купить BMW x5 Москве"])

    assert sk.extract(phrases, sk.word_case("CAPS")).tolist() == ["BMW"]
    assert sk.extract(phrases, sk.word_case("lower")).tolist() == ["x5"]


def test_word_position_variants() -> None:
    phrases = pd.Series(["a b c d e"])

    assert sk.extract(phrases, sk.word_position(last=2)).tolist() == ["d e"]
    assert sk.extract(phrases, sk.word_position(nth=2)).tolist() == ["b"]
    assert sk.extract(phrases, sk.word_position(to_middle=True)).tolist() == ["a b"]
    assert sk.extract(phrases, sk.word_position(at_most=2)).tolist() == ["a"]


def test_phrases_extract_as_the_phrase_spells_them() -> None:
    phrases = pd.Series(["Купить Угловой ДИВАН дёшево", "стол"])

    matcher = sk.phrases(["угловой диван", "стол"])

    assert sk.extract(phrases, matcher).tolist() == ["Угловой ДИВАН", "стол"]
    assert sk.find(phrases, matcher).tolist() == [True, True]
