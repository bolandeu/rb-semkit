"""The help of this CLI as one document for people: OpenCLI 0.1 with the commands at the root, as InSpectra reads it.

Built from the Click tree with no hand step, by the help standard (docs/help-standard.md), so the same code gives the
same document byte for byte. The entries of options and arguments are those of `core.opencli`; on top of them a
command's docstring is split into the description (the summary, then the paragraphs without the option lines and the
example lines) and the examples («<command>  # -> <result>»), an option's description ends with its default and
allowed values, and an option that does not repeat takes at most one value.

A docstring line «name: text» explains the parameters it names (`ARGUMENT_LINE`); `doc_lines` joins the lines of a
paragraph but keeps such a line, an item of a list and an example line apart.

An example in the document holds only what follows «<program> <command path>»; the docstring keeps the whole command,
and an example that does not start with its command path fails the document (`ExampleOutsidePath`). A `Hook` of the
CLI may bring a docstring example to that form, put a line before a description, and name the options of a group that
all its subcommands take: the group shows them as recursive, the subcommands do not copy them.
"""

from __future__ import annotations

import json
import re
from collections.abc import Collection, Sequence
from itertools import pairwise
from typing import Any

from . import opencli
from .errors import CliError
from .version import cli_name

# A docstring line that explains arguments of the function: «mode: …», «`action`: …», «core, column: …», «first / last: …».
ARGUMENT_NAMES = r"`?\w+`?(?:(?:, | / )`?\w+`?)*"
ARGUMENT_LINE = re.compile(rf"^(?P<names>{ARGUMENT_NAMES}): ")
# An explanation of another argument inside a line, after the end of a sentence: «… is bad. good: a phrase …».
INLINE_ARGUMENT = re.compile(rf"(?<=[.;]) (?P<names>{ARGUMENT_NAMES}): ")
LIST_ITEM = re.compile(r"^(?:[-*]|\d+[.)]) ")
EXAMPLE = "Example: "
RESULT = "-> "  # the line after an example: what it gives
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


class ExampleOutsidePath(CliError):
    """An example whose command does not start with its command path: the docstring breaks the help standard."""

    def __init__(self, path: str, example: str) -> None:
        super().__init__("EXAMPLE_OUTSIDE_PATH", f"The example of '{path}' does not start with it: {example}")


class Hook:
    """What a CLI adds to the document; this base adds nothing. `path` is the names of a command below the root."""

    def inherited(self, group: Any) -> Sequence[Any]:
        """The options (Click's) of `group` that every subcommand below it also takes; never an argument."""
        return ()

    def example(self, path: Sequence[str], command: str) -> str:
        """The command of a docstring example as a command that starts with its command path."""
        return command

    def lead(self, path: Sequence[str]) -> str:
        """A line that begins the description of the command at `path`; empty for none."""
        return ""


def doc_lines(paragraph: str, parameters: Collection[str]) -> list[str]:
    """The lines of a docstring paragraph as the help shows them.

    A line goes on the line before it, unless it starts an item of a list, the explanation of arguments, an example or
    its result; so does the explanation of an argument of `parameters` that follows the end of a sentence.
    """
    lines: list[str] = []
    for line in paragraph.splitlines():
        text = line.strip()
        if lines and not (ARGUMENT_LINE.match(text) or LIST_ITEM.match(text) or text.startswith((EXAMPLE, RESULT))):
            lines[-1] += f" {text}"
        else:
            lines.append(text)
    return [part for line in lines for part in _argument_parts(line, parameters)]


def argument_names(found: re.Match[str]) -> list[str]:
    """The names an explanation of arguments (ARGUMENT_LINE or INLINE_ARGUMENT) is for."""
    return [name.strip("`") for name in re.split(r", | / ", found["names"])]


def _argument_parts(line: str, parameters: Collection[str]) -> list[str]:
    parts, start = [], 0
    for found in INLINE_ARGUMENT.finditer(line):
        if all(name in parameters for name in argument_names(found)):
            parts.append(line[start : found.start()])
            start = found.start() + 1
    return [*parts, line[start:]]


def text(root: Any, hook: Hook | None = None) -> str:
    """The document as the file holds it: indented JSON, the same bytes for the same code."""
    return json.dumps(document(root, hook), ensure_ascii=False, indent=2) + "\n"


def document(root: Any, hook: Hook | None = None) -> dict:
    """The document of the CLI whose root command is `root`; `hook` is what the CLI adds to it."""
    command = _command(cli_name(), root, hook or Hook(), ())
    shape = {"opencli": opencli.OPENCLI_VERSION, "info": opencli.info()}
    return shape | {key: command.get(key, []) for key in ("commands", "options", "arguments", "examples")}


