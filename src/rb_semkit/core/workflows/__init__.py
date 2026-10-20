"""Workflows: a named chain of semkit's own steps, kept in a file NAME.toml so that a frequent chain runs by its name.

A file holds `description` (one line), `steps` (the chain as read takes it, one step per line, with {name}
placeholders), `per_phrase` (true: the chain runs once for each phrase of the input, {text} being that phrase) and a
table `[parameters.NAME]` of `default` and `help` for each parameter. Every parameter has a default, so a workflow runs
with the input alone. The bundled workflows are in data/workflows; the project folder .rb_semkit/workflows/ adds more,
and one of the same name overrides the bundled one. The former project folder .rb_semkit/scenarios/ is read too; a
name in both folders is the one in workflows/.

`load` refuses a file that is no workflow, a parameter without a default and a placeholder that names no parameter;
whether a step and its options exist is the pipeline's to check (`pipeline.workflows`). `settings` reads the values
of --set: NAME=VALUE fills a parameter, STEP.OPTION=VALUE sets an option of a step.
"""

from __future__ import annotations

import re
import shlex
import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from .. import services
from ..datastore import DATA_DIR
from ..errors import InvalidArguments
from ..version import cli_name

BUNDLED = DATA_DIR / "workflows"
SUFFIX = ".toml"
TEXT = "text"  # the placeholder of the input phrase
PLACEHOLDER = re.compile(r"\{([A-Za-z_]\w*)\}")
STEPS_KEY = re.compile(r"^\s*steps\s*=")
FIX_FILE = "Fix the workflow file, or remove it."


@dataclass(frozen=True)
class Parameter:
    """A parameter of a workflow: its {name} in the steps takes `default` unless --set gives another value."""

    name: str
    default: str
    help: str


@dataclass(frozen=True)
class StepLine:
    """One step of a workflow as written, and its line in the file."""

    number: int
    text: str

    def words(self, values: Mapping[str, str]) -> list[str]:
        """The words of the step as read takes them, each placeholder filled from `values`."""
        return [PLACEHOLDER.sub(lambda found: values[found[1]], word) for word in shlex.split(self.text)]

    def step(self) -> str:
        return shlex.split(self.text)[0]


@dataclass(frozen=True)
class Settings:
    """What --set gives: the values of parameters, and the options of steps (step → option → value)."""

    values: dict[str, str] = field(default_factory=dict)
    options: dict[str, dict[str, str]] = field(default_factory=dict)


@dataclass(frozen=True)
class Workflow:
    """A workflow as its file holds it; its name is the name of the file."""

    name: str
    path: Path
    description: str
    parameters: tuple[Parameter, ...]
    steps: tuple[StepLine, ...]
    per_phrase: bool = False

    def values(self, given: Mapping[str, str], text: str | None) -> dict[str, str]:
        """The value of each placeholder: the defaults, the parameters `given`, and {text} when there is a phrase."""
        found = {parameter.name: parameter.default for parameter in self.parameters} | dict(given)
        return found if text is None else found | {TEXT: text}

    def refused(self, line: StepLine, reason: str) -> InvalidArguments:
        """A step line of the workflow refused for `reason`, naming the file and the line."""
        return InvalidArguments(f"{self.path}:{line.number}: {line.text}: {reason}", action=FIX_FILE)

    def help(self) -> str:
        """The help of `run NAME`: the description, the parameters with their defaults, the steps and an example."""
        parameters = [f"- {p.name} (default {p.default}): {p.help}" for p in self.parameters] or ["None."]
        runs = (
            "The chain runs once for each phrase of the input, {text} being that phrase; the parts are joined in the"
            " order of the input under a first column input."
            if self.per_phrase
            else "The chain runs once over the whole table."
        )
        return "\n\n".join(
            [
                self.description,
                "\n".join(["Parameters, set with --set NAME=VALUE:", *parameters]),
                "\n".join(["Steps, as read takes them:", *(f"- {line.text}" for line in self.steps)]),
                f"{runs} An option of a step is set with --set STEP.OPTION=VALUE: it replaces the value of the option"
                " in that step, or adds the option.",
                f"Example: {cli_name()} run {self.name} core.csv write out.csv",
            ]
        )


