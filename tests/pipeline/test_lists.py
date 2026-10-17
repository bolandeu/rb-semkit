"""An argument that takes items: @path, a comma list, @name."""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

from .runner import jsonl, semkit

PHRASES = ["купить диван", "диван б/у", "кресло и диван", "диван москва"]


def _source(tmp_path: Path) -> Path:
    source = tmp_path / "in.jsonl"
    source.write_text("\n".join(json.dumps({"phrase": p}, ensure_ascii=False) for p in PHRASES), encoding="utf-8")
    return source


def _drop(tmp_path: Path, items: str):
    return semkit("read", str(_source(tmp_path)), "drop-words", "--items", items, "write", "-")


def _kept(result) -> list[str]:
    assert result.exit_code == 0, result.output
    return [row["phrase"] for row in jsonl(result.stdout)]


def test_a_file_with_a_bom_and_crlf(tmp_path: Path) -> None:
    (tmp_path / "minus.txt").write_bytes("﻿купить\r\nб/у\r\n\r\n".encode())

    assert _kept(_drop(tmp_path, f"@{tmp_path / 'minus.txt'}")) == ["кресло и диван", "диван москва"]


def test_a_comma_list(tmp_path: Path) -> None:
    assert _kept(_drop(tmp_path, "купить, москва")) == ["диван б/у", "кресло и диван"]


def test_the_bundled_stopwords_by_name(tmp_path: Path) -> None:
    assert _kept(_drop(tmp_path, "@stopwords")) == ["купить диван", "диван б/у", "диван москва"]


def test_a_marker_list_by_name(tmp_path: Path) -> None:
    source = tmp_path / "in.jsonl"
    source.write_text('{"phrase": "диван москва"}\n{"phrase": "диван"}\n', encoding="utf-8")

    result = semkit("read", str(source), "keep-phrases", "--items", "@geo", "write", "-")

    assert _kept(result) == ["диван москва"]


def test_an_unknown_name_is_refused_with_the_names_that_exist(tmp_path: Path) -> None:
    result = semkit("--json", "read", str(_source(tmp_path)), "drop-words", "--items", "@nope", "write", "-")

    payload = json.loads(result.stdout)
    assert result.exit_code == 2
    message = payload["error"]["message"]
    assert "drop-words" in message and "@nope" in message
    assert "stopwords" in message and "geo" in message


def test_names_resolve_through_the_word_list_module_when_it_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wordlists = types.ModuleType("rb_semkit.core.wordlists")
    wordlists.resolve = lambda name: {"minus/cheap": ["москва"]}[name]  # ty: ignore[unresolved-attribute]
    wordlists.names = lambda: ["minus/cheap"]  # ty: ignore[unresolved-attribute]
    monkeypatch.setitem(sys.modules, "rb_semkit.core.wordlists", wordlists)

    assert _kept(_drop(tmp_path, "@minus/cheap")) == ["купить диван", "диван б/у", "кресло и диван"]
