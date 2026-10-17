"""The --help contract: every command's help is complete, and any change to it shows up in review.

Help text is rendered from command docstrings and `typer.Option`/`Argument`
`help=` strings — it's the documentation agents and humans read, so it's
tested like an API:

- contract tests: every command (walked from the app's registry, so a new
  command is covered automatically) has a docstring with an
  `Example: semkit <command> ...` line, every parameter has non-empty help,
  every group has a description;
- snapshots: `<command> --help` is stored in tests/snapshots/help/<command>.txt
  (syrupy); a step of the pipeline in tests/snapshots/help/steps/<area>/<step>.txt, one folder per
  module of the step table, and its help is that of `semkit read IN <step>`. A changed help text fails until the snapshot is refreshed with
  `uv run pytest --snapshot-update`, which puts the new text in the diff.
  A new command fails until its snapshot exists; a removed one leaves an
  orphan file that fails too.
"""

from __future__ import annotations

import functools
import inspect
import typing
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
import typer
from syrupy.extensions.single_file import SingleFileSnapshotExtension, WriteMode
from typer.models import ParameterInfo
from typer.testing import CliRunner

from rb_semkit import output, steps
from rb_semkit.cli import app
from rb_semkit.pipeline.commands import step_options

CLI = "semkit"
SNAPSHOT_DIR = Path(__file__).parent / "snapshots" / "help"
# Fixed width and no colour so the rendering doesn't depend on the terminal running the tests.
HELP_ENV = {"COLUMNS": "100", "NO_COLOR": "1", "TERM": "dumb"}
PIPELINE = "read"  # its commands follow IN on the command line: `read IN <step> --help`
STEP_AREAS = {step.name: area for area, area_steps in steps.areas().items() for step in area_steps}


def _commands(group: typer.Typer, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Callable]]:
    for info in group.registered_commands:
        assert info.callback is not None
        name = info.name or getattr(info.callback, "__name__", "").replace("_", "-")
        yield (*prefix, name), info.callback
    for sub in group.registered_groups:
        assert sub.name is not None and sub.typer_instance is not None
        yield from _commands(sub.typer_instance, (*prefix, sub.name))


def _groups(group: typer.Typer, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], typer.Typer]]:
    for sub in group.registered_groups:
        assert sub.name is not None and sub.typer_instance is not None
        yield (*prefix, sub.name), sub.typer_instance
        yield from _groups(sub.typer_instance, (*prefix, sub.name))


COMMANDS = dict(_commands(app))
GROUPS = dict(_groups(app))
HELP_PAGES = sorted([*COMMANDS, *GROUPS])


def _slug(path: tuple[str, ...]) -> str:
    return "-".join(path)


def help_argv(path: tuple[str, ...]) -> list[str]:
    """The command line that shows the help of `path`."""
    in_pipeline = path[0] == PIPELINE and len(path) > 1
    return [PIPELINE, "IN", *path[1:], "--help"] if in_pipeline else [*path, "--help"]


def _snapshot_file(path: tuple[str, ...]) -> Path:
    """Where the help of `path` is kept, without the extension."""
    if path[0] == PIPELINE and path[-1] in STEP_AREAS:
        return SNAPSHOT_DIR / "steps" / STEP_AREAS[path[-1]] / path[-1]
    return SNAPSHOT_DIR / _slug(path)


def _render_help(path: tuple[str, ...]) -> str:
    result = CliRunner().invoke(app, help_argv(path), env=HELP_ENV, prog_name=CLI)
    assert result.exit_code == 0, result.output
    # Trailing padding isn't content; keeping it out keeps the diffs readable.
    return "\n".join(line.rstrip() for line in result.output.splitlines()) + "\n"


class HelpSnapshot(SingleFileSnapshotExtension):
    """One plain-text file per help page: tests/snapshots/help/<command>.txt."""

    _write_mode = WriteMode.TEXT
    file_extension = "txt"

    @classmethod
    def dirname(cls, *, test_location) -> str:
        return str(SNAPSHOT_DIR)

    @classmethod
    def get_snapshot_name(cls, *, test_location, index=0) -> str:
        return str(index)


@functools.cache
def _snapshot_in(folder: Path) -> type[HelpSnapshot]:
    """The snapshot extension of the help pages kept in `folder`."""
    return type(
        HelpSnapshot.__name__, (HelpSnapshot,), {"dirname": classmethod(lambda cls, *, test_location: str(folder))}
    )


@pytest.mark.parametrize("path", HELP_PAGES, ids=_slug)
def test_help_snapshot(path: tuple[str, ...], snapshot) -> None:
    file = _snapshot_file(path)
    assert _render_help(path) == snapshot(extension_class=_snapshot_in(file.parent), name=file.name)


def test_no_orphan_help_snapshots() -> None:
    stored = {p.with_suffix("") for p in SNAPSHOT_DIR.rglob("*.txt")}
    expected = {_snapshot_file(path) for path in HELP_PAGES}
    assert stored <= expected, f"snapshots for commands that no longer exist: {sorted(stored - expected)}"


