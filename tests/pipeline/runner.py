"""The pipeline through its command line: `semkit read IN STEP … write OUT`, in-process or as a process."""

from __future__ import annotations

import json
import subprocess
import sys

from typer.testing import CliRunner

from rb_semkit.cli import app

CORE = ["купить диван", "диван", "купить угловой диван", "угловые диваны", "диван недорого"]


def semkit(*args: str, input: str | None = None):
    """`semkit ARGS` in-process: the result has exit_code, stdout and stderr apart."""
    return CliRunner().invoke(app, list(args), input=input, prog_name="semkit")


def semkit_process(*args: str, input: str) -> subprocess.CompletedProcess[str]:
    """`semkit ARGS` as its own process, for the real stdin and stdout."""
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "rb_semkit.cli", *args],
        input=input,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def jsonl(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]
