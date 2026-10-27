"""relate-phrases acceptance: the table of section 4 of docs/plans/relate-phrases.md end to end, the join of the Latin
reading and the dictionary, and the documents.

The table runs twice: with the small test thesaurus (the real senses of its words) and the test --synonyms file for
«починить стиральную машину», and against the real thesaurus from the cache (marker real_encoder; skipped when it is
not pulled).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rb_semkit.core.errors import CliError
from rb_semkit.core.word_vectors import thesaurus

from .runner import relate, rows

ROOT = Path(__file__).parents[2]
REPAIR = "ремонт | починка | ремонтировать | починить"

# H, C, the class of C, the reason: the rows of the table, the pairs (H first, C second)
PAIRS = [
    ("ремонт стиральных машин", "ремонт стиральной машины", "same", "lemmas"),
    ("ремонт стиральных машин", "стиральная машина ремонт", "same", "lemmas"),
    ("создание сайтов", "создание сайта", "same", "lemmas"),
    ("создание сайтов", "создать сайт", "variation", "создать~создание (pos_synonymy)"),
    ("создание сайтов", "создавать сайты", "variation", "создавать~создание (pos_synonymy)"),
    ("разработка сайтов", "разработать сайт", "variation", "разработать~разработка (pos_synonymy)"),
    (
        "ремонт стиральных машин",
        "отремонтировать стиральную машину",
        "variation",
        "отремонтировать~ремонт (pos_synonymy)",
    ),
    ("разработка сайтов", "разработка веб сайтов", "variation", "веб-сайт~сайт (synset)"),
    ("разработка сайтов", "разработка интернет сайтов", "variation", "интернет-сайт~сайт (synset)"),
    ("разработка веб сайтов", "разработка web сайтов", "variation", "веб-сайт~веб-сайт (synset)"),
    ("разработка сайтов", "разработка web сайтов", "variation", "веб-сайт~сайт (synset)"),
    ("ремонт стиральных машин", "ремонтные работы стиральных машин", "variation", "ремонтные работы~ремонт (synset)"),
    ("ремонт стиральных машин", "ремонт стиралок", "variation", "стиралка~стиральная машина (synset)"),
    ("ремонт стиральных машин бош", "ремонт стиральных машин bosch", "variation", "bosch~бош (latin)"),
    ("ремонт стиральных машин", "ремонт стиральных машин bosch", "refinement", "+bosch"),
    ("сделать сайт", "как сделать сайт", "refinement", "+как"),
    ("разработка сайтов", "разработка сайтов москва", "refinement", "+москва"),
    ("разработка сайтов", "разработка сайтов под ключ", "refinement", "+ключ"),
    ("создание сайтов", "разработка сайтов", "other", "unlinked: разработка | создание"),
    ("ремонт стиральных машин", "починить стиральную машину", "other", "unlinked: починить | ремонт"),
    ("как создать сайт на wordpress", "как создать сайт на вордпресс", "variation", "wordpress~вордпресс (latin)"),
    ("как создать сайт на wordpress", "как создать сайт на wordpress в москве", "refinement", "+москва"),
    ("как создать сайт на wordpress", "сайт на wordpress в москве", "other", "unlinked: москва | как, создавать"),
]


def _repair_file(tmp_path: Path) -> str:
    path = tmp_path / "repair.csv"
    path.write_text(f'synonyms\n"{REPAIR}"\n')
    return str(path)


def _check_row(tmp_path: Path, first: str, second: str, kind: str, reason: str, *options: str) -> None:
    found = relate(tmp_path, [first, second], *options)[second]
    assert found[0] == kind
    assert found[3] == reason
    if kind == "other":
        assert found[1] == ""
    else:
        assert found[1] == first


@pytest.mark.parametrize(("first", "second", "kind", "reason"), PAIRS)
def test_the_table_with_the_test_thesaurus(tmp_path: Path, first: str, second: str, kind: str, reason: str) -> None:
    _check_row(tmp_path, first, second, kind, reason)


def test_the_synonyms_file_makes_the_repair_row_a_variation(tmp_path: Path) -> None:
    found = relate(
        tmp_path, ["ремонт стиральных машин", "починить стиральную машину"], "--synonyms", _repair_file(tmp_path)
    )

    assert found["починить стиральную машину"][:2] == ("variation", "ремонт стиральных машин")
    assert "(synonyms)" in found["починить стиральную машину"][3]


def test_the_longer_phrase_refines_the_shorter_one_whatever_the_order(tmp_path: Path) -> None:
    assert rows(tmp_path, ["как сделать сайт", "сделать сайт"]) == [
        ("refinement", "сделать сайт", "как сделать сайт", "+как"),
        ("other", "", "как сделать сайт", "base of: как сделать сайт"),
    ]


def test_the_latin_reading_joins_the_dictionary(tmp_path: Path) -> None:
    found = relate(tmp_path, ["разработка сайтов", "разработка web сайтов"])

    assert found["разработка web сайтов"] == (
        "variation",
        "разработка сайтов",
        "разработка сайтов",
        "веб-сайт~сайт (synset)",
    )


@pytest.fixture
def real_thesaurus() -> None:
    try:
        thesaurus.open_thesaurus(Path.cwd())
    except CliError as error:
        pytest.skip(f"ruwordnet is not in the cache ({error.code}): run 'semkit models pull ruwordnet'.")


@pytest.mark.real_encoder
@pytest.mark.usefixtures("real_thesaurus")
@pytest.mark.parametrize(("first", "second", "kind", "reason"), PAIRS)
def test_the_table_with_the_real_thesaurus(tmp_path: Path, first: str, second: str, kind: str, reason: str) -> None:
    _check_row(tmp_path, first, second, kind, reason)


@pytest.mark.real_encoder
@pytest.mark.usefixtures("real_thesaurus")
def test_the_synonyms_file_fills_the_gap_of_the_real_thesaurus(tmp_path: Path) -> None:
    found = relate(
        tmp_path, ["ремонт стиральных машин", "починить стиральную машину"], "--synonyms", _repair_file(tmp_path)
    )

    assert found["починить стиральную машину"][:2] == ("variation", "ремонт стиральных машин")


@pytest.mark.parametrize("document", ["README.md", "src/rb_semkit/data/SKILL.md"])
def test_a_document_describes_the_step(document: str) -> None:
    text = (ROOT / document).read_text()

    for part in ("relate-phrases", "same", "variation", "refinement", "other", "group", "reason", "--synonyms", "|"):
        assert part in text, f"{document}: {part}"
    for gap in ("сделать", "создать", "починить", "ремонт"):
        assert gap in text, f"{document}: {gap}"
