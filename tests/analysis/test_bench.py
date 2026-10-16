"""scripts/bench.py, run in-process with small --rows."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bench.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("bench", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bench = _load()


def test_one_line_per_operation_with_rows_and_seconds(capsys: pytest.CaptureFixture[str]) -> None:
    code = bench.main(["--rows", "1000", "--ops", "ngrams,lemmatize"])

    lines = capsys.readouterr().out.splitlines()
    assert code == 0
    operations = [line.split()[0] for line in lines if line.split()[:1] in (["ngrams"], ["lemmatize"])]
    assert operations == ["ngrams", "lemmatize"]
    assert all("1000" in line for line in lines if line.startswith(("ngrams", "lemmatize")))


def test_a_limit_of_zero_fails_and_names_the_slow_operation(capsys: pytest.CaptureFixture[str]) -> None:
    code = bench.main(["--rows", "100", "--ops", "ngrams", "--limit", "0"])

    captured = capsys.readouterr()
    assert code != 0
    assert "ngrams" in captured.err


def test_phrases_come_from_the_input_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "core.csv"
    source.write_text("phrase,freq_msk_exact\nкупить диван,10\nдиван угловой,5\nкупить стол,1\n", encoding="utf-8")

    phrases = bench.build_phrases(10, source)
    code = bench.main(["--input", str(source), "--rows", "10", "--ops", "ngrams"])

    assert len(phrases) == 10
    assert {word for phrase in phrases for word in phrase.split()} <= {"купить", "диван", "угловой", "стол"}
    assert phrases[:3] == ["купить диван", "диван угловой", "купить стол"]
    assert code == 0
    assert "10" in capsys.readouterr().out


def test_synthetic_phrases_are_the_same_on_every_run() -> None:
    assert bench.build_phrases(50, None) == bench.build_phrases(50, None)
    assert len(bench.build_phrases(50, None)) == 50


def test_an_operation_whose_module_is_missing_is_skipped(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import sys

    import rb_semkit as sk

    monkeypatch.delattr(sk, "dupes", raising=False)
    monkeypatch.setitem(sys.modules, "rb_semkit.core.dupes", None)

    code = bench.main(["--rows", "20", "--ops", "dupes"])

    assert code == 0
    assert "skipped" in capsys.readouterr().out


def test_an_unknown_operation_is_refused() -> None:
    with pytest.raises(SystemExit) as stop:
        bench.main(["--ops", "nope"])

    assert stop.value.code == 2
