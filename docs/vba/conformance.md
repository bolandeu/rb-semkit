# Conformance with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/*.tsv`; do not edit it.
A case is one call of the public API (`import rb_semkit as sk`) on one input. `vba` is what the add-in's VBA handler
gives, traced by hand from `docs/vba/matchers.md` and `docs/vba/analysis.md`; `semkit` is what the library gives.

- **As the VBA**: semkit gives the VBA value.
- **Deviations**: semkit gives another value. ADR 0005 allows it: the case names the rule and says why.
- **xfail**: semkit does not give the expected value yet; the Architect has the finding.

A verb with no VBA handler is derived from a near handler, as its notes say; its `vba` is the derived value.
A value is in quotes; « | » separates the cells of a whole-column input or result.

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [around](#around) | 21 | 14 | 7 | 0 |
| [bigrams](#bigrams) | 10 | 8 | 2 | 0 |
| [cells](#cells) | 25 | 21 | 4 | 0 |
| [chars](#chars) | 32 | 27 | 5 | 0 |
| [counts](#counts) | 15 | 12 | 3 | 0 |
| [dupes](#dupes) | 102 | 89 | 13 | 0 |
| [lemmatize](#lemmatize) | 26 | 20 | 6 | 0 |
| [markers](#markers) | 44 | 35 | 9 | 0 |
| [ngrams](#ngrams) | 16 | 6 | 10 | 0 |
| [part_of_speech](#part_of_speech) | 13 | 7 | 6 | 0 |
| [phrases](#phrases) | 16 | 10 | 6 | 0 |
| [pos](#pos) | 17 | 17 | 0 | 0 |
| [positions](#positions) | 11 | 9 | 2 | 0 |
| [regex](#regex) | 16 | 10 | 6 | 0 |
| [repeats](#repeats) | 17 | 15 | 2 | 0 |
| [spaces](#spaces) | 6 | 6 | 0 | 0 |
| [stopwords](#stopwords) | 25 | 22 | 3 | 0 |
| [word_case](#word_case) | 13 | 13 | 0 | 0 |
| [word_content](#word_content) | 20 | 19 | 1 | 0 |
| [word_position](#word_position) | 23 | 21 | 2 | 0 |
| [wordforms](#wordforms) | 6 | 0 | 6 | 0 |
| [words](#words) | 18 | 15 | 3 | 0 |
| **All** | **492** | **396** | **96** | **0** |

## around

around. VBA, RibbonCallbacks.vba (docs/vba/matchers.md R1, X1). remove: before the first ––·a (L2125) with include, ––·— (L2786) without; before the last –—kk (L2923), ––·· (L2389); after the first ––—– (L1791), ––—o (L2721); after the last ––—a (L2687), ––—— (L2250). The first occurrence is found by InStr vbTextCompare, the last by InStrRev binary; no pattern: the cell stays. extract: before the first –—–o (L2775) with include, –—–– (L1794) without (bug: always ""); after the last –—o· (L2767) with include, –—–k (L1602) without (bug: always ""); binary search, no pattern: "".

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `around.extract` | 9 | 5 | 4 | 0 |
| `around.remove` | 12 | 9 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| around-remove-before-first-include | `"Товар: диван: синий"` | `" диван: синий"` | `"диван: синий"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | ––·a gives Mid(s, pos + Len(p)) as is: the space after the colon stays at the start |
| around-remove-before-last-include | `"москва диван москва кресло"` | `" кресло"` | `"кресло"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | –—kk gives the text after the last «москва» as is, with its leading space |
| around-remove-after-first-include-spaces | `"  купить  диван  в  москве "` | `"  купить  ди"` | `"купить ди"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | ––—– gives Left(s, pos − 1) as is: the leading and the double spaces stay («в» is found inside «диван») |
| around-extract-before-first-include-yo | `"ёлка Елка"` | `""` | `"ёлка"` | ё = е при сравнении | –—–o searches «елка» binary: «ёлка» has ё and «Елка» a capital, so it finds nothing and gives '' |
| around-extract-before-first | `"диван, кресло"` | `""` | `"диван"` | явные дефекты исправляем | –—–– runs its search only when the pattern is longer than the text, so it always gives '' |
| around-extract-after-last | `"a/b/c"` | `""` | `"c"` | явные дефекты исправляем | –—–k runs its search only when the pattern is longer than the text, so it always gives '' |
| around-extract-after-last-words | `"стол и кресло и шкаф"` | `""` | `"шкаф"` | явные дефекты исправляем | –—–k runs its search only when the pattern is longer than the text, so it always gives '' |

### xfail

None.

## bigrams

bigrams. VBA, RibbonCallbacks.vba: «Биграмм без учета порядка слов» –·ao (L2746) ak— 2, False, True; with lemmas –·ak (L2186) ak— 2, True, True. ak— (L572–639): LCase, srt (L2951, binary sort of the words), a·o (L1649, a repeated word dropped), kkko (L2243, every pair as w1+w2), then counted as 1-grams in the order of the first occurrence; a second column is summed. Without stopwords: no handler, derived as a·–· (L2285), then –·ao. Docs: the workbook sheet bigrams.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `bigrams` | 10 | 8 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| bigrams-yo | `"Ёлка Купить \| купить елка"` | `"купить+ёлка=1 \| елка+купить=1"` | `"елка+купить=2"` | ё = е при сравнении | –·ao keys by LCase and keeps ё, which sorts after я |
| ref-bigrams | `"купить диван \| Купить  диван \| диван купить \| купить диваны \| диван угловой недорого \| угловой диван недорого \| диван в москве \| москве диван \| диван у метро таганская \| купить iPhone 15 в Москве \| красный диван бу \| где купить диван \| как выбрать диван \| диван диван угловой \| стол столы \| диван-кровать икеа \| кровать для детей от 3 лет \| ремонт квартир в спб под ключ \|  \| диван"` | `"диван+купить=4 \| диваны+купить=1 \| диван+недорого=2 \| диван+угловой=3 \| недорого+угловой=2 \| в+диван=1 \| в+москве=2 \| диван+москве=2 \| диван+метро=1 \| диван+таганская=1 \| диван+у=1 \| метро+таганская=1 \| метро+у=1 \| таганская+у=1 \| 15+iphone=1 \| 15+в=1 \| 15+купить=1 \| 15+москве=1 \| iphone+в=1 \| iphone+купить=1 \| iphone+москве=1 \| в+купить=1 \| купить+москве=1 \| бу+диван=1 \| бу+красный=1 \| диван+красный=1 \| где+диван=1 \| где+купить=1 \| выбрать+диван=1 \| выбрать+как=1 \| диван+как=1 \| стол+столы=1 \| диван-кровать+икеа=1 \| 3+детей=1 \| 3+для=1 \| 3+кровать=1 \| 3+лет=1 \| 3+от=1 \| детей+для=1 \| детей+кровать=1 \| детей+лет=1 \| детей+от=1 \| для+кровать=1 \| для+лет=1 \| для+от=1 \| кровать+лет=1 \| кровать+от=1 \| лет+от=1 \| в+квартир=1 \| в+ключ=1 \| в+под=1 \| в+ремонт=1 \| в+спб=1 \| квартир+ключ=1 \| квартир+под=1 \| квартир+ремонт=1 \| квартир+спб=1 \| ключ+под=1 \| ключ+ремонт=1 \| ключ+спб=1 \| под+ремонт=1 \| под+спб=1 \| ремонт+спб=1"` | `"диван+купить=4 \| диван+угловой=3 \| в+москве=2 \| диван+москве=2 \| диван+недорого=2 \| недорого+угловой=2 \| 15+iphone=1 \| 15+в=1 \| 15+купить=1 \| 15+москве=1 \| 3+детей=1 \| 3+для=1 \| 3+кровать=1 \| 3+лет=1 \| 3+от=1 \| iphone+в=1 \| iphone+купить=1 \| iphone+москве=1 \| бу+диван=1 \| бу+красный=1 \| в+диван=1 \| в+квартир=1 \| в+ключ=1 \| в+купить=1 \| в+под=1 \| в+ремонт=1 \| в+спб=1 \| выбрать+диван=1 \| выбрать+как=1 \| где+диван=1 \| где+купить=1 \| детей+для=1 \| детей+кровать=1 \| детей+лет=1 \| детей+от=1 \| диван+как=1 \| диван+красный=1 \| диван+метро=1 \| диван+таганская=1 \| диван+у=1 \| диван-кровать+икеа=1 \| диваны+купить=1 \| для+кровать=1 \| для+лет=1 \| для+от=1 \| квартир+ключ=1 \| квартир+под=1 \| квартир+ремонт=1 \| квартир+спб=1 \| ключ+под=1 \| ключ+ремонт=1 \| ключ+спб=1 \| кровать+лет=1 \| кровать+от=1 \| купить+москве=1 \| лет+от=1 \| метро+таганская=1 \| метро+у=1 \| под+ремонт=1 \| под+спб=1 \| ремонт+спб=1 \| стол+столы=1 \| таганская+у=1"` | n-граммы сортируются по убыванию счёта | ak— writes the bigrams in the order they first appear |

### xfail

None.

## cells

cells. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F4, R4, X4). find: —kk— (L2556) contains, —ko· (L2172) starts, —koo (L2822) ends, findFFWprps (L2304) and findFLWprps (L2305) with prps (L1322), —koa (L2089) regex, —kk– (L1872) empty, —k—a (L2170) unique, —k–— (L2214) repeated, —k–k (L2846) first, —k–– (L2493) last (o—— L381–434, koo· L2929: key UCase, empty cells counted). remove: remBlankCellsUp (L178) empty, akok (L1868) contains, akk· (L2969) regex, ao—– (L2074) unique, ak·a (L2358) repeated. extract: –——k (L2101) contains, —·–· (L2935) starts, —·–– (L2645) ends, –·k— (L2942) unique, –aoa (L2911) repeated.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `cells.extract` | 6 | 5 | 1 | 0 |
| `cells.find` | 14 | 11 | 3 | 0 |
| `cells.remove` | 5 | 5 | 0 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| cells-find-starts-prepositions-po | `"по низкой цене \| диван"` | `"FALSE \| FALSE"` | `"TRUE \| FALSE"` | Список предлогов исправлен | prps holds «пo» with a latin «o», so «по» is never found |
| cells-find-unique-empty | `"диван \|  \| "` | `"TRUE \| FALSE \| FALSE"` | `"TRUE \| TRUE \| TRUE"` | пустые ячейки никогда не дубли | o—— counts the empty cells too: two of them are a repeated value |
| cells-find-repeated-yo | `"ёлка \| елка"` | `"FALSE \| FALSE"` | `"TRUE \| TRUE"` | ё = е при сравнении | o—— keys by UCase: «ЁЛКА» and «ЕЛКА» are two values |
| cells-extract-contains-yo | `"Ёлка \| стол"` | `" \| "` | `"Ёлка \| "` | ё = е при сравнении | –——k compares UCase: «ЁЛКА» does not contain «ЕЛК» |

### xfail

None.

## chars

chars. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F1, R1, X1). find: —·k— (L1824) latin, —·k– (L2088) cyrillic, —·ka (L1652) digits, —kko (L2874) letters_digits, —·ok (L2756) upper, —·k· (L1786) ua with fua (L1343). remove: ak·— (L1856) latin, ak–· (L1867) cyrillic, aokk (L1924) digits, aok— (L2404) punctuation. extract: –ako (L2441) latin, –—–a (L2350) cyrillic, –·ko (L2594) digits, aok— (L2404) letters_digits. A kind and verb with no handler (ua extract) is derived from the kind's find: vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `chars.extract` | 8 | 8 | 0 | 0 |
| `chars.find` | 16 | 14 | 2 | 0 |
| `chars.remove` | 8 | 5 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| chars-find-ua-russian-ending | `"купить кровати"` | `"TRUE"` | `"FALSE"` | Украинский текст (chars('ua')) — по буквам і ї є ґ, а не по 31 элементу `fua` | fua finds its item «ати » in «кровати »; semkit tests the letters і ї є ґ only |
| chars-find-ua-ge | `"ґанок"` | `"FALSE"` | `"TRUE"` | Украинский текст (chars('ua')) — по буквам і ї є ґ, а не по 31 элементу `fua` | ґ is none of the 31 fua items; semkit counts it as a Ukrainian letter |
| chars-remove-latin | `"Диван IKEA Ektorp"` | `"Диван  "` | `"Диван"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | ak·— cuts [a-zA-Z] and does not trim: two spaces stay at the end |
| chars-remove-cyrillic | `"Диван IKEA"` | `" IKEA"` | `"IKEA"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | ak–· cuts the Cyrillic letters and does not trim: the space before «IKEA» stays |
| chars-remove-digits-word | `"диван 2 местный"` | `"диван  местный"` | `"диван местный"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | aokk cuts [0-9] and does not trim: a word of digits leaves a double space |

### xfail

None.

## counts

counts. VBA, RibbonCallbacks.vba (docs/vba/analysis.md §4): words –·oa (L2229) with akk (L2414) = UBound(Split(s, " ")) + 1; chars –a·k (L1933) = Len; count ––k— (L1875): the rows with the same UCase(value) in column 1; number –kko (L2166): the running count of that key; share –koo (L2489, «Накопительным итогом»): the running sum in row order / the total; abc ABCA (L3497): sort descending, cumulative share ≤ 0.8 A, ≤ 0.95 B, else C. «Долю от суммы» –kok (L1607) is the kind share_of_total.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `counts` | 15 | 12 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| counts-words-spaces | `" купить  диван "` | `"5"` | `"2"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | akk counts the items of a split by one space: each extra space adds a word |
| counts-count-yo | `"ёлка \| елка"` | `"1 \| 1"` | `"2 \| 2"` | ё = е при сравнении | ––k— keys by UCase and keeps ё |
| counts-count-empty | `"диван \|  \| "` | `"1 \| 2 \| 2"` | `"1 \|  \| "` | пустые ячейки никогда не дубли | ––k— counts the empty cells as one key |

### xfail

None.

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

## lemmatize

lemmatize. VBA, RibbonCallbacks.vba: «Лемматизация › Словарь !SEMTools» —ak– (L1960) → kok— (L2835): Split(LCase(cell), " "), each word through aaa (L1354), joined by " ". aaa gives the lemma as the dictionary (lemms.tsv) stores it, a word it lacks as is; lemmSuf only when Evaluate fails. Docs: docs/vba/analysis.md §1.4, §2; the workbook sheet lemmas.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `lemmatize` | 26 | 20 | 6 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| lemmatize-yo | `"ёлки"` | `"ёлки"` | `"елка"` | ё = е при сравнении | aaa looks the word up as written, and the dictionary has no ё |
| lemmatize-unknown-pymorphy | `"лайфхаками"` | `"лайфхаками"` | `"лайфхак"` | Явное улучшение там, где Python может больше VBA | aaa returns a word the dictionary lacks as is; semkit asks pymorphy3 next (ADR 0003) |
| ref-lemmas-03 | `"Купить  диван"` | `"купить  диван"` | `"купить диван"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | kok— splits by one space and joins by one, so the double space stays |
| ref-lemmas-08 | `"диван в москве"` | `"диван в Москва"` | `"диван в москва"` | леммы в нижнем регистре | aaa gives the lemma as the dictionary stores it: москве → Москва |
| ref-lemmas-09 | `"москве диван"` | `"Москва диван"` | `"москва диван"` | леммы в нижнем регистре | aaa gives the lemma as the dictionary stores it: москве → Москва |
| ref-lemmas-11 | `"купить iPhone 15 в Москве"` | `"купить iphone 15 в Москва"` | `"купить iphone 15 в москва"` | леммы в нижнем регистре | aaa gives the lemma as the dictionary stores it: Москве → Москва |

### xfail

None.

## markers

markers. VBA, RibbonCallbacks.vba (docs/vba/matchers.md S10, F3, R3, X3). find: —k—— (L2520) geo, —k—o (L2040) questions and the other —k—* buttons, with –la (L645–646). remove: a·–a (L2204) geo with DeletePhrases (L3452–3470), lower-cases the cell; geo with prepositions a·—a (L2967) with udalit_toponimy_s_pryedlogami (L1194–1197). extract: –a·a (L2823) geo, –a—o (L2409) questions, with la— (L647–648): the found items as the list spells them, joined by a backslash; geo with prepositions –·kk (L2674) with k—–– (L1198–1199). The rows ref-markers_geo-* are the workbook sheet markers_geo. Prepositions on other lists and find with prepositions have no handler: derived from udalit_toponimy_s_pryedlogami; vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `markers.extract` | 28 | 21 | 7 | 0 |
| `markers.find` | 6 | 6 | 0 | 0 |
| `markers.remove` | 10 | 8 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| markers-extract-geo-inner | `"доставка в нижний новгород"` | `"Нижний Новгород\Новгород"` | `"Нижний Новгород"` | маркеры — в написании списка, через «, »; Извлечение маркеров берёт самое длинное совпадение | la— finds «Нижний Новгород» and gives «новгород», a key too, its own slot, joined by a backslash |
| markers-extract-geo-inner-long | `"отели в хересе де ла фронтере"` | `"Хересе де Ла Фронтере\Ла Фронтере"` | `"Хересе де Ла Фронтере"` | маркеры — в написании списка, через «, »; Извлечение маркеров берёт самое длинное совпадение | la— gives «ла», a key too, its own slot «Ла Фронтере», joined by a backslash |
| markers-extract-questions | `"Где Купить диван как сделать"` | `"где\как"` | `"где, как сделать"` | маркеры — в написании списка, через «, »; Извлечение маркеров берёт самое длинное совпадение | la— takes «как», first in the list order, and joins by a backslash; –a—o then lower-cases the cell |
| markers-extract-geo-prepositions | `"купить диван в москве недорого"` | `"\\в Москве\\\"` | `"в Москве"` | маркеры — в написании списка, через «, » | k—–– keeps one slot per word, the empty ones too, joined by a backslash |
| markers-extract-geo-prepositions-none | `"диван москва"` | `"\\"` | `""` | маркеры — в написании списка, через «, » | k—–– keeps one slot per word, the empty ones too, joined by a backslash |
| markers-extract-geo-prepositions-phrase | `"доставка в нижний новгород"` | `"\в Нижний Новгород\\\"` | `"в Нижний Новгород"` | маркеры — в написании списка, через «, » | k—–– keeps one slot per word, the empty ones too, joined by a backslash |
| markers-extract-geo-prepositions-long | `"отели в хересе де ла фронтере"` | `"\в Хересе де Ла Фронтере\\\\\"` | `"в Хересе де Ла Фронтере"` | маркеры — в написании списка, через «, » | k—–– keeps one slot per word, the empty ones too, joined by a backslash |
| markers-remove-geo-case | `"Диван Москва"` | `"диван"` | `"Диван"` | Удаление по списку фраз и маркеров сохраняет регистр | DeletePhrases lower-cases the whole cell |
| markers-remove-geo-prepositions-one-item | `"отели в хересе де ла фронтере"` | `"отели де ла фронтере"` | `"отели"` | Удаление топонимов с предлогами убирает топоним целиком | udalit_toponimy_s_pryedlogami cuts only the preposition and the next word when that word keys one list item |

### xfail

None.

## ngrams

ngrams. VBA, RibbonCallbacks.vba: N-грамм –·—– (L2591) ak— 1, –·—a (L1837) ak— 2; N-грамм-лемм –·—— (L2265) ak— 1, True, –·—· (L1834) ak— 2, True; ak— (L572–639) with ok– (L1391) and —·· (L2395, lemmas). An occurrence counts; the key is LCase, ё kept; a phrase splits by one space; the table is in the order of the first occurrence. A second column is summed per occurrence (no count). Without stopwords: n = 2 is «Биграмм без учета стоп-слов» —k·· (L2781) → ka–a (L1005); n = 1 has no handler: derived as «Удалить стоп-слова» a·–· (L2285), then ak— 1. Docs: the n-gram docstrings (SEMKIT-004), the workbook sheets ngrams_1, ngrams_2.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `ngrams` | 16 | 6 | 10 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| ngrams-case-yo | `"Ёлка \| ёлка \| елка"` | `"ёлка=2 \| елка=1"` | `"елка=3"` | ё = е при сравнении | ak— keys by LCase and keeps ё |
| ngrams-punctuation | `"диван, кресло \| диван"` | `"диван,=1 \| кресло=1 \| диван=1"` | `"диван=1 \| диван,=1 \| кресло=1"` | n-граммы сортируются по убыванию счёта | ak— writes the n-grams in the order they first appear |
| ngrams-lemmas | `"купила диваны \| купить диван"` | `"купить=2 \| диван=2"` | `"диван=2 \| купить=2"` | n-граммы сортируются по убыванию счёта | ak— writes the n-grams in the order they first appear |
| ngrams-lemmas-2 | `"купила красные диваны"` | `"купить красный=1 \| красный диван=1"` | `"красный диван=1 \| купить красный=1"` | n-граммы сортируются по убыванию счёта | ak— writes the n-grams in the order they first appear |
| ngrams-stopwords | `"диван в москве \| диван для дома"` | `"диван=2 \| москве=1 \| дома=1"` | `"диван=2 \| дома=1 \| москве=1"` | n-граммы сортируются по убыванию счёта | ak— writes the n-grams in the order they first appear |
| ngrams-stopwords-case | `"Диван В Москве"` | `"диван=1 \| в=1 \| москве=1"` | `"диван=1 \| москве=1"` | стоп-слова без учёта регистра | a·–· drops a stopword only as the list spells it, so «В» stays |
| ngrams-stopwords-2 | `"купить диван в москве"` | `"купить диван=1 \| диван в москве=1"` | `"диван в москве=1 \| купить диван=1"` | n-граммы сортируются по убыванию счёта | ka–a writes the bigrams in the order they first appear |
| ngrams-weight | `"купить диван [10] \| диван [5]"` | `"купить=10 \| диван=15"` | `"диван=15 \| купить=10"` | n-граммы сортируются по убыванию счёта | ak— writes the n-grams in the order they first appear |
| ref-ngrams_1 | `"купить диван \| Купить  диван \| диван купить \| купить диваны \| диван угловой недорого \| угловой диван недорого \| диван в москве \| москве диван \| диван у метро таганская \| купить iPhone 15 в Москве \| красный диван бу \| где купить диван \| как выбрать диван \| диван диван угловой \| стол столы \| диван-кровать икеа \| кровать для детей от 3 лет \| ремонт квартир в спб под ключ \|  \| диван"` | `"купить=6 \| диван=14 \| диваны=1 \| угловой=3 \| недорого=2 \| в=3 \| москве=3 \| у=1 \| метро=1 \| таганская=1 \| iphone=1 \| 15=1 \| красный=1 \| бу=1 \| где=1 \| как=1 \| выбрать=1 \| стол=1 \| столы=1 \| диван-кровать=1 \| икеа=1 \| кровать=1 \| для=1 \| детей=1 \| от=1 \| 3=1 \| лет=1 \| ремонт=1 \| квартир=1 \| спб=1 \| под=1 \| ключ=1"` | `"диван=14 \| купить=6 \| в=3 \| москве=3 \| угловой=3 \| недорого=2 \| 15=1 \| 3=1 \| iphone=1 \| бу=1 \| выбрать=1 \| где=1 \| детей=1 \| диван-кровать=1 \| диваны=1 \| для=1 \| икеа=1 \| как=1 \| квартир=1 \| ключ=1 \| красный=1 \| кровать=1 \| лет=1 \| метро=1 \| от=1 \| под=1 \| ремонт=1 \| спб=1 \| стол=1 \| столы=1 \| таганская=1 \| у=1"` | n-граммы сортируются по убыванию счёта | ak— writes the n-grams in the order they first appear |
| ref-ngrams_2 | `"купить диван \| Купить  диван \| диван купить \| купить диваны \| диван угловой недорого \| угловой диван недорого \| диван в москве \| москве диван \| диван у метро таганская \| купить iPhone 15 в Москве \| красный диван бу \| где купить диван \| как выбрать диван \| диван диван угловой \| стол столы \| диван-кровать икеа \| кровать для детей от 3 лет \| ремонт квартир в спб под ключ \|  \| диван"` | `"купить диван=2 \| купить =1 \|  диван=1 \| диван купить=1 \| купить диваны=1 \| диван угловой=2 \| угловой недорого=1 \| угловой диван=1 \| диван недорого=1 \| диван в=1 \| в москве=2 \| москве диван=1 \| диван у=1 \| у метро=1 \| метро таганская=1 \| купить iphone=1 \| iphone 15=1 \| 15 в=1 \| красный диван=1 \| диван бу=1 \| где купить=1 \| как выбрать=1 \| выбрать диван=1 \| диван диван=1 \| стол столы=1 \| диван-кровать икеа=1 \| кровать для=1 \| для детей=1 \| детей от=1 \| от 3=1 \| 3 лет=1 \| ремонт квартир=1 \| квартир в=1 \| в спб=1 \| спб под=1 \| под ключ=1"` | `"купить диван=3 \| в москве=2 \| диван угловой=2 \| 15 в=1 \| 3 лет=1 \| iphone 15=1 \| в спб=1 \| выбрать диван=1 \| где купить=1 \| детей от=1 \| диван бу=1 \| диван в=1 \| диван диван=1 \| диван купить=1 \| диван недорого=1 \| диван у=1 \| диван-кровать икеа=1 \| для детей=1 \| как выбрать=1 \| квартир в=1 \| красный диван=1 \| кровать для=1 \| купить iphone=1 \| купить диваны=1 \| метро таганская=1 \| москве диван=1 \| от 3=1 \| под ключ=1 \| ремонт квартир=1 \| спб под=1 \| стол столы=1 \| у метро=1 \| угловой диван=1 \| угловой недорого=1"` | n-граммы сортируются по убыванию счёта; фраза делится по любым пробелам, двойных пробелов в результатах нет | ak— writes the n-grams in the order they first appear; its split by one space makes «купить » and « диван» of «Купить  диван» |

### xfail

None.

## part_of_speech

part_of_speech. No VBA handler writes the part of speech. The word tests read it: ··– (L2207) noun, ·ok (L1344) verb, oa– (L2154) adverb, ··o (L1439) adjective (docs/vba/analysis.md §1.5). The vba column is the code they read per word of Split(phrase, " "): column 3 of the dictionary by oa(LCase(w), slovarlyemm, 3) (L2208), which gives the word itself when the dictionary lacks it; ·ok makes a word ending in тся, ься, ают, уют (but уют) a verb. Codes joined by " ".

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `part_of_speech` | 13 | 7 | 6 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| pos-unknown | `"бу"` | `"бу"` | `""` | у неё дефект или побочный эффект Excel | oa returns a key it does not find as the value, so an unknown word reads as its own code |
| pos-punctuation | `"диван,"` | `"диван,"` | `""` | у неё дефект или побочный эффект Excel | oa returns a key it does not find as the value, so «диван,» reads as its own code |
| pos-pymorphy | `"икеа"` | `"икеа"` | `"n"` | Явное улучшение там, где Python может больше VBA | the dictionary lacks the word and oa returns it as is; semkit asks pymorphy3 next (ADR 0003) |
| pos-adjective-ending | `"зюзюкный"` | `"зюзюкный"` | `"a"` | у неё дефект или побочный эффект Excel | oa returns the unknown word as its own code; ··o then calls it an adjective by the lemma ending (adjSuffixes), which semkit gives as the code a |
| pos-yo | `"ёлки"` | `"ёлки"` | `"n"` | ё = е при сравнении | oa looks the word up as written, and the dictionary has no ё |
| pos-double-space | `"купить  диван"` | `"v  n"` | `"v n"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | the word tests split by one space, so the empty word between two spaces gets the empty code |

### xfail

None.

## phrases

phrases. VBA, RibbonCallbacks.vba (docs/vba/matchers.md S10, F3, R3, X3): find —k—k (L2218) with –la (L645–646), remove aok– (L2733) with DeletePhrases (L3452–3470), extract –a–a (L1736) with la— (L647–648). A token is a key by UCase of its first word; a token glued to punctuation is no key.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `phrases.extract` | 5 | 3 | 2 | 0 |
| `phrases.find` | 6 | 5 | 1 | 0 |
| `phrases.remove` | 5 | 2 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| phrases-find-yo | `"елка искусственная"` | `"FALSE"` | `"TRUE"` | ё = е при сравнении | –la keys «ёлка» by UCase «ЁЛКА»: the word «елка» is no key |
| phrases-remove-case | `"Диван Москва"` | `"диван москва"` | `"Диван Москва"` | Удаление по списку фраз и маркеров сохраняет регистр | DeletePhrases lower-cases the whole cell, also when it removes nothing |
| phrases-remove-case-punct | `"Москва, диван москва"` | `"москва, диван"` | `"Москва, диван"` | Удаление по списку фраз и маркеров сохраняет регистр | DeletePhrases lower-cases the cell; «москва,» with its comma is no phrase of the list |
| phrases-remove-double-space | `"купить  диван"` | `"купить "` | `"купить"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | DeletePhrases splits on one space: the empty word of the double space stays and leaves a space at the end |
| phrases-extract-cities-two | `"доставка нижний новгород москва"` | `"Нижний Новгород\Москва"` | `"Нижний Новгород, Москва"` | маркеры — в написании списка, через «, » | la— joins the found phrases by a backslash |
| phrases-extract-inner | `"купить диван угловой диван"` | `"купить диван\диван\угловой диван\диван"` | `"купить диван, угловой диван"` | маркеры — в написании списка, через «, »; Извлечение маркеров берёт самое длинное совпадение | la— gives each word that is a key its own slot, joined by a backslash: the «диван» inside both phrases comes out again |

### xfail

None.

## pos

pos. VBA, RibbonCallbacks.vba (docs/vba/matchers.md S9, F2, R2, X2). find: —k–a (L2266) noun, –··· (L2909) adj, —k—· (L2494) verb, —kkk (L1663) adverb; remove: ak·· (L2642), —··a (L2697), ao—— (L1897), —··· (L2563); extract: –ao· (L2891), –—o— (L1948), –·ka (L2246), –—oa (L2480). The word tests: ··– (L2207) noun, ··o (L1439) adj, ·ok (L1344) verb, oa– (L2154) adverb, on the dictionary lemms.tsv; a token is looked up with its punctuation.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `pos.extract` | 5 | 5 | 0 | 0 |
| `pos.find` | 7 | 7 | 0 | 0 |
| `pos.remove` | 5 | 5 | 0 | 0 |

### Deviations

None.

### xfail

None.

## positions

positions. VBA, RibbonCallbacks.vba (docs/vba/matchers.md R1, X1): remove ak—— (L2702) first = Mid(s, N + 1), ak·k (L2086) last = Left(s, Len − N), "" when N > Len; extract –—·– (L2369) first = Left(s, N), –ak· (L1687) last = Right(s, N). No trim.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `positions.extract` | 5 | 4 | 1 | 0 |
| `positions.remove` | 6 | 5 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| positions-remove-first | `"1. диван"` | `" диван"` | `"диван"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | ak—— gives Mid(s, N + 1) as is: the space after «1.» stays at the start |
| positions-extract-first-space | `"купить диван"` | `"купить "` | `"купить"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | –—·– gives Left(s, N) as is: the space after «купить» stays at the end |

### xfail

None.

## regex

regex. VBA, RibbonCallbacks.vba (docs/vba/matchers.md S8, F4, R1, X1): VBScript.RegExp, IgnoreCase False, ASCII \w \b \d. find —koa (L2089) RegExMatch (L1646); remove aoka (L2363) RegExReplace (L2080), no trim; invert aok· (L1820) (bug: the pattern is an undeclared variable, ""); extract –a—– (L2712) the first match, –a—— (L2877–2878) every match joined by the separator the user types (here « »). invert find and extract have no handler: derived from aok· as intended (the matches kept); vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `regex.extract` | 5 | 4 | 1 | 0 |
| `regex.find` | 6 | 4 | 2 | 0 |
| `regex.remove` | 5 | 2 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| regex-find-cyrillic-boundary | `"диван в москве"` | `"FALSE"` | `"TRUE"` | Регулярные выражения понимают кириллицу: классы \w, \b, \d в режиме Unicode, а не ASCII, как в VBScript | VBScript \b is ASCII: «в» and the spaces round it are all non-word characters, so there is no boundary |
| regex-find-cyrillic-word | `"диван"` | `"FALSE"` | `"TRUE"` | Регулярные выражения понимают кириллицу: классы \w, \b, \d в режиме Unicode, а не ASCII, как в VBScript | VBScript \w is [A-Za-z0-9_]: a Cyrillic word does not match |
| regex-remove-plain | `"диван 2 места 3"` | `"диван  места "` | `"диван места"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | aoka replaces the matches by nothing and does not trim: a double space and a trailing space stay |
| regex-remove-cyrillic-boundary | `"купить диван в москве"` | `"купить диван в москве"` | `"купить диван москве"` | Регулярные выражения понимают кириллицу: классы \w, \b, \d в режиме Unicode, а не ASCII, как в VBScript; фраза делится по любым пробелам, двойных пробелов в результатах нет | VBScript \b is ASCII and finds no boundary round «в», so aoka leaves the phrase; semkit cuts «в» and the double space |
| regex-remove-invert | `"диван 120x200"` | `""` | `"120200"` | явные дефекты исправляем | aok· passes the undeclared variable o— as the pattern: the pattern is '' and every cell becomes '' |
| regex-extract-cyrillic-word | `"диван-кровать"` | `""` | `"диван"` | Регулярные выражения понимают кириллицу: классы \w, \b, \d в режиме Unicode, а не ASCII, как в VBScript | VBScript \w is ASCII: no Cyrillic letter matches, so –a—– gives '' |

### xfail

None.

## repeats

repeats. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F2, R2): find —k—– (L1731) with —la (L2938): two equal tokens of Split(UCase(s), " "); remove aala (L2514) all, aal1 (L2257) en, aall (L2703) ru, remrepW (L1697) adjacent, aal· (L2569) numbers, aook (L2371) wordforms; a later repeat goes, the first stays.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `repeats.find` | 6 | 4 | 2 | 0 |
| `repeats.remove` | 11 | 11 | 0 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| repeats-find-exact-double-space | `"a  b  c"` | `"TRUE"` | `"FALSE"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | —la splits on one space: the two empty words of the double spaces are equal |
| repeats-find-exact-yo | `"ёлка елка"` | `"FALSE"` | `"TRUE"` | ё = е при сравнении | —la compares UCase: «ЁЛКА» is not «ЕЛКА» |

### xfail

None.

## spaces

spaces.remove. VBA, RibbonCallbacks.vba (docs/vba/matchers.md R1): –aal (L1941) extra = a· (L1855), —ako (L2926) left = LTrim, a–o— (L2230) right = RTrim, a–k— (L1878) both = Trim; only U+0020 counts. all has no handler: derived from –aal, every space cut; vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `spaces.remove` | 6 | 6 | 0 | 0 |

### Deviations

None.

### xfail

None.

## stopwords

stopwords.remove. VBA: «Удалить › Из текста › Стоп-слова» a·–· (L2285) → Del1DimArr (L2284): Split(cell, " "), a word dropped when the list stopwords$ (L1374–1378) holds it as written; Join, Trim. The rows ref-stopwords-* are the workbook sheet stopwords. extra has no handler: derived from a·–· with the extra words in the list; vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `stopwords.remove` | 25 | 22 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| ref-stopwords-03 | `"Купить  диван"` | `"Купить  диван"` | `"Купить диван"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | Del1DimArr splits by one space and joins by one, so the double space stays |
| stopwords-remove-case | `"Диван В Москве"` | `"Диван В Москве"` | `"Диван Москве"` | стоп-слова без учёта регистра | Del1DimArr looks a word up as written: the list holds «в», not «В» |
| stopwords-remove-junk | `"диван g"` | `"диван"` | `"диван g"` | то же «g» убрано из стоп-слов | the VBA list stopwords holds the junk word «g» |

### xfail

None.

## word_case

word_case. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F2): find aakL (L1665) isLcase (L3387), aakP (L1666) isProper (L3388, Excel PROPER), aakC (L1667) isCaps (L3389); a token of digits or punctuation only is no case. extract has no handler: derived from the find tests (the tokens they pass); vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `word_case.extract` | 5 | 5 | 0 | 0 |
| `word_case.find` | 8 | 8 | 0 | 0 |

### Deviations

None.

### xfail

None.

## word_content

word_content. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F2, R2, X2). find: —ka— (L2082) starts, —kaa (L2225) starts a list, —kao (L2670) ends; remove: aoaa (L2653) starts, aoak (L2901) contains, a·—– (L2456) only_latin, a·a– (L2336) has_latin, a·—— (L2780) only_digits (IsNumeric, ru locale), a·a— (L1864) has_digits; extract: –·–a (L1903) starts, ——·– (L2107) only_latin, –—k— (L2442) has_latin, ——·— (L2127) only_digits, a·o– (L2916) mixed. A token is tested with its punctuation, UCase, ё ≠ е. find by a kind of characters has no handler: derived from its remove and extract handlers; vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `word_content.extract` | 6 | 6 | 0 | 0 |
| `word_content.find` | 7 | 6 | 1 | 0 |
| `word_content.remove` | 7 | 7 | 0 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| word_content-find-starts-yo | `"елки"` | `"FALSE"` | `"TRUE"` | ё = е при сравнении | —·– compares UCase: «ЕЛК» is not «ЁЛК» |

### xfail

None.

## word_position

word_position. VBA, RibbonCallbacks.vba (docs/vba/matchers.md R2, X2). remove: ak—k (L2081), ak—– (L2485), ak—a (L2939) first; aka— (L1940) last; "" when the cell has N words or fewer. extract: –—·— (L1828) first; –ak— (L1711) last; –—o– (L2133), –a–k (L1850) nth with k·k (L1851); –·—k (L1599) to_middle and –·—o (L1612) at_most with o·— (L1403). Split(s, " "): an empty token of a double space is a word. remove with at_most and every find have no handler: derived from the extract handlers (find is TRUE where extract gives words); vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `word_position.extract` | 11 | 10 | 1 | 0 |
| `word_position.find` | 6 | 6 | 0 | 0 |
| `word_position.remove` | 6 | 5 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| word_position-remove-first-double-space | `"a  b c"` | `"b c"` | `"c"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | Split on one space makes the double space an empty word, and it counts as the second word |
| word_position-extract-nth-double-space | `"купить  диван"` | `""` | `"диван"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | k·k splits on one space: the second word of «купить  диван» is the empty word |

### xfail

None.

## wordforms

wordforms. VBA, RibbonCallbacks.vba: «Генерация всех словоформ» ––aa (L380) with ·la (L651): lemma = aaa(LCase(w)); it writes (w, w), then (w, form) for every dictionary row whose lemma equals that lemma as stored (binary), in file order (alphabetical). The vba column is column 2 of that output. Docs: docs/vba/analysis.md §2.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `wordforms` | 6 | 0 | 6 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| wordforms-divan | `"диван"` | `"диван \| диван \| дивана \| диванам \| диванами \| диванах \| диване \| диванов \| диваном \| дивану \| диваны"` | `"диван \| дивана \| диванам \| диванами \| диванах \| диване \| диванов \| диваном \| дивану \| диваны"` | побочный эффект Excel | ––aa writes the word itself as the first row of its two-column output |
| wordforms-stol | `"стол"` | `"стол \| стол \| стола \| столам \| столами \| столах \| столе \| столом \| столу \| столы"` | `"стол \| стола \| столам \| столами \| столах \| столе \| столом \| столу \| столы"` | побочный эффект Excel | ––aa writes the word itself as the first row of its two-column output |
| wordforms-capital | `"Москва"` | `"Москва \| москв \| москва \| москвою"` | `"москв \| москва \| москве \| москвой \| москвою \| москву \| москвы"` | побочный эффект Excel; леммы в нижнем регистре | ––aa writes the word itself first; aaa(москва) is москва, and the forms москве, москвой, москву, москвы stand under the lemma Москва, which the binary key misses |
| wordforms-inflected | `"диваны"` | `"диваны \| диван \| дивана \| диванам \| диванами \| диванах \| диване \| диванов \| диваном \| дивану \| диваны"` | `"диван \| дивана \| диванам \| диванами \| диванах \| диване \| диванов \| диваном \| дивану \| диваны"` | побочный эффект Excel | ––aa writes the word itself first, then the forms of its lemma aaa(диваны) = диван |
| wordforms-unknown | `"xyz"` | `"xyz"` | `""` | побочный эффект Excel | ––aa writes the word itself first; the dictionary has no forms for it |
| wordforms-yo | `"ёлка"` | `"ёлка"` | `"елка \| елкам \| елками \| елках \| елке \| елки \| елкой \| елкою \| елку \| елок"` | побочный эффект Excel; ё = е при сравнении | ––aa writes the word itself first; aaa(ёлка) is ёлка, which the dictionary (no ё) has no forms for |

### xfail

None.

## words

words. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F2, R2, X2). find: –––o (L1927) one word = ·a– (L2573), –––k (L2805) all; remove: ao—a (L1835) one word, dFWCustom (L2309) start, dLWCustom (L2308) end; extract: –·oo (L2567). UCase on both sides, ё ≠ е, Split(s, " "); ignore_punct is the «Игнорировать пунктуацию» variant (oka, L2460). extract with where has no handler: derived from –·oo; vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `words.extract` | 5 | 4 | 1 | 0 |
| `words.find` | 7 | 6 | 1 | 0 |
| `words.remove` | 6 | 5 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| words-find-one-yo | `"ёлка"` | `"FALSE"` | `"TRUE"` | ё = е при сравнении | ·a– compares UCase: «ЁЛКА» is not «ЕЛКА» |
| words-remove-one-yo | `"Ёлка елка"` | `"елка"` | `""` | ё = е при сравнении | ao—a compares UCase: «ЕЛКА» is not «ЁЛКА», so «елка» stays |
| words-extract-one-yo | `"Ёлка"` | `""` | `"Ёлка"` | ё = е при сравнении | –·oo compares UCase: «ЁЛКА» is not «ЕЛКА» |

### xfail

None.
