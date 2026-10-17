"""The vectors tests: a project whose config key models.dir names a folder in tmp, and the hub as a local folder.

The local source serves the files of e5-small from `<tmp>/hub`; the registry pins their checksums, written out here.
The same repo is the hub model hf:test/e5.
It notes every download, can fail midway, and can make two pulls wait for each other.
"""

from __future__ import annotations

import dataclasses
import shutil
import threading
from pathlib import Path

import pytest

from rb_semkit.core import services
from rb_semkit.core.vectors import registry, source
from rb_semkit.core.vectors.registry import Model

FILES = {"model.onnx": b"weights", "tokenizer.json": b"tokens"}
CHECKSUMS = {
    "model.onnx": "9a129038d9a00aed0cf6a7ea059ca50a813449061ab87848cf1a13eafdf33b2c",
    "tokenizer.json": "c51e455b41df6c017327e16001dd064b8b6733faeaa69b23d9bd79c8079237d5",
}
REPO, REVISION = "test/e5", "abc123"


class LocalSource:
    """The hub as a folder: the file `path` of a repo is `<root>/<repo>/<path>`."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.downloads: list[str] = []
        self.fail_after: int | None = None  # the number of files written before the download breaks
        self.together: threading.Barrier | None = None  # the pulls that download at the same time

    def resolve(self, model: Model) -> Model:
        """A hub model gets the files of the repo, unpinned, at the revision «latest»."""
        if model.revision is not None:
            return model
        return dataclasses.replace(model, revision="latest", runtime="onnx", files=dict.fromkeys(FILES, ""))

    def download(self, model: Model, into: Path) -> None:
        self.downloads.append(model.name)
        if self.together is not None:
            self.together.wait(timeout=10)
        for number, path in enumerate(model.files):
            if number == self.fail_after:
                raise OSError("connection reset by peer")
            (into / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.root / model.repo / path, into / path)


@pytest.fixture
def hub(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> LocalSource:
    """The local source in place of the hub; e5-small is pinned to its files."""
    for path, content in FILES.items():
        (tmp_path / "hub" / REPO).mkdir(parents=True, exist_ok=True)
        (tmp_path / "hub" / REPO / path).write_bytes(content)
    bundled = registry.bundled()
    e5 = dataclasses.replace(bundled.models["e5-small"], repo=REPO, revision=REVISION, files=CHECKSUMS)
    pinned = dataclasses.replace(bundled, models={**bundled.models, "e5-small": e5})
    monkeypatch.setattr(registry, "bundled", lambda: pinned)
    local = LocalSource(tmp_path / "hub")
    monkeypatch.setattr(source, "SOURCE", local)
    return local


@pytest.fixture
def models_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """The folder of the encoders: the config key models.dir of a project, which is also the working folder."""
    project = tmp_path / "project"
    project.mkdir()
    config = services.init_project(project, "demo")
    config.models.dir = str(tmp_path / "models")
    services.save_config(project, config)
    monkeypatch.chdir(project)
    return tmp_path / "models"
