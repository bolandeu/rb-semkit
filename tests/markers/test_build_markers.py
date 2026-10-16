"""scripts/build_markers.py on the sandbox xlsx: re-runnable, byte-identical, the committed lists are its output."""

from __future__ import annotations

import gzip
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pandas as pd
import pytest

import rb_semkit as sk

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_markers.py"
CONFIG = ROOT / "scripts" / "build_data.toml"
PACKAGE_MARKERS = ROOT / "src" / "rb_semkit" / "data" / "markers"
SPISKI = Path(tomllib.loads(CONFIG.read_text())["sources"]["markers"])
LIST_NAMES = (
    *("geo", "mosmetro", "districts", "MO", "citiesRu", "questions", "fun", "DIY", "edu"),
    *("game", "sale", "rent", "reviews", "color", "material", "origin", "cars", "names"),
)

pytestmark = pytest.mark.skipif(not SPISKI.is_dir(), reason="the !SEMTools sandbox sources are not on this machine")


def _build(out: Path, config: Path = CONFIG) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), "--config", str(config), "--out", str(out)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("built")
    result = _build(out)
    assert result.returncode == 0, result.stderr
    return out / "markers"


def _lines(path: Path) -> list[str]:
    return gzip.decompress(path.read_bytes()).decode("utf-8").splitlines()


def test_two_runs_are_byte_identical_and_match_the_package(built: Path, tmp_path: Path) -> None:
    assert _build(tmp_path).returncode == 0
    for name in LIST_NAMES:
        assert (tmp_path / "markers" / f"{name}.txt.gz").read_bytes() == (built / f"{name}.txt.gz").read_bytes(), name
        assert (PACKAGE_MARKERS / f"{name}.txt.gz").read_bytes() == (built / f"{name}.txt.gz").read_bytes(), (
            f"{name}: rebuild the package data"
        )
    assert sorted(path.name for path in built.iterdir()) == sorted(f"{name}.txt.gz" for name in LIST_NAMES)


def test_lists_are_stripped_deduped_and_keep_the_display_case(built: Path) -> None:
    geo = _lines(built / "geo.txt.gz")

    assert len(geo) == len(set(geo)) == 36_012  # 36 013 rows, one repeated
    assert "Москве" in geo
    assert all(line == line.strip() and line for line in geo)


def test_diy_takes_its_first_sheet_and_cars_column_a(built: Path) -> None:
    diy = _lines(built / "DIY.txt.gz")
    cars = _lines(built / "cars.txt.gz")

    assert len(diy) == 206  # the 2nd sheet (Google Sheets formula junk) is dropped
    assert cars[0] == "Таун Эйс Ноух 4"
    assert "Тип" not in cars  # column C of the brand table
    assert "En" not in cars  # a header of the brand table, column E


@pytest.mark.parametrize("name", LIST_NAMES)
def test_every_list_loads_and_matches_its_own_first_item(built: Path, name: str) -> None:
    first = _lines(built / f"{name}.txt.gz")[0]

    mask = sk.find(pd.Series([first, "нечто совсем другое"]), sk.markers([name]))

    assert mask.tolist() == [True, False]


def test_a_missing_xlsx_exits_naming_it(tmp_path: Path) -> None:
    spiski = tmp_path / "spiski"
    shutil.copytree(SPISKI, spiski, ignore=shutil.ignore_patterns("cars.xlsx"))
    config = tmp_path / "build_data.toml"
    config.write_text(f'[sources]\nmarkers = "{spiski}"\n')

    result = _build(tmp_path / "out", config)

    assert result.returncode != 0
    assert "cars.xlsx" in result.stderr
    assert not (tmp_path / "out" / "markers").exists()


def test_gitattributes_marks_all_built_data_as_generated() -> None:
    lines = (ROOT / ".gitattributes").read_text().splitlines()

    marked = {line.split()[0] for line in lines if line.endswith("linguist-generated")}
    assert marked == {
        "src/rb_semkit/data/morph/**",
        "src/rb_semkit/data/lists/**",
        "src/rb_semkit/data/markers/**",
    }
    assert "ADR 0002" in lines[0]
