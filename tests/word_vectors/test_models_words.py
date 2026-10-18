"""`semkit models pull | list | remove` for the word data, as for the encoders (ADR 0009)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ..pipeline.runner import semkit
from ..vectors.conftest import LocalSource
from .conftest import NAVEC_FILE, THESAURUS_FILE, navec_bytes


def _listed(name: str) -> dict:
    result = semkit("--json", "models", "list")
    assert result.exit_code == 0, result.output
    return next(entry for entry in json.loads(result.stdout)["models"] if entry["name"] == name)


@pytest.mark.parametrize(("name", "file"), [("ruwordnet", THESAURUS_FILE), ("navec", NAVEC_FILE)])
def test_a_pull_puts_the_data_into_the_cache_and_list_shows_it_with_its_size(
    words_hub: LocalSource, models_dir: Path, name: str, file: str
) -> None:
    assert _listed(name)["pulled"] is False

    result = semkit("--json", "models", "pull", name)

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["downloaded"] is True
    assert (models_dir / name / file).is_file()
    entry = _listed(name)
    assert entry["pulled"] is True
    assert entry["size"] == (models_dir / name / file).stat().st_size


def test_a_second_pull_downloads_nothing(words_hub: LocalSource, models_dir: Path) -> None:
    semkit("models", "pull", "navec")

    result = semkit("--json", "models", "pull", "navec")

    assert json.loads(result.stdout)["downloaded"] is False
    assert words_hub.downloads == ["navec"]


def test_a_file_whose_checksum_differs_leaves_nothing(words_hub: LocalSource, models_dir: Path) -> None:
    (words_hub.root / "test/navec" / NAVEC_FILE).write_bytes(navec_bytes() + b"broken")

    result = semkit("--json", "models", "pull", "navec")

    assert result.exit_code != 0
    assert "checksum" in json.loads(result.stdout)["error"]["message"]
    assert _listed("navec")["pulled"] is False


def test_remove_takes_the_data_out_of_the_cache_and_the_list(words_hub: LocalSource, models_dir: Path) -> None:
    semkit("models", "pull", "ruwordnet")

    result = semkit("models", "remove", "ruwordnet")

    assert result.exit_code == 0, result.output
    assert not (models_dir / "ruwordnet").exists()
    assert _listed("ruwordnet")["pulled"] is False


def test_word_data_is_not_an_encoder_of_a_step_by_meaning(
    words_hub: LocalSource, models_dir: Path, tmp_path: Path
) -> None:
    core = tmp_path / "core.csv"
    core.write_text("phrase\nдиван\n", encoding="utf-8")

    result = semkit("--json", "read", str(core), "cluster-meaning", "--model", "navec", "write", "-")

    assert result.exit_code == 2
    message = json.loads(result.stdout)["error"]["message"]
    assert "navec" in message
    assert "e5-small" in message
    assert "ruwordnet" not in message
