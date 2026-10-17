"""The `Example:` line of every step's help is a command that runs on the small files of tests/steps/fixtures."""

from __future__ import annotations

import shlex
from pathlib import Path

import pytest

from rb_semkit import steps

from ..pipeline.runner import semkit

FIXTURES = Path(__file__).parent / "fixtures"
STEPS = sorted(step.name for area in steps.areas().values() for step in area)
WIDE = {"COLUMNS": "1000", "NO_COLOR": "1", "TERM": "dumb"}


def _example(name: str, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    for key, value in WIDE.items():
        monkeypatch.setenv(key, value)
    lines = semkit("read", "IN", name, "--help").stdout.splitlines()
    line = next(line for line in lines if line.startswith(" Example: "))
    program, *arguments = shlex.split(line.removeprefix(" Example: "))
    assert program == "semkit" and arguments[-2:] == ["write", "out.csv"]
    return [*arguments[:-1], "-"]


@pytest.mark.parametrize("name", STEPS)
def test_the_example_of_a_step_runs(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    arguments = _example(name, monkeypatch)
    monkeypatch.chdir(FIXTURES)

    result = semkit(*arguments)

    assert result.exit_code == 0, f"{arguments}: {result.output}"
