"""The bundled word lists: the manifest (`data/wordlists/manifest.toml`, built by scripts/build_parts/wordlists.py) and
the items of each list, loaded on the first use of the list.

A manifest line holds `name`, `description` (in Russian), `source` and `file`: a file under `data/` (`.txt.gz`, one
item per line) or `path.json:table`, a list of a JSON table.
"""

from __future__ import annotations

import gzip
import tomllib
from dataclasses import dataclass

from .. import datastore

MANIFEST = datastore.DATA_DIR / "wordlists" / "manifest.toml"
TABLE_SEPARATOR = ":"


@dataclass(frozen=True)
class Bundled:
    """One line of the manifest."""

    name: str
    description: str
    source: str
    file: str


def entries() -> dict[str, Bundled]:
    """The bundled lists by name, in the order of the manifest."""
    return datastore.once("wordlists/manifest", _read_manifest)


def items(name: str) -> list[str]:
    """The items of the bundled list `name`, one per line of its file; `name` is one of `entries()`."""
    return list(datastore.once(f"wordlists/{name}", lambda: _read_items(entries()[name].file)))


def _read_manifest() -> dict[str, Bundled]:
    lines = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))["lists"]
    return {line["name"]: Bundled(line["name"], line["description"], line["source"], line["file"]) for line in lines}


def _read_items(file: str) -> list[str]:
    path, _, table = file.partition(TABLE_SEPARATOR)
    if table:
        return datastore.table(path)[table]
    return gzip.decompress((datastore.DATA_DIR / path).read_bytes()).decode("utf-8").splitlines()
