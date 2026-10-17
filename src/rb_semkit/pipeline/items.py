"""The items of a list argument: '@path' (a file, one item per line), '@name' (a named list) or a comma list 'a,b'.

A name resolves through `rb_semkit.core.wordlists`: the project's lists, the Human's folders, then the bundled lists.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ..core import wordlists
from .tables import read_lines

SYNTAX = "Items: a comma list 'a,b', @FILE (one item per line) or @NAME of a list."


def items(value: str) -> list[str]:
    """The items `value` names, blank ones dropped."""
    if not value.startswith("@"):
        return _cleaned(value.split(","))
    reference = value.removeprefix("@")
    if Path(reference).is_file():
        return _cleaned(read_lines(reference))
    return wordlists.resolve(reference)


def _cleaned(values: Iterable[str]) -> list[str]:
    return [value.strip() for value in values if value.strip()]
