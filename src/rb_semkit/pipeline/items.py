"""The items of a list argument: '@path' (a file, one item per line), '@name' (a named list) or a comma list 'a,b'.

A name resolves through `rb_semkit.core.wordlists` when that module exists and has `resolve(name)` and `names()`;
without it, only the bundled stopwords and the marker lists have names.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable, Iterable
from pathlib import Path
from types import ModuleType

from ..core.errors import InvalidArguments
from ..core.markers import lists as marker_lists
from ..core.text.base import bundled_list
from .tables import read_lines

WORD_LISTS = "rb_semkit.core.wordlists"
STOPWORDS = "stopwords"
SYNTAX = "Items: a comma list 'a,b', @FILE (one item per line) or @NAME of a list."


def items(value: str) -> list[str]:
    """The items `value` names, blank ones dropped."""
    if not value.startswith("@"):
        return _cleaned(value.split(","))
    reference = value.removeprefix("@")
    if Path(reference).is_file():
        return _cleaned(read_lines(reference))
    return _named(reference)


def _cleaned(values: Iterable[str]) -> list[str]:
    return [value.strip() for value in values if value.strip()]


def _named(name: str) -> list[str]:
    resolve, names = _resolver()
    known = list(names())
    if name not in known:
        raise InvalidArguments(f"@{name}: no such file or list; allowed: {', '.join(f'@{item}' for item in known)}.")
    return _cleaned(resolve(name))


def _bundled(name: str) -> list[str]:
    return bundled_list(STOPWORDS) if name == STOPWORDS else marker_lists.phrases(name)


def _bundled_names() -> tuple[str, ...]:
    return (STOPWORDS, *marker_lists.names())


def _word_lists() -> ModuleType | None:
    try:
        return importlib.import_module(WORD_LISTS)
    except ModuleNotFoundError as error:
        if error.name != WORD_LISTS:
            raise
        return None


def _resolver() -> tuple[Callable[[str], Iterable[str]], Callable[[], Iterable[str]]]:
    module = _word_lists()
    if module is not None and hasattr(module, "resolve") and hasattr(module, "names"):
        return module.resolve, module.names
    return _bundled, _bundled_names
