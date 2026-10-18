"""The help of this CLI as one document for people: OpenCLI 0.1 with the commands at the root, as InSpectra reads it.

Built from the Click tree with no hand step, by the help standard (docs/help-standard.md), so the same code gives the
same document byte for byte. The entries of options and arguments are those of `core.opencli`; on top of them a
command's docstring is split into the description (the summary, then the paragraphs without the option lines and the
example lines) and the examples («<command>  # -> <result>»), an option's description ends with its default and
allowed values, and an option that does not repeat takes at most one value.

A docstring line «name: text» explains the parameters it names (`ARGUMENT_LINE`); `doc_lines` joins the lines of a
paragraph but keeps such a line, an item of a list and an example line apart. The hook `Inherited` names the parameters
of a group that a subcommand also takes: the document then shows them on the subcommand, before its own.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Collection, Sequence
from itertools import pairwise
from typing import Any

from . import opencli
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

# The parameters (Click's) of a group that its subcommand of this name also takes.
Inherited = Callable[[Any, str], Sequence[Any]]


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


def text(root: Any, inherited: Inherited | None = None) -> str:
    """The document as the file holds it: indented JSON, the same bytes for the same code."""
    return json.dumps(document(root, inherited), ensure_ascii=False, indent=2) + "\n"


def document(root: Any, inherited: Inherited | None = None) -> dict:
    """The document of the CLI whose root command is `root`; `inherited` adds a group's parameters to its subcommands."""
    command = _command(cli_name(), root, inherited)
    shape = {"opencli": opencli.OPENCLI_VERSION, "info": opencli.info()}
    return shape | {key: command.get(key, []) for key in ("commands", "options", "arguments", "examples")}


def _command(name: str, cmd: Any, inherited: Inherited | None, extra: Sequence[Any] = ()) -> dict:
    params = [*extra, *cmd.params]
    names = {param.name for param in params}
    paragraphs = [doc_lines(paragraph, names) for paragraph in opencli.cleaned(cmd.help).split("\n\n")]
    out: dict[str, Any] = {"name": name}
    if description := _description([_described(lines, names) for lines in paragraphs]):
        out["description"] = description
    if cmd.hidden:
        out["hidden"] = True
    out["options"] = [_option(param) for param in params if param.param_type_name == "option"]
    out["arguments"] = [_argument(param) for param in params if param.param_type_name == "argument"]
    out["examples"] = _examples([line for lines in paragraphs for line in lines])
    if (subcommands := getattr(cmd, "commands", None)) is not None:  # a group, in the order of registration
        out["commands"] = [
            _command(sub_name, sub, inherited, inherited(cmd, sub_name) if inherited else ())
            for sub_name, sub in subcommands.items()
        ]
    return {key: value for key, value in out.items() if value != []}


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


def _examples(lines: list[str]) -> list[str]:
    """Each example line as one string, with the result line after it: «<command>  # -> <result>»."""
    found: list[str] = []
    for previous, line in pairwise(["", *lines]):
        if line.startswith(EXAMPLE):
            found.append(line.removeprefix(EXAMPLE))
        elif line.startswith(RESULT) and previous.startswith(EXAMPLE):
            found[-1] += f"  # {line}"
    return found


def _option(param: Any) -> dict:
    out = opencli.option(param)
    del out["metadata"]
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