def _command(name: str, cmd: Any, hook: Hook, path: tuple[str, ...]) -> dict:
    params = cmd.params
    names = {param.name for param in params}
    paragraphs = [doc_lines(paragraph, names) for paragraph in opencli.cleaned(cmd.help).split("\n\n")]
    out: dict[str, Any] = {"name": name}
    description = [hook.lead(path), _description([_described(lines, names) for lines in paragraphs])]
    if description := "\n\n".join(part for part in description if part):
        out["description"] = description
    if cmd.hidden:
        out["hidden"] = True
    recursive = _recursive(cmd, hook)
    out["options"] = [_option(param, param in recursive) for param in params if param.param_type_name == "option"]
    out["arguments"] = [_argument(param) for param in params if param.param_type_name == "argument"]
    out["examples"] = _examples([line for lines in paragraphs for line in lines], hook, path)
    if (subcommands := getattr(cmd, "commands", None)) is not None:  # a group, in the order of registration
        out["commands"] = [_command(sub_name, sub, hook, (*path, sub_name)) for sub_name, sub in subcommands.items()]
    return {key: value for key, value in out.items() if value != []}


def _recursive(cmd: Any, hook: Hook) -> Sequence[Any]:
    """The options of a group that its subcommands take too; an argument there is a mistake of the hook."""
    if getattr(cmd, "commands", None) is None:
        return ()
    found = hook.inherited(cmd)
    if arguments := [param.name for param in found if param.param_type_name != "option"]:
        raise ValueError(f"A hook inherits options only, not the arguments {arguments} of '{cmd.name}'")
    return found


def _described(lines: list[str], names: Collection[str]) -> list[str]:
    """The lines of a paragraph that stay in the description: no option line (nor the items of its list), no example."""
    kept, in_option = [], False
    for line in lines:
        if in_option and LIST_ITEM.match(line):
            continue
        in_option = _option_line(line, names)
        if not in_option and not line.startswith((EXAMPLE, RESULT)):
            kept.append(line)
    return kept


def _option_line(line: str, names: Collection[str]) -> bool:
    found = ARGUMENT_LINE.match(line)
    return bool(found) and any(name in names for name in argument_names(found))


def _description(paragraphs: list[list[str]]) -> str:
    """The summary (the first sentence) as a paragraph of its own, then the other paragraphs."""
    kept = [lines for lines in paragraphs if lines]
    if not kept:
        return ""
    summary, *rest = SENTENCE_END.split(kept[0][0], maxsplit=1)
    return "\n\n".join("\n".join(lines) for lines in [[summary], [*rest, *kept[0][1:]], *kept[1:]] if lines)


def _examples(lines: list[str], hook: Hook, path: tuple[str, ...]) -> list[str]:
    """Each example line as one string, without «<program> <command path>», with the result line after it: «<rest>  # -> <result>»."""
    found: list[list[str]] = []
    for previous, line in pairwise(["", *lines]):
        if line.startswith(EXAMPLE):
            found.append([line.removeprefix(EXAMPLE), ""])
        elif line.startswith(RESULT) and previous.startswith(EXAMPLE):
            found[-1][1] = line
    return [_after_path(hook, path, command, result) for command, result in found]


def _after_path(hook: Hook, path: tuple[str, ...], command: str, result: str) -> str:
    start = " ".join([cli_name(), *path])
    full = hook.example(path, command)
    if full != start and not full.startswith(f"{start} "):
        raise ExampleOutsidePath(start, command)
    rest = full.removeprefix(start).strip()
    return f"{rest}  # {result}".strip() if result else rest


def _option(param: Any, recursive: bool) -> dict:
    out = opencli.option(param)
    del out["metadata"]
    if recursive:
        out["recursive"] = True
    for value in out.get("arguments", []):
        value["arity"] = {"minimum": 1} if param.multiple else {"minimum": 1, "maximum": 1}
    values = _values(param, out.get("arguments", [{}])[0].get("acceptedValues"))
    if description := "\n".join(part for part in (out.pop("description", ""), values) if part):
        out["description"] = description
    return out


def _argument(param: Any) -> dict:
    out = opencli.argument(param)
    del out["metadata"]
    return out


def _values(param: Any, allowed: list[str] | None) -> str:
    """The last line of an option's description: «Default: 10. Allowed: a, b.», each part only when it applies."""
    parts = []
    if (default := _default(param)) is not None:
        parts.append(f"Default: {default}.")
    if allowed:
        parts.append(f"Allowed: {', '.join(allowed)}.")
    return " ".join(parts)


def _default(param: Any) -> str | None:
    if param.is_flag:
        return "on" if param.default else "off"
    if param.required or callable(param.default):
        return None
    value = opencli.jsonable(param.default)
    if value in (None, "", []):
        return None
    return ", ".join(map(str, value)) if isinstance(value, list) else str(value)
