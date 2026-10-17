"""The ten runs of the end-to-end check on a real core and a real text, through the CLI, against `recount`.

Fixtures (tests/e2e/fixtures):
- sofa_core.csv: the first 1000 Bukvarix phrases for «купить диван», with the Moscow exact frequency;
- svh_core.csv: 204 phrases for «склад временного хранения»; svh.txt: the text of the page
  https://ost-term.ru/tamozhennoe-oformlenie/sklad-vremennogo-hraneniya, fetched for the check of v0.1.20;
- serp.csv: a synthetic SERP table of the sofa phrases (phrase, position, url), top 10 each;
- minus_words.txt, minus_phrases.txt: a list of words and a list of phrases of a user.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from ..pipeline.runner import jsonl, semkit
from . import recount

SOFA = "sofa_core.csv"
FREQ = "freq_msk_exact"
COMMON = 3
TOP = 10


@pytest.fixture(autouse=True)
def in_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(recount.FIXTURES)


def rows_of(*args: str) -> list[dict]:
    """The rows `semkit read ARGS write -` writes; the run must succeed."""
    result = semkit("read", *args, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def sofa_phrases() -> list[str]:
    return [row["phrase"] for row in recount.rows(SOFA)]


def test_the_dictionary_lemmas_of_the_recount_differ_from_pymorphy3_as_written() -> None:
    differing = {word: recount.pymorphy_lemma(word) for word in recount.DICTIONARY_LEMMAS}

    assert differing == {word: lemmas[1] for word, lemmas in recount.DICTIONARY_LEMMAS.items()}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_run_1_ngrams_with_weight(n: int) -> None:
    counted = rows_of(SOFA, "ngrams", "-n", str(n), "--weight", FREQ)

    assert counted == recount.ngrams(recount.rows(SOFA), "phrase", FREQ, n)


@pytest.mark.parametrize("lemmas", [[], ["--lemmas"]], ids=["forms", "lemmas"])
def test_run_2_drop_words_by_a_list(lemmas: list[str]) -> None:
    kept = rows_of(SOFA, "drop-words", "@minus_words.txt", *lemmas)

    expected = recount.kept_by_words(sofa_phrases(), recount.lines("minus_words.txt"), by_lemmas=bool(lemmas))
    assert [row["phrase"] for row in kept] == expected
    assert len(expected) < 1000


@pytest.mark.parametrize("lemmas", [[], ["--lemmas"]], ids=["forms", "lemmas"])
def test_run_3_drop_phrases_by_a_list(lemmas: list[str]) -> None:
    kept = rows_of(SOFA, "drop-phrases", "@minus_phrases.txt", *lemmas)

    expected = recount.kept_by_phrases(sofa_phrases(), recount.lines("minus_phrases.txt"), by_lemmas=bool(lemmas))
    assert [row["phrase"] for row in kept] == expected
    assert len(expected) < 1000


@pytest.mark.parametrize(
    ("step", "listed"), [("drop-words", "@minus_words.txt"), ("drop-phrases", "@minus_phrases.txt")]
)
def test_run_2_and_3_by_lemmas_drop_more_than_by_forms(step: str, listed: str) -> None:
    forms = rows_of(SOFA, step, listed)
    lemmas = rows_of(SOFA, step, listed, "--lemmas")

    assert len(lemmas) < len(forms)


def test_run_4_dupes_by_lemmas() -> None:
    marked = rows_of(SOFA, "dupes", "--kind", "lemmas", "--action", "mark_except_first")
    dropped = rows_of(SOFA, "dupes", "--kind", "lemmas", "--action", "drop")

    expected = recount.lemma_duplicates(sofa_phrases())
    assert [row["phrase_dupes"] for row in marked] == expected
    assert [row["phrase"] for row in dropped] == [
        p for p, dupe in zip(sofa_phrases(), expected, strict=True) if not dupe
    ]
    assert any(expected)


def _clusters(method: str) -> tuple[dict[str, frozenset[str]], dict[int, list[dict]]]:
    """The tops of the SERP and the rows of each cluster `cluster-serp --method METHOD` gives."""
    found = rows_of("serp.csv", "cluster-serp", "--method", method, "--common", str(COMMON), "--top", str(TOP))
    tops = recount.tops(recount.rows("serp.csv"), TOP)
    assert sorted(row["phrase"] for row in found) == sorted(tops)
    clusters: dict[int, list[dict]] = {}
    for row in found:
        clusters.setdefault(row["cluster"], []).append(row)
    sizes = [len(clusters[number]) for number in sorted(clusters)]
    assert sorted(clusters) == list(range(1, len(clusters) + 1))
    assert sizes == sorted(sizes, reverse=True)
    for members in clusters.values():
        center = members[0]["center"]
        assert {row["center"] for row in members} == {center}
        assert members[0]["phrase"] == center
        for row in members:
            expected = (
                len(tops[center]) if row["phrase"] == center else recount.shared(tops[row["phrase"]], tops[center])
            )
            assert row["common"] == expected, row
    return tops, clusters


def test_run_5_cluster_serp_soft() -> None:
    tops, clusters = _clusters("soft")

    centers = [members[0]["center"] for members in clusters.values()]
    for members in clusters.values():
        assert all(row["common"] >= COMMON for row in members), members
    for first, second in recount.pairs(centers):
        assert recount.shared(tops[first], tops[second]) < COMMON, (first, second)
    assert len(clusters) < len(tops)


def test_run_6_cluster_serp_hard() -> None:
    tops, clusters = _clusters("hard")

    for members in clusters.values():
        for first, second in recount.pairs([row["phrase"] for row in members]):
            assert recount.shared(tops[first], tops[second]) >= COMMON, (first, second)
    assert len(clusters) < len(tops)


def test_run_7_coverage_exact(tmp_path: Path) -> None:
    texts = tmp_path / "texts.jsonl"
    texts.write_text(json.dumps({"text": recount.text("svh.txt")}, ensure_ascii=False) + "\n", encoding="utf-8")

    found = rows_of("svh_core.csv", "coverage", "--against", str(texts), "--mode", "exact")

    phrases = [row["phrase"] for row in recount.rows("svh_core.csv")]
    expected = recount.coverage(phrases, recount.text("svh.txt"))
    assert found == expected
    assert any(row["count"] for row in expected)


def test_run_8_text_stats_chars_and_words() -> None:
    [stats] = rows_of("--whole", "svh.txt", "text-stats")

    expected = recount.char_stats(recount.text("svh.txt"))
    assert {name: stats[name] for name in expected} == expected


TABLE = pd.DataFrame(
    {
        "phrase": ["купить диван", "диван, угловой", "2024", ""],
        "freq": pd.array([10, 2, None, 7], dtype="Int64"),
        "share": [0.5, 1.25, 0.0, 2.0],
    }
)
ROWS = [
    {"phrase": "купить диван", "freq": 10, "share": 0.5},
    {"phrase": "диван, угловой", "freq": 2, "share": 1.25},
    {"phrase": "2024", "freq": None, "share": 0.0},
    {"phrase": "", "freq": 7, "share": 2.0},
]


@pytest.mark.parametrize("extension", ["csv", "xlsx", "parquet", "json", "jsonl"])
def test_run_9_the_round_trip_of_a_format(extension: str, tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    source.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in ROWS), encoding="utf-8")
    written = tmp_path / f"core.{extension}"

    assert semkit("read", str(source), "write", str(written)).exit_code == 0

    assert rows_of(str(written)) == ROWS


DECLINED = {
    ("decline", "accusative"): {
        "купить кожаный диван": "купить кожаный диван",
        "рыжий кот": "рыжего кота",
        "большая скидка": "большую скидку",
    },
    ("decline", "genitive"): {
        "угловые диваны": "угловых диванов",
        "большая скидка": "большой скидки",
        "диван-кровать": "дивана-кровати",
        "кожаный диван": "кожаного дивана",
    },
    ("decline-noun", "accusative"): {"диван": "диван", "кот": "кота", "книга": "книгу"},
}
LEMMAS = {
    "кафе": "кафе", "купе": "купе", "мини": "мини", "шириной": "ширина", "спину": "спина", "экокожи": "экокожа",
    "подростка": "подросток", "аскона": "аскона", "ножках": "ножка", "петушках": "петушки", "донецке": "донецк",
    "вещей": "вещь", "временного": "временный", "рус": "рус", "раскладывается": "раскладываться",
    "раскладывающийся": "раскладывающийся", "вперед": "вперед",
}  # fmt: skip


def _phrases(tmp_path: Path, phrases: list[str]) -> str:
    path = tmp_path / "phrases.csv"
    pd.DataFrame({"phrase": phrases}).to_csv(path, index=False)
    return str(path)


@pytest.mark.parametrize(("step", "case"), sorted(DECLINED))
def test_run_10_declension_of_the_morphology_task(step: str, case: str, tmp_path: Path) -> None:
    pairs = DECLINED[(step, case)]

    declined = rows_of(_phrases(tmp_path, list(pairs)), step, case, "--as", "declined")

    assert {row["phrase"]: row["declined"] for row in declined} == pairs


def test_run_10_lemmas_of_the_morphology_task(tmp_path: Path) -> None:
    lemmatized = rows_of(_phrases(tmp_path, list(LEMMAS)), "lemmatize", "--as", "lemma")

    assert {row["phrase"]: row["lemma"] for row in lemmatized} == LEMMAS
