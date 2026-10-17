"""Every word list by name: the Human's folders first, then the bundled ones (`bundled.py`).

A name found in a folder hides the same name in a later folder and in the bundled lists.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..errors import InvalidArguments
from ..version import cli_name
from . import bundled
from .folders import Folder, list_names, list_path, read_list, search_folders

BUNDLED = "bundled"
CLOSE_NAMES = 10  # the names an unknown name is shown, the closest first


@dataclass(frozen=True)
class WordList:
    """A list as `semkit lists` shows it: where it comes from (PROJECT, a folder as written, or BUNDLED)."""

    name: str
    source: str
    lines: int
    description: str


def _find(name: str, folders: list[Folder]) -> tuple[WordList, list[str]] | None:
    for folder in folders:
        path = list_path(folder.path, name)
        if path.is_file():
            description, items = read_list(path)
            return WordList(name, folder.label, len(items), description), items
    if name in bundled.entries():
        items = bundled.items(name)
        return WordList(name, BUNDLED, len(items), bundled.entries()[name].description), items
    return None


def _get(name: str, start: Path | None) -> tuple[WordList, list[str]]:
    found = _find(name, search_folders(start))
    if found is None:
        every = [info.name for info in names(start)]
        closest = sorted(every, key=lambda other: -difflib.SequenceMatcher(None, name, other).ratio())[:CLOSE_NAMES]
        raise InvalidArguments(
            f"{name}: no such list; the lists closest to it: {', '.join(closest)}.",
            action=f"Run '{cli_name()} lists' for every list.",
        )
    return found


def names(start: Path | None = None) -> tuple[WordList, ...]:
    """Every list that `resolve` finds, once, sorted by name; `start` is the folder the project is looked up from."""
    folders = search_folders(start)
    every = {name for folder in folders for name in list_names(folder.path)} | set(bundled.entries())
    found = (_find(name, folders) for name in sorted(every))
    return tuple(entry[0] for entry in found if entry is not None)


def resolve(name: str, start: Path | None = None) -> list[str]:
    """The items of the list `name`: the first match in the project's folder, SEMKIT_LISTS, the config's, the bundled."""
    return _get(name, start)[1]


def describe(name: str, start: Path | None = None) -> WordList:
    """Where the list `name` comes from, how many items it has and what it is."""
    return _get(name, start)[0]


def word_list(name: str) -> pd.Series:
    """The items of the word list `name` as a Series; an unknown name raises InvalidArguments with the close names.

    A name is a relative path without .txt (`minus/cheap`, `niche/mebel`); the project's lists, the folders of
    SEMKIT_LISTS, the folders of the config key `lists` and the bundled lists are searched in that order.
    """
    return pd.Series(resolve(name), dtype=object)
