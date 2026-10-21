"""The --help contract: every command's help is complete, and any change to it shows up in review.

Help text is rendered from command docstrings and `typer.Option`/`Argument`
`help=` strings — it's the documentation agents and humans read, so it's
tested like an API:

- the help standard on every command, walked from the app's
  registry so a new command is covered automatically: a one-line summary, one to three `Example:` lines that
  parse against the command tree, help on every parameter, no parameter help repeated in the description.
  A command not yet brought to the standard is listed in tests/help_allowlist.txt (one command path per line,
  `#` comments); a failing run prints the failing commands as lines ready to paste there. Every group has a
  description;
- snapshots: `<command> --help` is stored in tests/snapshots/help/<command>.txt
  (syrupy); a step of the pipeline in tests/snapshots/help/steps/<area>/<step>.txt, one folder per
  module of the step table, and its help is that of `semkit read IN <step>`. A changed help text fails until the snapshot is refreshed with
  `uv run pytest --snapshot-update`, which puts the new text in the diff.
  A new command fails until its snapshot exists; a removed one leaves an
  orphan file that fails too.
- the Commands panel of `read --help` lists the steps, so it is not in the snapshot of `read` (a new step would change
  it); a test checks the panel against the registered steps instead.
"""

from __future__ import annotations

import functools
import inspect
import shlex
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
import typer
import typer.rich_utils
from syrupy.extensions.single_file import SingleFileSnapshotExtension, WriteMode
from typer.testing import CliRunner

from rb_semkit import output, steps
from rb_semkit.cli import app
from rb_semkit.core import docs, opencli
from rb_semkit.pipeline.commands import step_options
from rb_semkit.steps.docs_hook import WRITE

CLI = "semkit"
SNAPSHOT_DIR = Path(__file__).parent / "snapshots" / "help"
ALLOWLIST = Path(__file__).parent / "help_allowlist.txt"
MAX_EXAMPLES = 3
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


@pytest.fixture(autouse=True)
def _plain_help(monkeypatch: pytest.MonkeyPatch) -> None:
    """Typer reads GITHUB_ACTIONS / FORCE_COLOR / PY_COLORS once, at import, and then forces terminal output (CI)."""
    monkeypatch.setattr(typer.rich_utils, "FORCE_TERMINAL", False)


def _slug(path: tuple[str, ...]) -> str:
    return "-".join(path)


def help_argv(path: tuple[str, ...]) -> list[str]:
    """The command line that shows the help of `path`."""
    in_pipeline = path[0] == PIPELINE and len(path) > 1
    return [PIPELINE, "IN", *path[1:], "--help"] if in_pipeline else [*path, "--help"]


def snapshot_name(path: tuple[str, ...]) -> Path:
    """Where the snapshot of `path` is kept in a snapshot folder, without the extension: a step in its area's folder."""
    if path[0] == PIPELINE and path[-1] in STEP_AREAS:
        return Path("steps") / STEP_AREAS[path[-1]] / path[-1]
    return Path(_slug(path))


def _render_help(path: tuple[str, ...]) -> str:
    result = CliRunner().invoke(app, help_argv(path), env=HELP_ENV, prog_name=CLI)
    assert result.exit_code == 0, result.output
    # Trailing padding isn't content; keeping it out keeps the diffs readable.
    lines = [line.rstrip() for line in result.output.splitlines()]
    return "\n".join(_without_commands_panel(lines) if path == (PIPELINE,) else lines) + "\n"


def _commands_panel(lines: list[str]) -> range:
    """The lines of the Commands panel, its frame included."""
    start = next(number for number, line in enumerate(lines) if line.startswith("╭─ Commands"))
    return range(start, next(number for number in range(start, len(lines)) if lines[number].startswith("╰")) + 1)


def _without_commands_panel(lines: list[str]) -> list[str]:
    panel = _commands_panel(lines)
    return [line for number, line in enumerate(lines) if number not in panel]


@functools.cache
def snapshot_in(folder: Path, extension: str) -> type[SingleFileSnapshotExtension]:
    """The snapshot extension of the files `.<extension>` kept in `folder`, one file per snapshot."""
    return type(
        "FolderSnapshot",
        (SingleFileSnapshotExtension,),
        {
            "_write_mode": WriteMode.TEXT,
            "file_extension": extension,
            "dirname": classmethod(lambda cls, *, test_location: str(folder)),
            "get_snapshot_name": classmethod(lambda cls, *, test_location, index=0: str(index)),
        },
    )


