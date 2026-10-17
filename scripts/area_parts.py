"""The per-area parts of a script: the `<area>.py` files of its parts folder (scripts/build_parts, scripts/bench_parts)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_parts(folder: Path) -> dict[str, ModuleType]:
    """Each part of `folder`, by area; a file whose name starts with «_» is not a part."""
    found = {}
    for path in sorted(folder.glob("[!_]*.py")):
        spec = importlib.util.spec_from_file_location(f"{folder.name}_{path.stem}", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"not a Python module: {path}")
        found[path.stem] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(found[path.stem])
    return found
