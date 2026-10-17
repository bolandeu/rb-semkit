"""A project folder as the working folder, and a home folder, both in tmp; no SEMKIT_LISTS from the machine."""

from __future__ import annotations

from pathlib import Path

import pytest

from rb_semkit.core import services


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    folder = tmp_path / "home"
    folder.mkdir()
    monkeypatch.setenv("HOME", str(folder))
    monkeypatch.delenv("SEMKIT_LISTS", raising=False)
    return folder


@pytest.fixture
def project(tmp_path: Path, home: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """An initialized project, which is also the working folder."""
    folder = tmp_path / "project"
    folder.mkdir()
    services.init_project(folder, "demo")
    monkeypatch.chdir(folder)
    return folder


def write_list(folder: Path, name: str, text: str) -> Path:
    path = folder / f"{name}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def set_config_lists(project: Path, folders: list[str]) -> None:
    config = services.load_config(project)
    config.lists = folders
    services.save_config(project, config)
