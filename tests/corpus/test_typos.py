"""sk.is_typo, sk.typo_correction and sk.levenshtein through the public library seam."""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk

TAILS = ["купить", "угловой", "кожаный", "бу", "икеа", "недорого", "красный", "большой", "детский", "белый"]
CORE = pd.Series([*(f"диван {tail}" for tail in TAILS), "купить диавн"])


def test_a_rare_word_near_a_frequent_one_is_a_typo_and_the_frequent_one_is_its_correction() -> None:
    assert sk.is_typo(CORE).tolist() == [False] * len(TAILS) + [True]
    assert sk.typo_correction(CORE).tolist() == [*CORE[: len(TAILS)], "купить диван"]


def test_a_word_not_frequent_enough_against_it_is_no_typo() -> None:
    core = pd.Series(["стол", "стол купить", "стул"])

    assert sk.is_typo(core).tolist() == [False, False, False]
    assert sk.is_typo(core, provider=sk.CoreSpelling(ratio=2)).tolist() == [False, False, True]


def test_a_short_word_allows_fewer_edits() -> None:
    core = pd.Series([f"кот {tail}" for tail in TAILS] + ["кит", "кто"])

    assert sk.is_typo(core, provider=sk.CoreSpelling(ratio=2)).tolist()[-2:] == [True, False]


def test_a_word_with_a_digit_is_no_typo() -> None:
    core = pd.Series([f"диван {tail}" for tail in TAILS] + ["диван2"])

    assert not sk.is_typo(core).iloc[-1]


def test_the_correction_keeps_the_other_words_and_the_phrase_of_a_table() -> None:
    table = pd.DataFrame({"phrase": CORE, "freq": range(len(CORE))})

    result = sk.typo_correction(table, column="phrase")

    assert result.columns.tolist() == ["phrase", "phrase_typo_correction", "freq"]
    assert result["phrase_typo_correction"].iloc[-1] == "купить диван"


class FakeSpelling:
    """A provider that knows one misspelt word: «дивн» → «диван»."""

    name = "fake"

    def check(self, phrases: list[str]) -> list[list[sk.Misspelling]]:
        return [[sk.Misspelling(phrase.find("дивн"), 4, ("диван",))] if "дивн" in phrase else [] for phrase in phrases]


def test_another_provider_decides_the_typos_and_their_corrections() -> None:
    phrases = pd.Series(["купить дивн", "стол", "купить дивн"])

    assert sk.is_typo(phrases, provider=FakeSpelling()).tolist() == [True, False, True]
    assert sk.typo_correction(phrases, provider=FakeSpelling()).tolist() == ["купить диван", "стол", "купить диван"]


@pytest.mark.parametrize(
    ("first", "second", "distance"),
    [("диван", "диавн", 2), ("кот", "кит", 1), ("", "abc", 3), ("диван", "диван", 0), ("а", "0", 1), ("ёж", "еж", 1)],
)
def test_levenshtein_counts_the_edits_of_whole_characters(first: str, second: str, distance: int) -> None:
    assert sk.levenshtein(first, second) == distance


@pytest.mark.parametrize("ratio", [0.5, True, "10"])
def test_a_ratio_below_one_or_not_a_number_is_refused(ratio: object) -> None:
    with pytest.raises(sk.InvalidArguments, match="ratio"):
        sk.CoreSpelling(ratio=ratio)
