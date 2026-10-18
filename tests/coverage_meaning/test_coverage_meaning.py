"""`coverage-meaning` in a pipeline: each core phrase gets the best paragraph of a text, its similarity and whether it
is covered; with --cluster, whether its cluster is covered too."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit

CORE = ["угловой диван", "диван кровать"]
ARTICLE = "Диваны\n\nПрямые диваны ставят у стены.\n\nУгловой диван\n\nШкафы купе бывают разные."
THRESHOLD = "0.9"


@pytest.fixture(autouse=True)
def in_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


def _core(tmp_path: Path, **columns: list) -> Path:
    path = tmp_path / "core.csv"
    pd.DataFrame(columns or {"phrase": CORE}).to_csv(path, index=False)
    return path


def _run(core: Path, *arguments: str) -> list[dict]:
    result = semkit("read", str(core), "coverage-meaning", *arguments, "--threshold", THRESHOLD, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def test_a_phrase_gets_its_best_paragraph_its_similarity_and_covered_by_the_threshold(tmp_path: Path) -> None:
    text = tmp_path / "article.txt"
    text.write_text(ARTICLE, encoding="utf-8")

    rows = _run(_core(tmp_path), "--text", str(text))

    assert list(rows[0]) == ["phrase", "url", "number", "paragraph", "similarity", "covered"]
    corner, bed = rows
    assert (corner["phrase"], corner["number"], corner["paragraph"]) == ("угловой диван", 3, "Угловой диван")
    assert (corner["similarity"], corner["covered"]) == (1.0, "yes")
    assert bed["phrase"] == "диван кровать"
    assert bed["paragraph"] != ""
    assert 0 < bed["similarity"] < float(THRESHOLD)
    assert bed["covered"] == "no"


def test_a_cluster_is_covered_when_any_of_its_phrases_is(tmp_path: Path) -> None:
    text = tmp_path / "article.txt"
    text.write_text(ARTICLE, encoding="utf-8")
    core = _core(
        tmp_path,
        phrase=["угловой диван", "диван кровать", "шкаф купе", "стол"],
        cluster=[1, 1, 2, 3],
    )

    rows = _run(core, "--text", str(text), "--cluster", "cluster")

    assert [(row["phrase"], row["covered"], row["cluster_covered"]) for row in rows] == [
        ("угловой диван", "yes", "yes"),
        ("диван кровать", "no", "yes"),
        ("шкаф купе", "no", "no"),
        ("стол", "no", "no"),
    ]
    assert [row["cluster"] for row in rows] == [1, 1, 2, 3]


def test_the_best_paragraph_is_searched_across_the_texts_of_a_table_and_gives_its_url(tmp_path: Path) -> None:
    texts = tmp_path / "pages.csv"
    pd.DataFrame(
        {"url": ["/sofas", "/beds"], "text": ["Прямые диваны\n\nУгловой диван", "Кровать двуспальная\n\nДиван кровать"]}
    ).to_csv(texts, index=False)

    rows = _run(_core(tmp_path), "--text", str(texts))

    assert [(row["url"], row["number"], row["paragraph"], row["covered"]) for row in rows] == [
        ("/sofas", 2, "Угловой диван", "yes"),
        ("/beds", 2, "Диван кровать", "yes"),
    ]


@pytest.mark.parametrize(
    ("arguments", "named"),
    [
        (["--text", "nosuch.txt"], "--text nosuch.txt"),
        (["--text", "article.txt", "--cluster", "nosuch"], "--cluster nosuch"),
    ],
)
def test_a_wrong_option_is_refused_naming_it(tmp_path: Path, arguments: list[str], named: str) -> None:
    (tmp_path / "article.txt").write_text(ARTICLE, encoding="utf-8")
    core = _core(tmp_path)

    result = semkit("read", str(core), "coverage-meaning", *arguments, "--threshold", THRESHOLD, "write", "-")

    assert result.exit_code == 2
    assert named in result.stderr


def test_an_empty_text_leaves_every_phrase_not_covered_with_an_empty_paragraph(tmp_path: Path) -> None:
    text = tmp_path / "empty.txt"
    text.write_text("", encoding="utf-8")

    rows = _run(_core(tmp_path), "--text", str(text))

    assert [(row["phrase"], row["paragraph"], row["covered"]) for row in rows] == [
        ("угловой диван", "", "no"),
        ("диван кровать", "", "no"),
    ]
    assert all(row["similarity"] is None and row["number"] is None for row in rows)
