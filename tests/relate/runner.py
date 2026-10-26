"""relate-phrases through the pipeline: `semkit read TABLE.jsonl relate-phrases … write -` on a table written here."""

from __future__ import annotations

import json
from pathlib import Path

from ..pipeline.runner import jsonl, semkit

COLUMNS = ("class", "of", "group", "reason")


def table(tmp_path: Path, phrases: list[str]) -> Path:
    """A JSONL table of the phrases, one per row, in this order."""
    path = tmp_path / "phrases.jsonl"
    path.write_text("".join(json.dumps({"phrase": phrase}, ensure_ascii=False) + "\n" for phrase in phrases))
    return path


def _run(tmp_path: Path, phrases: list[str], *options: str) -> list[dict]:
    result = semkit("read", str(table(tmp_path, phrases)), "relate-phrases", *options, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def relate(tmp_path: Path, phrases: list[str], *options: str) -> dict[str, tuple[str, ...]]:
    """The class, of, group and reason of each phrase."""
    return {row["phrase"]: tuple(row[name] for name in COLUMNS) for row in _run(tmp_path, phrases, *options)}


def rows(tmp_path: Path, phrases: list[str], *options: str) -> list[tuple[str, ...]]:
    """The class, of, group and reason of each row, in the order of the rows."""
    return [tuple(row[name] for name in COLUMNS) for row in _run(tmp_path, phrases, *options)]
