"""The data of the wordlists area: the Bukvarix word lists, cleaned, and the manifest of every bundled list.

    <name>.txt.gz   one item per line (`minus/cheap.txt.gz`); the file of a list is the `file` of its manifest line
    manifest.toml   the manifest, copied as it is written in wordlists.toml next to this part

Source: `bukvarix` (the folder with minus/, stop/ and combiner/). Each list is its file without the BOM, with LF line
ends, every line trimmed, empty lines and repeats dropped, in the order of the file. A line of the manifest without an
`origin` is a list of another area (the marker lists, the stopwords of the text area): it only names that data.
"""

from __future__ import annotations

import gzip
import json
import shutil
import tomllib
from pathlib import Path

from build_parts import REPEAT, Entry, SourceMissing

MANIFEST = Path(__file__).with_suffix(".toml")
MANIFEST_NAME = "manifest.toml"
SOURCE_SUFFIX = ".txt"
BUILT_PREFIX = "wordlists/"


class ManifestMismatch(SourceMissing):
    """The manifest and the files it names disagree."""


def read_manifest(path: Path = MANIFEST) -> list[dict[str, str]]:
    return tomllib.loads(path.read_text(encoding="utf-8"))["lists"]


def read_items(path: Path) -> list[str]:
    """The lines of a source list, trimmed, without the BOM and the empty ones; repeats stay."""
    if not path.is_file():
        raise SourceMissing(f"source file not found: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def _table_exists(data_dir: Path, file: str) -> bool:
    path, _, table = file.partition(":")
    if not (data_dir / path).is_file():
        return False
    return not table or table in json.loads((data_dir / path).read_text(encoding="utf-8"))


def check_sources(lines: list[dict[str, str]], source_dir: Path) -> None:
    """Raise ManifestMismatch naming every source file without a manifest line and every line without its file."""
    origins = {line["origin"] for line in lines if "origin" in line}
    problems = [
        f"{path.relative_to(source_dir).as_posix()}: a source file with no manifest line"
        for path in sorted(source_dir.rglob(f"*{SOURCE_SUFFIX}"))
        if path.relative_to(source_dir).as_posix() not in origins
    ]
    problems += [
        f"{line['name']}: a manifest line without its source file {line['origin']}"
        for line in lines
        if "origin" in line and not (source_dir / line["origin"]).is_file()
    ]
    problems += [
        f"{line['name']}: the file {line['file']} of a built list is outside {BUILT_PREFIX}"
        for line in lines
        if "origin" in line and not line["file"].startswith(BUILT_PREFIX)
    ]
    names = [line["name"] for line in lines]
    problems += [f"{name}: a name on two manifest lines" for name in sorted({n for n in names if names.count(n) > 1})]
    if problems:
        raise ManifestMismatch("; ".join(problems))


def check_pointers(lines: list[dict[str, str]], data_dir: Path) -> None:
    """Raise ManifestMismatch naming every line of a list built elsewhere whose data is not there."""
    problems = [
        f"{line['name']}: a manifest line without its data {line['file']}"
        for line in lines
        if "origin" not in line and not _table_exists(data_dir, line["file"])
    ]
    if problems:
        raise ManifestMismatch("; ".join(problems))


def _entry(line: dict[str, str], source_dir: Path) -> Entry:
    items = read_items(source_dir / line["origin"])
    entry = Entry(f"bukvarix/{line['origin']}", len(items))
    seen: set[str] = set()
    for item in items:
        if item in seen:
            entry.drop(item, REPEAT)
        seen.add(item)
    return entry


def manifest(sources: dict[str, Path]) -> dict[str, Entry]:
    lines = read_manifest()
    check_sources(lines, sources["bukvarix"])
    return {
        line["file"].removeprefix(BUILT_PREFIX): _entry(line, sources["bukvarix"]) for line in lines if "origin" in line
    }


def write_lists(lines: list[dict[str, str]], source_dir: Path, data_dir: Path) -> None:
    """Each built list of `lines` as its file under `data_dir`: the items of its source, repeats dropped, gzipped."""
    for line in lines:
        if "origin" in line:
            items = dict.fromkeys(read_items(source_dir / line["origin"]))
            target = data_dir / line["file"]
            target.parent.mkdir(parents=True, exist_ok=True)
            text = "\n".join(items) + "\n"
            target.write_bytes(gzip.compress(text.encode("utf-8"), compresslevel=9, mtime=0))


def build(sources: dict[str, Path], out: Path) -> None:
    lines = read_manifest()
    check_sources(lines, sources["bukvarix"])
    check_pointers(lines, out.parent)
    write_lists(lines, sources["bukvarix"], out.parent)
    shutil.copyfile(MANIFEST, out / MANIFEST_NAME)
