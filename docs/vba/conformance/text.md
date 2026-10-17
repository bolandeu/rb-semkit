# Conformance of the text area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/text/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [around](#around) | 21 | 14 | 7 | 0 |
| [cells](#cells) | 25 | 21 | 4 | 0 |
| [chars](#chars) | 32 | 27 | 5 | 0 |
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
| [words](#words) | 18 | 15 | 3 | 0 |
| **All** | **260** | **219** | **41** | **0** |

## around

around. VBA, RibbonCallbacks.vba (docs/vba/matchers.md R1, X1). remove: before the first ––·a (L2125) with include, ––·— (L2786) without; before the last –—kk (L2923), ––·· (L2389); after the first ––—– (L1791), ––—o (L2721); after the last ––—a (L2687), ––—— (L2250). The first occurrence is found by InStr vbTextCompare, the last by InStrRev binary; no pattern: the cell stays. extract: before the first –—–o (L2775) with include, –—–– (L1794) without (bug: always ""); after the last –—o· (L2767) with include, –—–k (L1602) without (bug: always ""); binary search, no pattern: "". extract before the last and after the first have no handler: derived from –—–o (L2775) and –—o· (L2767); vba is the derived value.

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

## cells

cells. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F4, R4, X4). find: —kk— (L2556) contains, —ko· (L2172) starts, —koo (L2822) ends, findFFWprps (L2304) and findFLWprps (L2305) with prps (L1322), —koa (L2089) regex, —kk– (L1872) empty, —k—a (L2170) unique, —k–— (L2214) repeated, —k–k (L2846) first, —k–– (L2493) last (o—— L381–434, koo· L2929: key UCase, empty cells counted). remove: remBlankCellsUp (L178) empty, akok (L1868) contains, akk· (L2969) regex, ao—– (L2074) unique, ak·a (L2358) repeated. extract: –——k (L2101) contains, —·–· (L2935) starts, —·–– (L2645) ends, –·k— (L2942) unique, –aoa (L2911) repeated. remove also: ak–a (L2613) starts, ak–k (L2248) ends. No handler, derived: find contains a preposition from findFFWprps (L2304); remove first, last, prepositions from ak·a (L2358) and ak–a (L2613); extract regex from akk· (L2969) (—·–a is broken); extract empty, first, last, prepositions from their find handlers; vba is the derived value.

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

chars. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F1, R1, X1). find: —·k— (L1824) latin, —·k– (L2088) cyrillic, —·ka (L1652) digits, —kko (L2874) letters_digits, —·ok (L2756) upper, —·k· (L1786) ua with fua (L1343). remove: ak·— (L1856) latin, ak–· (L1867) cyrillic, aokk (L1924) digits, aok— (L2404) punctuation. extract: –ako (L2441) latin, –—–a (L2350) cyrillic, –·ko (L2594) digits, aok— (L2404) letters_digits. A kind and verb with no handler (ua extract) is derived from the kind's find: vba is the derived value. No handler, derived from aok— (L2404): find punctuation; remove letters_digits, upper; extract punctuation, upper. ua remove and extract: derived from —·k·. The classes (docs/vba/matchers.md S4): VBA compares with Option Compare Binary, so [A-Za-z] and [0-9] are ASCII; a letter is cased when UCase(c) <> LCase(c); VBA strings are UTF-16, so only the BMP counts. upper ooa (L2655), has_latin a–— (L2153), has_digit ·kk (L1619), has_cyrillic —–o (L2147), only_latin ala (L1770), a number ··— (L2360) by IsNumeric.

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

## phrases

phrases. VBA, RibbonCallbacks.vba (docs/vba/matchers.md S10, F3, R3, X3): find —k—k (L2218) with –la (L645–646), remove aok– (L2733) with DeletePhrases (L3452–3470), extract –a–a (L1736) with la— (L647–648). A token is a key by UCase of its first word; a token glued to punctuation is no key. la— takes the first item in list order found anywhere in the phrase and gives a word inside a found phrase its own marker too; DeletePhrases lower-cases the whole cell.

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

pos. VBA, RibbonCallbacks.vba (docs/vba/matchers.md S9, F2, R2, X2). find: —k–a (L2266) noun, –··· (L2909) adj, —k—· (L2494) verb, —kkk (L1663) adverb; remove: ak·· (L2642), —··a (L2697), ao—— (L1897), —··· (L2563); extract: –ao· (L2891), –—o— (L1948), –·ka (L2246), –—oa (L2480). The word tests: ··– (L2207) noun, ··o (L1439) adj, ·ok (L1344) verb, oa– (L2154) adverb, on the dictionary lemms.tsv; a token is looked up with its punctuation. The verb endings of ·ok are in the bundled lemmatizer.

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

regex. VBA, RibbonCallbacks.vba (docs/vba/matchers.md S8, F4, R1, X1): VBScript.RegExp, IgnoreCase False, ASCII \w \b \d. find —koa (L2089) RegExMatch (L1646); remove aoka (L2363) RegExReplace (L2080), no trim; invert aok· (L1820) (bug: the pattern is an undeclared variable, ""); extract –a—– (L2712) the first match, –a—— (L2877–2878) every match joined by the separator the user types (here « »). invert find and extract have no handler: derived from aok· as intended (the matches kept); vba is the derived value. The library joins all_matches by a space (the VBA asks for the separator); invert remove aok· (L1820) has its bug fixed (it takes an empty pattern).

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

repeats. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F2, R2): find —k—– (L1731) with —la (L2938): two equal tokens of Split(UCase(s), " "); remove aala (L2514) all, aal1 (L2257) en, aall (L2703) ru, remrepW (L1697) adjacent, aal· (L2569) numbers, aook (L2371) wordforms; a later repeat goes, the first stays. find with the other modes and scopes has no handler: derived from their remove handlers; wordforms with a scope has no handler: derived from aook (L2371).

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