@pytest.mark.parametrize("path", sorted(COMMANDS), ids=_slug)
def test_command_docstring_has_summary_and_example(path: tuple[str, ...]) -> None:
    doc = inspect.getdoc(COMMANDS[path]) or ""
    assert doc.strip(), f"`{_slug(path)}` has no docstring — it is the command's --help text"
    invocation = f"{CLI} {' '.join(path)}"
    examples = [line for line in doc.splitlines() if line.startswith("Example:")]
    if path[0] == PIPELINE:  # a step stands after IN: `semkit read core.csv <step> ... write out.csv`
        assert any(f"{CLI} {PIPELINE} " in line and f" {path[-1]} " in line for line in examples), (
            f"`{_slug(path)}` docstring needs an `Example: {{cli}} {PIPELINE} IN {path[-1]} ...` line"
        )
        return
    assert any(invocation in line for line in examples), (
        f"`{_slug(path)}` docstring needs an `Example: {{cli}} {' '.join(path)} ...` line"
    )


@pytest.mark.parametrize("path", sorted(COMMANDS), ids=_slug)
def test_every_command_is_guarded(path: tuple[str, ...]) -> None:
    # output.guard gives the JSON error envelope, local --json/--quiet and the {cli} substitution in help.
    assert output.is_guarded(COMMANDS[path]), f"`{_slug(path)}` must be wrapped in @output.guard"


@pytest.mark.parametrize("path", sorted(COMMANDS), ids=_slug)
def test_every_parameter_has_help(path: tuple[str, ...]) -> None:
    callback = inspect.unwrap(COMMANDS[path])
    hints = typing.get_type_hints(callback, include_extras=True)
    for name, param in inspect.signature(callback).parameters.items():
        hint = hints.get(name)
        if hint is typer.Context:
            continue
        infos = [m for m in getattr(hint, "__metadata__", ()) if isinstance(m, ParameterInfo)]
        if isinstance(param.default, ParameterInfo):
            infos.append(param.default)
        assert infos, f"`{_slug(path)}` parameter `{name}` must be a typer.Option/Argument with help="
        assert all((info.help or "").strip() for info in infos), f"`{_slug(path)}` parameter `{name}` has no help"


@pytest.mark.parametrize("path", sorted(GROUPS), ids=_slug)
def test_every_group_has_help(path: tuple[str, ...]) -> None:
    assert (GROUPS[path].info.help or "").strip(), f"group `{_slug(path)}` has no description"


def test_help_keeps_brackets() -> None:
    """Typer renders help as rich markup, which drops `[...]`; output.guard escapes docstrings."""

    def cmd(ctx: typer.Context) -> None:
        """Declared in [[tool.rb.external]], see [x].

        Example: {cli} cmd
        """

    probe = typer.Typer()
    probe.command("cmd")(output.guard(cmd))
    probe.command("other")(output.guard(cmd))
    result = CliRunner().invoke(probe, ["cmd", "--help"], env=HELP_ENV)
    assert "[[tool.rb.external]], see [x]." in result.output


def _step(name: str) -> steps.Step:
    return next(step for area in steps.areas().values() for step in area if step.name == name)


def _option_help(step: str, option: str) -> str:
    return next(o.help for o in step_options(_step(step).function) if o.name == option)


def test_the_help_of_an_option_holds_only_its_own_text() -> None:
    assert _option_help("coverage", "mode").endswith("a piece with them is one occurrence.")
    assert "core" not in _option_help("coverage", "mode")
    assert _option_help("coverage", "text_column") == "the column of the texts."
    assert _option_help("split-by-words", "bad").startswith("a phrase with any of these words is bad. Items:")
    assert _option_help("split-by-words", "good").startswith("a phrase that is not bad and has only these words")
    assert "Every other phrase" not in _option_help("split-by-words", "bad")
    lists = _option_help("find-markers", "lists")
    assert (
        lists.startswith("the marker lists, comma-separated: a bundled one by its name (geo)") and "user:" not in lists
    )
    assert "A word glued" not in _option_help("find-markers", "with_prepositions")
    assert _option_help("remove-edges", "start") == "characters cut from the start of a word, any run of them."
    assert "inside a word" not in _option_help("remove-edges", "end")


def test_the_bullets_of_a_docstring_stay_lines_of_the_help() -> None:
    result = CliRunner().invoke(app, help_argv((PIPELINE, "change-case")), env=HELP_ENV, prog_name=CLI)

    lines = [line.strip() for line in result.output.splitlines()]
    assert '- "lower", "upper": the whole phrase;' in lines
    starts = [line for line in lines if line.startswith("- ")]
    assert len(starts) == 8
    assert any(line.startswith('- "toponyms": the place names') for line in starts)


def test_arguments_named_with_a_slash_each_hold_their_own_text() -> None:
    assert _option_help("find-word-position", "nth") == "the N-th word."
    assert _option_help("find-word-position", "first").startswith("the first or last N words.")
