"""The bundled marker lists (`data/markers/<name>.txt.gz`, one phrase per line, built by scripts/build_parts/markers.py).

The automaton of a list is built on the first use of the list: once per process, safe when many threads ask at once.
"""

from __future__ import annotations

import gzip

from .. import datastore
from ..text.matchers.phrases import PhraseList

MARKERS_DIR = datastore.DATA_DIR / "markers"
SUFFIX = ".txt.gz"


def names() -> tuple[str, ...]:
    """The names of the bundled lists, sorted."""
    return datastore.once(
        "marker_names", lambda: tuple(sorted(path.name.removesuffix(SUFFIX) for path in MARKERS_DIR.glob(f"*{SUFFIX}")))
    )


def bundled(name: str) -> PhraseList:
    """The bundled list `name`; `name` is one of `names()`."""
    return datastore.once(f"marker_list/{name}", lambda: PhraseList(name, _read(name)))


def _read(name: str) -> list[str]:
    return gzip.decompress((MARKERS_DIR / f"{name}{SUFFIX}").read_bytes()).decode("utf-8").splitlines()
