"""The hook of the help document (`core.docs`): each step under read also takes the input of read.

A step stands after `read IN` on the command line, so its page in the document shows IN, --text, --column and --whole
of read before its own options; a viewer that composes a command from the page then gives the step an input.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from . import areas

PIPELINE = "read"
INPUT = ("source", "texts", "column", "whole")  # the parameters of read that give the input, as Click names them


def inherited(group: Any, name: str) -> Sequence[Any]:
    """The input parameters of read for its subcommand `name` when it is a step; none for any other command."""
    if group.name != PIPELINE or name not in {step.name for found in areas().values() for step in found}:
        return []
    return [param for param in group.params if param.name in INPUT]
