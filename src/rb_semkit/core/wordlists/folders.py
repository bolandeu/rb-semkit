"""The folders of the Human's word lists, and a list as a file: `<name>.txt` under a folder, UTF-8, one item per line.

The folders, in the order they are searched: the project's own (`.rb_semkit/lists/`), the folders of the variable
SEMKIT_LISTS (separated as PATH is; a relative one is from the current folder), the folders of the config key `lists`
(a relative one is from the project). A first line that starts with '# ' is the description of the list, not an item.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .. import services
from ..errors import InvalidArguments

ENV_VAR = "SEMKIT_LISTS"
PROJECT = "project"
SUFFIX = ".txt"
DESCRIPTION_MARK = "# "


@dataclass(frozen=True)
class Folder:
    """A folder of lists and how the Human named it: PROJECT, or the path as written in the config or the variable."""

    label: str
    path: Path


def search_folders(start: Path | None = None) -> list[Folder]:
    """The folders to search from `start` (the working folder by default), in the order of the search."""
    root = services.find_project_root(start or Path.cwd())
    found = [] if root is None else [Folder(PROJECT, services.project_lists_dir(root))]
    listed = [text for text in os.environ.get(ENV_VAR, "").split(os.pathsep) if text]
    found += [Folder(text, Path.cwd() / Path(text).expanduser()) for text in listed]
    if root is not None and services.config_path(root).is_file():
        found += [Folder(text, root / Path(text).expanduser()) for text in services.load_config(root).lists]
    return found


def is_searched(folder: Path, start: Path | None = None) -> bool:
    """Whether `folder` is one of the folders searched from `start`, so that its lists are found by name."""
    return folder.resolve() in {searched.path.resolve() for searched in search_folders(start)}


def list_path(folder: Path, name: str) -> Path:
    """The file of the list `name` under `folder`; `name` is a relative path without the suffix (niche/mebel)."""
    parts = Path(name).parts
    if not name or Path(name).is_absolute() or ".." in parts or name.endswith(SUFFIX):
        raise InvalidArguments(f"{name!r}: not a list name; allowed: a relative path without {SUFFIX}, as niche/mebel.")
    return folder / f"{name}{SUFFIX}"


def read_list(path: Path) -> tuple[str, list[str]]:
    """The description (empty when the file has none) and the items of a list file; blank lines are not items."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    described = bool(lines) and lines[0].startswith(DESCRIPTION_MARK)
    description = lines[0].removeprefix(DESCRIPTION_MARK).strip() if described else ""
    return description, [line.strip() for line in lines[described:] if line.strip()]


def list_names(folder: Path) -> list[str]:
    """The names of the lists under `folder`, sorted; none when the folder does not exist."""
    return sorted(path.relative_to(folder).with_suffix("").as_posix() for path in folder.rglob(f"*{SUFFIX}"))
