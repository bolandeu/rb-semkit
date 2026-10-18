"""The hook of the help document (`core.docs`): the input of read stays on read, each step page shows how to give it.

A step stands after `read IN` on the command line. The document keeps IN, --text, --column and --whole on read only
(read takes them before the first step), so an example of a step is shown without them: «--all --source ruwordnet»,
and the description of the step begins with the line «Input: …» that gives the full form.
"""

from __future__ import annotations

import shlex
from collections.abc import Sequence
from typing import Any

from ..core import docs
from ..core.version import cli_name
from . import areas

PIPELINE = "read"
WRITE = "write"
INPUT_LINE = "Input: {cli} {read} IN|--text TEXT|- {step} [options] [{write} OUT]"


class ReadSteps(docs.Hook):
    """The steps of read, whose examples in the docstring are full commands «<cli> read <input> <step> …»."""

    def __init__(self, root: Any) -> None:
        self.read = root.commands[PIPELINE]
        self.steps = {step.name for found in areas().values() for step in found}
        self.program = cli_name()

    def lead(self, path: Sequence[str]) -> str:
        """The line «Input: …» for a step of read."""
        if len(path) == 2 and path[0] == PIPELINE and path[1] in self.steps:
            return INPUT_LINE.format(cli=self.program, read=PIPELINE, step=path[1], write=WRITE)
        return ""

    def example(self, path: Sequence[str], command: str) -> str:
        """A step's example without the input of read; write's without the steps before it; any other as it is."""
        if len(path) != 2 or path[0] != PIPELINE or path[1] not in {*self.steps, WRITE}:
            return command
        tokens = shlex.split(command, posix=False)
        if tokens[:2] != [self.program, PIPELINE]:
            return command
        stop = len(tokens) - tokens[::-1].index(WRITE) - 1 if path[1] == WRITE and WRITE in tokens else None
        index = stop if stop is not None else self._step_index(tokens, path[1])
        return command if index is None else " ".join([*tokens[:2], path[1], *tokens[index + 1 :]])

    def _step_index(self, tokens: list[str], step: str) -> int | None:
        """Where `step` stands after the input of read: IN, or the options of read with their values."""
        options = [param for param in self.read.params if param.param_type_name == "option"]
        takes = {opt: not param.is_flag for param in options for opt in param.opts}
        index = 2
        while index < len(tokens) and tokens[index] != step:
            index += 2 if takes.get(tokens[index]) else 1
        return index if index < len(tokens) else None
