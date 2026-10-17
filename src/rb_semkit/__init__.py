"""semkit: processing of a semantic core over pandas — `import rb_semkit as sk`.

A module of an area (a package under `rb_semkit.core`) declares its public names in `__all__`. On the first access of
a name the root reads the sources of the areas, without importing them, to find the module that declares it, then
loads that module; so `import rb_semkit` stays cheap and a new area module needs no edit here. A name whose module
cannot be imported yet raises AttributeError naming it.
"""

from __future__ import annotations

import ast
import functools
import importlib
from pathlib import Path
from typing import Any

_CORE = "rb_semkit.core"
_ROOT_NAMES = {"InvalidArguments": f"{_CORE}.errors"}


def _declared(path: Path) -> list[str]:
    """The names of the module's `__all__`, read from its source."""
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(target, "id", None) == "__all__" for target in node.targets):
            return list(ast.literal_eval(node.value))
    return []


@functools.cache
def _public_names() -> dict[str, str]:
    """Each public name and the module that declares it."""
    names = dict(_ROOT_NAMES)
    for entry in map(Path, importlib.import_module(_CORE).__path__):
        areas = sorted(folder for folder in entry.iterdir() if (folder / "__init__.py").is_file())
        for path in (path for area in areas for path in sorted(area.rglob("*.py"))):
            module = ".".join((_CORE, *path.relative_to(entry).with_suffix("").parts)).removesuffix(".__init__")
            for name in _declared(path):
                if names.setdefault(name, module) != module:
                    raise ImportError(f"rb_semkit.{name} is declared by both {names[name]} and {module}")
    return names


def __getattr__(name: str) -> Any:
    module_name = _public_names().get(name)
    if module_name is None:
        raise AttributeError(f"module 'rb_semkit' has no attribute {name!r}")
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name is None or not f"{module_name}.".startswith(f"{error.name}."):
            raise
        raise AttributeError(
            f"rb_semkit.{name} is not available yet: its module {module_name} does not exist"
        ) from None
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_public_names()))