@pytest.mark.parametrize("path", HELP_PAGES, ids=_slug)
def test_help_snapshot(path: tuple[str, ...], snapshot) -> None:
    file = SNAPSHOT_DIR / snapshot_name(path)
    assert _render_help(path) == snapshot(extension_class=snapshot_in(file.parent, "txt"), name=file.name)


def test_help_is_the_same_in_ci(same_in_ci: Callable[[str], None]) -> None:
    same_in_ci("test_help_snapshot")


def test_no_orphan_help_snapshots() -> None:
    stored = {p.relative_to(SNAPSHOT_DIR).with_suffix("") for p in SNAPSHOT_DIR.rglob("*.txt")}
    expected = {snapshot_name(path) for path in HELP_PAGES}
    assert stored <= expected, (
        f"snapshots for commands that no longer exist: {sorted(str(SNAPSHOT_DIR / name) + '.txt' for name in stored - expected)}"
    )


def test_the_commands_panel_of_read_lists_exactly_the_steps() -> None:
    result = CliRunner().invoke(app, help_argv((PIPELINE,)), env=HELP_ENV, prog_name=CLI)
    lines = result.output.splitlines()
    panel = [lines[number] for number in _commands_panel(lines)][1:-1]
    listed = {line.split()[1] for line in panel if line.startswith("│ ") and line[2] != " "}
    assert listed == {path[1] for path in COMMANDS if path[0] == PIPELINE and len(path) == 2}


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


def _leaves(command: Any, path: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Any]]:
    if (subcommands := getattr(command, "commands", None)) is not None:
        for name, sub in subcommands.items():
            yield from _leaves(sub, (*path, name))
    else:
        yield path, command


def _arguments_after_command(path: tuple[str, ...], tokens: list[str]) -> list[str] | str:
    """The tokens an example gives the command at `path`; a text when the example does not start with it.

    A step stands after the input of read, `semkit read IN <step> ... write OUT`: its own tokens are those between the
    step and `write`; the tokens of `write` are those after the last `write`.
    """
    if path[0] != PIPELINE or len(path) != 2:
        if tokens[: len(path) + 1] != [CLI, *path]:
            return f"does not start with `{CLI} {' '.join(path)}`"
        return tokens[len(path) + 1 :]
    if tokens[:2] != [CLI, PIPELINE] or path[1] not in tokens[2:]:
        return f"is not `{CLI} {PIPELINE} IN {path[1]} ...`"
    if path[1] == WRITE:
        return tokens[len(tokens) - tokens[::-1].index(WRITE) :]
    rest = tokens[tokens.index(path[1], 2) + 1 :]
    return rest[: rest.index(WRITE)] if WRITE in rest else rest


def _example_failure(path: tuple[str, ...], command: Any, example: str) -> str | None:
    """Why `example` does not parse against the command: its path, options and arguments. Nothing is run."""
    try:
        tokens = shlex.split(example)
    except ValueError as exc:
        return f"{exc}"
    arguments = _arguments_after_command(path, tokens)
    if isinstance(arguments, str):
        return arguments
    ctx = typer.Context(command, info_name=path[-1])
    try:
        values, _, _ = command.make_parser(ctx).parse_args(arguments)
        for param in command.get_params(ctx):  # type_cast_value stops before the option callbacks
            if param.is_eager and param.name in values:  # --help, --version: the parser keeps only what is given
                return "asks for help or the version instead of a command"
            value, _ = param.consume_value(ctx, values)
            if param.value_is_missing(value):
                if param.required:
                    return f"Missing {param.param_type_name} {param.get_error_hint(ctx)}."
            else:
                param.type_cast_value(ctx, value)
    except Exception as exc:  # Click's own UsageError has format_message; anything else is a bug in the command
        format_message = getattr(exc, "format_message", None)
        return format_message() if callable(format_message) else f"raised {type(exc).__name__}: {exc}"
    return None


class _OwnExamples(docs.Hook):
    """The document keeps an example only after its command path; this test checks the path itself, with the parse."""

    def example(self, path, command):
        return " ".join([CLI, *path])


def _descriptions(nodes: list[dict], path: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], str]]:
    for node in nodes:
        yield (*path, node["name"]), node.get("description", "")
        yield from _descriptions(node.get("commands", []), (*path, node["name"]))


