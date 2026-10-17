# Conformance of the compare area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/compare/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [bm25](#bm25) | 5 | 5 | 0 | 0 |
| [compare_grams](#compare_grams) | 6 | 6 | 0 | 0 |
| [compare_stats](#compare_stats) | 6 | 6 | 0 | 0 |
| **All** | **17** | **17** | **0** | **0** |

## bm25

compare. No VBA handler: bm25 is the Okapi BM25 of semkit's own comparison (SEMKIT-019), defined in its docstring; the `vba` column repeats `expected`. Counted by hand: N 3, lengths 2, 2, 4 (average 8/3); for диван df 2, idf ln(1.6) = 0.47; for кресло df 1, idf ln(8/3) = 0.9808.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `bm25` | 5 | 5 | 0 | 0 |

### Deviations

None.

### xfail

None.

## compare_grams

compare. No VBA handler: compare_grams is semkit's own comparison with the competitors' texts (SEMKIT-019), defined in its docstring; the `vba` column repeats `expected`. Counted by hand: the competitors' densities of диван are 1/2, 0, 3/4 (median 0.5, over 0.5 x 1.3 for mine 2/3); стол 1/2, 1/2, 1/4; стул 0, 1/2, 0.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `compare_grams` | 6 | 6 | 0 | 0 |

### Deviations

None.

### xfail

None.

## compare_stats

compare. No VBA handler: compare_stats is semkit's own comparison of the text metrics with the competitors' median (SEMKIT-019), defined in its docstring; the `vba` column repeats `expected`. Counted by hand: the competitors have 2, 2 and 4 words (median 2, max 4) and 10, 9 and 22 characters (median 10); mine has 3 words and 18 characters.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `compare_stats` | 6 | 6 | 0 | 0 |

### Deviations

None.

### xfail

None.
