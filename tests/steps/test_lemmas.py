"""The words and phrases steps compare by lemmas with --lemmas: a bundled list of lemmas finds the forms of a core."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..pipeline.runner import jsonl, semkit


def _core(tmp_path: Path, phrases: list[str]) -> Path:
    path = tmp_path / "core.csv"
    pd.DataFrame({"phrase": phrases}).to_csv(path, index=False)
    return path


def test_drop_phrases_by_lemmas_drops_the_forms_of_the_listed_phrases(tmp_path: Path) -> None:
    core = _core(tmp_path, ["купить дешевые диваны", "диван со скидкой", "купить диван"])

    result = semkit("read", str(core), "drop-phrases", "@minus/cheap", "--lemmas", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "купить диван"}]


def test_drop_phrases_without_lemmas_compares_the_forms_as_written(tmp_path: Path) -> None:
    core = _core(tmp_path, ["купить дешевые диваны", "диван со скидкой", "купить диван"])

    result = semkit("read", str(core), "drop-phrases", "@minus/cheap", "write", "-")

    assert result.exit_code == 0, result.output
    assert len(jsonl(result.stdout)) == 3


def test_a_listed_phrase_of_two_words_matches_its_forms_by_lemmas(tmp_path: Path) -> None:
    core = _core(tmp_path, ["угловые диваны недорого", "диван"])

    result = semkit("read", str(core), "find-phrases", "угловой диван", "--lemmas", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["phrase_find"] for row in jsonl(result.stdout)] == [True, False]


def test_drop_words_by_lemmas_drops_the_forms_of_a_listed_word(tmp_path: Path) -> None:
    core = _core(tmp_path, ["дешевые диваны", "диван"])

    result = semkit("read", str(core), "drop-words", "дешевый", "--lemmas", "write", "-")

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == [{"phrase": "диван"}]
