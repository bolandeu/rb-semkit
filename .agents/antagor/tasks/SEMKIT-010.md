---
id: SEMKIT-010
title: 'Frame for parallel areas: discovered public names, data build parts, per-area
  conformance and benchmark; product text without the VBA'
status: in_progress
attempts: 0
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: feature
owns_paths:
- src/rb_semkit/__init__.py
- src/rb_semkit/core/
- scripts/build_data.py
- scripts/build_markers.py
- scripts/build_parts/
- scripts/bench.py
- scripts/bench_parts/
- scripts/data_manifest.py
- scripts/conformance_report.py
- tests/conformance/
- tests/matchers_vba/
- tests/analysis/test_bench.py
- tests/markers/test_build_markers.py
- docs/vba/conformance/
- docs/vba/deviations/
test_paths:
- tests/core/
- tests/conformance/
docs:
- docs/adr/0005-port-vba-fix-defects.md
- docs/vba/conformance.md
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on:
- SEMKIT-008
budget_usd: null
epic: E-002
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Каркас для параллельных областей E-002: публичные имена находятся сами
  (корень пакета не правится), сборка справочников, манифест, случаи сверки, отчёт
  и замер — по частям на область; отходы от VBA — в документе области. Плюс ADR 0006:
  docstring v1 без имён обработчиков и строк VBA (они уходят в шапки файлов сверки),
  тест это проверяет.'
---

E-002 adds three areas of the library side by side (change, morph + text, analysis), each by its own task in parallel. Today every area would edit the same shared files: the public name map of the package, the data build script, the conformance case loader and report, the benchmark script and the ADR of deviations. This task splits each shared file into per-area parts that are discovered, so an area task only adds its own files. It also makes the product text free of the add-in's VBA (ADR 0006).

1. Public names: a module of an area declares its public names; the package finds them, so a new area module is reachable as sk.<name> without editing the package root; `import rb_semkit` stays cheap (lazy loading kept).
2. Reference data build: the build script runs every per-area build part it finds; each part writes its data into the area's own folder of the package data and reports to its own per-area data manifest; the data test checks every manifest.
3. Conformance cases: case files are discovered in per-area subfolders (cases/<area>/<function>.tsv); the loader holds no list of function names; how a function's result renders (a Series, a list, a table) is chosen by the result type, plus an optional per-area hook module for special inputs. Move the existing case files into their area folders unchanged.
4. Deviations: a rule in a case may be quoted from ADR 0005 or from the area's deviations document (docs/vba/deviations/<area>.md); ADR 0005 gets one line pointing to those documents.
5. Report: the conformance report script writes one report per area (docs/vba/conformance/<area>.md, checked by a test against the script output) and the summary docs/vba/conformance.md, checked only by `scripts/conformance_report.py --check` (the epic check), so parallel area tasks never edit the same report file.
6. Benchmark: the benchmark script runs every per-area benchmark part it finds; the existing measurements move into parts with the same budgets.
7. ADR 0006: the public docstrings of the v1 modules describe the behaviour in user terms, without VBA handler names or line numbers; those move into the header notes of the case files. Replace the docstring test that demands VBA references with a test that no public docstring under the package names the VBA (the word VBA, the obfuscated handler names, «L<number>» line references).

## Per-area names (the area tasks rely on them exactly)

For an area <area> (v1 areas: text, markers, dupes, analysis, morph; E-002 adds change):
- package code: the area package under the package core; data: the area folder under the package data;
- build part: scripts/build_parts/<area>.py; data manifest: tests/conformance/data_manifest/<area>.json;
- benchmark part: scripts/bench_parts/<area>.py;
- case files: tests/conformance/cases/<area>/<function>.tsv; optional hook: tests/conformance/areas/<area>.py;
- deviations: docs/vba/deviations/<area>.md; report: docs/vba/conformance/<area>.md.
Move the v1 content into these names for the v1 areas.

## Acceptance

- Given a new module with declared public names inside an area package, When rb_semkit is imported and the name accessed, Then sk.<name> works without an edit of the package root, and importing rb_semkit loads no area module [check: tests/core/test_public_names.py]
- Given a new per-area build part, When the build script runs, Then it writes that area's data and manifest, and the data test checks it [check: tests/core/test_build_parts.py]
- Given a case file in a new area subfolder, When the conformance tests run, Then its cases run and their rules may be quoted from that area's deviations document [check: tests/conformance/test_cases.py]
- Given the conformance cases, When the report script runs, Then each area's report equals the committed one, and `--check` fails on a stale summary [check: tests/conformance/test_report.py]
- Given a new per-area benchmark part, When the benchmark script runs, Then the part's measurements run with their budgets [check: tests/core/test_bench_parts.py]
- Given the package sources, When the docstring test runs, Then no public docstring names the VBA or a VBA line; the VBA references stand in the case file headers [check: tests/core/test_no_vba_in_docs.py]

## How to test

Public library seam (import rb_semkit as sk) and the scripts' own entry points, with temporary area modules, build parts and case files created by the tests.
## Basis

The v1 package root (lazy name map), the data build and manifest scripts, the conformance loader, report and benchmark of SEMKIT-004/006/008; ADR 0005 and ADR 0006.

## Read first

- `docs/adr/0006-vba-is-a-porting-source.md`
- `docs/adr/0005-port-vba-fix-defects.md`
- `CONTEXT.md`

## Out of scope

- New functions of any area: the area tasks add them.
- Changing behaviour of v1 functions or the values of existing cases.
