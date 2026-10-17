# Conformance of the dupes area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/dupes/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [dupes](#dupes) | 102 | 89 | 13 | 0 |
| **All** | **102** | **89** | **13** | **0** |

## dupes

dupes. VBA, RibbonCallbacks.vba. Find (TRUE / FALSE): —kka (L2488) exact, all but the first, key UCase$; —kk· (L2232) exact, all with the first, key UCase$; —kok (L2661) implicit, all but the first, key srt(UCase$); —ko— (L1808) implicit against another range. Delete (clears the cell): ak–— (L1648) exact, key the value as is; ako— (L2073) explicit, key a·(UCase$); akoa (L2450) implicit, key srt(a·(UCase$)); ako· (L2851) by wordforms, key srt(—··(a·(LCase$))); ak–o (L2949) against another range, key UCase$; ak–– (L2247) implicit against another range. A kind and action with no handler: the key of the kind's handler, marked as the action's handler marks. Every handler keys an empty cell by "". Docs: docs/vba/analysis.md (header), the dupes docstring (SEMKIT-003), the workbook sheet dupes.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `dupes` | 102 | 89 | 13 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| dupes-exact-case | `"Диван \| диван"` | `"FALSE \| TRUE"` | `"FALSE \| FALSE"` | противоречия решаем без отдельного вопроса, в пользу более качественного варианта | —kka keys by UCase$, the delete button ak–— by the value as is; semkit takes the value as is: exact is the same string, case belongs to explicit |
| dupes-exact-all-case | `"диван \| Диван \| стол"` | `"TRUE \| TRUE \| FALSE"` | `"FALSE \| FALSE \| FALSE"` | противоречия решаем без отдельного вопроса, в пользу более качественного варианта | —kk· keys by UCase$, the delete button ak–— by the value as is; semkit takes the value as is: exact is the same string, case belongs to explicit |
| dupes-exact-empty | `"диван \|  \| "` | `"FALSE \| FALSE \| TRUE"` | `"FALSE \| FALSE \| FALSE"` | пустые ячейки никогда не дубли | —kka keys an empty cell by "", so the second empty cell is a duplicate of the first |
| dupes-exact-drop | `"Диван \| диван \| Диван"` | `"Диван \| диван \| "` | `"Диван \| диван"` | побочный эффект Excel | ak–— clears the cell of a duplicate and the row stays on the sheet; semkit drops the row |
| dupes-explicit-yo | `"ёлка \| елка"` | `"FALSE \| FALSE"` | `"FALSE \| TRUE"` | ё = е при сравнении | ako— keys by a·(UCase$) and keeps ё |
| dupes-explicit-drop | `"диван \|  Диван  \| стол"` | `"диван \|  \| стол"` | `"диван \| стол"` | побочный эффект Excel | ako— clears the cell of a duplicate and the row stays on the sheet; semkit drops the row |
| dupes-explicit-against-drop | `"Диван угловой \| диван  угловой \| стол"` | `" \| диван  угловой \| стол"` | `"стол"` | побочный эффект Excel; фраза делится по любым пробелам, двойных пробелов в результатах нет | ak–o clears a found cell, the row stays; it keys by UCase$ alone, so «диван  угловой» with two spaces is not found |
| dupes-implicit-yo | `"ёлка купить \| купить елка"` | `"FALSE \| FALSE"` | `"FALSE \| TRUE"` | ё = е при сравнении | —kok keys by srt(UCase$) and keeps ё |
| dupes-implicit-drop | `"купить диван \| диван купить \| стол"` | `"купить диван \|  \| стол"` | `"купить диван \| стол"` | побочный эффект Excel | akoa clears the cell of a duplicate and the row stays on the sheet; semkit drops the row |
| dupes-implicit-against-empty | `"купить диван \| "` | `"TRUE \| TRUE"` | `"TRUE \| FALSE"` | пустые ячейки никогда не дубли | —ko— keys an empty cell of either range by "", so an empty cell is found in a range with one |
| dupes-lemmas-capital | `"Москве диван \| диван москва"` | `"FALSE \| FALSE"` | `"FALSE \| TRUE"` | леммы в нижнем регистре | ako· keeps the lemma as the dictionary stores it: москве → Москва, москва → москва, so the keys differ |
| dupes-lemmas-unknown | `"лайфхаками \| лайфхак"` | `"FALSE \| FALSE"` | `"FALSE \| TRUE"` | Явное улучшение там, где Python может больше VBA | aaa returns a word the dictionary lacks as is; semkit asks pymorphy3 next (ADR 0003) |
| dupes-lemmas-drop | `"стол \| столы \| стул"` | `"стол \|  \| стул"` | `"стол \| стул"` | побочный эффект Excel | ako· clears the cell of a duplicate and the row stays on the sheet; semkit drops the row |

### xfail

None.
