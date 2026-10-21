"""The commands package: one module for each command (or command group) of the CLI.

`modules()` lists them by name, so the root command registers a new module without an edit, and `ai_sections()`
gives the text each module adds to `--ai`.
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType


def modules() -> list[ModuleType]:
    """Every module of this package, by name."""
    names = sorted(info.name for info in pkgutil.iter_modules(__path__))
    return [importlib.import_module(f"{__name__}.{name}") for name in names]


def ai_sections() -> list[str]:
    """The section each command module gives by `ai_section()` (the pipeline steps, the lists)."""
    return [module.ai_section() for module in modules() if hasattr(module, "ai_section")]
