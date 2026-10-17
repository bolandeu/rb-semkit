"""The `Example:` line of every step's help is a command that runs on the small files of tests/steps/fixtures and does
something there: a change changes cells, a filter drops rows, a report gives rows."""

from __future__ import annotations

import json
import shlex
from pathlib import Path

import pytest

from rb_semkit import steps

from ..pipeline.runner import semkit

FIXTURES = Path(__file__).parent / "fixtures"
STEPS = {step.name: step for area in steps.areas().values() for step in area}
WIDE = {"COLUMNS": "1000", "NO_COLOR": "1", "TERM": "dumb"}


def _example(name: str, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    for key, value in WIDE.items():
        monkeypatch.setenv(key, value)
    lines = semkit("read", "IN", name, "--help").stdout.splitlines()
    line = next(line for line in lines if line.startswith(" Example: "))
    program, *arguments = shlex.split(line.removeprefix(" Example: "))
    assert program == "semkit" and arguments[-2:] == ["write", "out.csv"]
    return arguments[:-1]


@pytest.mark.parametrize("name", sorted(STEPS))
def test_the_example_of_a_step_runs_and_does_something(
    name: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    arguments = _example(name, monkeypatch)
    monkeypatch.chdir(FIXTURES)

    result = semkit("--json", *arguments, str(tmp_path / "out.jsonl"))

    assert result.exit_code == 0, f"{arguments}: {result.output}"
    summary = json.loads(result.stdout)["steps"][-1]
    did = {
        "change": summary["cells_changed"] > 0,
        "filter": summary["rows_after"] < summary["rows_before"],
        "report": summary["rows_after"] > 0,
    }
    assert did[STEPS[name].kind], f"{arguments}: {summary}"
