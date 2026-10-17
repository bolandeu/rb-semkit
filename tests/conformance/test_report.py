"""docs/vba/conformance.md against the case files: it is what scripts/conformance_report.py writes from them now.

The report has a summary row and a section per public function (a case file); a section lists the deviations (the
cases with `expected` != `vba`) and the xfail cases by case id.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from .case_files import case_files

ROOT = Path(__file__).resolve().parents[2]
REPORT_FILE = ROOT / "docs" / "vba" / "conformance.md"
SCRIPT = ROOT / "scripts" / "conformance_report.py"
SECTION = re.compile(r"^## (.+)$", re.MULTILINE)
SUBSECTION = re.compile(r"^### (.+)$", re.MULTILINE)


def _split(text: str, heading: re.Pattern[str]) -> dict[str, str]:
    parts = heading.split(text)
    return dict(zip(parts[1::2], parts[2::2], strict=True))


def _first_cells(table: str) -> list[str]:
    """The first cell of each body row of the markdown table in `table` (its header and rule rows left out)."""
    rows = [line for line in table.splitlines() if line.startswith("| ")]
    return [row.split(" | ")[0].removeprefix("| ") for row in rows[1:]]


def test_the_committed_report_is_what_the_script_writes(tmp_path: Path) -> None:
    out = tmp_path / "conformance.md"

    subprocess.run([sys.executable, str(SCRIPT), "--out", str(out)], check=True, capture_output=True)  # noqa: S603

    assert REPORT_FILE.read_text(encoding="utf-8") == out.read_text(encoding="utf-8"), (
        "docs/vba/conformance.md is stale: run `uv run scripts/conformance_report.py`"
    )


def test_each_function_has_its_summary_row_and_section_with_its_deviations_and_xfails() -> None:
    sections = _split(REPORT_FILE.read_text(encoding="utf-8"), SECTION)
    files = case_files()

    summary = [re.sub(r"\[(.+)\]\(.*\)", r"\1", cell) for cell in _first_cells(sections.pop("Summary"))]

    assert summary == [*(file.function for file in files), "**All**"]
    assert list(sections) == [file.function for file in files]
    for file in files:
        tables = _split(sections[file.function], SUBSECTION)
        assert _first_cells(tables["Deviations"]) == [case.case_id for case in file.cases if case.expected != case.vba]
        assert _first_cells(tables["xfail"]) == [case.case_id for case in file.cases if case.xfail]
