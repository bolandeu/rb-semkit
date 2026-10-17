"""`semkit models pull | list | remove`: an encoder downloaded once into the cache (ADR 0009), whole or not at all."""

from __future__ import annotations

import dataclasses
import json
import threading
from pathlib import Path

from rb_semkit.core.errors import CliError
from rb_semkit.core.vectors import cache, registry

from ..pipeline.runner import semkit
from .conftest import FILES, REVISION, LocalSource


def _listed(name: str) -> dict:
    result = semkit("--json", "models", "list")
    assert result.exit_code == 0, result.output
    return next(entry for entry in json.loads(result.stdout)["models"] if entry["name"] == name)


def test_a_pull_puts_the_model_into_the_cache_at_its_revision_and_list_shows_it(
    hub: LocalSource, models_dir: Path
) -> None:
    result = semkit("--json", "models", "pull", "e5-small")

    assert result.exit_code == 0, result.output
    pulled = json.loads(result.stdout)
    assert pulled["downloaded"] is True
    assert pulled["revision"] == REVISION
    assert Path(pulled["path"]).parent == models_dir
    assert {path: (Path(pulled["path"]) / path).read_bytes() for path in FILES} == FILES
    entry = _listed("e5-small")
    assert entry["pulled"] is True
    assert entry["revision"] == REVISION
    assert entry["size"] == len(b"weights") + len(b"tokens")


def test_a_second_pull_says_the_model_is_there_and_downloads_nothing(hub: LocalSource, models_dir: Path) -> None:
    semkit("models", "pull", "e5-small")

    result = semkit("--json", "models", "pull", "e5-small")

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["downloaded"] is False
    assert hub.downloads == ["e5-small"]
    assert "already" in semkit("models", "pull", "e5-small").stdout


def test_a_model_not_pulled_is_listed_as_not_pulled(hub: LocalSource, models_dir: Path) -> None:
    assert _listed("e5-small")["pulled"] is False
    assert {"bge-m3", "potion"} <= {
        entry["name"] for entry in json.loads(semkit("--json", "models", "list").stdout)["models"]
    }


def _no_model_left(models_dir: Path) -> bool:
    return not models_dir.exists() or not any(models_dir.iterdir())


def test_a_download_that_breaks_midway_leaves_no_partial_model(hub: LocalSource, models_dir: Path) -> None:
    hub.fail_after = 1

    result = semkit("--json", "models", "pull", "e5-small")

    assert result.exit_code != 0
    error = json.loads(result.stdout)["error"]
    assert "connection reset by peer" in error["message"]
    assert "semkit models pull e5-small" in error["action"]
    assert _no_model_left(models_dir)
    assert _listed("e5-small")["pulled"] is False


def test_a_file_whose_checksum_differs_leaves_no_model(hub: LocalSource, models_dir: Path) -> None:
    (hub.root / "test/e5/model.onnx").write_bytes(b"broken")

    result = semkit("--json", "models", "pull", "e5-small")

    assert result.exit_code != 0
    error = json.loads(result.stdout)["error"]
    assert "model.onnx" in error["message"]
    assert "checksum" in error["message"]
    assert "semkit models pull e5-small" in error["action"]
    assert _no_model_left(models_dir)


def test_two_pulls_at_once_leave_one_valid_copy(hub: LocalSource, models_dir: Path) -> None:
    hub.together = threading.Barrier(2)
    errors: list[CliError] = []

    def pull() -> None:
        try:
            cache.pull("e5-small", Path.cwd())
        except CliError as error:
            errors.append(error)

    threads = [threading.Thread(target=pull) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)

    assert errors == []
    assert [path.name for path in models_dir.iterdir()] == ["e5-small"]
    assert {path: (models_dir / "e5-small" / path).read_bytes() for path in FILES} == FILES
    assert _listed("e5-small")["pulled"] is True


def test_remove_takes_the_model_out_of_the_cache_and_the_list(hub: LocalSource, models_dir: Path) -> None:
    semkit("models", "pull", "e5-small")

    result = semkit("models", "remove", "e5-small")

    assert result.exit_code == 0, result.output
    assert _no_model_left(models_dir)
    assert _listed("e5-small")["pulled"] is False


def test_remove_of_a_model_not_pulled_is_refused_with_the_pulled_ones(hub: LocalSource, models_dir: Path) -> None:
    semkit("models", "pull", "e5-small")

    result = semkit("--json", "models", "remove", "potion")

    assert result.exit_code == 2
    assert "e5-small" in json.loads(result.stdout)["error"]["message"]
    assert (models_dir / "e5-small").is_dir()


def test_remove_with_dry_run_keeps_the_model(hub: LocalSource, models_dir: Path) -> None:
    semkit("models", "pull", "e5-small")

    result = semkit("--dry-run", "models", "remove", "e5-small")

    assert result.exit_code == 0, result.output
    assert _listed("e5-small")["pulled"] is True


def test_a_hub_model_is_pulled_at_the_latest_revision_and_listed_after_the_known_ones(
    hub: LocalSource, models_dir: Path
) -> None:
    result = semkit("--json", "models", "pull", "hf:test/e5")

    assert result.exit_code == 0, result.output
    entry = _listed("hf:test/e5")
    assert (entry["pulled"], entry["revision"], entry["threshold"]) == (True, "latest", None)
    assert [path.name for path in models_dir.iterdir()] == ["hf--test--e5"]
    names = [entry["name"] for entry in json.loads(semkit("--json", "models", "list").stdout)["models"]]
    assert names[-1] == "hf:test/e5"


def test_a_copy_at_another_revision_is_not_pulled_and_a_pull_replaces_it(
    hub: LocalSource, models_dir: Path, monkeypatch
) -> None:
    semkit("models", "pull", "e5-small")
    bundled = registry.bundled()
    newer = dataclasses.replace(bundled.models["e5-small"], revision="def456")
    monkeypatch.setattr(
        registry, "bundled", lambda: dataclasses.replace(bundled, models={**bundled.models, "e5-small": newer})
    )
    assert _listed("e5-small")["pulled"] is False

    result = semkit("--json", "models", "pull", "e5-small")

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["revision"] == "def456"
    assert [path.name for path in models_dir.iterdir()] == ["e5-small"]
    assert _listed("e5-small")["pulled"] is True
