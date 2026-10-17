#!/usr/bin/env python3
"""Build the bundled reference data (ADR 0002) and its data manifests from the !SEMTools sources.

    uv run scripts/build_data.py [--config scripts/build_data.toml] [--out src/rb_semkit/data]
                                 [--manifests tests/conformance/data_manifest] [--parts scripts/build_parts]

It runs every build part of the parts folder (`<area>.py`, the contract in scripts/build_parts/__init__.py): the part
writes the data of its area into `<out>/<area>/`, and the script writes what the part takes from its sources into the
area's data manifest `<manifests>/<area>.json`. The source paths come from `[sources]` of the config file
(docs/brief.md «Materials»). Every part reads its sources before any file is written; the same sources give
byte-identical files, so the script is safe to re-run. The built files are committed;
tests/conformance/test_data.py checks the package data against the manifests, offline.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

from area_parts import load_parts
from build_parts import Entry, SourceMissing, Sources

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = Path(__file__).with_suffix(".toml")
DEFAULT_OUT = ROOT / "src" / "rb_semkit" / "data"
DEFAULT_MANIFESTS = ROOT / "tests" / "conformance" / "data_manifest"
DEFAULT_PARTS = Path(__file__).resolve().parent / "build_parts"


def _manifest(area: str, entries: dict[str, Entry]) -> dict[str, dict]:
    for entry in entries.values():
        entry.bundled_items = entry.source_items - len(entry.dropped) + len(entry.added)
    return {f"{area}/{name}": vars(entry) for name, entry in sorted(entries.items())}


def build(sources: dict[str, Path], out: Path, manifests: Path, parts_dir: Path) -> None:
    found = load_parts(parts_dir)
    described = {area: _manifest(area, part.manifest(sources)) for area, part in found.items()}
    for area, part in found.items():
        part.build(sources, out / area)
        manifests.mkdir(parents=True, exist_ok=True)
        text = json.dumps(described[area], ensure_ascii=False, indent=1) + "\n"
        (manifests / f"{area}.json").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the bundled reference data from the !SEMTools sources.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="TOML with a [sources] table")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="the package data directory")
    parser.add_argument("--manifests", type=Path, default=DEFAULT_MANIFESTS, help="the data manifest directory")
    parser.add_argument("--parts", type=Path, default=DEFAULT_PARTS, help="the build parts directory")
    args = parser.parse_args(argv)
    sources = Sources({key: Path(value) for key, value in tomllib.loads(args.config.read_text())["sources"].items()})
    try:
        build(sources, args.out, args.manifests, args.parts)
    except SourceMissing as error:
        print(f"build_data: {error}", file=sys.stderr)
        return 1
    print(f"build_data: built {args.out} and {args.manifests}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
