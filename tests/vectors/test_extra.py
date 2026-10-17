"""semkit without the vectors extra: the steps by meaning and `semkit models` name the install command; the other
steps run as before."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import semkit

pytestmark = pytest.mark.real_encoder


@pytest.fixture(autouse=True)
def _no_extra(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The imports of the extra fail, as they do when it is not installed."""
    monkeypatch.setitem(sys.modules, "onnxruntime", None)
    monkeypatch.chdir(tmp_path)
    pd.DataFrame({"phrase": ["купить диван!", "диван"]}).to_csv(tmp_path / "core.csv", index=False)


def _install_command(result) -> str:
    assert result.exit_code != 0
    error = json.loads(result.stdout)["error"]
    assert error["code"] == "VECTORS_NOT_INSTALLED"
    return error["action"]


def test_cluster_meaning_names_the_install_command_of_the_extra() -> None:
    action = _install_command(semkit("--json", "read", "core.csv", "cluster-meaning", "write", "out.csv"))

    assert "uv tool install" in action
    assert "rb-semkit[vectors]" in action
    assert not Path("out.csv").exists()


@pytest.mark.parametrize("command", [["list"], ["pull", "e5-small"], ["remove", "e5-small"]])
def test_semkit_models_names_the_install_command_of_the_extra(command: list[str]) -> None:
    action = _install_command(semkit("--json", "models", *command))

    assert "rb-semkit[vectors]" in action


def test_a_pipeline_of_other_steps_runs_as_before() -> None:
    result = semkit("read", "core.csv", "remove-chars", "punctuation", "write", "-")

    assert result.exit_code == 0, result.output
    assert [json.loads(line)["phrase"] for line in result.stdout.splitlines()] == ["купить диван", "диван"]
