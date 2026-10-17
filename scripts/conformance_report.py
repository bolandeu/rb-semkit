#!/usr/bin/env python3
"""Write the conformance reports: the library against the add-in's VBA, from the conformance case files.

    uv run scripts/conformance_report.py [--out docs/vba] [--check]

One report per area (a folder of tests/conformance/cases), `<out>/conformance/<area>.md`: a section per public
function (a case file) with the VBA handlers and lines its cases are traced from, the counts per function and verb,
the cases where semkit deviates from the VBA (with the rule and why) and the xfail cases; a table over the area's
functions comes first. The summary `<out>/conformance.md` has a row per area. tests/conformance/test_report.py checks
the area reports; `--check` writes nothing and fails when a report, the summary too, is not what the script writes.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.conformance.case_files import Case, CaseFile, case_files  # noqa: E402

DEFAULT_OUT = ROOT / "docs" / "vba"
SUMMARY = "conformance.md"
AREAS = "conformance"
COUNTS = ("Cases", "As the VBA", "Deviations", "xfail")
DEVIATIONS = "Deviations"
XFAIL = "xfail"
INTRO = """\
# Conformance with the !SEMTools VBA

`scripts/conformance_report.py` writes this file and the area reports `conformance/<area>.md` from the case files
`tests/conformance/cases/<area>/*.tsv`; do not edit them. An area task updates its own area report; this summary is
checked by `scripts/conformance_report.py --check` when the epic closes. A case is one call of the public API
(`import rb_semkit as sk`) on one input. `vba` is what the add-in's VBA handler gives, traced by hand from
`docs/vba/matchers.md` and `docs/vba/analysis.md`; `semkit` is what the library gives.

- **As the VBA**: semkit gives the VBA value.
- **Deviations**: semkit gives another value. ADR 0005 or the area's deviations document (`docs/vba/deviations/<area>.md`)
  allows it: the case names the rule and says why.
- **xfail**: semkit does not give the expected value yet; the Architect has the finding.

A verb with no VBA handler is derived from a near handler, as its notes say; its `vba` is the derived value.
A value is in quotes; « | » separates the cells of a whole-column input or result.
"""
AREA_INTRO = """\
# Conformance of the {area} area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/{area}/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).
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


def _cases(files: list[CaseFile]) -> list[Case]:
    return [case for file in files for case in file.cases]


def _total(files: list[CaseFile], *counts: int) -> list[str]:
    return ["**All**", *(f"**{count}**" for count in (*counts, *_counts(_cases(files))))]


def _summary(areas: dict[str, list[CaseFile]]) -> list[str]:
    rows = [
        [f"[{area}]({AREAS}/{area}.md)", str(len(files)), *map(str, _counts(_cases(files)))]
        for area, files in areas.items()
    ]
    every = [file for files in areas.values() for file in files]
    return ["## Summary", "", *_table(("Area", "Functions", *COUNTS), [*rows, _total(every, len(every))])]


def _area_summary(files: list[CaseFile]) -> list[str]:
    rows = [[f"[{file.function}](#{file.function})", *map(str, _counts(file.cases))] for file in files]
    return ["## Summary", "", *_table(("Function", *COUNTS), [*rows, _total(files)])]


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


def _join(*parts: Sequence[str]) -> str:
    return "\n\n".join("\n".join(part) for part in parts) + "\n"


def reports(files: list[CaseFile]) -> dict[str, str]:
    """Each report by its path under the output folder: the summary and one per area."""
    areas = {area: list(group) for area, group in groupby(files, key=lambda file: file.area)}
    texts = {SUMMARY: _join(INTRO.rstrip("\n").split("\n"), _summary(areas))}
    for area, area_files in areas.items():
        intro = AREA_INTRO.format(area=area).rstrip("\n").split("\n")
        texts[f"{AREAS}/{area}.md"] = _join(intro, _area_summary(area_files), *map(_section, area_files))
    return texts


def _matches(path: Path, text: str) -> bool:
    return path.is_file() and path.read_text(encoding="utf-8") == text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="the folder of the summary and the area reports")
    parser.add_argument("--check", action="store_true", help="write nothing; fail when a report is stale")
    args = parser.parse_args(argv)
    texts = reports(case_files())
    if args.check:
        stale = [name for name, text in texts.items() if not _matches(args.out / name, text)]
        for name in stale:
            print(
                f"conformance_report: {args.out / name} is stale: run `uv run scripts/conformance_report.py`",
                file=sys.stderr,
            )
        return 1 if stale else 0
    for name, text in texts.items():
        (args.out / name).parent.mkdir(parents=True, exist_ok=True)
        (args.out / name).write_text(text, encoding="utf-8")
    print(f"conformance_report: wrote {len(texts)} reports into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
