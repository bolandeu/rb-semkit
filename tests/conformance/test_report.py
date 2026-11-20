"""The area reports `docs/vba/conformance/<area>.md` against the case files: each is what scripts/conformance_report.py
writes from them now. The summary `docs/vba/conformance.md` is checked only by `--check` (the epic check), so parallel
area tasks never edit the same report file; here `--check` is shown to fail on a stale summary.

An area report has a summary row and a section per public function (a case file); a section lists the deviations (the
cases with `expected` != `vba`) and the xfail cases by case id.
"""

from __future__ import annotations

import re
import subprocess
import sys
from itertools import groupby
from pathlib import Path

import pytest

from .case_files import case_files

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "docs" / "vba" / "conformance"
SCRIPT = ROOT / "scripts" / "conformance_report.py"
SECTION = re.compile(r"^## (.+)$", re.MULTILINE)
SUBSECTION = re.compile(r"^### (.+)$", re.MULTILINE)
AREAS = {area: list(files) for area, files in groupby(case_files(), key=lambda file: file.area)}


def _report(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)  # noqa: S603


@pytest.fixture(scope="module")
def written(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("reports")
    assert _report("--out", str(out)).returncode == 0
    return out


def _split(text: str, heading: re.Pattern[str]) -> dict[str, str]:
    parts = heading.split(text)
    return dict(zip(parts[1::2], parts[2::2], strict=True))


def _first_cells(table: str) -> list[str]:
    """The first cell of each body row of the markdown table in `table` (its header and rule rows left out)."""
    rows = [line for line in table.splitlines() if line.startswith("| ")]
    return [row.split(" | ")[0].removeprefix("| ") for row in rows[1:]]


def test_check_passes_on_fresh_reports_and_fails_on_a_stale_summary(written: Path, tmp_path: Path) -> None:
    for path in written.rglob("*.md"):
        copy = tmp_path / path.relative_to(written)
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(path.read_bytes())
    assert _report("--out", str(tmp_path), "--check").returncode == 0

    summary = tmp_path / "conformance.md"
    summary.write_text(summary.read_text(encoding="utf-8").replace("**All**", "**Every**"), encoding="utf-8")
    result = _report("--out", str(tmp_path), "--check")

    assert result.returncode == 1
    assert str(summary) in result.stderr
    assert summary.read_text(encoding="utf-8").count("**Every**") == 1  # --check writes nothing
