"""The items of a list argument: '@path' (a file), '@name' (a named list) or a comma list 'a,b'.

A text file holds one item per line; a table file (csv, xlsx, jsonl…) holds them in its first column, under its
header. A name resolves through `rb_semkit.core.wordlists`: the project's lists, the Human's folders, then the bundled
lists.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ..core import wordlists
from ..core.errors import InvalidArguments
from .tables import Source, read_lines

SYNTAX = "Items: a comma list 'a,b', @FILE (one item per line, or the first column of a table) or @NAME of a list."
TEXT_SUFFIXES = ("", ".txt", ".text", ".lst")


def items(value: str) -> list[str]:
    """The items `value` names, blank ones dropped."""
    if not value.startswith("@"):
        return _cleaned(value.split(","))
    reference = value.removeprefix("@")
    path = Path(reference).expanduser()
    if path.is_file():
        return _cleaned(_file_items(path))
    if path.suffix or reference.startswith((".", "/", "~")):
        raise InvalidArguments(f"@{reference}: the file does not exist.", action="Name a file that exists after @.")
    return wordlists.resolve(reference)


def _file_items(path: Path) -> list[str]:
    """The lines of a text file; the cells of the first column of a table file."""
    if path.suffix.lower() in TEXT_SUFFIXES:
        return read_lines(str(path))
    table = Source(str(path)).read()
    return [] if table.columns.empty else table.iloc[:, 0].astype(str).tolist()


def _cleaned(values: Iterable[str]) -> list[str]:
    return [value.strip() for value in values if value.strip()]
