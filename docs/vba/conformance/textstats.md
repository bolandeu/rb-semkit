# Conformance of the textstats area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/textstats/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [text_stats](#text_stats) | 10 | 10 | 0 | 0 |
| **All** | **10** | **10** | **0** | **0** |

## text_stats

textstats. No VBA handler: text_stats is semkit's own set of text metrics (SEMKIT-017), defined in its docstring; the `vba` column repeats `expected`. Counted by hand: the sample has 7 words, the stopwords и and в (2/7), the lemma диван three times (sqrt 3 = 1.73, 3/7).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `text_stats` | 10 | 10 | 0 | 0 |

### Deviations

None.

### xfail

None.
