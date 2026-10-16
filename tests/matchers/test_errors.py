"""Wrong arguments raise InvalidArguments naming the argument and the allowed values."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk
from rb_semkit.core.errors import InvalidArguments

PHRASES = pd.Series(["диван"])


def test_a_bad_regex_names_the_pattern() -> None:
    with pytest.raises(InvalidArguments, match=r"pattern='\(';.*allowed: a valid regular expression"):
        sk.regex("(")


def test_an_unsupported_verb_names_the_supported_ones() -> None:
    with pytest.raises(InvalidArguments, match=r"find: .*allowed: remove\."):
        sk.find(PHRASES, sk.spaces("extra"))
    with pytest.raises(InvalidArguments, match=r"remove: .*allowed: find, extract\."):
        sk.remove(PHRASES, sk.word_case("lower"))
    with pytest.raises(InvalidArguments, match=r"extract: .*allowed: find, remove\."):
        sk.extract(PHRASES, sk.repeats())
    with pytest.raises(InvalidArguments, match=r"find: .*allowed: remove, extract\."):
        sk.find(PHRASES, sk.positions(2))


@pytest.mark.parametrize(
    "call",
    [
        lambda: sk.positions(0),
        lambda: sk.word_position(first=0),
        lambda: sk.word_position(last=-1),
        lambda: sk.word_position(nth=0),
        lambda: sk.word_position(at_most=0),
    ],
)
def test_n_below_one_is_refused(call) -> None:
    with pytest.raises(InvalidArguments, match=r"allowed: .*1"):
        call()


def test_word_position_needs_exactly_one_selector() -> None:
    with pytest.raises(InvalidArguments, match="first, last, nth, to_middle, at_most"):
        sk.word_position()
    with pytest.raises(InvalidArguments, match="first, last, nth, to_middle, at_most"):
        sk.word_position(first=1, last=1)


@pytest.mark.parametrize(
    ("call", "argument", "allowed"),
    [
        (lambda: sk.chars("greek"), "kind", "'latin'"),
        (lambda: sk.spaces("middle"), "kind", "'extra'"),
        (lambda: sk.word_case("Title"), "kind", "'Capital'"),
        (lambda: sk.word_content("starts"), "pattern", "starts"),
        (lambda: sk.word_content("ending"), "kind", "'only_latin'"),
        (lambda: sk.pos("noun phrase"), "kind", "'noun'"),
        (lambda: sk.repeats("fuzzy"), "mode", "'wordforms'"),
        (lambda: sk.repeats(scope="all words"), "scope", "'adjacent'"),
        (lambda: sk.cells("middle"), "kind", "'repeated'"),
        (lambda: sk.cells("contains"), "items", "prepositions"),
        (lambda: sk.cells("regex"), "pattern", "regular"),
        (lambda: sk.phrases([]), "items", "non-empty"),
        (lambda: sk.stopwords([""]), "extra", "words"),
    ],
)
def test_bad_choices_name_the_argument_and_the_allowed_values(call, argument: str, allowed: str) -> None:
    with pytest.raises(InvalidArguments) as error:
        call()

    assert argument in str(error.value)
    assert allowed in str(error.value)