def _failures(path: tuple[str, ...], command: Any, description: str) -> list[str]:
    """The rules of the help standard that the command breaks, each as a line naming the command."""
    name = " ".join(path)
    help_text = opencli.cleaned(command.help)
    found: list[str] = []
    if not help_text:
        return [f"`{name}`: no docstring"]
    params = {param.name for param in command.params}
    lines = [line for paragraph in help_text.split("\n\n") for line in docs.doc_lines(paragraph, params)]
    examples = [line.removeprefix(docs.EXAMPLE) for line in lines if line.startswith(docs.EXAMPLE)]
    summary = description.split("\n\n")[0]
    if not summary:
        found.append(f"`{name}`: no summary")
    elif not help_text.splitlines()[0].startswith(summary):
        found.append(f"`{name}`: summary not one line")
    if not examples:
        found.append(f"`{name}`: no Example")
    if len(examples) > MAX_EXAMPLES:
        found.append(f"`{name}`: more than three examples")
    for example in examples:
        if problem := _example_failure(path, command, example):
            found.append(f"`{name}`: example `{example}` {problem}")
    flat = " ".join(description.split())
    for param in command.params:
        help_of_param = " ".join((getattr(param, "help", None) or "").split())
        if not help_of_param:
            found.append(f"`{name}`: parameter `{param.name}` has no help")
        elif help_of_param in flat:
            found.append(f"`{name}`: description repeats the help of `{param.name}`")
    return found


def help_failures(root: typer.Typer) -> dict[tuple[str, ...], list[str]]:
    """The failures of every command of `root`, by command path; a command that meets the standard is absent."""
    click_root = typer.main.get_command(root)
    descriptions = dict(_descriptions(docs.document(click_root, _OwnExamples()).get("commands", [])))
    found = {path: _failures(path, command, descriptions.get(path, "")) for path, command in _leaves(click_root)}
    return {path: failures for path, failures in found.items() if failures}


def _allowed(text: str) -> set[tuple[str, ...]]:
    lines = (line.split("#", 1)[0].strip() for line in text.splitlines())
    return {tuple(line.split()) for line in lines if line}


def _why_allowed_is_stale(click_root: Any, path: tuple[str, ...]) -> str:
    """Why an allowlist line that no failure needs is there: the command passes, is a group, or does not exist."""
    command = click_root
    for name in path:
        command = getattr(command, "commands", {}).get(name)
        if command is None:
            return "no such command"
    return "is a group, not a command" if hasattr(command, "commands") else "it meets the standard"


def check_help_standard(root: typer.Typer, allowlist: str) -> str:
    """The report of a run against the allowlist: empty when the help meets the standard."""
    failing, allowed = help_failures(root), _allowed(allowlist)
    report = [line for path, lines in failing.items() if path not in allowed for line in lines]
    click_root = typer.main.get_command(root)
    report += [
        f"remove from tests/help_allowlist.txt, {_why_allowed_is_stale(click_root, p)}: {' '.join(p)}"
        for p in sorted(allowed - failing.keys())
    ]
    new = sorted(" ".join(path) for path in failing if path not in allowed)
    if new:
        report += ["Lines for tests/help_allowlist.txt:", *new]
    return "\n".join(report)


def test_help_meets_the_standard() -> None:
    report = check_help_standard(app, ALLOWLIST.read_text(encoding="utf-8"))
    assert not report, f"\n{report}"


def _other(ctx: typer.Context) -> None:
    """Stand beside the command under test.

    Example: {cli} other
    """


def _probe(**commands: Callable[..., None]) -> typer.Typer:
    probe = typer.Typer(add_completion=False)
    for name, callback in commands.items():
        probe.command(name)(output.guard(callback))
    probe.command("other")(output.guard(_other))  # a Typer app of one command has no command name
    return probe


def _report(callback: Callable[..., None], allowlist: str = "") -> str:
    return check_help_standard(_probe(cmd=callback), allowlist)


def _good(ctx: typer.Context, size: int = typer.Option(3, "--size", help="The size.")) -> None:
    """Do the thing.

    Example: {cli} cmd --size 2
    """


def test_a_command_that_meets_the_standard_passes() -> None:
    assert _report(_good) == ""


def test_a_command_without_an_example_fails() -> None:
    def cmd(ctx: typer.Context) -> None:
        """Do the thing."""

    assert "`cmd`: no Example" in _report(cmd)


def test_a_summary_on_two_lines_fails() -> None:
    def cmd(ctx: typer.Context) -> None:
        """Do the thing that takes
        two lines to say.

        Example: {cli} cmd
        """

    assert "`cmd`: summary not one line" in _report(cmd)


