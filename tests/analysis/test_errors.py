"""Wrong arguments of the analysis functions raise InvalidArguments naming the argument and the allowed values."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk

S = pd.Series(["купить диван"])
DF = pd.DataFrame({"phrase": ["купить диван"], "freq": [1], "region": ["msk"]})


@pytest.mark.parametrize("n", [0, -1, 1.5, "2", True])
def test_n_must_be_a_positive_integer(n: object) -> None:
    with pytest.raises(sk.InvalidArguments, match=r"n=.*allowed: an integer of 1 or more"):
        sk.ngrams(S, n=n)


def test_unknown_what_lists_the_allowed_values() -> None:
    with pytest.raises(sk.InvalidArguments, match=r"what='nope'.*allowed: 'words', 'chars', 'count'"):
        sk.counts(S, what="nope")


@pytest.mark.parametrize("call", [sk.ngrams, sk.bigrams])
def test_a_weight_column_that_is_not_numeric(call) -> None:
    with pytest.raises(sk.InvalidArguments, match=r"weight='region'.*not numeric.*allowed: 'freq'"):
        call(DF, weight="region", column="phrase")


def test_a_weight_column_that_is_missing() -> None:
    with pytest.raises(sk.InvalidArguments, match=r"weight='nope'.*allowed: 'freq'"):
        sk.ngrams(DF, weight="nope", column="phrase")


def test_a_weight_needs_a_dataframe() -> None:
    with pytest.raises(sk.InvalidArguments, match=r"weight.*only for a DataFrame"):
        sk.ngrams(S, weight="freq")


@pytest.mark.parametrize("what", ["share", "abc"])
def test_share_and_abc_need_a_weight(what: str) -> None:
    with pytest.raises(sk.InvalidArguments, match=rf"what='{what}'.*weight"):
        sk.counts(DF, what=what, column="phrase")


def test_the_input_is_checked_like_in_every_function() -> None:
    with pytest.raises(sk.InvalidArguments, match="column"):
        sk.ngrams(DF)
