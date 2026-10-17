# Conformance of the morph area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/morph/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [lemmatize](#lemmatize) | 26 | 20 | 6 | 0 |
| [part_of_speech](#part_of_speech) | 13 | 7 | 6 | 0 |
| [wordforms](#wordforms) | 6 | 0 | 6 | 0 |
| **All** | **45** | **27** | **18** | **0** |

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
