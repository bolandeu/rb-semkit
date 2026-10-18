"""The steps of every area of the library through the command line, on the small files of tests/steps/fixtures."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

import rb_semkit as sk
from rb_semkit import steps

from ..pipeline.runner import jsonl, semkit
from .areas import AREAS

FIXTURES = Path(__file__).parent / "fixtures"
# Public names of rb_semkit that are no steps, with the reason.
NOT_STEPS = {
    "CoreSpelling": "a spelling provider, the default of is-typo",
    "InvalidArguments": "the error",
    "LanguageTool": "a spelling provider",
    "LanguageToolSettings": "the settings of a spelling provider",
    "Lemmatizer": "the type of a lemmatizer",
    "Matcher": "the type of a matcher",
    "Misspelling": "the answer of a spelling provider",
    "SemtoolsLemmatizer": "the default lemmatizer",
    "SpellingProvider": "the type of a spelling provider",
    "extract": "a verb of a matcher: the steps extract-<matcher>",
    "find": "a verb of a matcher: the steps find-<matcher>",
    "levenshtein": "a distance of two strings, no table",
    "pipe": "the chain of verbs of the library",
    "remove": "a verb of a matcher: the steps remove-<matcher>",
    "word_list": "a list of words of the library",
}


def run(*args: str):
    """`semkit read <args>` in the folder of the fixtures; the result has the rows of stdout as `rows`."""
    result = semkit("read", *args)
    result.rows = jsonl(result.stdout) if result.exit_code == 0 else []
    return result


@pytest.fixture(autouse=True)
def in_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(FIXTURES)


def test_every_public_function_is_a_step_or_listed_as_none() -> None:
    functions = {inspect.unwrap(step.function) for area in steps.areas().values() for step in area}

    unlisted = [name for name in dir(sk) if name not in NOT_STEPS and getattr(sk, name) not in functions]

    assert unlisted == [], f"neither a step nor in NOT_STEPS: {unlisted}"


def test_the_not_a_step_list_names_only_public_names_or_future_ones() -> None:
    stepped = {inspect.unwrap(step.function).__name__ for area in steps.areas().values() for step in area}

    assert not stepped & NOT_STEPS.keys()


@pytest.mark.parametrize("area", sorted(AREAS))
def test_an_area_has_the_steps_written_out_for_it(area: str) -> None:
    assert sorted(step.name for step in steps.areas()[area]) == AREAS[area]


def test_chpu_writes_the_url_column() -> None:
    result = run("core.csv", "chpu", "--as", "url", "write", "-")

    assert result.exit_code == 0, result.output
    assert result.rows[0] == {"phrase": "Диван-кровать 2 м!", "url": "divan-krovat-2-m", "freq": 5}


def test_split_text_then_ngrams_of_lemmas_counts_with_docs_and_forms() -> None:
    result = run("--whole", "article.txt", "split-text", "ngrams", "-n", "1", "--lemmas", "write", "-")

    assert result.exit_code == 0, result.output
    top = result.rows[0]
    assert top["ngram"] == "диван"
    assert top["count"] == 4
    assert top["docs"] == 1
    assert top["forms"] == "диван, дивана"
    assert list(top) == ["ngram", "count", "docs", "forms"]


def test_wordforms_of_an_unknown_word_is_an_empty_table() -> None:
    result = run("phrases.csv", "wordforms", "тиктокер", "write", "-")

    assert result.exit_code == 0, result.output
    assert result.rows == []


def test_compare_grams_gives_the_table_of_the_verdicts() -> None:
    result = run("--whole", "mine.txt", "compare-grams", "--competitors", "competitors.csv", "write", "-")

    assert result.exit_code == 0, result.output
    assert list(result.rows[0]) == [
        "ngram", "docs", "docs_share", "median", "mean", "min", "max", "mine", "verdict", "need", "have", "add",
        "med_count",
    ]  # fmt: skip
    verdicts = {row["ngram"]: row["verdict"] for row in result.rows}
    assert verdicts["диван"] == "within"
    assert verdicts["кресло"] == "below"
    assert verdicts["кожаный"] == "above"


def test_cluster_serp_gives_each_phrase_a_cluster_and_a_center() -> None:
    result = run("serp.csv", "cluster-serp", "--method", "hard", "--common", "3", "write", "-")

    assert result.exit_code == 0, result.output
    clusters = {row["phrase"]: (row["cluster"], row["center"]) for row in result.rows}
    assert clusters["купить диван"][0] == clusters["диван купить"][0]
    assert clusters["кресло"][0] != clusters["купить диван"][0]
    assert clusters["кресло"][1] == "кресло"


def test_a_wrong_value_is_refused_with_the_step_the_option_and_the_allowed_values() -> None:
    result = semkit("--json", "read", str(FIXTURES / "core.csv"), "decline", "--case", "падеж", "write", "-")

    assert result.exit_code == 2
    message = json.loads(result.stdout)["error"]["message"]
    assert message.startswith("decline: Invalid value for '--case': 'падеж' is not one of 'nominative', 'genitive'")


def test_a_wrong_value_is_refused_before_the_input_is_read(tmp_path: Path) -> None:
    result = semkit("read", str(tmp_path / "missing.csv"), "decline", "--case", "падеж", "write", "-")

    assert result.exit_code == 2
    assert "decline: Invalid value for '--case'" in result.output


def test_coverage_counts_the_core_phrases_in_the_texts() -> None:
    result = run("phrases.csv", "coverage", "--against", "competitors.csv", "write", "-")

    assert result.exit_code == 0, result.output
    found = {row["phrase"]: row["count"] for row in result.rows}
    assert found == {"купить диван": 1, "кресло": 3, "диван недорого": 1}
    assert list(result.rows[0]) == ["phrase", "count", "docs", "density", "first"]


def test_compare_lists_gives_the_phrases_of_both() -> None:
    result = run("phrases.csv", "compare-lists", "--against", "second.csv", "--op", "both", "write", "-")

    assert result.exit_code == 0, result.output
    assert result.rows == [{"phrase": "купить диван"}, {"phrase": "кресло"}, {"phrase": "диван недорого"}]


def test_a_file_option_refuses_stdin() -> None:
    result = run("phrases.csv", "compare-lists", "--against", "-", "write", "-")

    assert result.exit_code == 2
    assert "compare-lists: --against -: '-' is the input of the pipeline." in result.output


def test_sentiment_reads_the_dictionary_file() -> None:
    result = run("phrases.csv", "sentiment", "--dictionary", "dictionary.csv", "write", "-")

    assert result.exit_code == 0, result.output
    assert "phrase_sentiment" in result.rows[0]


def test_replace_words_reads_the_pairs_file() -> None:
    result = run("phrases.csv", "replace-words", "--pairs", "pairs.csv", "write", "-")

    assert result.exit_code == 0, result.output
    assert [row["phrase"] for row in result.rows] == ["купить софа", "кресло", "софа недорого"]


def test_split_by_words_keeps_one_part() -> None:
    result = run(
        "phrases.csv", "split-by-words", "--good", "купить,диван", "--bad", "недорого", "--keep", "good", "write", "-"
    )

    assert result.exit_code == 0, result.output
    assert [row["phrase"] for row in result.rows] == ["купить диван"]


def test_markers_follow_the_matcher_steps() -> None:
    result = run("phrases.csv", "drop-markers", "--lists", "sale", "write", "-")

    assert result.exit_code == 0, result.output
    assert "купить диван" not in [row["phrase"] for row in result.rows]


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["change-case", "upper"], "КУПИТЬ ДИВАН"),
        (["insert", "--before", "+"], "+купить диван"),
        (["reverse", "--what", "words"], "диван купить"),
        (["sort-words"], "диван купить"),
        (["translit", "--to", "en"], "kupit divan"),
        (["lemmatize"], "купить диван"),
        (["decline", "genitive"], "купить дивана"),
        (["phonetic"], "купить диван"),
        (["match-type", "brackets"], "[купить диван]"),
        (["hash-text"], "b85908bb0ec978af96f2ce5a66e0b4a3"),
    ],
)  # fmt: skip
def test_a_change_step_rewrites_the_working_column(argv: list[str], expected: str) -> None:
    result = run("phrases.csv", *argv, "write", "-")

    assert result.exit_code == 0, result.output
    assert result.rows[0]["phrase"] == expected


def test_help_of_a_step_with_a_file_option_names_the_file() -> None:
    result = semkit("read", "IN", "coverage", "--help")

    assert result.exit_code == 0, result.output
    assert "--against" in result.output


# A command line for each step of the areas written out in tests/steps/areas.py: the file it reads and its words.
COMMANDS = {
    "add-minus-words": ["phrases.csv", "add-minus-words", "--synonyms", "synonyms.csv"],
    "basis-phrases": ["phrases.csv", "basis-phrases"],
    "bm25": ["phrases.csv", "bm25", "--query", "диван"],
    "change-case": ["phrases.csv", "change-case", "title"],
    "chpu": ["phrases.csv", "chpu"],
    "cluster-by-frequency": ["phrases.csv", "cluster-by-frequency", "--threshold", "1"],
    "compare-grams": ["--whole", "mine.txt", "compare-grams", "--competitors", "competitors.csv"],
    "compare-lists": ["phrases.csv", "compare-lists", "--against", "second.csv"],
    "compare-stats": ["--whole", "mine.txt", "compare-stats", "--competitors", "competitors.csv"],
    "coverage": ["phrases.csv", "coverage", "--against", "competitors.csv"],
    "coverage-meaning": ["core.csv", "coverage-meaning", "--text", "article.txt"],
    "decline": ["phrases.csv", "decline", "genitive"],
    "decline-adjective": ["phrases.csv", "decline-adjective", "genitive"],
    "decline-full-name": ["names.csv", "decline-full-name", "genitive"],
    "decline-noun": ["phrases.csv", "decline-noun", "genitive"],
    "drop-markers": ["phrases.csv", "drop-markers", "--lists", "sale"],
    "drop-minus-words": ["phrases.csv", "drop-minus-words"],
    "drop-modifiers": ["phrases.csv", "drop-modifiers"],
    "drop-ready-pattern": ["ready.csv", "drop-ready-pattern", "domain"],
    "extract-complements": ["ready.csv", "extract-complements"],
    "extract-markers": ["phrases.csv", "extract-markers", "--lists", "sale"],
    "extract-ready-pattern": ["ready.csv", "extract-ready-pattern", "domain"],
    "extract-utm": ["urls.csv", "extract-utm", "source"],
    "find-markers": ["phrases.csv", "find-markers", "--lists", "sale"],
    "find-ready-pattern": ["ready.csv", "find-ready-pattern", "domain"],
    "first-children": ["phrases.csv", "first-children", "--children", "диван"],
    "first-parents": ["phrases.csv", "first-parents", "--parents", "диван"],
    "fix-word-order": ["phrases.csv", "fix-word-order"],
    "guillemets": ["phrases.csv", "guillemets"],
    "headings": ["--column", "html", "pages.csv", "headings"],
    "hash-text": ["phrases.csv", "hash-text", "--algorithm", "sha256"],
    "insert": ["phrases.csv", "insert", "--after", "!"],
    "irrelevant-words": ["ready.csv", "irrelevant-words", "--word", "телефон"],
    "is-typo": ["phrases.csv", "is-typo"],
    "keep-markers": ["phrases.csv", "keep-markers", "--lists", "sale"],
    "keep-ready-pattern": ["ready.csv", "keep-ready-pattern", "domain"],
    "lemmatize": ["phrases.csv", "lemmatize"],
    "linear-combinations": ["phrases.csv", "linear-combinations"],
    "match-type": ["phrases.csv", "match-type", "quotes"],
    "move-words": ["phrases.csv", "move-words", "недорого"],
    "nearest-parents": ["phrases.csv", "nearest-parents", "--parents", "диван"],
    "ordered-pairs": ["phrases.csv", "ordered-pairs"],
    "parse-html": ["--column", "html", "pages.csv", "parse-html"],
    "part-of-speech": ["phrases.csv", "part-of-speech"],
    "permutations": ["phrases.csv", "permutations"],
    "phonetic": ["phrases.csv", "phonetic"],
    "remove-markers": ["phrases.csv", "remove-markers", "--lists", "sale"],
    "remove-phrase-end": ["ready.csv", "remove-phrase-end", "prepositions"],
    "remove-ready-pattern": ["ready.csv", "remove-ready-pattern", "domain"],
    "remove-utm": ["urls.csv", "remove-utm"],
    "replace-text": ["phrases.csv", "replace-text", "--pairs", "pairs.csv"],
    "replace-words": ["phrases.csv", "replace-words", "--pairs", "pairs.csv"],
    "reverse": ["phrases.csv", "reverse"],
    "sentiment": ["phrases.csv", "sentiment", "--dictionary", "dictionary.csv"],
    "similar-chars": ["phrases.csv", "similar-chars", "--to", "en"],
    "sort-words": ["phrases.csv", "sort-words"],
    "split-by-words": ["phrases.csv", "split-by-words", "--keep", "rest"],
    "split-digits": ["phrases.csv", "split-digits"],
    "split-text": ["phrases.csv", "split-text"],
    "summary": ["core.csv", "summary"],
    "switch-layout": ["phrases.csv", "switch-layout", "--to", "ru"],
    "synonyms": ["report.csv", "synonyms"],
    "text-stats": ["phrases.csv", "text-stats"],
    "translit": ["phrases.csv", "translit", "--to", "en"],
    "typo-correction": ["phrases.csv", "typo-correction"],
    "wordforms": ["phrases.csv", "wordforms", "диван"],
    "cluster-serp": ["serp.csv", "cluster-serp"],
    "cluster-meaning": ["core.csv", "cluster-meaning"],
    "ad-groups": ["core.csv", "ad-groups"],
    "synonym-candidates": ["core.csv", "synonym-candidates"],
    "assign-pages": ["core.csv", "assign-pages", "--pages", "page_texts.csv"],
    "classify-queries": ["phrases.csv", "classify-queries", "--against", "core.csv"],
    "off-topic": ["core.csv", "off-topic", "--threshold", "0.5"],
    "nearest": ["core.csv", "nearest", "--against", "page_texts.csv", "--top", "2"],
    "split-paragraphs": ["--whole", "article.txt", "split-paragraphs"],
}


def test_every_step_of_the_areas_has_a_command_line() -> None:
    assert sorted(COMMANDS) == sorted(name for names in AREAS.values() for name in names)


@pytest.mark.parametrize("step", sorted(COMMANDS))
def test_a_step_runs_on_its_fixture(step: str) -> None:
    result = run(*COMMANDS[step], "write", "-")

    assert result.exit_code == 0, result.output
    assert result.rows, "the step wrote no rows"


def test_text_stats_is_a_change_that_adds_its_metric_columns_after_the_working_column() -> None:
    result = run("core.csv", "text-stats", "write", "-")

    assert result.exit_code == 0, result.output
    assert len(result.rows) == 14
    first = result.rows[1]
    assert list(first)[:3] == ["phrase", "chars", "chars_no_spaces"] and list(first)[-1] == "freq"
    assert (first["phrase"], first["words"], first["freq"]) == ("купить диван", 2, 4)
    assert "text-stats: 14 → 14 rows" in result.stderr


def test_summary_reports_the_mean_and_median_of_the_numeric_columns() -> None:
    result = run("core.csv", "text-stats", "summary", "write", "-")

    assert result.exit_code == 0, result.output
    assert {row["column"] for row in result.rows} >= {"freq", "words", "chars"}
    assert list(result.rows[0]) == ["column", "count", "mean", "median", "min", "max"]


def test_summary_of_a_table_without_numbers_exits_2_naming_the_reason() -> None:
    result = run("texts.csv", "summary", "write", "-")

    assert result.exit_code == 2
    assert "no numeric column" in result.output


def test_compare_grams_per_text_names_the_columns_by_the_url_of_the_competitors(tmp_path: Path) -> None:
    competitors = tmp_path / "pages.csv"
    competitors.write_text("url,text\na.ru,диван стол\nb.ru,диван\n", encoding="utf-8")

    result = run("--whole", "mine.txt", "compare-grams", "--competitors", str(competitors), "--per-text", "write", "-")

    assert result.exit_code == 0, result.output
    assert list(result.rows[0])[-2:] == ["a.ru", "b.ru"]


def test_the_new_options_of_the_comparisons_reach_the_functions() -> None:
    grams = run(
        "--whole", "mine.txt", "compare-grams", "--competitors", "competitors.csv",
        "--norm", "mean", "--words", "1000", "--no-digits", "--exclude", "диван", "write", "-",
    )  # fmt: skip
    stats = run(
        "--whole", "mine.txt", "compare-stats", "--competitors", "competitors.csv", "--norm", "mean", "write", "-"
    )

    assert grams.exit_code == 0, grams.output
    assert "диван" not in {row["ngram"] for row in grams.rows}
    assert stats.exit_code == 0, stats.output
    assert "mean" in stats.rows[0]
