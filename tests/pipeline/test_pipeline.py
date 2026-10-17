"""A pipeline reads, runs its steps in the order written and writes the result."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import rb_dataio

from .runner import jsonl, semkit, semkit_process


def _phrases(path: Path) -> list[str]:
    return pd.read_csv(path, dtype=str)["phrase"].tolist()


def test_steps_run_in_order_and_write_the_file(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    result = semkit(
        "read", str(core_csv), "remove-words", "--items", "купить", "dupes", "--kind", "lemmas", "--action", "drop",
        "write", str(out),
    )  # fmt: skip

    assert result.exit_code == 0, result.output
    assert _phrases(out) == ["диван", "угловой диван", "диван недорого"]
    assert result.stdout == ""


def test_jsonl_stdin_to_jsonl_stdout_with_a_report_step(tmp_path: Path) -> None:
    (tmp_path / "stop.txt").write_text("купить\n", encoding="utf-8")
    rows = "\n".join(json.dumps({"phrase": p}, ensure_ascii=False) for p in ["купить диван в москве", "диван в москве"])

    result = semkit_process(
        "read", "-", "drop-words", "--items", f"@{tmp_path / 'stop.txt'}", "ngrams", "-n", "2", "write", "-",
        input=rows,
    )  # fmt: skip

    assert result.returncode == 0, result.stderr
    assert jsonl(result.stdout) == [
        {"ngram": "в москве", "count": 1, "docs": 1},
        {"ngram": "диван в", "count": 1, "docs": 1},
    ]
    lines = result.stderr.splitlines()
    assert [line.split(":")[0] for line in lines] == ["drop-words", "ngrams"]
    assert "2 → 1 rows" in lines[0]


def test_change_step_with_as_adds_a_column(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    result = semkit("read", str(core_csv), "remove-words", "--items", "купить", "--as", "clean", "write", str(out))

    table = pd.read_csv(out, dtype=str)
    assert result.exit_code == 0, result.output
    assert table["phrase"].tolist()[:3] == ["купить диван", "диван", "купить угловой диван"]
    assert table["clean"].tolist()[:3] == ["диван", "диван", "угловой диван"]


def test_change_step_without_as_rewrites_the_working_column(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    semkit("read", str(core_csv), "remove-words", "--items", "купить", "write", str(out))

    table = pd.read_csv(out, dtype=str)
    assert list(table.columns) == ["phrase", "freq"]
    assert table["phrase"].tolist()[:3] == ["диван", "диван", "угловой диван"]


def test_find_adds_a_bool_column(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    semkit("read", str(core_csv), "find-words", "--items", "купить", "write", str(out))

    table = pd.read_csv(out)
    assert list(table.columns) == ["phrase", "phrase_find", "freq"]
    assert table["phrase_find"].tolist() == [True, False, True, False, False]


def test_keep_filter_keeps_the_rows_where_the_matcher_finds(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    semkit("read", str(core_csv), "keep-words", "--items", "купить", "write", str(out))

    assert _phrases(out) == ["купить диван", "купить угловой диван"]


def test_column_picks_the_working_column(tmp_path: Path) -> None:
    source, out = tmp_path / "in.csv", tmp_path / "out.csv"
    pd.DataFrame({"id": ["1", "2"], "query": ["купить диван", "диван"]}).to_csv(source, index=False)

    semkit("read", str(source), "--column", "query", "remove-words", "--items", "купить", "write", str(out))

    assert pd.read_csv(out, dtype=str)["query"].tolist() == ["диван", "диван"]


def test_a_report_makes_its_table_current_and_its_first_text_column_the_working_one(
    core_csv: Path, tmp_path: Path
) -> None:
    out = tmp_path / "out.csv"

    semkit("read", str(core_csv), "ngrams", "remove-words", "--items", "диван", "write", str(out))

    table = pd.read_csv(out, dtype=str, keep_default_na=False)
    assert table.columns[0] == "ngram"
    assert "диван" not in table["ngram"].tolist()
    assert "" in table["ngram"].tolist()


def test_whole_reads_a_text_file_as_one_cell(tmp_path: Path) -> None:
    article, out = tmp_path / "article.txt", tmp_path / "out.jsonl"
    article.write_text("Диваны в Москве.\nКупить диван недорого.\n", encoding="utf-8")

    result = semkit("read", "--whole", str(article), "write", str(out))

    assert result.exit_code == 0, result.output
    assert jsonl(out.read_text(encoding="utf-8")) == [{"text": "Диваны в Москве.\nКупить диван недорого."}]


def test_parquet_in_and_out(tmp_path: Path) -> None:
    source, out = tmp_path / "in.parquet", tmp_path / "out.parquet"
    rb_dataio.write(pd.DataFrame({"phrase": ["купить диван", None], "freq": ["5", "4"]}), source)

    result = semkit("read", str(source), "remove-words", "--items", "купить", "write", str(out))

    assert result.exit_code == 0, result.output
    assert rb_dataio.read(out)["phrase"].tolist() == ["диван", ""]


def test_json_reports_each_step_of_a_written_file(core_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    result = semkit("--json", "read", str(core_csv), "remove-words", "--items", "купить", "write", str(out))

    assert json.loads(result.stdout) == {
        "ok": True,
        "output": str(out),
        "rows": 5,
        "written": True,
        "steps": [{"step": "remove-words", "rows_before": 5, "rows_after": 5, "cells_changed": 2}],
    }
