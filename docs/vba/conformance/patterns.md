# Conformance of the patterns area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/patterns/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [complements](#complements) | 6 | 5 | 1 | 0 |
| [phrase_end](#phrase_end) | 9 | 6 | 3 | 0 |
| [ready_pattern](#ready_pattern) | 18 | 8 | 10 | 0 |
| **All** | **33** | **19** | **14** | **0** |

## complements

complements. VBA, RibbonCallbacks.vba (docs/vba/matchers.md X3, docs/vba/analysis.md §12): «Дополнения с предлогами» findCollocs (L448) → k– "collocs" (L1428): for a word in « для с в из на к со о во у по под от после за над » (case-sensitive), the next ≤ 5 words up to the next preposition; v = the last noun (k—·— L2905 = aoo("··–", w, True), the word after oko); «prep … v» joined by ", ". Extract only.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `complements.extract` | 6 | 5 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| compl-capital | `"диван В Москве"` | `""` | `"В Москве"` | Предлог дополнения — в любом регистре, ё = е | collocs finds the preposition case-sensitively: «В» is none |

### xfail

None.

## phrase_end

phrase_end. VBA, RibbonCallbacks.vba (docs/vba/matchers.md W1): «Предлоги в конце фраз» remLWprps (L2306): dLW (L2301) four times with stopwords (L1374–1378), prps (L1322), stopwords, prps: the last word (eLW L2432, UCase) in the list is dropped (–·a L2319). «Маркеры покупки в конце фраз» remLWsales (L2307): one pass of dLWrng (L2302) with markyerypokupki (spiski/sale). Remove only.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `phrase_end.remove` | 9 | 6 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| end-five-words | `"диван для и в на по"` | `"диван для"` | `"диван"` | Предлоги в конце фразы удаляются, пока последнее слово не станет чистым | remLWprps makes four passes, so it drops four words at most |
| end-buy-two | `"диван купить недорого"` | `"диван купить"` | `"диван"` | Маркеры покупки в конце фразы удаляются, пока последнее слово не станет чистым, и маркер из нескольких слов тоже | remLWsales makes one pass: «купить» stays |
| end-buy-phrase | `"диван по низкой цене"` | `"диван по низкой"` | `"диван"` | Маркеры покупки в конце фразы удаляются, пока последнее слово не станет чистым, и маркер из нескольких слов тоже | dLWrng compares the last word only, so a marker of several words never matches |

### xfail

None.

## ready_pattern

ready_pattern. VBA, RibbonCallbacks.vba (docs/vba/matchers.md X1): «Готовые паттерны» extract: domain a·k– (L2863) every match joined by " "; date_ddmmyyyy –a—a (L2960), date_yyyymmdd –aa– (L1765), email –a—· (L2845) the first match (–—o L2517); phone –aak (L2714) "\" and every match joined by "|" (l–a L1330). RegExExtract (L2970), VBScript.RegExp, ASCII classes. find and remove have no handler: derived from the regex find —koa (L2089, RegExMatch L1646) and remove aoka (L2363, RegExReplace L2080, no trim) with the same pattern; vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `ready_pattern.extract` | 8 | 4 | 4 | 0 |
| `ready_pattern.find` | 5 | 3 | 2 | 0 |
| `ready_pattern.remove` | 5 | 1 | 4 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| ready-find-date-plain | `"пишите на info@site.ru до 01022024"` | `"FALSE"` | `"TRUE"` | Дата находится и без разделителей, но не внутри длинного числа | the VBA pattern needs a separator |
| ready-find-date-in-number | `"артикул 101.02.20245"` | `"TRUE"` | `"FALSE"` | Дата находится и без разделителей, но не внутри длинного числа | the VBA pattern finds the date inside the longer number |
| ready-remove-email | `"пишите на info@site.ru"` | `"пишите на "` | `"пишите на"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | RegExReplace does not trim: the trailing space stays |
| ready-remove-phone | `"звоните 8 (999) 123-45-67 или +7 999 111 22 33"` | `"звоните  или "` | `"звоните или"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | RegExReplace does not trim: a double space and a trailing space stay |
| ready-remove-date-plain | `"заказ 20231105"` | `"заказ 20231105"` | `"заказ"` | Дата находится и без разделителей, но не внутри длинного числа | the VBA pattern needs a separator, so the date stays |
| ready-remove-domain | `"сайт mail.ru"` | `"сайт "` | `"сайт"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | RegExReplace does not trim: the trailing space stays |
| ready-extract-date-plain | `"пишите на info@site.ru до 01022024"` | `""` | `"01022024"` | Дата находится и без разделителей, но не внутри длинного числа | the VBA pattern needs a separator |
| ready-extract-phone | `"звоните 8 (999) 123-45-67"` | `"\8 (999) 123-45-67"` | `"8 (999) 123-45-67"` | Телефоны — без обратной косой черты, через «, » | –aak puts a backslash before the numbers |
| ready-extract-phone-none | `"нет телефона"` | `"\"` | `""` | Телефоны — без обратной косой черты, через «, » | –aak writes the backslash into a cell without a number |
| ready-extract-email-long | `"hello@site.travel"` | `"hello@site.trav"` | `"hello@site.travel"` | E-mail — латинские буквы, домен верхнего уровня любой длины | [A-z]{2,4} cuts the domain to four letters |

### xfail

None.