def test_a_description_that_repeats_an_option_help_fails() -> None:
    def cmd(ctx: typer.Context, size: int = typer.Option(3, "--size", help="The size of it.")) -> None:
        """Do the thing.

        The size of it. Then it goes.

        Example: {cli} cmd
        """

    assert "`cmd`: description repeats the help of `size`" in _report(cmd)


def test_an_example_with_an_unknown_option_fails() -> None:
    def cmd(ctx: typer.Context) -> None:
        """Do the thing.

        Example: {cli} cmd --nope
        """

    report = _report(cmd)
    assert "`cmd`: example `semkit cmd --nope`" in report
    assert "No such option: --nope" in report


def test_an_example_does_not_run_the_callback_of_an_option() -> None:
    calls: list[str] = []

    def record(value: str) -> str:
        calls.append(value)
        return value

    def cmd(ctx: typer.Context, name: str = typer.Option("x", "--name", help="The name.", callback=record)) -> None:
        """Do the thing.

        Example: {cli} cmd --name Ann
        """

    assert _report(cmd) == ""
    assert calls == []


def test_an_error_that_is_not_click_names_its_type() -> None:
    def explode(value: str) -> str:
        raise ZeroDivisionError("boom")

    def cmd(ctx: typer.Context, name: str = typer.Option("x", "--name", help="The name.", parser=explode)) -> None:
        """Do the thing.

        Example: {cli} cmd --name Ann
        """

    assert "ZeroDivisionError" in _report(cmd)


def test_an_allowlist_line_for_a_missing_command_says_so() -> None:
    assert "remove from tests/help_allowlist.txt, no such command: ghost" in _report(_good, "ghost\n")


def test_an_example_that_asks_for_help_fails() -> None:
    def cmd(ctx: typer.Context) -> None:
        """Do the thing.

        Example: {cli} cmd --help
        """

    assert "`cmd`: example `semkit cmd --help` asks for help or the version instead of a command" in _report(cmd)


def test_an_example_missing_a_required_option_names_the_flag() -> None:
    def cmd(ctx: typer.Context, name: str = typer.Option(..., "--name", help="The name.")) -> None:
        """Do the thing.

        Example: {cli} cmd
        """

    assert "`cmd`: example `semkit cmd` Missing option '--name'." in _report(cmd)


def test_an_allowlist_line_for_a_group_says_so() -> None:
    probe = _probe(cmd=_good)
    probe.add_typer(_probe(cmd=_good), name="sub", help="A group.")
    assert "remove from tests/help_allowlist.txt, is a group, not a command: sub" in check_help_standard(probe, "sub\n")


def test_an_example_outside_the_command_path_fails() -> None:
    def cmd(ctx: typer.Context) -> None:
        """Do the thing.

        Example: {cli} other
        """

    assert "does not start with `semkit cmd`" in _report(cmd)


def test_an_example_missing_an_argument_fails() -> None:
    def cmd(ctx: typer.Context, key: str = typer.Argument(..., help="The key.")) -> None:
        """Do the thing.

        Example: {cli} cmd
        """

    assert "`cmd`: example `semkit cmd`" in _report(cmd)


def test_a_parameter_without_help_fails() -> None:
    def cmd(ctx: typer.Context, size: int = typer.Option(3, "--size")) -> None:
        """Do the thing.

        Example: {cli} cmd
        """

    assert "`cmd`: parameter `size` has no help" in _report(cmd)


def test_more_than_three_examples_fail() -> None:
    def cmd(ctx: typer.Context) -> None:
        """Do the thing.

        Example: {cli} cmd
        Example: {cli} cmd
        Example: {cli} cmd
        Example: {cli} cmd
        """

    assert "`cmd`: more than three examples" in _report(cmd)


def test_a_failing_command_in_the_allowlist_passes() -> None:
    def cmd(ctx: typer.Context) -> None:
        """Do the thing."""

    assert _report(cmd, "# not yet\ncmd  # old\n") == ""


def test_an_allowlisted_command_that_meets_the_standard_must_be_removed() -> None:
    assert "remove from tests/help_allowlist.txt, it meets the standard: cmd" in _report(_good, "cmd\n")


def test_a_failure_prints_the_lines_for_the_allowlist() -> None:
    def cmd(ctx: typer.Context) -> None:
        """Do the thing."""

    assert _report(cmd).splitlines()[-2:] == ["Lines for tests/help_allowlist.txt:", "cmd"]


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
