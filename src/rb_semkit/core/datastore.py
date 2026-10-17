"""The bundled reference data (ADR 0002), loaded on first use: once per process, safe when many threads ask at once.

`scripts/build_data.py` writes the files under `rb_semkit/data/`; tries are memory-mapped, JSON tables parsed.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import marisa_trie  # ty: ignore[unresolved-import]  # a compiled extension without type stubs

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

T = TypeVar("T")
_lock = threading.RLock()  # a loader may load another table: re-entered by the same thread
_loaded: dict[str, Any] = {}


def once(key: str, load: Callable[[], T]) -> T:
    """`load()` the first time `key` is asked for, by whichever thread asks first; the same object after that."""
    try:
        return _loaded[key]
    except KeyError:
        with _lock:
            if key not in _loaded:
                _loaded[key] = load()
            return _loaded[key]


def trie(name: str) -> marisa_trie.BytesTrie:
    """A trie of the package data by its path under `data/` (`"morph/lemmas.marisa"`)."""
    return once(name, lambda: _open_trie(DATA_DIR / name))


def table(name: str) -> dict[str, Any]:
    """A JSON table of the package data by its path under `data/` (`"text/lists.json"`)."""
    return once(name, lambda: json.loads((DATA_DIR / name).read_text(encoding="utf-8")))


def _open_trie(path: Path) -> marisa_trie.BytesTrie:
    return marisa_trie.BytesTrie().mmap(str(path))