spaces.remove. VBA, RibbonCallbacks.vba (docs/vba/matchers.md R1): –aal (L1941) extra = a· (L1855), —ako (L2926) left = LTrim, a–o— (L2230) right = RTrim, a–k— (L1878) both = Trim; only U+0020 counts. all has no handler: derived from –aal, every space cut; vba is the derived value. –aal (L1941) is the button «Лишние пробелы > Все».

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

word_content. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F2, R2, X2). find: —ka— (L2082) starts, —kaa (L2225) starts a list, —kao (L2670) ends; remove: aoaa (L2653) starts, aoak (L2901) contains, a·—– (L2456) only_latin, a·a– (L2336) has_latin, a·—— (L2780) only_digits (IsNumeric, ru locale), a·a— (L1864) has_digits; extract: –·–a (L1903) starts, ——·– (L2107) only_latin, –—k— (L2442) has_latin, ——·— (L2127) only_digits, a·o– (L2916) mixed. A token is tested with its punctuation, UCase, ё ≠ е. find by a kind of characters has no handler: derived from its remove and extract handlers; vba is the derived value. More handlers. find: —ka– (L2759) ends a list, —kk— (L2556) contains a list; contains one pattern has no handler (SEM_findCellsContainingPattern is missing): derived from —kk— (L2556). remove: aoa· (L1762) starts a list, aoa– (L1887) ends, aoa— (L2706) ends a list, aoao (L2183–2185) contains a list; mixed has no handler: derived from a·o– (L2916). extract: –·–· (L2513) starts a list, –·–– (L1816) ends, –·–— (L2330) ends a list, –·k· (L2156) contains a list, –—k– (L2416) has_digits; contains one pattern has no handler: derived from –·k· (L2156).

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

word_position. VBA, RibbonCallbacks.vba (docs/vba/matchers.md R2, X2). remove: ak—k (L2081), ak—– (L2485), ak—a (L2939) first; aka— (L1940) last; "" when the cell has N words or fewer. extract: –—·— (L1828) first; –ak— (L1711) last; –—o– (L2133), –a–k (L1850) nth with k·k (L1851); –·—k (L1599) to_middle and –·—o (L1612) at_most with o·— (L1403). Split(s, " "): an empty token of a double space is a word. remove with at_most and every find have no handler: derived from the extract handlers (find is TRUE where extract gives words); vba is the derived value. More handlers. remove: ak—o (L2659) first; ak·o (L2270) and the other «Последние» buttons last; nth and to_middle have no handler: derived from k·k (L1851) and o·— (L1403), the words extract would not give. extract: –—a— (L1877) first; –ak– (L1778), –aok (L2137) last; –—oo (L2847) nth (the 1st word is –—a—). o·— (L1403): the leading words while the phrase so far has the limit of characters at most; the first always.

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

## words

words. VBA, RibbonCallbacks.vba (docs/vba/matchers.md F2, R2, X2). find: –––o (L1927) one word = ·a– (L2573), –––k (L2805) all; remove: ao—a (L1835) one word, dFWCustom (L2309) start, dLWCustom (L2308) end; extract: –·oo (L2567). UCase on both sides, ё ≠ е, Split(s, " "); ignore_punct is the «Игнорировать пунктуацию» variant (oka, L2460). extract with where has no handler: derived from –·oo; vba is the derived value. More handlers. find: —k—k (L2218) any; start and end have no handler: derived from dFWCustom (L2309) and dLWCustom (L2308). remove: aok– (L2733) any; all has no handler: derived from –––k (L2805). extract: one word or any of the list as the phrase spells them; start, end and all have no handler: derived from –·oo (L2567). ignore_punct takes only the edges of a word; lemmatizer has no handler: derived from –––o (L1927).

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
