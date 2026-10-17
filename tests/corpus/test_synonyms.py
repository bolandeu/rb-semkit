"""sk.synonyms and sk.add_minus_words through the public library seam."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


def rows(table: pd.DataFrame) -> list[tuple]:
    return list(table.itertuples(index=False, name=None))


def report(*lines: tuple[str, str, str]) -> pd.DataFrame:
    return pd.DataFrame(lines, columns=["phrase", "condition", "matched"])


def test_the_initial_word_comes_from_the_condition() -> None:
    table = sk.synonyms(report(("купить софу", "купить диван", "купить софа")))

    assert table.columns.tolist() == ["word", "sure", "synonyms"]
    assert rows(table) == [("диван", True, "софа")]


def test_the_condition_is_cleaned_of_minus_words_and_operators_and_the_words_are_lemmas() -> None:
    table = sk.synonyms(report(("", "+купить !диваны -бу -дешево", "купила софы")))

    assert rows(table) == [("диван", True, "софа")]


def test_without_a_matched_phrase_the_search_phrase_gives_a_synonym_to_check() -> None:
    table = sk.synonyms(report(("купить кушетку", "купить диван", "-"), ("купить софу", "купить диван", "купить софа")))

    assert rows(table) == [("диван", True, "софа"), ("диван", False, "кушетка")]


def test_a_synonym_to_check_that_is_sure_already_is_not_repeated() -> None:
    table = sk.synonyms(report(("купить софу", "купить диван", "-"), ("", "купить диван", "купить софа")))

    assert rows(table) == [("диван", True, "софа")]


def test_phrases_that_differ_in_more_than_one_word_or_in_length_give_no_synonym() -> None:
    table = sk.synonyms(report(("", "купить диван", "заказать софа"), ("", "купить диван", "купить диван угловой")))

    assert table.empty
    assert table.columns.tolist() == ["word", "sure", "synonyms"]


def test_stopwords_do_not_count() -> None:
    table = sk.synonyms(report(("", "диван в москве", "софа москва")))

    assert rows(table) == [("диван", True, "софа")]


def test_synonyms_of_a_word_are_joined_by_a_space() -> None:
    table = sk.synonyms(report(("", "купить диван", "купить софа"), ("", "купить диван", "купить тахта")))

    assert rows(table) == [("диван", True, "софа тахта")]


def test_a_report_without_its_columns_is_refused() -> None:
    with pytest.raises(sk.InvalidArguments, match="matched"):
        sk.synonyms(pd.DataFrame({"phrase": ["x"], "condition": ["y"]}))


SYNONYMS = pd.DataFrame({"word": ["диван"], "synonyms": ["софа тахта"]})


def test_minus_words_skip_a_synonym_already_in_the_phrase() -> None:
    result = sk.add_minus_words(pd.Series(["купить диван -софа", "купить диваны", "стол"]), SYNONYMS)

    assert result.tolist() == ["купить диван -софа -тахта", "купить диваны -софа -тахта", "стол"]


def test_minus_words_skip_a_synonym_that_is_a_word_of_the_phrase() -> None:
    assert sk.add_minus_words(pd.Series(["диван софа"]), SYNONYMS).tolist() == ["диван софа -тахта"]


def test_a_phrase_in_quotes_gets_no_minus_words() -> None:
    assert sk.add_minus_words(pd.Series(['"купить диван"']), SYNONYMS).tolist() == ['"купить диван"']


def test_the_minus_words_of_a_table_column() -> None:
    table = pd.DataFrame({"phrase": ["Диван"], "freq": [3]})

    result = sk.add_minus_words(table, SYNONYMS, column="phrase", inplace=True)

    assert rows(result) == [("Диван -софа -тахта", 3)]


def test_a_synonyms_table_without_its_columns_is_refused() -> None:
    with pytest.raises(sk.InvalidArguments, match="synonyms"):
        sk.add_minus_words(pd.Series(["диван"]), pd.DataFrame({"word": ["диван"]}))
