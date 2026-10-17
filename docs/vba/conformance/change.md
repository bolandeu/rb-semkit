# Conformance of the change area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/change/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [change_case](#change_case) | 24 | 18 | 6 | 0 |
| [chpu](#chpu) | 5 | 0 | 5 | 0 |
| [drop_minus_words](#drop_minus_words) | 6 | 3 | 3 | 0 |
| [drop_modifiers](#drop_modifiers) | 5 | 4 | 1 | 0 |
| [extract_utm](#extract_utm) | 6 | 1 | 5 | 0 |
| [fix_word_order](#fix_word_order) | 8 | 4 | 4 | 0 |
| [guillemets](#guillemets) | 5 | 3 | 2 | 0 |
| [hash_text](#hash_text) | 5 | 5 | 0 | 0 |
| [insert](#insert) | 6 | 6 | 0 | 0 |
| [match_type](#match_type) | 19 | 12 | 7 | 0 |
| [move_words](#move_words) | 6 | 4 | 2 | 0 |
| [phonetic](#phonetic) | 7 | 5 | 2 | 0 |
| [remove_utm](#remove_utm) | 7 | 5 | 2 | 0 |
| [replace_text](#replace_text) | 10 | 5 | 5 | 0 |
| [replace_words](#replace_words) | 7 | 4 | 3 | 0 |
| [reverse](#reverse) | 5 | 4 | 1 | 0 |
| [similar_chars](#similar_chars) | 5 | 5 | 0 | 0 |
| [sort_words](#sort_words) | 5 | 5 | 0 | 0 |
| [split_digits](#split_digits) | 5 | 3 | 2 | 0 |
| [switch_layout](#switch_layout) | 7 | 3 | 4 | 0 |
| [translit](#translit) | 6 | 5 | 1 | 0 |
| **All** | **159** | **104** | **55** | **0** |

## change_case

change_case. VBA, RibbonCallbacks.vba (docs/vba/change.md 1.1–1.10): lower a––a (L2597); upper a––– (L2242); title a––— (L2098) by a·a (L1721); sentence a––o (L1909) by ooo­ (L1328); sentence_lower a·o· (L2915) by o·a– (L1329); latin_title a–o· (L2314); latin_upper a–oa (L2177); list_title ––kk (L2096) and list_upper ––ko (L1749) by kko (L2860), the user list in place of the selected range; toponyms ———k (L2623) with the geo list (GEO_Toponyms); abbreviations a––k (L1894): TransformWordsCase (L1012–1014), then ChangeCase1ColumnRange (L1011) with abbrs.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `change_case` | 24 | 18 | 6 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| case-sentence-after-space | `"привет. как дела?да"` | `"Привет. как дела?Да"` | `"Привет. Как дела?Да"` | Предложение начинается после «.», «!» или «?» и пробелов за ними | ooo­ splits right after «.» and upper-cases the space before «как» |
| case-sentence-backslash | `"a\b"` | `"AB"` | `"A\b"` | Предложение начинается после «.», «!» или «?» и пробелов за ними | the backslash is a split point of ooo­ and is lost; each part gets its first char upper |
| case-sentence-lower-glued | `"Да.ДА"` | `"да.да"` | `"да.дА"` | Строчное начало предложения меняет одну первую букву | o·a– lowers the first two chars of each part: «ДА» → «да» |
| case-list-yo | `"искусственная елка"` | `"искусственная елка"` | `"искусственная ЕЛКА"` | ё = е при сравнении | kko compares UCase as typed: «ЕЛКА» is not «ЁЛКА» |
| case-toponyms-yo | `"отели в орел"` | `"отели в Орел"` | `"отели в Орёл"` | ё = е при сравнении | the geo list holds «Орёл» before «Орел»; semkit takes both as one name and its first spelling |
| case-abbreviations-pollution | `"2шт ао2"` | `"2ШТ ао2"` | `"2ШТ АО2"` | Признак аббревиатуры не зависит от соседних слов | the first char «2» of «2шт» enters the class dictionary with no class, and inside «ао2» it makes the vowel word mixed |

### xfail

None.

## chpu

chpu. VBA, RibbonCallbacks.vba (docs/vba/change.md 6.5): ––oa (L2749) with chpuSym (abc!E10000:F10965) and the digits added in code.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `chpu` | 5 | 0 | 5 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| chpu-hyphen | `"Диван-кровать 2 м!"` | `"Divankrovat-2-m"` | `"divan-krovat-2-m"` | ЧПУ в нижнем регистре; пробелы и знаки между словами — один «-», без «-» по краям и двойных «-» | the case stays, «-» and «!» are not keys of chpuSym and are dropped |
| chpu-spaces | `"Щётка  ёж"` | `"Schetka--ezh"` | `"schetka-ezh"` | ЧПУ в нижнем регистре; пробелы и знаки между словами — один «-», без «-» по краям и двойных «-» | each space gives «-»: two spaces give «--» |
| chpu-edges | `" диван "` | `"-divan-"` | `"divan"` | ЧПУ в нижнем регистре; пробелы и знаки между словами — один «-», без «-» по краям и двойных «-» | the spaces at the edges give «-» at the edges |
| chpu-accents | `"Café Æon"` | `"Cafe-AEon"` | `"cafe-aeon"` | ЧПУ в нижнем регистре; пробелы и знаки между словами — один «-», без «-» по краям и двойных «-» | the case stays: «Cafe-AEon» |
| chpu-latin | `"iphone_13.pro"` | `"iphone13pro"` | `"iphone-13-pro"` | ЧПУ в нижнем регистре; пробелы и знаки между словами — один «-», без «-» по краям и двойных «-» | «_» and «.» are not keys of chpuSym and are dropped: the words glue together |

### xfail

None.

## drop_minus_words

drop_minus_words. VBA, RibbonCallbacks.vba (docs/vba/change.md 7.9): a·ao (L1783) by –k– (L2355): the cell up to the first « -».

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `drop_minus_words` | 6 | 3 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| drop-minus-dash | `"диван - кровать"` | `"диван"` | `"диван - кровать"` | Минус-слово — слово, которое начинается с «-» и не равно ему | « - » cuts the cell like a minus-word |
| drop-minus-start | `"-бесплатно"` | `"-бесплатно"` | `""` | Минус-слово — слово, которое начинается с «-» и не равно ему | no space stands before «-бесплатно»: InStrB finds only the appended « -» and keeps the cell |
| drop-minus-trailing | `"a  -b"` | `"a "` | `"a"` | Минус-слово — слово, которое начинается с «-» и не равно ему | the cut keeps the space before « -b» |

### xfail

None.

## drop_modifiers

drop_modifiers. VBA, RibbonCallbacks.vba (docs/vba/change.md 7.8): a·ak (L2680) by oo·— (L2279), with a–l (L1008) and ka—· (L1681) that never cut the minus-words (the Select Case bug).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `drop_modifiers` | 5 | 4 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| drop-modifiers-case | `"+купить +В москве"` | `"+купить +В москве"` | `"+купить В москве"` | стоп-слова без учёта регистра | the set of oo·— holds «+в», in lower case only |

### xfail

None.

## extract_utm

extract_utm. VBA, RibbonCallbacks.vba (docs/vba/change.md 8.2): source –aa— (L2139), medium –ao— (L2598), campaign –—–· (L1754), term –a·o (L2399), content –—a– (L2313), all by extrUTM (L2763): the first match of utm_<name>=[^$#&]+.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `extract_utm` | 6 | 1 | 5 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| utm-extract-source | `"https://site.ru/?utm_source=yandex&utm_medium=cpc"` | `"utm_source=yandex"` | `"yandex"` | Извлечение UTM-метки даёт только значение, раскодированное из URL | extrUTM returns the whole match, with «utm_source=» |
| utm-extract-medium | `"https://site.ru/?utm_source=yandex&utm_medium=cpc"` | `"utm_medium=cpc"` | `"cpc"` | Извлечение UTM-метки даёт только значение, раскодированное из URL | extrUTM returns the whole match, with «utm_medium=» |
| utm-extract-decoded | `"?utm_source=%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81"` | `"utm_source=%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81"` | `"Яндекс"` | Извлечение UTM-метки даёт только значение, раскодированное из URL | extrUTM returns the whole match and does not URL-decode the value |
| utm-extract-case | `"https://site.ru/?UTM_CAMPAIGN=sale"` | `""` | `"sale"` | UTM-метка — параметр с именем на «utm_» в любом регистре | «UTM_CAMPAIGN» does not match the case-sensitive «utm_campaign» |
| utm-extract-content | `"https://site.ru/?utm_content=banner#top"` | `"utm_content=banner"` | `"banner"` | Извлечение UTM-метки даёт только значение, раскодированное из URL | extrUTM returns the whole match, with «utm_content=» |

### xfail

None.

## fix_word_order

fix_word_order. VBA, RibbonCallbacks.vba (docs/vba/change.md 3.3–3.4): with complements betterKeysPat (L1433) → BKP (L1429), betterKeysFem (L1434) → BKF (L1430), betterKeysFem2 (L1435) → BKF2 (L1431), betterKeysPlur (L1436) → BKM (L1432), by AdjToBeg (L1438), ··o (L1439), ··– (L2207) and moveToBeg (L1587); without complements characsPat (L1880), characsFem (L1881), characsFem2 (L1883), characsPlur (L1885). The list charsPat (abc!BA1:BA644) is declined by l­ (L2470) with adjSuffixes and adjExclusions; the parts of speech come from lemms.xlsb, here from the bundled lemmatizer.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `fix_word_order` | 8 | 4 | 4 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| order-plural | `"диваны купить недорогие"` | `"купить недорогие диваны "` | `"купить недорогие диваны"` | Без дополнений фраза не кончается пробелом | BKM returns Trim(r) & " " & Trim(ex): with no complements a space ends it |
| order-no-complement | `"диван угловой"` | `"угловой диван "` | `"угловой диван"` | Без дополнений фраза не кончается пробелом | BKP returns Trim(r) & " " & Trim(ex): with no complements a space ends it |
| order-main-word | `"для гостиной диван раскладной"` | `"раскладной для гостиной диван"` | `"раскладной диван для гостиной"` | Главное слово не уходит в дополнение | BKP resets the main word to "", so «для» takes «гостиной диван»: «диван» is the last noun of the scan |
| order-feminine-accusative | `"кровать купить двуспальную"` | `"купить двуспальную кровать "` | `"купить двуспальную кровать"` | Без дополнений фраза не кончается пробелом | BKF2 returns Trim(r) & " " & Trim(ex): with no complements a space ends it |

### xfail

None.

## guillemets

guillemets. VBA, RibbonCallbacks.vba (docs/vba/change.md 6.1): a·oa (L2008) by a·k— (L2057).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `guillemets` | 5 | 3 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| guillemets-tail | `"диван "Честер" купить"` | `"диван «Честер»"` | `"диван «Честер» купить"` | Кавычки в ёлочки сохраняют текст после последней кавычки | a·k— never appends the part « купить » after the closing quote |
| guillemets-odd | `"диван "Честер"` | `"диван «"` | `"диван «Честер"` | Кавычки в ёлочки сохраняют текст после последней кавычки | a·k— drops the part «Честер » after the last quote |

### xfail

None.

## hash_text

hash_text. VBA, RibbonCallbacks.vba (docs/vba/change.md 8.3): md5 (L1912) and sha256 (L1913) by zHashSel (L1914–1920) and zHash (L3259): the UTF-8 bytes, lower-case hex.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `hash_text` | 5 | 5 | 0 | 0 |

### Deviations

None.

### xfail

None.

## insert

insert. VBA, RibbonCallbacks.vba (docs/vba/change.md 2.1–2.3): before each word ——ak (L1717) and after each word ———a (L2616) by ——k (L2379); at the end –o—a (L2340), at the start –o—· (L2867), at both ends the same text ———· (L2722), different texts SEM_AddBnA (L329). The text comes from an InputBox or a form; here from before and after.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `insert` | 6 | 6 | 0 | 0 |

### Deviations

None.

### xfail

None.

## match_type

match_type. VBA, RibbonCallbacks.vba (docs/vba/change.md 7.1–7.7): broad a—·1 (L1610) by a·k (L1325); plus_every_word —·a· (L1891) by ·—1 (L2658); broad_modifier —·a— (L1935), then oo·— (L2279); stopword_modifier —·aa (L1846) by oa–· (L1009), the modifier from an InputBox; fixed_forms a·11 (L2747) by оо·· (L1318); quoted_fixed_forms a·—1 (L1800) by oo—a (L1320); quoted_fixed_order a·–1 (L2707) by oo–· (L1321); brackets a–·1 (L2817) by ·1l (L1316); quotes –a·1 (L2809) by oo­ (L1315); antisemantic antisem (L1010).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `match_type` | 19 | 12 | 7 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| match-plus-every-word-minus | `"купить !диван -бесплатно"` | `"+купить +!диван +-бесплатно"` | `"+купить !диван -бесплатно"` | Слово с оператором («+», «!», «-») не получает второй оператор | every token gets «+»: «+!диван», «+-бесплатно» |
| match-broad-modifier-case | `"Купить В Москве"` | `"+Купить +В +Москве"` | `"+Купить В +Москве"` | стоп-слова без учёта регистра | oo·— takes «+» off a stopword in lower case only: «+В» stays |
| match-fixed-forms-empty | `""` | `"!"` | `""` | Пустая фраза остаётся пустой | «!» & the Join of no tokens gives «!» |
| match-fixed-forms-operators | `"купить +в москве -бесплатно"` | `"!купить !+в !москве !-бесплатно"` | `"!купить +в !москве -бесплатно"` | Слово с оператором («+», «!», «-») не получает второй оператор | every token gets «!»: «!+в», «!-бесплатно» |
| match-quoted-fixed-order-empty | `""` | `""[!]""` | `""` | Пустая фраза остаётся пустой | the Join of no tokens inside «"[!» and «]"» gives «"[!]"» |
| match-brackets-minus | `"купить диван -бесплатно"` | `"[купить диван -бесплатно]"` | `"[купить диван] -бесплатно"` | Минус-слова остаются вне скобок и кавычек | ·1l puts the whole cell inside the brackets |
| match-antisemantic-spaces | `"диван  в москве -бесплатно"` | `"[диван] [] в [москве] [-бесплатно]"` | `"[диван] в [москве] -бесплатно"` | фраза делится по любым пробелам, двойных пробелов в результатах нет; Слово с оператором («+», «!», «-») не получает второй оператор | the empty token of the double space becomes «[]», and the minus-word gets brackets |

### xfail

None.

## move_words

move_words. VBA, RibbonCallbacks.vba (docs/vba/change.md 3.1–3.2): to the start —aao (L1879) by moveToBeg (L1587), to the end —aa– (L2784) by moveToEnd (L1588); the list is the first column of the selected range, here words.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `move_words` | 6 | 4 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| move-yo | `"искусственная елка"` | `"искусственная елка"` | `"ёлка искусственная"` | ё = е при сравнении | moveToBeg compares LCase: «ёлка» is not «елка» |
| move-spaces | `"диван купить"` | `"диван купить"` | `"купить диван"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | Split on the ASCII space only: «диван купить» with a no-break space is one token |

### xfail

None.

## phonetic

phonetic. VBA, RibbonCallbacks.vba (docs/vba/change.md 6.4): SEM_rT (L2426) by revtranslit (L3392), revTrans (L174–176) and the tables of InitDicts (L52–61), CheckCase (L3390), AdjustCase (L3391).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `phonetic` | 7 | 5 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| phonetic-latin-c | `"pictures"` | `"пикчерк"` | `"пикчерс"` | В фонетических таблицах латинская «c» в русских значениях заменена на «с» | s5 maps «tures» to «черc» with a latin «c», which a1 turns into «к» |
| phonetic-spaces | `"apple  iphone"` | `"эпл  айфон"` | `"эпл айфон"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | Split(s & " ") keeps the empty token: the two spaces stay |

### xfail

None.

## remove_utm

remove_utm. VBA, RibbonCallbacks.vba (docs/vba/change.md 8.1): a·aa (L2686) by —–1 (L2728): RegExReplace of (\?|&)utm_[^$#&]+, then the first «&» becomes «?» when no «?» is left.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `remove_utm` | 7 | 5 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| utm-remove-case | `"https://site.ru/?UTM_Source=ya&utm_medium=cpc&id=5#top"` | `"https://site.ru/?UTM_Source=ya&id=5#top"` | `"https://site.ru/?id=5#top"` | UTM-метка — параметр с именем на «utm_» в любом регистре | «UTM_Source» does not match the case-sensitive «utm_» |
| utm-remove-fragment-amp | `"https://site.ru/?utm_source=ya#a&b"` | `"https://site.ru/#a?b"` | `"https://site.ru/#a&b"` | Удаление UTM-меток оставляет правильные «?» и «&» | with no «?» left, the first «&» of the string, in the fragment, becomes «?» |

### xfail

None.

## replace_text

replace_text. VBA, RibbonCallbacks.vba (docs/vba/change.md 4.4–4.6): by substring ao·a (L2693) by k—o (L2870); the whole cell ao·k (L2483) by ko–— (L1016–1087) with ·–— (L1350) and ·ao (L2423); by regex, all matches —··— (L2278), the first ao·– (L2287), by RegExReplace (L2080). The VBA writes the groups as $1; the call here as \1.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `replace_text` | 10 | 5 | 5 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| replace-text-substring-yo | `"ёлка искусственная"` | `"ёлка искусственная"` | `"ель искусственная"` | ё = е при сравнении | vbTextCompare does not take «е» for «ё» |
| replace-text-phrase-spaces | `"москва "` | `"москва "` | `"спб"` | Целая фраза сравнивается без учёта лишних пробелов | the cell «москва » with its trailing space is not the key «МОСКВА» |
| replace-text-phrase-yo | `"елка"` | `"елка"` | `"ель"` | ё = е при сравнении | the UCase key «ЁЛКА» is not «ЕЛКА» |
| replace-text-regex-cyrillic | `"диван в москве"` | `"диван в москве"` | `"диван во москве"` | Регулярные выражения понимают кириллицу | VBScript \b is ASCII: there is no boundary round «в» |
| replace-text-regex-formula | `"x"` | `"'=+-x"` | `"=+-x"` | Результат замены по регулярному выражению не получает апостроф | the result starts with «=+-», so RegExReplace puts «'» before it |

### xfail

None.

## replace_words

replace_words. VBA, RibbonCallbacks.vba (docs/vba/change.md 4.1–4.3): word to word a–ko (L2228); list to list with the new case a–k– (L1760) by ReplacePhrases (L3471–3483), keeping the case a–k–2 (L1761) by ReplacePhrasesCS (L3484–3496) with CheckCase (L3390) and AdjustCase (L3391). The two columns of the selected range are pairs here.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `replace_words` | 7 | 4 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| replace-words-delete | `"диван купить москва"` | `"диван  москва"` | `"диван москва"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | the empty replacement leaves two spaces: « диван  москва » |
| replace-words-yo | `"искусственная елка"` | `"искусственная елка"` | `"искусственная ель"` | ё = е при сравнении | the LCase key «ёлка» is not «елка» |
| replace-words-spaces | `"купить  диван"` | `"купить  софа"` | `"купить софа"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | Split on single spaces keeps the empty token of the double space |

### xfail

None.

## reverse

reverse. VBA, RibbonCallbacks.vba (docs/vba/change.md 5.2–5.3): chars a·1— (L2604) by StrReverse; words —ka· (L2292) by ka–– (L1819).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `reverse` | 5 | 4 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| reverse-words-spaces | `"купить  диван"` | `"диван  купить"` | `"диван купить"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | Split on single spaces: the empty token of the double space is reversed too |

### xfail

None.

## similar_chars

similar_chars. VBA, RibbonCallbacks.vba (docs/vba/change.md 6.7): to en ao·· (L2945) by ok·a (L1896); to ru ao·o (L1660) by ok·— (L2146); 19 pairs.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `similar_chars` | 5 | 5 | 0 | 0 |

### Deviations

None.

### xfail

None.

## sort_words

sort_words. VBA, RibbonCallbacks.vba (docs/vba/change.md 5.4): a–ao (L2820) by srt (L2951) and the quicksort kkka (L1015), binary order.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `sort_words` | 5 | 5 | 0 | 0 |

### Deviations

None.

### xfail

None.

## split_digits

split_digits. VBA, RibbonCallbacks.vba (docs/vba/change.md 5.1): a—–1 (L2853) by a1a (L1690) = RegExExtract(s, "(\d+|[^\d]+)", True, sep) (L2970); sep from an InputBox.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `split_digits` | 5 | 3 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| split-digits-apart | `"iphone 13 pro"` | `"iphone  13  pro"` | `"iphone 13 pro"` | Разделитель ставится только между цифрами и текстом, которые стоят слитно | the runs «iphone », «13», « pro» joined by a space give double spaces |
| split-digits-apart-sep | `"iphone 13pro"` | `"iphone \|13\|pro"` | `"iphone 13\|pro"` | Разделитель ставится только между цифрами и текстом, которые стоят слитно | the space stays inside the run «iphone » |

### xfail

None.

## switch_layout

switch_layout. VBA, RibbonCallbacks.vba (docs/vba/change.md 6.6): to ru —··k (L2837) by okok (L1615); to en sem_revr (L2838) by revraskl (L1616).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `switch_layout` | 7 | 3 | 4 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| layout-ru-z | `"zyltrc"` | `"zндекс"` | `"яндекс"` | Клавиша «z» в раскладке — это «я» | the key of «я» in the literal is «·», so «z» stays |
| layout-en-ya | `"яндекс"` | `"·yltrc"` | `"zyltrc"` | Клавиша «z» в раскладке — это «я» | «я» becomes the 33rd char of the literal, «·» |
| layout-en-shifted | `"Бык"` | `",sr"` | `"<sr"` | Заглавная буква на клавише знака даёт знак с Shift | «Б» becomes UCase(«,»), which is «,» |
| layout-ru-shifted | `"<sr"` | `"<ык"` | `"Бык"` | Заглавная буква на клавише знака даёт знак с Shift | «<» is not in the literal and stays |

### xfail

None.

## translit

translit. VBA, RibbonCallbacks.vba (docs/vba/change.md 6.2–6.3): to en aa·o (L2144) by ooa— (L2275); to ru a·—· (L2368) by o·a— (L1351), 79 pairs replaced in order.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `translit` | 6 | 5 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| translit-en-caps | `"ЖУК ЩИ"` | `"ZhUK SchI"` | `"ZHUK SCHI"` | Слово заглавными в транслите остаётся заглавным | StrConv ProperCase writes «Ж» as «Zh» and «Щ» as «Sch» inside a word in capitals |

### xfail

None.
