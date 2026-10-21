"""`semkit run NAME`: a named workflow of semkit's own steps, bundled or in the project, run as one read pipeline.

The steps by meaning get the test encoder and the thesaurus of the shared fixtures (растаможка and таможенное
оформление are synonyms), so the bundled intent-synonyms runs offline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import typer.rich_utils
from typer.testing import CliRunner

from rb_semkit.cli import app
from rb_semkit.core import services
from rb_semkit.core.vectors import encoder
from rb_semkit.core.vectors.registry import Model

from ..conftest import WordEncoder
from ..pipeline.runner import jsonl, semkit

PHRASE = "растаможка авто"
OTHER = "таможенное оформление импорта"
DESCRIPTION = (
    "Phrase synonyms of one intent: every variation of the phrase by the thesaurus, scored by meaning against it."
)
HELP_ENV = {"COLUMNS": "200", "NO_COLOR": "1", "TERM": "dumb"}


@pytest.fixture(autouse=True)
def _plain_help(monkeypatch: pytest.MonkeyPatch) -> None:
    """Typer reads GITHUB_ACTIONS / FORCE_COLOR / PY_COLORS once, at import, and then forces terminal output (CI)."""
    monkeypatch.setattr(typer.rich_utils, "FORCE_TERMINAL", False)


def _chain(text: str, *, threshold: str = "0", model: str = "bge-m3", top: tuple[str, ...] = ()) -> list[str]:
    """The steps of intent-synonyms written out for read."""
    return [
        *("synonym-candidates", "--all", "--source", "ruwordnet", "--as-slots", *top),
        "linear-combinations",
        "agree",
        *("nearest", "--to", text, "--threshold", threshold, "--model", model),
        *("use-column", "match"),
        *("drop-cells", "empty"),
        *("sort-rows", "--by", "similarity", "--desc"),
    ]


def _read(text: str, **options) -> list[dict]:
    result = semkit("read", "--text", text, *_chain(text, **options), "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def _run(*args: str, project: Path | None = None) -> list[dict]:
    result = semkit(*(("--project", str(project)) if project else ()), "run", *args, "write", "-")
    assert result.exit_code == 0, result.output
    return jsonl(result.stdout)


def _refused(*args: str) -> dict:
    result = semkit("--json", *args)
    assert result.exit_code == 2, result.output
    return json.loads(result.stdout)["error"]


def _help(*args: str) -> list[str]:
    """The lines of a help as the terminal shows it, without the frames of its panels."""
    result = CliRunner().invoke(app, [*args, "--help"], env=HELP_ENV, prog_name="semkit")
    assert result.exit_code == 0, result.output
    return [line.strip(" │") for line in result.stdout.splitlines()]


def _with_input(text: str, rows: list[dict]) -> list[dict]:
    return [{"input": text, **row} for row in rows]


@pytest.fixture
def models_opened(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """The names of the encoders the steps by meaning open, in order."""
    names: list[str] = []

    def opened(model: Model, start: Path) -> WordEncoder:
        names.append(model.name)
        return WordEncoder()

    monkeypatch.setattr(encoder, "encoder_for", opened)
    return names


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    services.init_project(root, "demo")
    (root / ".rb_semkit" / "workflows").mkdir()
    return root


def _workflow(project: Path, name: str, text: str) -> Path:
    path = project / ".rb_semkit" / "workflows" / f"{name}.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_intent_synonyms_equals_the_chain_written_out_in_read_and_every_row_has_a_match(models_opened) -> None:
    rows = _run("intent-synonyms", "--text", PHRASE)

    assert rows == _with_input(PHRASE, _read(PHRASE))
    assert rows and all(row["match"] for row in rows)


def test_without_set_every_combination_is_there_the_input_phrase_first_by_similarity_from_the_highest() -> None:
    slots = semkit("read", "--text", PHRASE, *_chain(PHRASE)[:7], "write", "-")
    combinations = {row["phrase"] for row in jsonl(slots.stdout)}

    rows = _run("intent-synonyms", "--text", PHRASE)

    assert combinations == {"растаможка авто", "таможенное оформление авто"}
    assert {row["phrase"] for row in rows} == combinations
    assert rows[0]["phrase"] == PHRASE
    similarities = [row["similarity"] for row in rows]
    assert similarities == sorted(similarities, reverse=True)


def test_the_defaults_of_every_parameter_are_taken(models_opened: list[str]) -> None:
    rows = _run("intent-synonyms", "--text", PHRASE)

    assert rows == _with_input(PHRASE, _read(PHRASE, threshold="0", model="bge-m3"))
    assert set(models_opened) == {"bge-m3"}


def test_set_threshold_reaches_the_nearest_step() -> None:
    rows = _run("intent-synonyms", "--text", PHRASE, "--set", "threshold=0.9")

    assert rows == _with_input(PHRASE, _read(PHRASE, threshold="0.9"))
    assert [row["phrase"] for row in rows] == [PHRASE]


def test_set_step_option_replaces_or_adds_the_option_of_that_step(models_opened: list[str]) -> None:
    rows = _run(
        "intent-synonyms", "--text", PHRASE, "--set", "nearest.model=e5-small", "--set", "synonym-candidates.top=20"
    )

    assert rows == _with_input(PHRASE, _read(PHRASE, model="e5-small", top=("--top", "20")))
    assert models_opened[0] == "e5-small"
    refused = _refused("run", "intent-synonyms", "--text", PHRASE, "--set", "synonym-candidates.top=0")
    assert refused["message"].startswith("synonym-candidates: --top")


@pytest.mark.parametrize("setting", ["nosuchstep.x=1", "nearest.nosuch=1"])
def test_set_of_a_step_or_option_the_workflow_lacks_is_refused_naming_the_steps_and_their_options(setting) -> None:
    error = _refused("run", "intent-synonyms", "--text", PHRASE, "--set", setting)

    assert error["message"].startswith(f"run intent-synonyms: --set {setting}:")
    listed = error["action"]
    for step in ("synonym-candidates", "linear-combinations", "nearest", "sort-rows"):
        assert f"{step} (" in listed
    assert "nearest (against, against-column, top, threshold, to, model)" in listed


def test_set_of_an_unknown_parameter_is_refused_naming_the_parameters() -> None:
    error = _refused("run", "intent-synonyms", "--text", PHRASE, "--set", "nosuch=1")

    assert error["message"] == "run intent-synonyms: --set nosuch=1: the workflow has no parameter nosuch."
    assert "threshold, model, source" in error["action"]


def test_two_phrases_give_a_first_column_input_and_the_part_of_each_phrase_as_run_alone() -> None:
    alone = [*_run("intent-synonyms", "--text", PHRASE), *_run("intent-synonyms", "--text", OTHER)]

    rows = _run("intent-synonyms", "--text", PHRASE, "--text", OTHER)

    assert rows == alone
    assert list(rows[0]) == ["input", "phrase", "match", "rank", "similarity"]
    assert [row["input"] for row in rows] == [PHRASE] * 2 + [OTHER] * 2


def test_a_file_of_phrases_gives_the_same_table_as_the_phrases_given_with_text(tmp_path: Path) -> None:
    source = tmp_path / "in.csv"
    pd.DataFrame({"phrase": [PHRASE, OTHER]}).to_csv(source, index=False)

    rows = _run("intent-synonyms", str(source))

    assert rows == _run("intent-synonyms", "--text", PHRASE, "--text", OTHER)


def test_without_write_the_result_is_a_table_on_stdout_as_jsonl_when_not_a_terminal() -> None:
    result = semkit("run", "intent-synonyms", "--text", PHRASE)

    assert result.exit_code == 0, result.output
    assert jsonl(result.stdout) == _run("intent-synonyms", "--text", PHRASE)


def test_write_out_writes_the_file(tmp_path: Path) -> None:
    out = tmp_path / "out.csv"

    result = semkit("run", "intent-synonyms", "--text", PHRASE, "write", str(out))

    assert result.exit_code == 0, result.output
    assert pd.read_csv(out).to_dict("records") == _run("intent-synonyms", "--text", PHRASE)


def test_a_workflow_without_per_phrase_runs_once_over_the_whole_table(project: Path) -> None:
    _workflow(project, "upper", 'description = "Upper case."\nsteps = """\nchange-case --kind {case}\n"""\n'
              '[parameters.case]\ndefault = "upper"\nhelp = "the case"\n')  # fmt: skip

    rows = _run("upper", "--text", "a b", "--text", "c", project=project)

    assert rows == [{"phrase": "A B"}, {"phrase": "C"}]


def test_set_replaces_an_option_the_step_takes_positionally(project: Path) -> None:
    _workflow(project, "lower", 'description = "Lower case."\nsteps = "change-case lower"\n')

    rows = _run("lower", "--text", "Ab", "--set", "change-case.kind=upper", project=project)

    assert rows == [{"phrase": "AB"}]


def test_a_project_workflow_overrides_the_bundled_one_of_the_same_name(project: Path) -> None:
    _workflow(project, "intent-synonyms", 'description = "Project one."\nsteps = """\nchange-case upper\n"""\n')

    assert _run("intent-synonyms", "--text", PHRASE, project=project) == [{"phrase": "РАСТАМОЖКА АВТО"}]


def test_a_file_in_the_former_scenarios_folder_still_runs_and_workflows_wins_over_it(project: Path) -> None:
    old = project / ".rb_semkit" / "scenarios"
    old.mkdir()
    (old / "only-old.toml").write_text('description = "Old."\nsteps = "change-case upper"\n', encoding="utf-8")
    (old / "both.toml").write_text('description = "Old."\nsteps = "change-case lower"\n', encoding="utf-8")
    _workflow(project, "both", 'description = "New."\nsteps = "change-case upper"\n')

    assert _run("only-old", "--text", "ab", project=project) == [{"phrase": "AB"}]
    assert _run("both", "--text", "ab", project=project) == [{"phrase": "AB"}]


def test_a_parameter_without_a_default_is_refused_naming_the_file_and_the_parameter(project: Path) -> None:
    path = _workflow(
        project, "broken", 'description = "x"\nsteps = "change-case upper"\n[parameters.mode]\nhelp = "m"\n'
    )

    error = _refused("--project", str(project), "run", "broken", "--text", PHRASE)

    assert error["message"] == f"{path}: the parameter mode has no default."


@pytest.mark.parametrize(
    ("line", "found"),
    [("no-such-step --x 1", "no step no-such-step"), ("change-case --nosuch 1", "No such option: --nosuch")],
)
def test_a_step_or_option_that_does_not_exist_is_refused_naming_the_file_and_the_line(project, line, found) -> None:
    path = _workflow(project, "broken", f'description = "x"\nsteps = """\nchange-case upper\n{line}\n"""\n')

    for args in (("run", "--help"), ("run", "broken", "--text", PHRASE)):
        error = _refused("--project", str(project), *args)
        assert error["message"].startswith(f"{path}:4: {line}: ")
        assert found in error["message"]


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("description = ", "no TOML: "),
        ('steps = "agree"\n', "a workflow needs the texts description and steps."),
        ('description = "x"\nsteps = "change-case {case}"\n', "change-case {case}: {case} is no parameter;"),
        ('description = "x"\nsteps = "nearest --to {text}"\n', "nearest --to {text}: {text} is the phrase of"),
        ('description = "x"\nsteps = "change-case \'upper"\n', "change-case 'upper: No closing quotation."),
    ],
)
def test_a_file_that_is_no_workflow_is_refused_naming_the_file(project: Path, text: str, reason: str) -> None:
    path = _workflow(project, "broken", text)

    error = _refused("--project", str(project), "run", "broken", "--text", PHRASE)

    assert error["message"].startswith(str(path)) and reason in error["message"]


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (("a.csv", "b.csv"), "run intent-synonyms: a.csv b.csv: a workflow runs as"),
        (("--text", PHRASE, "write"), "run intent-synonyms: write: a workflow runs as"),
        (("--text", PHRASE, "--set", "threshold"), "run intent-synonyms: --set threshold: no '='."),
    ],
)
def test_a_command_line_of_another_shape_is_refused(args: tuple[str, ...], message: str) -> None:
    error = _refused("run", "intent-synonyms", *args)

    assert error["message"].startswith(message)


def test_run_help_lists_the_workflows_with_their_descriptions() -> None:
    rows = [line.split(None, 1) for line in _help("run")]

    assert ["intent-synonyms", DESCRIPTION] in rows


def test_the_help_of_a_workflow_shows_its_parameters_with_defaults_and_its_steps() -> None:
    lines = _help("run", "intent-synonyms")

    for parameter in ("- threshold (default 0):", "- model (default bge-m3):", "- source (default ruwordnet):"):
        assert any(line.startswith(parameter) for line in lines), parameter
    steps = [
        "synonym-candidates --all --source {source} --as-slots",
        "linear-combinations",
        "agree",
        "nearest --to {text} --threshold {threshold} --model {model}",
        "use-column match",
        "drop-cells empty",
        "sort-rows --by similarity --desc",
    ]
    assert [line for line in lines if line.removeprefix("- ") in steps] == [f"- {step}" for step in steps]


def test_docs_lists_each_workflow_under_run(tmp_path: Path) -> None:
    out = tmp_path / "docs.json"
    assert semkit("docs", "--out", str(out)).exit_code == 0

    document = json.loads(out.read_text(encoding="utf-8"))
    run = next(command for command in document["commands"] if command["name"] == "run")
    workflow = next(command for command in run["commands"] if command["name"] == "intent-synonyms")
    assert workflow["description"].startswith(f"{DESCRIPTION}\n\nParameters, set with --set NAME=VALUE:\n")
