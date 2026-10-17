#!/usr/bin/env python3
"""Write docs/vba/conformance.md: the library core against the add-in's VBA, from the conformance case files.

    uv run scripts/conformance_report.py [--out docs/vba/conformance.md]

One section per public function (a case file of tests/conformance/cases): the VBA handlers and lines its cases are
traced from, the counts per function and verb, the cases where semkit deviates from the VBA (with the ADR 0005 rule
and why) and the xfail cases. A summary table over all functions comes first. tests/conformance/test_report.py checks
that the committed report is what this script writes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.conformance.case_files import Case, CaseFile, case_files  # noqa: E402

DEFAULT_OUT = ROOT / "docs" / "vba" / "conformance.md"
COUNTS = ("Cases", "As the VBA", "Deviations", "xfail")
DEVIATIONS = "Deviations"
XFAIL = "xfail"
INTRO = """\
# Conformance with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/*.tsv`; do not edit it.
A case is one call of the public API (`import rb_semkit as sk`) on one input. `vba` is what the add-in's VBA handler
gives, traced by hand from `docs/vba/matchers.md` and `docs/vba/analysis.md`; `semkit` is what the library gives.

- **As the VBA**: semkit gives the VBA value.
- **Deviations**: semkit gives another value. ADR 0005 allows it: the case names the rule and says why.
- **xfail**: semkit does not give the expected value yet; the Architect has the finding.

A verb with no VBA handler is derived from a near handler, as its notes say; its `vba` is the derived value.
A value is in quotes; « | » separates the cells of a whole-column input or result.
"""


def _counts(cases: list[Case]) -> list[int]:
    deviations = sum(case.expected != case.vba for case in cases)
    return [len(cases), len(cases) - deviations, deviations, sum(bool(case.xfail) for case in cases)]


def _text(text: str) -> str:
    return text.replace("|", "\\|")


def _value(text: str) -> str:
    return f'`"{_text(text)}"`'


def _table(header: tuple[str, ...], rows: list[list[str]]) -> list[str]:
    lines = [f"| {' | '.join(header)} |", f"|{'---|' * len(header)}"]
    return lines + [f"| {' | '.join(row)} |" for row in rows]


def _summary(files: list[CaseFile]) -> list[str]:
    rows = [[f"[{file.function}](#{file.function})", *map(str, _counts(file.cases))] for file in files]
    total = _counts([case for file in files for case in file.cases])
    rows.append(["**All**", *(f"**{count}**" for count in total)])
    return ["## Summary", "", *_table(("Function", *COUNTS), rows)]


def _cases_table(title: str, header: tuple[str, ...], rows: list[list[str]]) -> list[str]:
    return [f"### {title}", "", *(_table(header, rows) if rows else ["None."])]


def _section(file: CaseFile) -> list[str]:
    counts = []
    for name in sorted({case.function for case in file.cases}):
        cases = [case for case in file.cases if case.function == name]
        counts.append([f"`{name}`", *map(str, _counts(cases))])
    deviations = [
        [case.case_id, _value(case.input), _value(case.vba), _value(case.expected), _text(case.rule), _text(case.why)]
        for case in file.cases
        if case.expected != case.vba
    ]
    xfails = [
        [case.case_id, _value(case.input), _value(case.vba), _value(case.expected), _text(case.xfail)]
        for case in file.cases
        if case.xfail
    ]
    return [
        f"## {file.function}",
        "",
        file.notes,
        "",
        *_table(("Function", *COUNTS), counts),
        "",
        *_cases_table(DEVIATIONS, ("Case", "Input", "VBA", "semkit", "Rule", "Why"), deviations),
        "",
        *_cases_table(XFAIL, ("Case", "Input", "VBA", "Expected", "Reason"), xfails),
    ]


def render(files: list[CaseFile]) -> str:
    parts = [INTRO.rstrip("\n").split("\n"), _summary(files), *(_section(file) for file in files)]
    return "\n\n".join("\n".join(part) for part in parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="the report file to write")
    out = parser.parse_args().out
    out.write_text(render(case_files()), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
