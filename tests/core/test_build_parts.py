"""scripts/build_data.py runs every build part it finds: each writes its area's data and its area's data manifest.

The tests write a temporary part, its source and its config, then check the built data against the built manifest
the way tests/conformance/test_data.py checks the package data.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.conformance.manifests import mismatches

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "build_data.py"
PART = '''"""A temporary area: the colors of a text file, one per line, repeats dropped."""

from build_parts import Entry, read_lines, write_json


def manifest(sources):
    lines = read_lines(sources["colors"])
    entry = Entry("colors.txt: every line", len(lines))
    for index, line in enumerate(lines):
        if line in lines[:index]:
            entry.drop(line, "a repeat of an earlier item")
    return {"colors.json:colors": entry}


def build(sources, out):
    write_json(out / "colors.json", {"colors": list(dict.fromkeys(read_lines(sources["colors"])))})
'''


def _run(tmp_path: Path, sources: str) -> subprocess.CompletedProcess[str]:
    """The build script with only the temporary part and the config `[sources]` + `sources`, in folders of `tmp_path`."""
    (tmp_path / "parts").mkdir()
    (tmp_path / "parts" / "zarea.py").write_text(PART, encoding="utf-8")
    (tmp_path / "config.toml").write_text(f"[sources]\n{sources}", encoding="utf-8")
    folders = {"--config": "config.toml", "--out": "data", "--manifests": "manifests", "--parts": "parts"}
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), *(arg for flag, name in folders.items() for arg in (flag, str(tmp_path / name)))],
        capture_output=True,
        text=True,
        check=False,
    )


def _build(tmp_path: Path) -> subprocess.CompletedProcess[str]:
    (tmp_path / "colors.txt").write_text("red\ngreen\nred\nblue\n", encoding="utf-8")
    return _run(tmp_path, f'colors = "{tmp_path / "colors.txt"}"\n')


def test_a_new_part_writes_the_data_of_its_area_and_its_manifest(tmp_path: Path) -> None:
    result = _build(tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads((tmp_path / "data" / "zarea" / "colors.json").read_text()) == {"colors": ["red", "green", "blue"]}
    manifest = json.loads((tmp_path / "manifests" / "zarea.json").read_text())
    assert manifest == {
        "zarea/colors.json:colors": {
            "source": "colors.txt: every line",
            "source_items": 4,
            "bundled_items": 3,
            "dropped": [{"item": "red", "reason": "a repeat of an earlier item"}],
            "added": [],
        }
    }


def test_the_data_test_checks_the_manifest_of_a_new_area(tmp_path: Path) -> None:
    assert _build(tmp_path).returncode == 0
    assert mismatches(tmp_path / "data", tmp_path / "manifests") == []

    (tmp_path / "data" / "zarea" / "colors.json").write_text('{"colors": ["red"]}\n', encoding="utf-8")

    assert mismatches(tmp_path / "data", tmp_path / "manifests") == [
        "zarea/colors.json:colors: 1 items bundled, the manifest says 3"
    ]


def test_a_missing_source_exits_naming_it_and_writes_nothing(tmp_path: Path) -> None:
    result = _run(tmp_path, f'colors = "{tmp_path / "nope.txt"}"\n')

    assert result.returncode == 1
    assert "nope.txt" in result.stderr
    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "manifests").exists()


def test_a_source_the_config_lacks_exits_naming_its_key(tmp_path: Path) -> None:
    result = _run(tmp_path, "")

    assert result.returncode == 1
    assert "[sources] colors" in result.stderr
