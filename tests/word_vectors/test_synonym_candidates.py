"""`synonym-candidates` in a pipeline: candidates per word of the core from the thesaurus and the word vectors."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit
from ..vectors.conftest import LocalSource

pytestmark = pytest.mark.real_encoder


@pytest.fixture
def pulled(words_hub: LocalSource, core_csv: Path) -> Path:
    """Both word data in the cache; the core."""
    for name in ("ruwordnet", "navec"):
        assert semkit("models", "pull", name).exit_code == 0
    return core_csv


def _report(core: Path, *options: str) -> list[dict]:
    result = semkit("read", str(core), "synonym-candidates", *options, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def _of(rows: list[dict], word: str) -> list[tuple]:
    return [(row["candidate"], row["source"], row["score"], row["in_core"]) for row in rows if row["word"] == word]


def test_a_word_gets_its_synonym_with_the_source_and_the_score_and_not_a_related_word(pulled: Path) -> None:
    rows = _report(pulled)

    found = _of(rows, "диван")
    assert ("софа", "ruwordnet", 1.0, True) in found
    assert ("софа", "navec", 0.8, True) in found
    assert [candidate for candidate, source, *_ in found if source == "ruwordnet"] == ["софа"]
    assert list(rows[0]) == ["word", "candidate", "source", "score", "in_core"]


def test_the_words_are_the_lemmas_of_the_core_without_stopwords_and_numbers(pulled: Path) -> None:
    rows = _report(pulled)

    assert list(dict.fromkeys(row["word"] for row in rows)) == ["диван", "софа", "кресло"]


def test_without_all_the_candidates_not_in_the_core_are_left_out(pulled: Path) -> None:
    assert all(row["in_core"] for row in _report(pulled))


def test_all_gives_the_candidates_not_in_the_core_marked_so_and_each_lemma_once(pulled: Path) -> None:
    found = _of(_report(pulled, "--all"), "диван")

    assert ("тахта", "ruwordnet", 1.0, False) in found
    assert ("тахта", "navec", 0.6, False) in found
    assert [candidate for candidate, source, *_ in found if source == "navec"] == ["софа", "тахта", "кресло"]
    assert [row[2] for row in found if row[1] == "navec"] == [0.8, 0.6, 0.0]


def test_top_limits_the_candidates_of_the_word_vectors(pulled: Path) -> None:
    found = _of(_report(pulled, "--all", "--top", "1"), "диван")

    assert [candidate for candidate, source, *_ in found if source == "navec"] == ["софа"]


def test_a_source_leaves_the_other_one_out(pulled: Path) -> None:
    assert {row["source"] for row in _report(pulled, "--source", "ruwordnet")} == {"ruwordnet"}
    assert {row["source"] for row in _report(pulled, "--source", "navec")} == {"navec"}


def test_as_synonyms_gives_the_file_of_synonyms_that_a_step_with_synonyms_reads(pulled: Path, tmp_path: Path) -> None:
    written = tmp_path / "synonyms.csv"
    result = semkit(
        "read", str(pulled), "synonym-candidates", "--source", "ruwordnet", "--as-synonyms", "write", str(written)
    )
    assert result.exit_code == 0, result.output

    table = pd.read_csv(written)
    assert list(table.columns) == ["word", "synonyms"]
    assert table.to_dict("records") == [{"word": "диван", "synonyms": "софа"}, {"word": "софа", "synonyms": "диван"}]
    minus = semkit("read", str(pulled), "add-minus-words", "--synonyms", str(written), "write", "-")
    assert [row["phrase"] for row in jsonl(minus.stdout)][:1] == ["диван -софа"]


def _error(*arguments: str) -> tuple[int, dict]:
    result = semkit("--json", "read", *arguments, "write", "out.csv")
    return result.exit_code, json.loads(result.stdout)["error"]


def test_data_not_in_the_cache_downloads_nothing_and_gives_the_pull_command(
    words_hub: LocalSource, core_csv: Path
) -> None:
    semkit("models", "pull", "ruwordnet")
    downloaded = list(words_hub.downloads)

    code, error = _error(str(core_csv), "synonym-candidates")

    assert code != 0
    assert error["code"] == "MODEL_NOT_PULLED"
    assert "semkit models pull navec" in error["action"]
    assert words_hub.downloads == downloaded


def test_a_source_the_step_lacks_is_refused_with_the_allowed_ones(words_hub: LocalSource, core_csv: Path) -> None:
    result = semkit("--json", "read", str(core_csv), "synonym-candidates", "--source", "nosuch", "write", "out.csv")

    assert result.exit_code == 2
    text = result.stdout + result.stderr
    assert all(name in text for name in ("nosuch", "ruwordnet", "navec", "both"))


def test_a_top_below_one_is_refused(pulled: Path) -> None:
    code, error = _error(str(pulled), "synonym-candidates", "--top", "0")

    assert code == 2
    assert "top" in error["message"]
