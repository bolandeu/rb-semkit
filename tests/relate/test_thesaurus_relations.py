"""The thesaurus file with the tables of the real one: the POS-synonymy pairs are read, the derivation pairs are not,
the synonyms stay; relate-phrases refuses when RuWordNet is not pulled."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rb_semkit.core.word_vectors.thesaurus import load

from ..pipeline.runner import semkit
from ..vectors.conftest import models_dir  # noqa: F401  (a fixture the tests use)
from .conftest import thesaurus_file


def test_the_pos_synonymy_pairs_are_read_in_both_directions(tmp_path: Path) -> None:
    loaded = load(thesaurus_file(tmp_path / "relations.db"))

    assert dict(loaded.pos_synonyms) == {
        "106493-N": {"106493-V"},
        "106493-V": {"106493-N"},
        "119670-N": {"119670-V"},
        "119670-V": {"119670-N"},
        "464-N": {"464-V"},
        "464-V": {"464-N"},
        "3852-N": {"3852-V"},
        "3852-V": {"3852-N"},
    }


def test_the_derivation_pairs_are_not_read_and_the_synonyms_stay(tmp_path: Path) -> None:
    loaded = load(thesaurus_file(tmp_path / "relations.db"))

    assert [sense.name for sense in loaded.synonyms(("купить",))] == ["подкупить", "накупить"]
    assert [sense.name for sense in loaded.synonyms(("покупатель",))] == []
    assert [sense.name for sense in loaded.synonyms(("сайт",))] == ["веб-сайт", "интернет-сайт", "вебсайт"]
    assert [sense.name for sense in loaded.synonyms(("стиральный", "машина"))] == ["стиралка"]


@pytest.mark.real_encoder
@pytest.mark.usefixtures("models_dir")
def test_relate_phrases_without_ruwordnet_refuses_before_it_reads_the_input(tmp_path: Path) -> None:
    result = semkit("--json", "read", str(tmp_path / "no-such-input.jsonl"), "relate-phrases", "write", "-")

    error = json.loads(result.stdout)["error"]
    assert result.exit_code == 1
    assert error["code"] == "MODEL_NOT_PULLED"
    assert "semkit models pull ruwordnet" in error["action"]
