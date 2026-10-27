"""relate-phrases: a phrase is a refinement by words even when the thesaurus reads a part of it as a unit of several
words that takes a word of the base («мастер по ремонту» takes «ремонт»), or holds the words of the base apart.

The pairs run with the test thesaurus plus the real senses of their words, and against the real thesaurus from the
cache (marker real_encoder; skipped when it is not pulled).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rb_semkit.core.errors import CliError
from rb_semkit.core.word_vectors import thesaurus

from .conftest import SENSES
from .runner import relate, rows

UNITS = [  # the senses of the real thesaurus for the words of these pairs (the ids and the lemmas as the file has them)
    ("134620-N-141967", "МАСТЕР", "МАСТЕР"),
    ("111590-N-201222", "МАСТЕР ПО РЕМОНТУ", "МАСТЕР ПО РЕМОНТ"),
    ("154-N-106224", "МАШИНА", "МАШИНА"),
    ("154-N-165023", "АВТО", "АВТО"),
    ("154-N-100133", "АВТОМОБИЛЬ", "АВТОМОБИЛЬ"),
    ("154-N-707914", "МАШИНКА", "МАШИНКА"),
    ("1731-N-109315", "ПОСУДОМОЕЧНАЯ МАШИНА", "ПОСУДОМОЕЧНЫЙ МАШИНА"),
    ("126573-N-105582", "КУЗОВ", "КУЗОВ"),
    ("126573-N-720986", "КУЗОВ АВТОМОБИЛЯ", "КУЗОВ АВТОМОБИЛЬ"),
    ("2380-N-117531", "РАСТАМОЖКА", "РАСТАМОЖКА"),
    ("2526-N-103320", "ДОМ", "ДОМ"),
]
REPAIR = "ремонт стиральных машин"
MASTER = "мастер по ремонту стиральных машин"
MASTER_AT_HOME = "мастер по ремонту машинок стиральных на дому"
CUSTOMS, BODY = "растаможка авто", "растаможка кузова автомобиля"
TWO_KINDS = "ремонт стиральных и посудомоечных машин"

# H, C and the class, of and reason of C in the table of the two (H first)
PAIRS = [
    (REPAIR, MASTER, ("refinement", REPAIR, "+мастер")),
    (REPAIR, MASTER_AT_HOME, ("refinement", REPAIR, "+мастер +дом; машинка~машина (synset)")),
    (CUSTOMS, BODY, ("refinement", CUSTOMS, "+кузов; автомобиль~авто (synset)")),
    (REPAIR, TWO_KINDS, ("refinement", REPAIR, "+посудомоечный")),
]


@pytest.fixture
def real_senses(use_senses) -> None:
    use_senses([*SENSES, *UNITS])


def _check_pair(tmp_path: Path, base: str, phrase: str, expected: tuple[str, str, str]) -> None:
    kind, of, _, reason = relate(tmp_path, [base, phrase])[phrase]
    assert (kind, of, reason) == expected


@pytest.mark.usefixtures("real_senses")
@pytest.mark.parametrize(("base", "phrase", "expected"), PAIRS)
def test_a_unit_that_takes_a_word_of_the_base_still_makes_a_refinement(
    tmp_path: Path, base: str, phrase: str, expected: tuple[str, str, str]
) -> None:
    _check_pair(tmp_path, base, phrase, expected)


@pytest.mark.usefixtures("real_senses")
def test_both_phrases_of_the_master_refine_the_repair(tmp_path: Path) -> None:
    found = relate(tmp_path, [REPAIR, MASTER, MASTER_AT_HOME])

    assert found[MASTER] == ("refinement", REPAIR, REPAIR, "+мастер")
    assert found[MASTER_AT_HOME][:3] == ("refinement", REPAIR, REPAIR)
    assert found[REPAIR] == ("other", "", REPAIR, f"base of: {MASTER} | {MASTER_AT_HOME}")


@pytest.mark.usefixtures("real_senses")
def test_the_words_of_the_base_apart_make_a_refinement_in_any_order_of_the_rows(tmp_path: Path) -> None:
    assert rows(tmp_path, [TWO_KINDS, REPAIR]) == [
        ("refinement", REPAIR, TWO_KINDS, "+посудомоечный"),
        ("other", "", TWO_KINDS, f"base of: {TWO_KINDS}"),
    ]


@pytest.mark.usefixtures("real_senses")
def test_the_words_never_make_a_variation(tmp_path: Path) -> None:
    found = relate(tmp_path, ["мастер по ремонту", "мастер отремонтировать"])

    assert found["мастер отремонтировать"][:2] == ("other", "")


@pytest.fixture
def real_thesaurus() -> None:
    try:
        thesaurus.open_thesaurus(Path.cwd())
    except CliError as error:
        pytest.skip(f"ruwordnet is not in the cache ({error.code}): run 'semkit models pull ruwordnet'.")


@pytest.mark.real_encoder
@pytest.mark.usefixtures("real_thesaurus")
@pytest.mark.parametrize(("base", "phrase", "expected"), PAIRS)
def test_the_pairs_with_the_real_thesaurus(
    tmp_path: Path, base: str, phrase: str, expected: tuple[str, str, str]
) -> None:
    _check_pair(tmp_path, base, phrase, expected)
