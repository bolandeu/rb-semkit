"""The thesaurus of the relate tests: a small RuWordNet file with the real senses, POS-synonymy pairs and a derivation
pair of the words the tests name (the ids and the lemmas as the real file has them), loaded as semkit loads the file.

It takes the place of the thesaurus the root conftest gives; a test marked `real_encoder` gets neither.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from rb_semkit.core.word_vectors import thesaurus

SENSES = [  # the id, the name and the lemma of each sense; the synset is the id up to its last part
    ("106493-N-153566", "СОЗДАНИЕ", "СОЗДАНИЕ"),
    ("106493-V-153565", "СОЗДАВАТЬ", "СОЗДАВАТЬ"),
    ("106493-V-153568", "СОЗДАТЬ", "СОЗДАТЬ"),
    ("119670-N-160016", "РАЗРАБОТКА", "РАЗРАБОТКА"),
    ("119670-V-160015", "РАЗРАБАТЫВАТЬ", "РАЗРАБАТЫВАТЬ"),
    ("119670-V-160014", "РАЗРАБОТАТЬ", "РАЗРАБОТАТЬ"),
    ("121978-N-206367", "ВЕБ-САЙТ", "ВЕБ-САЙТ"),
    ("121978-N-763642", "ВЕБСАЙТ", "ВЕБСАЙТ"),
    ("121978-N-213643", "ИНТЕРНЕТ-САЙТ", "ИНТЕРНЕТ-САЙТ"),
    ("121978-N-165570", "САЙТ", "САЙТ"),
    ("464-N-110767", "РЕМОНТ", "РЕМОНТ"),
    ("464-N-110780", "РЕМОНТНЫЕ РАБОТЫ", "РЕМОНТНЫЙ РАБОТА"),
    ("464-V-145684", "ОТРЕМОНТИРОВАТЬ", "ОТРЕМОНТИРОВАТЬ"),
    ("464-V-110774", "РЕМОНТИРОВАТЬ", "РЕМОНТИРОВАТЬ"),
    ("5200-N-767042", "СТИРАЛКА", "СТИРАЛКА"),
    ("5200-N-112129", "СТИРАЛЬНАЯ МАШИНА", "СТИРАЛЬНЫЙ МАШИНА"),
    ("3852-N-109116", "ПОКУПКА", "ПОКУПКА"),
    ("3852-V-105625", "КУПИТЬ", "КУПИТЬ"),
    ("3852-V-142995", "НАКУПИТЬ", "НАКУПИТЬ"),
    ("142493-V-105625", "КУПИТЬ", "КУПИТЬ"),
    ("142493-V-115377", "ПОДКУПИТЬ", "ПОДКУПИТЬ"),
    ("4885-N-109113", "ПОКУПАТЕЛЬ", "ПОКУПАТЕЛЬ"),
    ("107292-N-136883", "ДИВАН", "ДИВАН"),
    ("132323-N-184809", "ТЕКУЩИЙ РЕМОНТ", "ТЕКУЩИЙ РЕМОНТ"),
    ("132323-N-119080", "КОСМЕТИЧЕСКИЙ РЕМОНТ", "КОСМЕТИЧЕСКИЙ РЕМОНТ"),
    ("133125-N-185056", "РЕМОНТ ОБУВИ", "РЕМОНТ ОБУВЬ"),
    ("133125-N-199376", "ПОЧИНКА ОБУВИ", "ПОЧИНКА ОБУВЬ"),
]
POS_SYNONYMS = [  # the real file holds most pairs in both directions; some here only in one
    ("106493-N", "106493-V"),
    ("106493-V", "106493-N"),
    ("119670-V", "119670-N"),
    ("464-N", "464-V"),
    ("3852-V", "3852-N"),
]
DERIVATIONS = [("3852-V-105625", "4885-N-109113")]  # купить → покупатель


def thesaurus_file(path: Path, senses: list[tuple[str, str, str]] = SENSES) -> Path:
    """A RuWordNet file at `path` with the tables of the real file: sense, synset, pos_synonymy_relation and
    derivation_relation."""
    synsets = sorted({sense_id.rsplit("-", 1)[0] for sense_id, _, _ in senses})
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE synset (id VARCHAR, title VARCHAR, definition VARCHAR, part_of_speech VARCHAR)"
        )
        connection.execute("CREATE TABLE sense (id VARCHAR, name VARCHAR, lemma VARCHAR, synset_id VARCHAR)")
        connection.execute("CREATE TABLE pos_synonymy_relation (left_id VARCHAR, right_id VARCHAR)")
        connection.execute("CREATE TABLE derivation_relation (source_id VARCHAR, derivative_id VARCHAR)")
        connection.executemany(
            "INSERT INTO synset VALUES (?, ?, '', ?)", [(synset, synset, synset[-1]) for synset in synsets]
        )
        connection.executemany(
            "INSERT INTO sense VALUES (?, ?, ?, ?)",
            [(sense_id, name, lemma, sense_id.rsplit("-", 1)[0]) for sense_id, name, lemma in senses],
        )
        connection.executemany("INSERT INTO pos_synonymy_relation VALUES (?, ?)", POS_SYNONYMS)
        connection.executemany("INSERT INTO derivation_relation VALUES (?, ?)", DERIVATIONS)
    connection.close()
    return path


@pytest.fixture
def use_senses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Gives the steps a thesaurus of these senses (with the pairs above) in place of the one of all `SENSES`."""

    def use(senses: list[tuple[str, str, str]]) -> None:
        loaded = thesaurus.load(thesaurus_file(tmp_path / "ruwordnet-senses.db", senses))
        monkeypatch.setattr(thesaurus, "open_thesaurus", lambda start: loaded)

    return use


@pytest.fixture(autouse=True)
def _relate_thesaurus(request: pytest.FixtureRequest, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.node.get_closest_marker("real_encoder"):
        return
    loaded = thesaurus.load(thesaurus_file(tmp_path / "ruwordnet.db"))
    monkeypatch.setattr(thesaurus, "open_thesaurus", lambda start: loaded)
