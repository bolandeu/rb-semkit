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

## Summary

| Area | Functions | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|---|
| [analysis](conformance/analysis.md) | 3 | 41 | 26 | 15 | 0 |
| [dupes](conformance/dupes.md) | 1 | 102 | 89 | 13 | 0 |
| [markers](conformance/markers.md) | 1 | 44 | 35 | 9 | 0 |
| [morph](conformance/morph.md) | 3 | 45 | 27 | 18 | 0 |
| [text](conformance/text.md) | 14 | 260 | 219 | 41 | 0 |
| [textstats](conformance/textstats.md) | 1 | 10 | 10 | 0 | 0 |
| **All** | **23** | **502** | **406** | **96** | **0** |
