"""The steps of a pipeline use the project of the CLI (--project), not the current folder."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rb_semkit.core import services
from rb_semkit.core.errors import ModelNotPulled
from rb_semkit.core.vectors import cache, encoder, registry
from rb_semkit.core.vectors.registry import Model

from ..conftest import WordEncoder
from .runner import jsonl, semkit

PHRASES = ["купить диван", "диван б/у", "кресло и диван", "диван москва"]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    services.init_project(root, "demo")
    return root


@pytest.fixture
def elsewhere(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    folder = tmp_path / "elsewhere"
    folder.mkdir()
    monkeypatch.chdir(folder)
    return folder


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "in.jsonl"
    path.write_text("\n".join(json.dumps({"phrase": p}, ensure_ascii=False) for p in PHRASES), encoding="utf-8")
    return path


@pytest.fixture
def pulled_only_in_the_models_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    """The encoder opens only when the model is in the cache of the project it is asked for."""

    def opened(model: Model, start: Path) -> WordEncoder:
        folder = cache.models_dir(start)
        if not (folder / model.folder).is_dir():
            raise ModelNotPulled(model.name, str(folder))
        return WordEncoder()

    monkeypatch.setattr(encoder, "encoder_for", opened)


def _set_config(project: Path, **keys: object) -> None:
    services.save_config(project, services.load_config(project).model_copy(update=keys))


def _model_in(folder: Path) -> None:
    (folder / registry.model(registry.default_name()).folder).mkdir(parents=True)


def _kept(result) -> list[str]:
    assert result.exit_code == 0, result.output
    return [row["phrase"] for row in jsonl(result.stdout)]


@pytest.mark.usefixtures("elsewhere", "pulled_only_in_the_models_dir")
def test_a_step_by_meaning_takes_the_models_dir_of_the_project(project: Path, source: Path) -> None:
    models = project / "models"
    _model_in(models)
    config = services.load_config(project)
    _set_config(project, models=config.models.model_copy(update={"dir": "models"}))

    result = semkit("--project", str(project), "read", str(source), "cluster-meaning", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["phrase"] for row in jsonl(result.stdout)] == PHRASES


@pytest.mark.usefixtures("elsewhere", "pulled_only_in_the_models_dir")
def test_a_project_without_the_model_still_says_it_is_missing(project: Path, source: Path) -> None:
    _set_config(project, models=services.load_config(project).models.model_copy(update={"dir": "models"}))

    result = semkit("--project", str(project), "read", str(source), "cluster-meaning", "write", "-")

    assert result.exit_code == 1
    assert "is not in" in result.output


@pytest.mark.usefixtures("elsewhere")
def test_a_list_of_the_project_is_used(project: Path, source: Path) -> None:
    lists = services.project_lists_dir(project) / "niche"
    lists.mkdir(parents=True)
    (lists / "minus.txt").write_text("москва\nб/у\n", encoding="utf-8")

    result = semkit("--project", str(project), "read", str(source), "drop-words", "@niche/minus", "write", "-")

    assert _kept(result) == ["купить диван", "кресло и диван"]


@pytest.mark.usefixtures("elsewhere")
def test_a_lists_folder_relative_in_the_config_is_from_the_project(project: Path, source: Path) -> None:
    (project / "words" / "niche").mkdir(parents=True)
    (project / "words" / "niche" / "minus.txt").write_text("купить\n", encoding="utf-8")
    _set_config(project, lists=["words"])

    result = semkit("--project", str(project), "read", str(source), "drop-words", "@niche/minus", "write", "-")

    assert _kept(result) == ["диван б/у", "кресло и диван", "диван москва"]


def test_without_the_option_the_project_is_the_current_folder(
    project: Path, source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (services.project_lists_dir(project)).mkdir(parents=True)
    (services.project_lists_dir(project) / "minus.txt").write_text("москва\n", encoding="utf-8")
    monkeypatch.chdir(project)

    result = semkit("read", str(source), "drop-words", "@minus", "write", "-")

    assert _kept(result) == ["купить диван", "диван б/у", "кресло и диван"]
