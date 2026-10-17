"""The wordlists build part: cleaning, the manifest against the source files and the data, the committed data."""

from __future__ import annotations

import gzip
import importlib
import subprocess
import sys
import tomllib
from pathlib import Path
from types import ModuleType

import pytest

from rb_semkit.core import datastore, wordlists
from rb_semkit.core.wordlists import bundled

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CONFIG = SCRIPTS / "build_data.toml"
SOURCES = tomllib.loads(CONFIG.read_text())["sources"]
BUKVARIX = Path(SOURCES["bukvarix"])
WORDLISTS = datastore.DATA_DIR / "wordlists"


@pytest.fixture
def part(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    monkeypatch.syspath_prepend(str(SCRIPTS))  # the part imports build_parts, as scripts/build_data.py does
    return importlib.import_module("area_parts").load_parts(SCRIPTS / "build_parts")["wordlists"]


def _line(name: str, origin: str | None = None, file: str | None = None) -> dict[str, str]:
    line = {"name": name, "description": "d", "source": "s", "file": file or f"wordlists/{name}.txt.gz"}
    return line | ({"origin": origin} if origin else {})


def _sources(folder: Path, files: dict[str, bytes]) -> Path:
    for name, content in files.items():
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_bytes(content)
    return folder


def test_a_list_is_cleaned_of_bom_crlf_blanks_and_repeats_in_order(part: ModuleType, tmp_path: Path) -> None:
    source = _sources(tmp_path / "src", {"minus/A.txt": "﻿b\r\n a \r\n\r\nb\r\n\r\nc".encode()})

    part.write_lists([_line("minus/a", "minus/A.txt")], source, tmp_path / "data")

    built = gzip.decompress((tmp_path / "data" / "wordlists" / "minus" / "a.txt.gz").read_bytes())
    assert built.decode("utf-8") == "b\na\nc\n"


def test_a_source_file_without_a_manifest_line_fails_the_check_naming_it(part: ModuleType, tmp_path: Path) -> None:
    source = _sources(tmp_path / "src", {"minus/A.txt": b"a", "minus/New.txt": b"n"})

    with pytest.raises(Exception, match=r"minus/New\.txt: a source file with no manifest line"):
        part.check_sources([_line("minus/a", "minus/A.txt")], source)


def test_a_manifest_line_without_a_file_fails_the_check_naming_it(part: ModuleType, tmp_path: Path) -> None:
    source = _sources(tmp_path / "src", {"minus/A.txt": b"a"})
    lines = [_line("minus/a", "minus/A.txt"), _line("minus/gone", "minus/Gone.txt")]

    with pytest.raises(Exception, match=r"minus/gone: a manifest line without its source file minus/Gone\.txt"):
        part.check_sources(lines, source)


def test_a_pointer_to_data_that_is_not_there_fails_naming_it(part: ModuleType, tmp_path: Path) -> None:
    (tmp_path / "markers").mkdir()
    (tmp_path / "markers" / "geo.txt.gz").write_bytes(b"")
    (tmp_path / "text").mkdir()
    (tmp_path / "text" / "lists.json").write_text('{"stopwords": []}', encoding="utf-8")
    present = [_line("markers/geo", file="markers/geo.txt.gz"), _line("stop/s", file="text/lists.json:stopwords")]
    part.check_pointers(present, tmp_path)

    for missing in ("markers/none.txt.gz", "text/lists.json:nope"):
        with pytest.raises(Exception, match="a manifest line without its data"):
            part.check_pointers([_line("x/y", file=missing)], tmp_path)


def test_two_lines_with_one_name_fail_the_check(part: ModuleType, tmp_path: Path) -> None:
    source = _sources(tmp_path / "src", {"A.txt": b"a", "B.txt": b"b"})

    with pytest.raises(Exception, match="x/a: a name on two manifest lines"):
        part.check_sources([_line("x/a", "A.txt"), _line("x/a", "B.txt")], source)


def test_the_manifest_has_a_line_with_every_key_for_each_bundled_list() -> None:
    lines = tomllib.loads((WORDLISTS / "manifest.toml").read_text(encoding="utf-8"))["lists"]

    assert len(lines) == len({line["name"] for line in lines}) == 86
    for line in lines:
        assert {"name", "description", "source", "file"} <= set(line), line
        assert line["description"].strip(), line["name"]
        assert any("а" <= char.lower() <= "я" for char in line["description"]), f"{line['name']}: not in Russian"


def test_every_manifest_line_has_its_data_and_every_file_of_the_folder_has_its_line() -> None:
    entries = bundled.entries()
    files = {path.relative_to(datastore.DATA_DIR).as_posix() for path in WORDLISTS.rglob("*.txt.gz")}

    assert all(bundled.items(name) for name in entries)
    built = {entry.file for entry in entries.values() if entry.file.startswith("wordlists/")}
    assert built == files


@pytest.mark.skipif(not BUKVARIX.exists(), reason="the Bukvarix sources are not on this machine")
def test_every_bukvarix_file_has_a_line_and_the_committed_lists_are_what_the_build_writes(tmp_path: Path) -> None:
    result = subprocess.run(  # noqa: S603
        [
            sys.executable,
            str(SCRIPTS / "build_data.py"),
            "--out",
            str(tmp_path / "data"),
            "--manifests",
            str(tmp_path / "manifests"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    built = tmp_path / "data" / "wordlists"
    committed = sorted(path.relative_to(WORDLISTS) for path in WORDLISTS.rglob("*") if path.is_file())
    assert sorted(path.relative_to(built) for path in built.rglob("*") if path.is_file()) == committed
    for path in committed:
        assert (built / path).read_bytes() == (WORDLISTS / path).read_bytes(), f"{path}: rebuild the package data"
    assert len(list(BUKVARIX.rglob("*.txt"))) == 66


def test_the_names_in_the_scheme_of_the_task(home: Path) -> None:
    names = {entry.name for entry in wordlists.names()}

    assert {f"minus/{kind}" for kind in ("universal", "computer", "free", "cheap", "handmade", "abusive")} <= names
    assert {"combine/russia-cities-500k", "combine/spb-metro", "combine/tourism", "combine/tourism/czech"} <= names
    assert {f"markers/{name}" for name in ("geo", "mosmetro", "cars", "names")} <= names


def test_an_item_the_manifest_line_drops_is_not_built_and_the_entry_says_why(part: ModuleType, tmp_path: Path) -> None:
    source = _sources(tmp_path / "src", {"minus/A.txt": "купить\nскачать\n".encode()})
    line = _line("minus/a", "minus/A.txt") | {"drop": {"купить": "a commercial core buys"}}

    part.write_lists([line], source, tmp_path / "data")

    built = gzip.decompress((tmp_path / "data" / "wordlists" / "minus" / "a.txt.gz").read_bytes())
    assert built.decode("utf-8") == "скачать\n"
    assert part.entry(line, source).dropped == [{"item": "купить", "reason": "a commercial core buys"}]


def test_the_universal_minus_list_holds_no_buy_word() -> None:
    items = bundled.items("minus/universal")

    assert "купить" not in items
    assert "скачать" in items
