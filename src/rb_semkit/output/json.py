"""The --json envelope on stdout: one line of JSON, Cyrillic as it is (not escaped)."""

from __future__ import annotations

import json

import typer


def emit(data: dict) -> None:
    typer.echo(json.dumps(data, ensure_ascii=False))
