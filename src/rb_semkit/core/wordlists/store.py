"""Adding a list file to a folder of lists and removing it: what `semkit lists add` and `rm` do."""

from __future__ import annotations

import shutil
from pathlib import Path

from ..errors import InvalidArguments
from . import bundled
from .folders import list_path


def add(name: str, source: Path, folder: Path, *, replace: bool = False, dry_run: bool = False) -> Path:
    """Copy `source` to the list `name` under `folder`; the file it writes. An existing list needs `replace`."""
    if not source.is_file():
        raise InvalidArguments(f"{source}: not a file; allowed: a text file, one item per line.")
    target = list_path(folder, name)
    if target.exists() and not replace:
        raise InvalidArguments(f"{name}: already in {folder}; allowed: --replace to overwrite it.")
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return target


def remove(name: str, folder: Path, *, dry_run: bool = False) -> Path:
    """Delete the list `name` under `folder`, and the folders of its name left empty; the file it deletes."""
    target = list_path(folder, name)
    if not target.is_file():
        reason = "a bundled list is never removed" if name in bundled.entries() else f"no such list in {folder}"
        raise InvalidArguments(f"{name}: {reason}.")
    if not dry_run:
        target.unlink()
        for parent in target.parents:
            if parent == folder or any(parent.iterdir()):
                break
            parent.rmdir()
    return target
