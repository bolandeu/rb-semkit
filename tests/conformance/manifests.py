"""The data manifests (`data_manifest/<area>.json`, written by scripts/build_data.py) against the data they describe.

A manifest names each file of its area's data folder (a JSON file: each of its tables) by its path under the data
folder, with its source, the number of items in the source, the number the build keeps, and every item the build drops
or adds, with the reason. An item is a key–value pair of a trie, an entry of a JSON table, a line of a list.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

import marisa_trie  # ty: ignore[unresolved-import]  # a compiled extension without type stubs

MANIFEST_DIR = Path(__file__).resolve().parent / "data_manifest"
DATA_SUFFIXES = (".marisa", ".json", ".gz")


def read_manifests(manifest_dir: Path) -> dict[str, dict[str, Any]]:
    """The manifest of each area, by area."""
    return {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in sorted(manifest_dir.glob("*.json"))}


def _table(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bundled_items(data_dir: Path, name: str) -> int:
    path, _, table = name.partition(":")
    if path.endswith(".marisa"):
        return len(marisa_trie.BytesTrie().mmap(str(data_dir / path)))
    if table:
        return len(_table(data_dir / path)[table])
    return len(gzip.decompress((data_dir / path).read_bytes()).decode("utf-8").splitlines())


def bundled_names(data_dir: Path) -> set[str]:
    names = set()
    for path in data_dir.rglob("*"):
        relative = path.relative_to(data_dir).as_posix()
        if path.suffix == ".json":
            names |= {f"{relative}:{table}" for table in _table(path)}
        elif path.suffix in DATA_SUFFIXES:
            names.add(relative)
    return names


def _entry_mismatches(data_dir: Path, name: str, entry: dict[str, Any]) -> list[str]:
    found = []
    items = bundled_items(data_dir, name)
    if items != entry["bundled_items"]:
        found.append(f"{name}: {items} items bundled, the manifest says {entry['bundled_items']}")
    if entry["source_items"] - len(entry["dropped"]) + len(entry["added"]) != entry["bundled_items"]:
        found.append(f"{name}: the source items less the dropped plus the added are not the bundled items")
    if not all(change["item"] and change["reason"] for change in entry["dropped"] + entry["added"]):
        found.append(f"{name}: a dropped or added item without its item or reason")
    return found


def mismatches(data_dir: Path, manifest_dir: Path) -> list[str]:
    """Where the data and the manifests disagree, one line each; none when they agree."""
    manifests = read_manifests(manifest_dir)
    described = {name: area for area, manifest in manifests.items() for name in manifest}
    bundled = bundled_names(data_dir)
    found = [f"{name}: bundled, but in no manifest" for name in sorted(bundled - set(described))]
    found += [
        f"{name}: in the manifest of {area}, but not bundled" for name, area in described.items() if name not in bundled
    ]
    found += [
        f"{name}: in the manifest of {area}, outside its folder"
        for name, area in described.items()
        if not name.startswith(f"{area}/")
    ]
    for manifest in manifests.values():
        for name, entry in manifest.items():
            if name in bundled:
                found += _entry_mismatches(data_dir, name, entry)
    return found
