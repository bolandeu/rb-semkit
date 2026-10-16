"""semkit: processing of a semantic core over pandas — `import rb_semkit as sk`.

Every public name maps to the module that defines it and loads it on first access, so `import rb_semkit`
stays cheap. A name whose module does not exist yet raises AttributeError naming it.
"""

from __future__ import annotations

import importlib
from typing import Any

_MATCHERS = (
    "chars",
    "spaces",
    "positions",
    "around",
    "regex",
    "words",
    "word_content",
    "word_case",
    "word_position",
    "pos",
    "repeats",
    "stopwords",
    "phrases",
    "cells",
)
_MODULES: dict[str, str] = {
    **dict.fromkeys(("Matcher", "find", "remove", "extract", "pipe"), "rb_semkit.core.text"),
    **{name: f"rb_semkit.core.text.matchers.{name}" for name in _MATCHERS},
    "markers": "rb_semkit.core.markers",
    "dupes": "rb_semkit.core.dupes",
    **dict.fromkeys(("ngrams", "bigrams", "counts"), "rb_semkit.core.analysis"),
    **dict.fromkeys(
        ("Lemmatizer", "SemtoolsLemmatizer", "lemmatize", "part_of_speech", "wordforms"), "rb_semkit.core.morph"
    ),
    "InvalidArguments": "rb_semkit.core.errors",
}


def __getattr__(name: str) -> Any:
    module_name = _MODULES.get(name)
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
    return sorted(set(globals()) | set(_MODULES))