def find(start: Path) -> dict[str, Path]:
    """The workflow files by name: the bundled ones, then the project's at or above `start` over them."""
    root = services.find_project_root(start)
    project = [] if root is None else [services.project_old_workflows_dir(root), services.project_workflows_dir(root)]
    folders = [BUNDLED, *project]
    found = {path.stem: path for folder in folders for path in sorted(folder.glob(f"*{SUFFIX}"))}
    return dict(sorted(found.items()))


def load(path: Path) -> Workflow:
    """The workflow of the file `path`; a file that is no workflow is refused with exit 2, naming the file."""
    text = path.read_text(encoding="utf-8")
    try:
        content = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise InvalidArguments(f"{path}: no TOML: {error}.", action=FIX_FILE) from None
    description, steps = content.get("description"), content.get("steps")
    if not isinstance(description, str) or not isinstance(steps, str):
        raise InvalidArguments(f"{path}: a workflow needs the texts description and steps.", action=FIX_FILE)
    workflow = Workflow(
        path.stem,
        path,
        description.strip(),
        tuple(_parameter(path, name, table) for name, table in content.get("parameters", {}).items()),
        _step_lines(text, steps),
        content.get("per_phrase") is True,
    )
    for line in workflow.steps:
        _check_placeholders(workflow, line)
    return workflow


def _parameter(path: Path, name: str, table: object) -> Parameter:
    if not isinstance(table, dict) or "default" not in table:
        raise InvalidArguments(
            f"{path}: the parameter {name} has no default.", action=f"Give [parameters.{name}] a default = VALUE."
        )
    return Parameter(name, str(table["default"]), str(table.get("help", "")))


def _step_lines(text: str, steps: str) -> tuple[StepLine, ...]:
    """The steps, one a line, each with its line in the file: the first line at or after the key steps that holds it."""
    lines = text.splitlines()
    number = next((index for index, line in enumerate(lines) if STEPS_KEY.match(line)), 0)
    found = []
    for step in filter(None, (line.strip() for line in steps.splitlines())):
        number = next((index for index in range(number, len(lines)) if step in lines[index]), number)
        found.append(StepLine(number + 1, step))
    return tuple(found)


def _check_placeholders(workflow: Workflow, line: StepLine) -> None:
    """Refuse a line that is no command line, or names a placeholder that is no parameter, or {text} of no phrase."""
    try:
        shlex.split(line.text)
    except ValueError as error:
        raise workflow.refused(line, f"{error}.") from None
    known = [parameter.name for parameter in workflow.parameters]
    for name in PLACEHOLDER.findall(line.text):
        if name == TEXT and not workflow.per_phrase:
            raise workflow.refused(line, "{text} is the phrase of a workflow with per_phrase = true.")
        if name != TEXT and name not in known:
            raise workflow.refused(line, f"{{{name}}} is no parameter; the parameters: {_names(known)}.")


def settings(workflow: Workflow, given: Iterable[str]) -> Settings:
    """The values of --set: NAME=VALUE of a parameter (an unknown one is refused), STEP.OPTION=VALUE of a step."""
    found = Settings()
    known = [parameter.name for parameter in workflow.parameters]
    for setting in given:
        name, equals, value = setting.partition("=")
        step, dot, option = name.partition(".")
        if not equals:
            raise InvalidArguments(
                f"run {workflow.name}: --set {setting}: no '='.", action="Give --set NAME=VALUE or STEP.OPTION=VALUE."
            )
        if dot:
            found.options.setdefault(step, {})[option] = value
        elif name in known:
            found.values[name] = value
        else:
            raise InvalidArguments(
                f"run {workflow.name}: --set {setting}: the workflow has no parameter {name}.",
                action=f"Set one of its parameters: {_names(known)}; or an option of a step as STEP.OPTION=VALUE.",
            )
    return found


def _names(names: Iterable[str]) -> str:
    return ", ".join(names) or "none"
