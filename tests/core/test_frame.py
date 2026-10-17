"""find / remove / extract with the words matcher over a Series or a DataFrame column."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


@pytest.fixture
def phrases() -> pd.Series:
    return pd.Series(["купить диван", "Диван бу", None], index=["a", "b", "c"])


def test_three_verbs_over_a_series(phrases: pd.Series) -> None:
    matcher = sk.words(["диван"])

    found = sk.find(phrases, matcher)
    removed = sk.remove(phrases, matcher)
    extracted = sk.extract(phrases, matcher)

    assert found.tolist() == [True, True, False]
    assert found.dtype == bool
    assert removed.tolist() == ["купить", "бу", ""]
    assert extracted.tolist() == ["диван", "Диван", ""]
    for result in (found, removed, extracted):
        assert result.index.tolist() == ["a", "b", "c"]


def test_matching_ignores_case_and_yo_and_keeps_the_original_text() -> None:
    phrases = pd.Series(["Ёлка  купить", "купить ЕЛКУ"])

    assert sk.extract(phrases, sk.words("елка")).tolist() == ["Ёлка", ""]
    assert sk.remove(phrases, sk.words(["ЁЛКА"])).tolist() == ["купить", "купить ЕЛКУ"]


def test_results_never_hold_double_spaces() -> None:
    phrases = pd.Series(["  диван  в\tмоскве  диван "])

    assert sk.remove(phrases, sk.words("в")).tolist() == ["диван москве диван"]
    assert sk.extract(phrases, sk.words("диван")).tolist() == ["диван диван"]


def test_all_or_any_of_the_words() -> None:
    phrases = pd.Series(["купить диван", "купить стол", "диван"])

    assert sk.find(phrases, sk.words(["купить", "диван"], mode="all")).tolist() == [True, False, False]
    assert sk.find(phrases, sk.words(["купить", "диван"], mode="any")).tolist() == [True, True, True]
    assert sk.remove(phrases, sk.words(["купить", "диван"], mode="all")).tolist() == ["", "купить стол", "диван"]


def test_words_at_the_start_or_the_end() -> None:
    phrases = pd.Series(["диван купить диван", "купить диван", "диван"])

    assert sk.find(phrases, sk.words("купить", where="start")).tolist() == [False, True, False]
    assert sk.remove(phrases, sk.words("диван", where="start")).tolist() == ["купить диван", "купить диван", ""]
    assert sk.extract(phrases, sk.words("диван", where="end")).tolist() == ["диван", "диван", "диван"]
    assert sk.remove(phrases, sk.words("диван", where="end")).tolist() == ["диван купить", "купить", ""]


def test_ignore_punct() -> None:
    phrases = pd.Series(["диван, купить", "«диван»"])

    assert sk.find(phrases, sk.words("диван")).tolist() == [False, False]
    assert sk.find(phrases, sk.words("диван", ignore_punct=True)).tolist() == [True, True]
    assert sk.remove(phrases, sk.words("диван", ignore_punct=True)).tolist() == ["купить", ""]


def test_dataframe_gets_a_new_column_right_after_the_source() -> None:
    df = pd.DataFrame({"phrase": ["купить диван бу", "стол"], "freq": [10, 5]})

    out = sk.remove(df, sk.words(["бу"]), column="phrase")

    assert out is df
    assert list(df.columns) == ["phrase", "phrase_remove", "freq"]
    assert df["phrase_remove"].tolist() == ["купить диван", "стол"]
    assert df["phrase"].tolist() == ["купить диван бу", "стол"]


def test_inplace_replaces_the_column() -> None:
    df = pd.DataFrame({"phrase": ["купить диван бу", None], "freq": [10, 5]})

    sk.remove(df, sk.words(["бу"]), column="phrase", inplace=True)

    assert list(df.columns) == ["phrase", "freq"]
    assert df["phrase"].tolist() == ["купить диван", ""]


def test_a_second_run_overwrites_its_own_column() -> None:
    df = pd.DataFrame({"phrase": ["купить диван"]})

    sk.find(df, sk.words("диван"), column="phrase")
    sk.find(df, sk.words("стол"), column="phrase")

    assert list(df.columns) == ["phrase", "phrase_find"]
    assert df["phrase_find"].tolist() == [False]


def test_pipe_chains_verbs_over_one_column() -> None:
    df = pd.DataFrame({"phrase": ["купить диван бу", "диван в москве"]})

    chain = sk.pipe(df, "phrase").remove(sk.words("бу")).remove(sk.words("в"))

    assert chain.phrases.tolist() == ["купить диван", "диван москве"]
    assert chain.extract(sk.words("диван")).phrases.tolist() == ["диван", "диван"]
    assert chain.find(sk.words("москве")).tolist() == [False, True]
    assert list(df.columns) == ["phrase"]


@pytest.mark.parametrize(
    ("call", "argument", "allowed"),
    [
        (lambda df: sk.find(df, sk.words("бу"), column="nope"), "column", "'phrase', 'freq'"),
        (lambda df: sk.find(df, sk.words("бу"), column="freq"), "column", "'phrase'"),
        (lambda df: sk.find(df, sk.words("бу")), "column", "'phrase', 'freq'"),
        (lambda df: sk.find(df["freq"], sk.words("бу")), "data", "text"),
        (lambda df: sk.find(df["phrase"].tolist(), sk.words("бу")), "data", "Series, DataFrame"),
        (lambda df: sk.find(df["phrase"], sk.words("бу"), column="phrase"), "column", "DataFrame"),
        (lambda df: sk.find(df["phrase"], sk.words("бу"), inplace=True), "inplace", "DataFrame"),
        (lambda df: sk.find(df, "бу", column="phrase"), "matcher", "sk.words"),
        (lambda df: sk.find(df, sk.words([]), column="phrase"), "items", "one word"),
        (lambda df: sk.find(df, sk.words(["купить диван"]), column="phrase"), "items", "one word"),
        (lambda df: sk.find(df, sk.words("бу", mode="some"), column="phrase"), "mode", "'any', 'all'"),
        (
            lambda df: sk.find(df, sk.words("бу", where="middle"), column="phrase"),
            "where",
            "'anywhere', 'start', 'end'",
        ),
    ],
)
def test_wrong_input_names_the_argument_and_the_allowed_values(call, argument: str, allowed: str) -> None:
    df = pd.DataFrame({"phrase": ["купить диван бу"], "freq": [10]})
    before = df.copy()

    with pytest.raises(sk.InvalidArguments) as error:
        call(df)

    assert argument in error.value.message
    assert allowed in error.value.message
    pd.testing.assert_frame_equal(df, before)
