"""The bundled data against data_manifest.json (built from the !SEMTools sources by scripts/data_manifest.py).

Each bundled file, or each table of a JSON file, holds the number of items the manifest says; the source count less
the dropped items plus the added ones is that number; every dropped item has its reason; and no bundled file is
missing from the manifest. Runs offline: only the package data and the manifest are read. Where the sources are on
the machine, the manifest is also checked to be what scripts/data_manifest.py builds from them.
"""

from __future__ import annotations

import gzip
import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from rb_semkit.core import datastore

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_FILE = Path(__file__).resolve().parent / "data_manifest.json"
MANIFEST = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
SOURCES = tomllib.loads((ROOT / "scripts" / "build_data.toml").read_text())["sources"]


def _bundled_items(name: str) -> int:
    """The items of a bundled file: the key–value pairs of a trie, the entries of a JSON table, the lines of a list."""
    path, _, table = name.partition(":")
    if path.endswith(".marisa"):
        return len(datastore.trie(path))
    if table:
        return len(datastore.table(path)[table])
    return len(gzip.decompress((datastore.DATA_DIR / path).read_bytes()).decode("utf-8").splitlines())


def _bundled_names() -> set[str]:
    names = set()
    for path in datastore.DATA_DIR.rglob("*"):
        relative = path.relative_to(datastore.DATA_DIR).as_posix()
        if path.suffix == ".json":
            names |= {f"{relative}:{table}" for table in datastore.table(relative)}
        elif path.suffix in {".marisa", ".gz"}:
            names.add(relative)
    return names


@pytest.mark.parametrize("name", sorted(MANIFEST))
def test_a_bundled_file_holds_the_items_of_the_manifest(name: str) -> None:
    entry = MANIFEST[name]

    assert _bundled_items(name) == entry["bundled_items"]
    assert entry["source_items"] - len(entry["dropped"]) + len(entry["added"]) == entry["bundled_items"]


@pytest.mark.parametrize("name", sorted(MANIFEST))
def test_every_dropped_item_has_its_reason(name: str) -> None:
    changes = MANIFEST[name]["dropped"] + MANIFEST[name]["added"]

    assert all(change["item"] and change["reason"] for change in changes)


def test_every_bundled_file_is_in_the_manifest() -> None:
    assert _bundled_names() == set(MANIFEST)


@pytest.mark.skipif(
    not all(Path(path).exists() for path in SOURCES.values()), reason="the !SEMTools sources are not on this machine"
)
def test_the_manifest_is_what_the_script_builds_from_the_sources(tmp_path: Path) -> None:
    out = tmp_path / "manifest.json"

    result = subprocess.run(  # noqa: S603
        [sys.executable, str(ROOT / "scripts" / "data_manifest.py"), "--out", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert out.read_bytes() == MANIFEST_FILE.read_bytes()
