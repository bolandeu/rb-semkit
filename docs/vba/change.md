# !SEMTools VBA reference — CHANGE functions

Algorithms of the «ИЗМЕНИТЬ» ribbon group and of the CHANGE-type buttons in «Web (Парсинг, SEO, PPC)», traced
from `/Users/bolandau/Work/_sandbox/semtools/reverse/vba/RibbonCallbacks.vba`. Names are the obfuscated VBA names
as they appear in the file; line numbers are lines of that file. Ribbon paths come from
`/Users/bolandau/Work/_sandbox/semtools/reverse/ribbon_full.txt`. Named ranges are from the add-in's
`xl/workbook.xml` (sheet `abc` data is in `/Users/bolandau/Work/_sandbox/semtools/reverse/data/sheet_abc.tsv`).

Out of scope here: declension («Просклонять»), translation, numbers, range sort, fill blanks, pivots.

## Index

| Menu path | Handler | Section |
|---|---|---|
| ИЗМЕНИТЬ › Символы › Регистр › Слов › аб аб. аб | `a––a` | [1.1](#11-lower-case) |
| ИЗМЕНИТЬ › Символы › Регистр › Слов › Аб Аб. Аб | `a––—` | [1.2](#12-every-word-capitalised) |
| ИЗМЕНИТЬ › Слова › Изменить регистр › Каждое слово с заглавной | `a––—` | [1.2](#12-every-word-capitalised) |
| ИЗМЕНИТЬ › Символы › Регистр › Слов › АБ АБ. АБ | `a–––` | [1.3](#13-upper-case) |
| ИЗМЕНИТЬ › Символы › Регистр › Предложений › Аб аб аб. Аб | `a––o` | [1.4](#14-sentence-starts-upper) |
| ИЗМЕНИТЬ › Символы › Регистр › Предложений › аб Аб АБ. аБ | `a·o·` | [1.5](#15-sentence-starts-lower) |
| ИЗМЕНИТЬ › Символы › Регистр › Слов с латиницей › аб Ab аб | `a–o·` | [1.6](#16-latin-words-capitalised) |
| ИЗМЕНИТЬ › Символы › Регистр › Слов с латиницей › аб ABC аб | `a–oa` | [1.7](#17-latin-words-upper) |
| ИЗМЕНИТЬ › Символы › Регистр › Топонимы с заглавной | `———k` | [1.8](#18-toponyms-capitalised) |
| ИЗМЕНИТЬ › Символы › Регистр › BMW RPG RGB | `a––k` | [1.9](#19-abbreviations) |
| ИЗМЕНИТЬ › Слова › Изменить регистр › Слова из списка - с заглавной | `––kk` | [1.10](#110-list-words-capitalised--upper) |
| ИЗМЕНИТЬ › Слова › Изменить регистр › Слова из списка - все заглавные | `––ko` | [1.10](#110-list-words-capitalised--upper) |
| ИЗМЕНИТЬ › Слова › Вставить символы › После каждого слова | `———a` | [2.1](#21-insert-after--before-each-word) |
| ИЗМЕНИТЬ › Слова › Вставить символы › Перед каждым словом | `——ak` | [2.1](#21-insert-after--before-each-word) |
| ИЗМЕНИТЬ › Ячейки › Вставить › В конце | `–o—a` | [2.2](#22-insert-at-cell-end--start--both) |
| ИЗМЕНИТЬ › Ячейки › Вставить › В начале | `–o—·` | [2.2](#22-insert-at-cell-end--start--both) |
| ИЗМЕНИТЬ › Ячейки › Вставить › В конце и в начале (одно и то же) | `———·` | [2.2](#22-insert-at-cell-end--start--both) |
| ИЗМЕНИТЬ › Ячейки › Вставить › В конце и в начале (разные значения) | `SEM_AddBnA` | [2.3](#23-insert-different-text-at-start-and-end) |
| ИЗМЕНИТЬ › Слова › Переместить › В начало строки | `—aao` | [3.1](#31-move-list-words-to-start) |
| ИЗМЕНИТЬ › Слова › Переместить › В конец строки | `—aa–` | [3.2](#32-move-list-words-to-end) |
| Web › Изменить › Слова › Поправить порядок слов › определения › Мужской род объекта | `characsPat` | [3.3](#33-word-order-definitions-charspat) |
| Web › … › определения › Женский, именительный | `characsFem` | [3.3](#33-word-order-definitions-charspat) |
| Web › … › определения › Женский, винительный | `characsFem2` | [3.3](#33-word-order-definitions-charspat) |
| Web › … › определения › Множественное | `characsPlur` | [3.3](#33-word-order-definitions-charspat) |
| Web › … › определения+дополнения › Мужской род объекта | `betterKeysPat` → `BKP` | [3.4](#34-word-order-definitions--complements-bk) |
| Web › … › определения+дополнения › Женский, именительный | `betterKeysFem` → `BKF` | [3.4](#34-word-order-definitions--complements-bk) |
| Web › … › определения+дополнения › Женский, винительный | `betterKeysFem2` → `BKF2` | [3.4](#34-word-order-definitions--complements-bk) |
| Web › … › определения+дополнения › Множественное | `betterKeysPlur` → `BKM` | [3.4](#34-word-order-definitions--complements-bk) |
| ИЗМЕНИТЬ › Слова › Заменить › Слово на слово | `a–ko` | [4.1](#41-word--word) |
| ИЗМЕНИТЬ › Заменить › Целые слова и фразы › Слово на слово | `a–ko` | [4.1](#41-word--word) |
| ИЗМЕНИТЬ › Слова › Заменить › Список на список | `a–k–` | [4.2](#42-list--list-apply-target-case) |
| ИЗМЕНИТЬ › Заменить › Целые слова и фразы › Список на список (применить конечный регистр) | `a–k–` | [4.2](#42-list--list-apply-target-case) |
| ИЗМЕНИТЬ › Заменить › Целые слова и фразы › Список на список (сохранить исходный регистр) | `a–k–2` | [4.3](#43-list--list-keep-source-case) |
| ИЗМЕНИТЬ › Заменить › Массовая замена по вхождению | `ao·a` | [4.4](#44-mass-replace-by-substring) |
| ИЗМЕНИТЬ › Заменить › Массовая замена целых ячеек | `ao·k` | [4.5](#45-mass-replace-of-whole-cells) |
| ИЗМЕНИТЬ › Заменить › По RegEx › Первое вхождение | `ao·–` | [4.6](#46-regex-replace-first--all) |
| ИЗМЕНИТЬ › Заменить › По RegEx › Все вхождения | `—··—` | [4.6](#46-regex-replace-first--all) |
| ИЗМЕНИТЬ › Слова › Отделить текст от цифр | `a—–1` | [5.1](#51-split-text-from-digits) |
| ИЗМЕНИТЬ › Ячейки › Развернуть › Символы | `a·1—` | [5.2](#52-reverse-characters) |
| ИЗМЕНИТЬ › Ячейки › Развернуть › Порядок слов | `—ka·` | [5.3](#53-reverse-word-order) |
| ИЗМЕНИТЬ › Ячейки › Сортировать А-Я внутри | `a–ao` | [5.4](#54-sort-words-inside-a-cell) |
| ИЗМЕНИТЬ › Символы › Кавычки->Ёлочки | `a·oa` | [6.1](#61-quotes--ёлочки) |
| ИЗМЕНИТЬ › Символы › Замена en-ru-en › Транслит › Фыва -> Fyva | `aa·o` | [6.2](#62-translit-ru--en) |
| ИЗМЕНИТЬ › Символы › Замена en-ru-en › Транслит › Fyva -> Фыва | `a·—·` | [6.3](#63-translit-en--ru) |
| ИЗМЕНИТЬ › Символы › Замена en-ru-en › Транслит › Dreamline -> Дримлайн | `SEM_rT` | [6.4](#64-phonetic-en--ru-dreamline--дримлайн) |
| Web › Изменить › Символы - транслитерация в ЧПУ | `––oa` | [6.5](#65-чпу-transliteration) |
| ИЗМЕНИТЬ › Символы › Замена en-ru-en › Сменить раскладку › Asdf -> Фыва | `—··k` | [6.6](#66-keyboard-layout-switch) |
| ИЗМЕНИТЬ › Символы › Замена en-ru-en › Сменить раскладку › Фыва -> Asdf | `sem_revr` | [6.6](#66-keyboard-layout-switch) |
| ИЗМЕНИТЬ › Символы › Замена en-ru-en › Заменить похожие › Ru -> En | `ao··` | [6.7](#67-similar-characters-cyr--lat) |
| ИЗМЕНИТЬ › Символы › Замена en-ru-en › Заменить похожие › En -> Ru | `ao·o` | [6.7](#67-similar-characters-cyr--lat) |
| Web › Изменить › Типы соотв-я › Широкое › A в Б | `a—·1` | [7.1](#71-broad-a-в-б-strip-operators) |
| Web › Изменить › Типы соотв-я › Широкое › +A +в +Б | `—·a·` | [7.2](#72-plus-on-every-word-a-в-б) |
| Web › Изменить › Типы соотв-я › Широкое › +A в +Б | `—·a—` | [7.3](#73-plus-on-every-word-except-stopwords-a-в-б) |
| Web › Изменить › Типы соотв-я › Широкое › A +в Б | `—·aa` | [7.4](#74-modifier-only-on-stopwords-a-в-б) |
| Web › Изменить › Типы соотв-я › Широкое › !A !в !Б | `a·11` | [7.5](#75-a-в-б-and-quoted-variants) |
| Web › Изменить › Типы соотв-я › Фразовое › [A в Б] - Yandex | `a–·1` | [7.6](#76-brackets-and-quotes-around-the-cell) |
| Web › Изменить › Типы соотв-я › Точное › Google › [A в Б] - Google | `a–·1` | [7.6](#76-brackets-and-quotes-around-the-cell) |
| Web › Изменить › Типы соотв-я › Фразовое › ''A в Б'' - Google | `–a·1` | [7.6](#76-brackets-and-quotes-around-the-cell) |
| Web › Изменить › Типы соотв-я › Точное › Yandex › ''А в Б'' | `–a·1` | [7.6](#76-brackets-and-quotes-around-the-cell) |
| Web › Изменить › Типы соотв-я › Точное › Yandex › ''!А !в !Б'' | `a·—1` | [7.5](#75-a-в-б-and-quoted-variants) |
| Web › Изменить › Типы соотв-я › Точное › Yandex › ''[!А !в !Б]'' | `a·–1` | [7.5](#75-a-в-б-and-quoted-variants) |
| Web › Изменить › Типы соотв-я › Анти-семантическое (Yandex) › [А] в [Б] | `antisem` | [7.7](#77-anti-semantic-а-в-б) |
| Web › Изменить › Типы соотв-я › Удалить модификаторы у стоп-слов | `a·ak` | [7.8](#78-remove-modifiers-from-stopwords) |
| Web › Изменить › Типы соотв-я › Удалить минус-слова | `a·ao` | [7.9](#79-remove-minus-words) |
| Web › Удалить › Из URL › UTM-метки | `a·aa` | [8.1](#81-remove-utm-tags-from-url) |
| Web › Извлечь › Из URL › utm_... › source / medium / campaign / term / content | `–aa—` / `–ao—` / `–—–·` / `–a·o` / `–—a–` | [8.2](#82-extract-utm_-value) |
| Web › Изменить › Шифровать md5 хешированием | `md5` | [8.3](#83-hashes-md5--sha-256) |
| Web › Изменить › Шифровать SHA-256 хешированием | `sha256` | [8.3](#83-hashes-md5--sha-256) |

72 ribbon buttons, 67 distinct handlers.

---

## 0. Shared helpers and conventions

### 0.1 VBA semantics that matter for a port

- `Option Base 1` is set for the module. So `Array(...)` is 1-based. `Split(...)` is always 0-based.
- No `Option Compare Text`: `=`, `<`, `InStr`, `Replace` are binary (case-sensitive, code-unit order) unless
  `vbTextCompare` is passed. `UCase$`/`LCase$` are Unicode-aware (Cyrillic works).
- `Split(s)` and `Split(s, " ")` split on the ASCII space only. Consecutive spaces give empty tokens.
  Tab, NBSP and line breaks are not separators. `Split("")` returns an empty array (UBound −1).
- `Trim$` removes ASCII spaces only.
- `Scripting.Dictionary` keys are case-sensitive (binary). Reading `dict(missingKey)` inserts the key with value Empty.
- Many functions use the idiom `Split(s & " ")` and loop `0 .. UBound-1`: this processes every space token
  (empty tokens included) and skips the artificial last empty token.
- `Application.VLookup(key, col, 1, True) = key` is used as "key is in the sorted list" (approximate binary
  search plus equality check). Excel compares case-insensitively, the following `=` is binary. In Python: set
  membership with the case rule of the caller.

### 0.2 Run frame (Excel only, not ported)

Every handler starts with some of these and ends with `—k`:

| Helper | Lines | What it does |
|---|---|---|
| `·l` | 2753 | If a whole column is selected, shrink the selection to row 1 … last used row. |
| `k–—` | 2150 | Same shrink, only for a single whole column. |
| `·——` | 2631 | Undo backup: copies every selected area to sheet `def` (same addresses), unless "output right" mode. Used by `retP` (undo button). |
| `a–` | 2667 | `zArm` (30 s safety timer), ScreenUpdating off, manual calculation, alerts off. |
| `—k` | 2344 | Restores Excel state. |
| `zSel` | 2752 | Returns `Selection.Value2` as a 2-D array (a 1×1 array for one cell). For a multi-area selection this is the first area only. |
| `k–k` | 2933 | Writes the result array back to `Selection`. If "output right" is on (`–aa`, line 1742: licensed and `abc!AU4` = True) and the selection is one column, it inserts a new column to the right and writes there. |
| `oao` | 2464 | Same as `k–k` for one area `rng`. |

Settings: `abc!AU4` = checkbox «Выводить результат справа» (`–aa`); `abc!AU3` = checkbox «Игнорировать пунктуацию»
(`·Oo`, line 1952). In the CHANGE area `·Oo` is read only by 1.10 (list words case) and 4.5 (whole-cell replace).

### 0.3 License gate (ignore in the port)

`—–(al(k—()), <range>)` (lines 2006, 302, 1810) checks the machine hash against `abc!O:O`. When it fails:
`c_h` (line 841) overwrites ⌊rows/3⌉ random rows of column 1 with «Доступно в полной версии !SEMTools»; in the
per-column runners (0.4, pattern B) columns 2+ become `—aa` (line 1701, the same text with Latin look-alike
letters) and in column 1 each row is processed with probability 2/3 (`o–·`, line 2657). Multi-area selections
show `MsgBox okk` and stop. The port behaves as licensed.

### 0.4 Runner patterns

Each handler applies a per-string function `f` with one of three runners:

- **A — every cell** (`a = zSel(); for r, d: a(r,d) = f(CStr(a(r,d))); k–k a`). All columns of the first area.
  Empty cells are processed as `""`.
- **B — per area, per column** (`k–` line 1937, `·a` 441, `–1` 442, `strStrRng` 443, and the inline copies in
  `a–ko`, `a—–1`, `SEM_AddBnA`, `ao·–`, `—··—`, `—aao`, `—aa–`, `ao·a`, `zHashSel`). Every area, every column,
  every row; a one-cell area is processed directly. Result written with `oao`.
- **C — column 1 only** (`oa—·`, `TransformWordsCase`, `ChangeCase1ColumnRange`, `ReplacePhrases*`, `ko–—`,
  `––oa`, `oo·—`, `oa–·`, `antisem`). Only `a(r, 1)` is read and changed; other columns are written back unchanged.

For the port all three reduce to `list[str] -> list[str]` (map over cells). Pattern C is an Excel limitation:
apply to every input string.

Excel side effect of writing: the result array is assigned to `Range.Value`, so Excel re-parses strings
(numeric-looking text becomes a number, leading zeros are lost, text that starts with `=` becomes a formula).
`RegExReplace` tries to guard this (see 4.6). Not ported: the port returns strings.

### 0.5 String helpers

| Helper | Lines | Exact behaviour |
|---|---|---|
| `a·(s)` | 1855 | `Trim$`, then replace `"  "` with `" "` until none left. "Normalize spaces" (ASCII space only). |
| `a·a(s)` | 1721 | "Proper": `s = LCase(s)`; `up = True`; for each char: if it is a letter (`LCase(ch) <> UCase(ch)`): if `up` then upper-case it and `up = False`; else (any non-letter, digits included) `up = True`. So every letter that follows a non-letter is capitalised: `o'neil` → `O'Neil`, `5g` → `5G`, `иван-петров` → `Иван-Петров`. |
| `ka–o(s)` | 1327 | `UCase(Left(s,1)) & Mid(s,2)`. |
| `–o—(s)` / `о·—a(s)` / `oo—·(s)` | 2560 / 1654 / 2605 | `UCase$` / `LCase$` / `LCase$`. |
| `a—k(s)` | 2175 | First space token: `Left(s, InStr(s & " ", " ") - 1)`. |
| `oko(s)` | 1332 | "Clean punctuation": each char that is a space, a digit `0-9`, or a cased letter is kept; any other char becomes a space; then `a·`. `"wi-fi!"` → `"wi fi"`. |
| `—a—(tok, rng)` | 2675 | `UCase$(tok)` is in column 1 of the sorted list `rng` (VLookup idiom). |
| `oa(key, rng, k)` | 2208 | If `key` is in column 1 of sorted `rng` → value of column `k` of that row; else `key` itself (also on any error). |
| `·–—(s)` | 1350 | Case class of a whole string: `"UP"` if `s = UCase(s)` (also true for digits-only and empty); else `"Pr"` if `a·a(s) = s`; else `"lc"`. |
| `·ao(t, cls)` | 2423 | Apply class: `"lc"` → `LCase(t)`; `"Pr"` → `a·a(t)`; anything else → `UCase(t)`. |
| `CheckCase(p)` | 3390 | Class of the first space token `w` of `p`: `""` → 0; `w = LCase(w)` → 1; `w = Application.Proper(w)` → 2; `w = UCase(w)` → 3; else 4. Note: digits-only `w` → 1. Excel `PROPER` capitalises the first letter of each letter run (like `a·a`). |
| `AdjustCase(t, ct)` | 3391 | 1 → `LCase(t)`; 2 → `UCase(Left(t,1)) & Mid(t,2)` (rest unchanged); 3 → `UCase(t)`; else `t`. |
| `RegExReplace(s, pat, rep, glob=True, ic=False, ml=False)` | 2080 | If `s` or `pat` is empty → `s`. Else VBScript.RegExp replace (ECMAScript-3 dialect, `$1` back-references); an invalid pattern returns `s` unchanged. Then if the result starts with the literal 3 chars `=+-` (case-insensitive) it is prefixed with `'`. |
| `RegExExtract(s, pat, glob=False, sep="")` | 2970 | Joins the values of all matches with `sep` (only the first match when `glob=False`). Case-sensitive (`IgnoreCase` is an undeclared variable = False). |
| `——k(fn, s, arg)` | 2379 | If `a·(s) = ""` → `s` unchanged. Else `o = Split(s & " ")`; `o(g) = fn(o(g), arg)` for `g = 0..UBound-1`; return `a·(Join(o," "))`. |
| `ka(fn, s, k)` | 2669 | Same as `——k` without the empty check. |
| `–—l(test, fn, s)` | 1938 | Per token of `Split(s & " ")`: if `test(tok)` then `tok = fn(tok)`; return `a·(Join)`. |
| `kko(test, fn, s, rng, clean=False)` | 2860 | Per token: `test(tok, rng)` (or `test(oko(tok), rng)` when `clean`) → `tok = fn(tok)` (the original token, punctuation kept); return `a·(Join)`. |
| `moveToBeg` / `moveToEnd` | 1587 / 1588 | See 3.1 / 3.2. |
| `stopwords()` | 1374–1378 | 440 space-separated lowercase words, English then Russian (includes the odd entry `g`). No duplicates, also none after `UCase`. |

---

## 1. Case

### 1.1 Lower case
### ИЗМЕНИТЬ › Символы › Регистр › Слов › аб аб. аб
- Handler: `a––a` (line 2597); helpers: `о·—a` (1654).
- Input / output: selection, runner A; every cell replaced in place.
- Algorithm: `LCase$(cell)`.
- Quirks: none.
- ADR 0005 deviation: none.

### 1.2 Every word capitalised
### ИЗМЕНИТЬ › Символы › Регистр › Слов › Аб Аб. Аб (also Слова › Изменить регистр › Каждое слово с заглавной)
- Handler: `a––—` (line 2098); helpers: `a·a` (1721).
- Input / output: runner A, in place.
- Algorithm: `a·a(cell)` — lower-case everything, then upper-case each letter that is the first letter of the
  string or follows any non-letter character.
- Quirks: apostrophes and digits start a new "word": `don't` → `Don'T`, `iphone12pro` → `Iphone12Pro`.
- ADR 0005 deviation: none.
- Example: `купить ДИВАН-кровать в спб` → `Купить Диван-Кровать В Спб`.

### 1.3 Upper case
### ИЗМЕНИТЬ › Символы › Регистр › Слов › АБ АБ. АБ
- Handler: `a–––` (line 2242); helpers: `–o—` (2560).
- Input / output: runner A, in place. Algorithm: `UCase$(cell)`. Quirks: none. ADR 0005 deviation: none.

### 1.4 Sentence starts upper
### ИЗМЕНИТЬ › Символы › Регистр › Предложений › Аб аб аб. Аб
- Handler: `a––o` (line 1909); helpers: `ooo­` (1328), `ka–o` (1327).
- Input / output: runner A, in place.
- Algorithm:
  1. `t = Replace(Replace(Replace(s, "!", "!\"), ".", ".\"), "?", "?\")`.
  2. `parts = Split(t, "\")`.
  3. Result = concatenation of `ka–o(part)` (upper-case the first character of each part) for all parts.
- Quirks:
  - The first char after `.`/`!`/`?` is usually a space, and `ka–o(" как")` changes nothing. So only the first
    char of the cell and a char glued to the punctuation are capitalised.
  - Any backslash already in the text is a split point and is deleted.
  - Other chars (rest of the text) are not lowered.
- ADR 0005 deviation: defect — capitalise the first letter after the sentence end and following spaces; keep
  backslashes.
- Examples: `привет. как дела?да` → `Привет. как дела?Да`; `ул.ленина` → `Ул.Ленина`; `a\b` → `Ab`.

### 1.5 Sentence starts lower
### ИЗМЕНИТЬ › Символы › Регистр › Предложений › аб Аб АБ. аБ
- Handler: `a·o·` (line 2915); helpers: `o·a–` (1329).
- Input / output: runner A, in place.
- Algorithm: same split as 1.4. Part 0: `LCase(Left(p,1)) & Mid(p,2)`. Parts 1+: `LCase(Left(p,2)) & Mid(p,3)`
  (two chars, to cover the space). Concatenate.
- Quirks:
  - An empty cell raises "subscript out of range" (`Split("")` has no element 0) and the macro stops with Excel
    left in manual mode.
  - With no space after the dot, the first two letters are lowered: `Да.ДА` → `да.дА`.
  - Backslashes are deleted (as 1.4).
- ADR 0005 deviation: defect — empty string → empty string; lower only the first letter of each sentence.
- Example: `Привет. Как Дела` → `привет. как Дела`.

### 1.6 Latin words capitalised
### ИЗМЕНИТЬ › Символы › Регистр › Слов с латиницей › аб Ab аб
- Handler: `a–o·` (line 2314); helpers: `koo–` (2866).
- Input / output: runner A, in place.
- Algorithm: `a = Split(s, " ")`; for each token: if its first char is in `abcdefghijklmnopqrstuvwxyz` (binary)
  → `UCase(first char) & rest`. `Join(a, " ")` (spaces kept as is).
- Quirks: only a lowercase ASCII first char triggers; `(iphone` and `Iphone` are unchanged; `iPhone` → `IPhone`.
- ADR 0005 deviation: none (whitespace rule: split on any whitespace).
- Example: `чехол iphone 13 для samsung` → `чехол Iphone 13 для Samsung`.

### 1.7 Latin words upper
### ИЗМЕНИТЬ › Символы › Регистр › Слов с латиницей › аб ABC аб
- Handler: `a–oa` (line 2177); helpers: `о·–—` (2758) → `–—l("a–—", "–o—", s)` (1938), `a–—` (2153).
- Input / output: runner A, in place.
- Algorithm: tokens of `Split(s & " ")`; a token that matches `Like "*[A-Za-z]*"` (contains an ASCII letter) is
  upper-cased whole; result `a·(Join)`.
- Quirks: a mixed token is upper-cased whole, Cyrillic included: `wi-fi-роутер` → `WI-FI-РОУТЕР`. Double spaces
  collapse.
- ADR 0005 deviation: none.

### 1.8 Toponyms capitalised
### ИЗМЕНИТЬ › Символы › Регистр › Топонимы с заглавной
- Handler: `———k` (line 2623); helpers: `chk` (2511), `oa—·` (649–650), `a—k` (2175), `a·` (1855).
- Data: named range `GEO_Toponyms` = `ggg!R1:R36013`, filled from `semtools.guru/dl/spiski/geo.xlsx`
  (`/Users/bolandau/Work/_sandbox/semtools/reverse/downloads/spiski/geo.xlsx`, column A, 36 013 rows, list order matters).
- Input / output: selection, runner C (column 1); result written with `k–k`.
- Algorithm:
  1. If the selection is one cell → exit (no change).
  2. Index: for each toponym `t` in list order, `key = UCase(a—k(t))` (its first space token).
     `idx[key]` = `t`, or `idx[key] & vbTab & t` if the key exists (all toponyms with that first word, list order).
  3. For each cell `s`: `cur = s`. For each token `w` of `Split(s & " ")` (original tokens, in order):
     - if `UCase(w)` not in `idx` → skip;
     - if `UCase(idx[key]) = UCase(w)` (the only toponym with that first word is the word itself):
       `cur = Replace(" " & cur & " ", " " & w & " ", " " & idx[key] & " ", vbTextCompare)` — every
       space-delimited occurrence of the word, any case, becomes the list spelling;
     - else: for each candidate `c` in `Split(idx[key], vbTab)` in list order: if
       `" " & UCase(cur) & " "` contains `" " & UCase(c) & " "` → replace it the same way (case-insensitive, all
       occurrences) with `c` and stop at the first hit.
  4. Cell = `a·(cur)`.
- Quirks:
  - The first candidate in list order wins, not the longest one.
  - Tokens are split by space only; `москва,` is not found.
  - Every row gets `a·` (spaces collapsed) even with no toponym.
  - Single-cell selection exits after `a–` without `—k` (Excel stays in manual calculation until the 30 s timer).
  - If the list is missing, `chk` offers to download all marker lists (`upd`, line 2001).
- ADR 0005 deviation: ё = е when comparing; split on any whitespace.
- Example (with the real list): `квартира нижний новгород` → key `НИЖНИЙ` has candidates `Нижний Суык Су`,
  `Нижний или область`, … `Нижний Новгород` (row 3899) … → `квартира Нижний Новгород`.

### 1.9 Abbreviations
### ИЗМЕНИТЬ › Символы › Регистр › BMW RPG RGB
- Handler: `a––k` (line 1894); helpers: `TransformWordsCase` (1012–1014), `ChangeCase1ColumnRange` (1011).
- Data: named range `abbrs` = `abc!M1:M1016` (1 016 spellings, e.g. `ИНН`, `см`, `СПб`, `USB`, `Xbox`, `кВт`).
- Input / output: runner C (column 1), two passes, each writes `Selection.Value2` directly (ignores "output right").
- Algorithm, pass 1 (`TransformWordsCase`):
  1. Classes: consonants `b c d f g h j k l m n p q r s t v w x z б в г д ж з й к л м н п р с т ф х ц ч ш щ ъ ь`;
     vowels `a e i o u y а е ё и о у ы э ю я`.
  2. Tokens `Split(cell)` (space). For a token of length 2..5 only:
     - `isVowel = class(lower(first char))`; a first char that is in neither class counts as consonant
       (`isVowel = False`, `isCons = True`).
     - For chars 2..n (lower-cased): if the char has a class and the class differs from the first char's
       class → mixed, stop. Chars with no class are ignored.
     - If all-consonant (length ≥ 2) or all-vowel and length ≥ 3 → `UCase(token)`.
  3. `Join(tokens, " ")`.
- Algorithm, pass 2 (`ChangeCase1ColumnRange(abbrs)`):
  1. `map[LCase(v)] = v` for each non-empty list cell (later duplicates overwrite; there are none).
  2. Tokens `Split(cell, " ")`; a token whose `LCase` is in `map` becomes `map[...]`; result `Trim(Join)`.
- Quirks:
  - Pass 1 uses a dictionary read `dict(firstChar)` that inserts unknown first chars (digits, `-`, …) with value
    Empty. Within one run such a char then counts as a consonant when it appears later inside other words. Port:
    treat non-letters as "no class" everywhere except as the first char (consonant). The pollution is a defect.
  - Words with punctuation: `спб,` → `СПБ,` (pass 1), not found in pass 2.
  - Pass 2 can also lower-case: `СМ` → `см`.
- ADR 0005 deviation: split on any whitespace; drop the dictionary-pollution side effect.
- Example: `купить мфу hp в спб 200 см ооо usb` → pass 1 `купить мфу HP в СПБ 200 СМ ООО usb` → pass 2
  `купить мфу HP в СПб 200 см ООО USB`.

### 1.10 List words capitalised / upper
### ИЗМЕНИТЬ › Слова › Изменить регистр › Слова из списка - с заглавной; … - все заглавные
- Handlers: `––kk` (line 2096) and `––ko` (line 1749); helpers: `a–a` (1686), `a—a` (2677), `–1` (442),
  `kooa`/`koo—` (2561/1876), `kooo`/`kook` (1655/2173), `kko` (2860), `—a—` (2675), `oko` (1332), `a·a`, `–o—`, `a–k` (2244).
- Data: the user list (InputBox «Выделите список слов:», a range). It is copied upper-cased to `abc!K1:K…`,
  sorted, named `BSR`, cleared at the end (`a–k`).
- Input / output: runner B over the selection.
- Algorithm per cell (`kko`):
  1. `o = Split(s & " ")`. For each token `tok` (0..UBound-1):
     - normal mode: test `UCase(tok)` ∈ `UCase(list)`;
     - «Игнорировать пунктуацию» on (`abc!AU3`): test `UCase(oko(tok))` ∈ list.
  2. On hit: `––kk` → `tok = a·a(tok)`; `––ko` → `tok = UCase(tok)` (the whole original token, punctuation kept).
  3. Cell = `a·(Join(o, " "))`.
- Quirks: in punctuation mode a token with inner punctuation becomes several words (`wi-fi` → `WI FI`) and never
  matches a list entry `wi-fi`. `a·a` capitalises after punctuation: `(москва)` → `(Москва)`.
- ADR 0005 deviation: ё = е when comparing; split on any whitespace.
- Example (list `москва`, `спб`; ––kk): `квартира москва спб` → `квартира Москва Спб`; (––ko) → `квартира МОСКВА СПБ`.

---

## 2. Insert

### 2.1 Insert after / before each word
### ИЗМЕНИТЬ › Слова › Вставить символы › После каждого слова; Перед каждым словом
- Handlers: `———a` (line 2616, after) and `——ak` (line 1717, before); helpers: `k·ka` (2625) / `a·ka` (1324),
  `——k` (2379), `l·1` (2267: `w & x`), `l·l` (2930: `x & w`).
- Input / output: InputBox «Символы для вставки:» (text `x`); runner A over the selection.
- Algorithm: if `a·(s) = ""` → unchanged. Else `t = a·(s)`; tokens `Split(t & " ")`; each token `w` →
  `w & x` (after) or `x & w` (before); result `a·(Join)`.
- Quirks: spaces are normalised; if `x` ends/starts with spaces they are trimmed at the cell edges by `a·`.
- ADR 0005 deviation: split on any whitespace.
- Example: `купить  диван` + `+` before → `+купить +диван`; `,` after → `купить, диван,`.

### 2.2 Insert at cell end / start / both
### ИЗМЕНИТЬ › Ячейки › Вставить › В конце; В начале; В конце и в начале (одно и то же)
- Handlers: `–o—a` (line 2340), `–o—·` (2867), `———·` (2722); helpers: form `frmInsertText` (one textbox,
  `Me.tag = tbxInput.value`), `insA` (2341), `insB` (837), `insBA` (838).
- Input / output: text `x` from the form (empty → exit); runner A.
- Algorithm: `s & x` (end), `x & s` (start), `x & s & x` (both). No trimming.
- Quirks: empty cells get the text too (`""` → `x`).
- ADR 0005 deviation: none.

### 2.3 Insert different text at start and end
### ИЗМЕНИТЬ › Ячейки › Вставить › В конце и в начале (разные значения)
- Handler: `SEM_AddBnA` (line 329); helpers: `bNa` (340).
- Input / output: InputBox «Дописать в начало:» (`b`), «Приписать в конце:» (`a`); runner B.
- Algorithm: `b & s & a`.
- Quirks: `b`/`a` are `String` variables compared with `False` to detect Cancel; an empty answer probably raises
  a VBA type-mismatch error (not verified). Empty cells get `b & a`.
- ADR 0005 deviation: none.

---

## 3. Move words and word order

### 3.1 Move list words to start
### ИЗМЕНИТЬ › Слова › Переместить › В начало строки
- Handler: `—aao` (line 1879); helpers: `moveToBeg` (1587), `a·`.
- Input / output: InputBox «Переместить слова в начало строки:» (range; column 1 is the list); runner B.
- Algorithm `moveToBeg(s, list)`:
  1. `arr = Split(" " & s)` → `arr[0] = ""`, words in `arr[1..]`.
  2. For each list item `L` in list order: find the first `i ≥ 1` with `LCase(L) = LCase(arr[i])`; if found:
     `arr[0] = arr[0] & " " & L` (the **list** spelling), `arr[i] = ""`.
  3. Return `a·(Join(arr, " "))`.
- Quirks: moved words come in list order and list spelling; only the first occurrence of each list item moves;
  a repeated list item moves the next occurrence. A blank list cell matches a blank token (harmless).
- ADR 0005 deviation: ё = е when comparing; split on any whitespace.
- Example (list `купить`, `угловой`): `диван угловой купить` → `купить угловой диван`;
  (list `Купить`): `диван купить` → `Купить диван`.

### 3.2 Move list words to end
### ИЗМЕНИТЬ › Слова › Переместить › В конец строки
- Handler: `—aa–` (line 2784); helpers: `moveToEnd` (1588).
- Input / output: InputBox «Переместить в конец:» (range); runner B.
- Algorithm: `arr = Split(s & " ")`; `x = UBound(arr)` (the extra empty slot). For each list item in list order:
  first `i < x` with equal `LCase` → `arr[x] = arr[x] & " " & L`, `arr[i] = ""`. Return `a·(Join(arr, " "))`.
- Quirks: as 3.1.
- ADR 0005 deviation: as 3.1.
- Example (list `купить`): `купить диван москва` → `диван москва купить`.

### 3.3 Word order: definitions (charsPat)
### Web › Изменить › Слова › Поправить порядок слов › определения › Мужской род объекта; Женский, именительный; Женский, винительный; Множественное
- Handlers: `characsPat` (line 1880), `characsFem` (1881–1882), `characsFem2` (1883–1884), `characsPlur` (1885–1886);
  helpers: `moveToBeg` (1587); declension: `ka·a` (2681), `o–kk` (2135), `о·—·` (1787) → `ka("l­", word, k)` (2669),
  `l­` (2470), `root` (2161), `———` (1849), `oa` (2208).
- Data: `charsPat` = `abc!BA1:BA644` (644 words in priority order: `где можно купить заказать выбрать недорогой
  дешевый дорогой … детский подростковый мужской женский молодежный`); `adjSuffixes` = `abc!AD2:AS90`
  (col 1 = last 3 letters of the base form; 16 form columns, header in row 1:
  `и р д в т п ми мр мд мв мт мп и-ж рдтп-ж в-ж и-ср`); `adjExclusions` = `abc!AD93:AD136`,
  `adjExclusions2` = `abc!AD93:AS136`.
- Input / output: runner B over the selection.
- Algorithm:
  1. Build the list: `characsPat` uses `charsPat` as is (masculine nominative). The others decline every list word:
     Fem → column 13 (`и-ж`), Fem2 → column 15 (`в-ж`), Plur → column 7 (`ми`). For each space token `w` of the
     list cell, `l­(w, k)`: if `LCase(w)` is in `adjExclusions` → `oa(LCase(w), adjExclusions2, k)`; else
     `Left(w, Len(w)-3) & oa(LCase(Right(w,3)), adjSuffixes, k)` (`oa` returns the 3 letters unchanged when not
     in the table, so non-adjectives such as `купить` stay).
  2. Each cell → `moveToBeg(cell, declinedList)` (3.1).
- Quirks: the VBA writes the declined list into `abc!BA` and restores it afterwards (Excel only).
- ADR 0005 deviation: as 3.1.
- Example (characsPat): `диван раскладной кожаный` → list order puts `кожаный` (row 304) before `раскладной`
  (row 414) → `кожаный раскладной диван`. (characsFem): `недорогой` → `недорогая` is in the list, so
  `кровать недорогая` → `недорогая кровать`.

### 3.4 Word order: definitions + complements (BK*)
### Web › Изменить › Слова › Поправить порядок слов › определения+дополнения › Мужской род объекта; Женский, именительный; Женский, винительный; Множественное
- Handlers: `betterKeysPat` (line 1433) → `BKP` (1429); `betterKeysFem` (1434) → `BKF` (1430);
  `betterKeysFem2` (1435) → `BKF2` (1431); `betterKeysPlur` (1436) → `BKM` (1432); runner `strStrRng` (443).
  Helpers: `AdjToBeg` (1438), `··o` (1439, is adjective), `k—·—` (2905) → `aoo("··–", w, True)` (1772),
  `··–` (2207, is noun), `aaa` (1354, lemma), `moveToBeg`, declension of 3.3.
- Data: lemma dictionary `lemms.xlsb` (`lemmdict!slovarlyemm`: wordform, lemma, POS; port:
  `/Users/bolandau/Work/_sandbox/semtools/reverse/data/lemms.tsv`), `charsPat` (declined as in 3.3:
  Pat none, Fem col 13, Fem2 col 15, Plur col 7), `adjSuffixes`, `nounsLikeAdj` = `abc!J1:J417`, `lemmSuf`.
- Input / output: requires `lemms.xlsb` open (else offers download, `o–·—` 2196). InputBox «Главное слово»
  (`entity`). Runner B.
- Algorithm `BKx(s)` (identical bodies, only the `AdjToBeg` letter differs):
  1. `P = {для с без в из на к со о во у по под от после за над}` (exact, case-sensitive).
     `w = Split(s, " ")`; `r = ""` (main words), `ex = ""` (complements).
  2. `i = 0`; while `i ≤ last`:
     - if `w[i]` ∉ P → `r += w[i] + " "`; `i += 1`; continue.
     - else scan `j = i+1 .. min(i+5, last)`: stop before `w[j]` if `w[j]` ∈ P or `w[j] = ""`; for each scanned
       `w[j]`, if it is a noun → `v = j` (the last noun wins).
     - if no noun: `r += w[i] + " "` (the preposition stays); `i += 1`.
     - else: `ex += Join(w[i..v], " ") + " "`; `i = v + 1`.
  3. `r = moveToBeg(Trim(AdjToBeg(Trim(r), f)), charsPatDeclined)` with `f` = 1 (BKP), 2 (BKF), 3 (BKF2), 4 (BKM).
  4. Return `Trim(r) & " " & Trim(ex)`.
- `AdjToBeg(x, f)`: letter `j = Mid("йяюе", f, 1)`. Tokens of `Split(x, " ")` that are adjectives (`··o`) and end
  with `j` go to the front (their order kept), the rest follow (order kept); `Trim`.
- Is noun `··–(w)`: `oko(w)` split into sub-tokens; true if any sub-token's `LCase` has POS `n` in the dictionary.
- Is adjective `··o(w)`: POS of `w` (dictionary column 3, as typed) = `a` → True; POS in
  `n v advb p prep conj nv` → False; else: `lemma = aaa(LCase(w))` (dictionary lemma, or fallback
  `Left(w, Len-4) & oa(Right(w,4), lemmSuf, 2)`); True if `Right(lemma,3)` is in `adjSuffixes` and `lemma` is not in
  `nounsLikeAdj`.
- Quirks:
  - `e` (the entity) is reset to `""` at the start of `BKx`, so the user's «Главное слово» is ignored; the
    `w(j) = e` test only stops at empty tokens.
  - The result ends with a space when there are no complements (`Trim(r) & " " & ""`).
  - The `–` range argument is overwritten with `charsPat`.
- ADR 0005 deviation: defect — no trailing space; decide with the Human whether `entity` should stop the scan
  (it is unused in VBA). Split on any whitespace. Phase: later (needs morph POS).
- Example (BKP; dictionary POS: `гостиной` n, `раскладной` a, `кожаный` a, `диван` n):
  `диван для гостиной раскладной кожаный` → step 2: `для` scans `гостиной` (noun, v) `раскладной` `кожаный` →
  `ex = "для гостиной"`, `r = "диван раскладной кожаный"` → `AdjToBeg` (`й`) → `раскладной кожаный диван` →
  `moveToBeg(charsPat)` → `кожаный раскладной диван` → `кожаный раскладной диван для гостиной`.

---

## 4. Replace

### 4.1 Word → word
### ИЗМЕНИТЬ › Слова › Заменить › Слово на слово (also Заменить › Целые слова и фразы › Слово на слово)
- Handler: `a–ko` (line 2228); helpers: `ok··` (2289).
- Input / output: InputBox «Заменяемое слово:» (`f`), «Заменить на:» (`t`); runner B.
- Algorithm: tokens `Split(s & " ", " ")`; each token with `UCase(tok) = UCase(f)` becomes `t` (as typed);
  result `a·(Join)`.
- Quirks: a multi-word `f` never matches; punctuation is part of the token (`диван,` ≠ `диван`); an empty `t`
  probably raises a type-mismatch error (String vs False check, not verified), so a word cannot be deleted.
- ADR 0005 deviation: ё = е when comparing; split on any whitespace; empty `t` deletes the word.
- Example (`диван` → `софа`): `Диван угловой диван,` → `софа угловой диван,`.

### 4.2 List → list (apply target case)
### ИЗМЕНИТЬ › Слова › Заменить › Список на список; Заменить › Целые слова и фразы › Список на список (применить конечный регистр)
- Handler: `a–k–` (line 1760); helpers: `ReplacePhrases` (3471–3483).
- Input / output: InputBox «Выделите 2 столбца» (range: col 1 find, col 2 replace). Selection: column 1 only,
  `Selection.Value2` written directly.
- Algorithm:
  1. `n(cell) = UBound(Split(cell, " ")) + 1` (space tokens, empties included). `maxN` = max over list col 1.
  2. `dict[n][LCase(find)] = replace`; the first occurrence of a find wins.
  3. For each phrase: for `i = maxN .. 1`:
     - `cur` = current phrase; skip if it has fewer than `i` tokens;
     - `tokens = Split(cur, " ")` (fixed for this `i`); for `j = 0 .. len-i`: `ng = Join(tokens[j..j+i-1], " ")`;
       if `LCase(ng)` ∈ `dict[i]`: `cur = Replace(" " & cur & " ", " " & ng & " ", " " & dict[i][...] & " ")`
       (binary, all occurrences of that exact spelling);
     - phrase = `Trim(cur)`.
- Quirks:
  - Longer phrases first; within one length left to right on the tokens taken before any replacement of that
    length (a window that was already changed is a no-op).
  - The replacement is inserted as typed (no case adjustment).
  - A blank cell in list column 1 gives `n = 0` → "subscript out of range" → the handler's `On Error Resume Next`
    swallows it and **nothing** is replaced. A one-cell selection also does nothing (`Value2` is a scalar).
  - Double spaces inside the phrase are kept (only `Trim`).
- ADR 0005 deviation: defects — skip blank list rows; single string works. ё = е; split on any whitespace.
- Example (list `стиральная машинка`→`стиральная машина`, `машинка`→`машина`):
  `Стиральная машинка купить` → `стиральная машина купить`.

### 4.3 List → list (keep source case)
### ИЗМЕНИТЬ › Заменить › Целые слова и фразы › Список на список (сохранить исходный регистр)
- Handler: `a–k–2` (line 1761); helpers: `ReplacePhrasesCS` (3484–3496), `CheckCase` (3390), `AdjustCase` (3391).
- Input / output: as 4.2.
- Algorithm: as 4.2, but the inserted text is `AdjustCase(replace, CheckCase(ng))`: the class of the first word
  of the matched n-gram — lower → `LCase(replace)`; Proper → first char of `replace` upper-cased, rest as typed;
  UPPER → `UCase(replace)`; mixed → as typed.
- Quirks: as 4.2. A digits-only first word counts as lower (`12 стульев` → replacement lower-cased).
- ADR 0005 deviation: as 4.2.
- Example (same list): `Стиральная машинка купить` → `Стиральная машина купить`;
  `СТИРАЛЬНАЯ МАШИНКА` → `СТИРАЛЬНАЯ МАШИНА`.

### 4.4 Mass replace by substring
### ИЗМЕНИТЬ › Заменить › Массовая замена по вхождению
- Handler: `ao·a` (line 2693); helpers: `k—o` (2870).
- Input / output: InputBox «Выделите 2 столбца» (range); runner B.
- Algorithm: `res = s`; for each list row in order: if `UCase(res)` contains `UCase(find)` →
  `res = Replace(res, find, repl, 1, -1, vbTextCompare)` (all occurrences, case-insensitive). Rows chain: a later
  row works on the output of earlier rows.
- Quirks: the replacement is inserted as typed (the matched case is lost); an empty `find` changes nothing.
- ADR 0005 deviation: none.
- Example (rows `ё`→`е`, `стол`→`стул`): `Столик Ёлка` → `стулик елка`.

### 4.5 Mass replace of whole cells
### ИЗМЕНИТЬ › Заменить › Массовая замена целых ячеек
- Handler: `ao·k` (line 2483) → `ko–— False, rng, "replace", ·Oo` (1016–1087); helpers: `·–—` (1350), `·ao` (2423), `oko`.
- Input / output: InputBox «Выделите 2 столбца» (exactly 2 columns, else MsgBox); runner C (column 1).
- Algorithm:
  1. Map: key = `UCase(find)` (with «Игнорировать пунктуацию»: `oko(UCase(find))`); first occurrence wins.
  2. For each cell `s`: `cls = ·–—(s)` (`UP` / `Pr` / `lc`); key of `s` built the same way; if in the map:
     cell = `·ao(repl, cls)`.
- Quirks:
  - The replacement is re-cased by the **source** cell class: `lc` → all lower, `Pr` → `a·a`, `UP` → all upper.
    Digits-only or empty source counts as `UP`.
  - A blank row in the list maps the empty key: blank cells get that row's replacement (upper-cased).
- ADR 0005 deviation: none (keep the re-casing; it is the VBA behaviour). Ask the Human if «empty cells never
  match» should apply here.
- Example (row `москва` → `санкт-петербург`): `Москва` → `Санкт-Петербург`; `МОСКВА` → `САНКТ-ПЕТЕРБУРГ`;
  `москва` → `санкт-петербург`.

### 4.6 RegEx replace (first / all)
### ИЗМЕНИТЬ › Заменить › По RegEx › Первое вхождение; Все вхождения
- Handlers: `ao·–` (line 2287, first) → `оk–a` (2582) = `RegExReplace(s, pat, rep, Global:=False)`;
  `—··—` (line 2278, all) → `RegExReplace(s, pat, rep)` (2080).
- Input / output: InputBox «Что заменить» / «Паттерн» (`pat`), «Заменить на:» (`rep`); runner B.
- Algorithm: VBScript RegExp, case-sensitive, not multiline. Empty cell or empty pattern → unchanged.
- Quirks:
  - Invalid pattern → cell unchanged (error swallowed).
  - The formula guard checks `UCase(Left(result, 3)) = "=+-"`, i.e. the literal prefix `=+-`, not "starts with
    one of `=`, `+`, `-`". Results like `=x` still become formulas in Excel.
  - `$1`, `$&` are the back-reference syntax; translate to Python `\1`, `\g<0>`.
- ADR 0005 deviation: drop the `'` guard (no Excel); translate the replacement syntax.
- Example (`(\d+)\s*мм` → `$1 мм`, all): `труба 20мм и 32  мм` → `труба 20 мм и 32 мм`.

---

## 5. Split, reverse, sort

### 5.1 Split text from digits
### ИЗМЕНИТЬ › Слова › Отделить текст от цифр
- Handler: `a—–1` (line 2853); helpers: `a1a` (1690) → `RegExExtract(s, "(\d+|[^\d]+)", True, sep)` (2970).
- Input / output: InputBox «Введите разделитель:» (`sep`); runner B.
- Algorithm: all matches of `(\d+|[^\d]+)` (runs of ASCII digits and runs of everything else, spaces included)
  joined by `sep`.
- Quirks: spaces stay inside the non-digit runs, so `iphone 13 pro` with `sep = " "` → `iphone  13  pro` (double
  spaces, not trimmed). Empty cell → `""`.
- ADR 0005 deviation: no double spaces in results — apply `a·`-like normalisation when `sep` is a space (confirm).
- Example (`sep = " "`): `iphone13pro` → `iphone 13 pro`; (`sep = "|"`): `a1b22` → `a|1|b|22`.

### 5.2 Reverse characters
### ИЗМЕНИТЬ › Ячейки › Развернуть › Символы
- Handler: `a·1—` (line 2604); helpers: `·1a` (2741) = `StrReverse`.
- Input / output: runner A. Algorithm: reverse UTF-16 code units. Quirks: surrogate pairs (emoji) break.
- ADR 0005 deviation: none (Python reverses code points).
- Example: `абв 12` → `21 вба`.

### 5.3 Reverse word order
### ИЗМЕНИТЬ › Ячейки › Развернуть › Порядок слов
- Handler: `—ka·` (line 2292); helpers: `ka––` (1819).
- Input / output: runner A. Algorithm: `Split(s, " ")`, reverse the array, `Join(" ")`. No trimming; empty tokens
  (double spaces) are reversed too.
- ADR 0005 deviation: split on any whitespace, single spaces in the result.
- Example: `купить диван москва` → `москва диван купить`.

### 5.4 Sort words inside a cell
### ИЗМЕНИТЬ › Ячейки › Сортировать А-Я внутри
- Handler: `a–ao` (line 2820); helpers: `srt` (2951), quicksort `kkka` (1015).
- Input / output: runner A.
- Algorithm: if `s` is empty or has no space → unchanged. Else `Split(s)` (space), sort ascending with binary
  string comparison (UTF-16 code-unit order), `a·(Join)`.
- Quirks:
  - The tooltip says "sorts characters", the code sorts words.
  - Binary order: digits < `A–Z` < `a–z` < `Ё` (U+0401) < `А–Я` < `а–я` < `ё` (U+0451). So `ёлка` sorts after `яблоко`,
    `Яблоко` before `арбуз`.
  - Empty tokens sort first and are then removed by `a·`.
- ADR 0005 deviation: split on any whitespace. Keep binary order (Python `sorted` on `str` gives the same order for
  BMP text).
- Example: `стол Белый 2 ёлка арбуз` → `2 Белый арбуз стол ёлка`.

---

## 6. Characters: quotes, translit, layout, look-alikes

### 6.1 Quotes → «ёлочки»
### ИЗМЕНИТЬ › Символы › Кавычки->Ёлочки
- Handler: `a·oa` (line 2008); helpers: `a·k—` (2057).
- Input / output: runner A.
- Algorithm: if `s` has no `"` → unchanged. Else `arr = Split(" " & s & " ", """")`; for `i = 0 .. UBound-1`:
  append `arr[i]` then `«` if `i` is even else `»`; result `Trim`.
- Quirks: **the text after the last `"` is dropped** (`arr[UBound]` is never appended). With an odd number of
  quotes the last opening `«` is followed by nothing.
- ADR 0005 deviation: defect — append the tail `arr[UBound]`.
- Examples: `"Честер"` → `«Честер»`; `диван "Честер" купить` → `диван «Честер»` (VBA; fixed: `диван «Честер» купить`).

### 6.2 Translit ru → en
### ИЗМЕНИТЬ › Символы › Замена en-ru-en › Транслит › Фыва -> Fyva
- Handler: `aa·o` (line 2144); helpers: `ooa—` (2275).
- Input / output: runner A.
- Algorithm: for the 33 letters in order `абвгдеёжзийклмнопрстуфхцчшщъыьэюя`, replace the lowercase letter with its
  Latin string, then the uppercase letter with `StrConv(latin, vbProperCase)` (first letter upper):

  | а | б | в | г | д | е | ё | ж | з | и | й | к | л | м | н | о | п | р | с | т | у | ф | х | ц | ч | ш | щ | ъ | ы | ь | э | ю | я |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | a | b | v | g | d | e | e | zh | z | i | y | k | l | m | n | o | p | r | s | t | u | f | kh | ts | ch | sh | sch | y | y | (empty) | e | yu | ya |

- Quirks: upper-case words become mixed: `ЖУК` → `ZhUK`, `ЩИ` → `SchI`. `ъ` → `y`.
- ADR 0005 deviation: none.
- Example: `Щука жёлтая` → `Schuka zheltaya`.

### 6.3 Translit en → ru
### ИЗМЕНИТЬ › Символы › Замена en-ru-en › Транслит › Fyva -> Фыва
- Handler: `a·—·` (line 2368); helpers: `o·a—` (1351).
- Input / output: runner A.
- Algorithm: sequential case-sensitive `Replace` over these 79 pairs, in this order:
  `Sch→Щ sch→щ ''→ъ Kh→Х kh→х Ch→Ч ch→ч yu→ю ya→я yo→ё iy→ий oy→ой ey→ей Ya→Я Ja→Я Zh→Ж zh→ж Yo→Ё Yu→Ю Sh→Ш sh→ш
  Y→Ы y→ы Zh→Ж zh→ж 'e→э '→ь A→А a→а B→Б b→б C→Ц c→ц D→Д d→д E→Е e→е F→Ф f→ф G→Г g→г H→Х h→х I→И i→и j→дж J→Дж
  K→К k→к L→Л l→л M→М m→м N→Н n→н O→О o→о P→П p→п Q→К q→к R→Р r→р S→С s→с T→Т t→т U→У u→у V→В v→в w→в W→В x→кс
  X→Кс y→ы Y→Ы Z→З z→з`.
- Quirks: the guard `InStr(1, s, l)` uses an undeclared `l` (= ""), so it is always true — harmless. Not the inverse
  of 6.2 (`Shch` → `Шч`, `ts` → `тс`, `ye` → `ые`).
- ADR 0005 deviation: none.
- Examples: `Fyva` → `Фыва`; `Yandex` → `Яндекс`; `Jeep` → `Джееп`; `ob'em` → `обэм`.

### 6.4 Phonetic en → ru («Dreamline → Дримлайн»)
### ИЗМЕНИТЬ › Символы › Замена en-ru-en › Транслит › Dreamline -> Дримлайн
- Handler: `SEM_rT` (line 2426); helpers: `revtranslit` (3392), `revTrans` (174–176), `InitDicts` (52–61),
  `FillDict` (2981), `rByDict` (2980), `CheckCase`, `AdjustCase`.
- Data: string literals inside `InitDicts` (lines 52–61), parsed by `FillDict`: `Split` both strings on single
  spaces and zip by position; `dict[key] = value` (a repeated key keeps its first position, last value wins).

  | Dict | Literals | Pairs | Use |
  |---|---|---|---|
  | `fDict` | `fEn` / `fRu` | 65 | whole-word exceptions (`xiaomi`→`сяоми`, `nvidia`→`нвидиа`, `ipod`→`айпод`) |
  | `s5 s4 s3 s2` | `sEn5..sEn2` / `sRu5..sRu2` | 44 / 84 / 125 / 32 | suffixes of exactly n letters |
  | `p5 p4 p3 p2` | `pEn5..pEn2` / `pRu5..pRu2` | 14 / 43 / 46 / 26 | prefixes of exactly n letters |
  | `a5 a4 a3 a2 a1` | `aEn5..aEn1` / `aRu5..aRu1` | 81 / 58 / 37 / 20 / 26 | substrings anywhere (a5 keys are 5–9 letters) |

  Extract them in Python from the file with `re.findall(r'(\w+) = "([^"]*)"', text_of_lines_52_61)`.
  `a1`: `a→а b→б c→к d→д e→е f→ф g→г h→х i→и j→дж k→к l→л m→м n→н o→о p→п q→к r→р s→с t→т u→у v→в w→в x→кс y→и z→з`.
- Input / output: runner A.
- Algorithm `revtranslit(s)`: tokens `Split(s & " ")`; each token → `AdjustCase(revTrans(LCase(tok)), CheckCase(tok))`;
  `Trim(Join)`.
- Algorithm `revTrans(x)` (`x` lower-case, `word` = original `x`, flags `sTo = pTo = True`):
  1. If `x` ∈ `fDict` → return `fDict[x]`.
  2. For `n = 5, 4, 3, 2`:
     - if `Len(word) ≥ n`: if `sTo` and `Right(x, n)` ∈ `s_n` → replace that suffix, `sTo = False`; then if `pTo`
       and `Left(x, n)` ∈ `p_n` → replace that prefix, `pTo = False`. (At most one suffix and one prefix overall,
       the longest that matches first.)
     - `x = rByDict(x, a_n)`: for each key in insertion order, `Replace(x, key, value, vbTextCompare)` (all
       occurrences).
  3. `x = rByDict(x, a1)`; return `x`.
  `Len(word)` is the original length; `Right`/`Left` look at the partly converted `x`.
- Quirks: dead keys that never match a fixed-length lookup: `special`, `tblanc` (s5), `aughey` (s4), `e` (s2),
  `action` (p5), `wildе` (p5, contains a Cyrillic `е`). `sRu2` maps `e` → `\` (dead) and `ne` → Latin `n` (later
  turned into `н` by `a1`). Some Russian values contain a Latin `c` (`черc`, `сиc`, `джиc`, `ивc`, `ейсиc`).
  `p4` has `chri` twice. Case: Proper token → first letter upper; ALL CAPS → all upper; mixed (`DreamLine`) → lower.
- ADR 0005 deviation: none (phase later). Replace the Latin `c` in values with Cyrillic `с` (defect).
- Examples (traced with the tables): `Dreamline` → `Дримлайн`; `iphone` → `айфон`; `apple` → `эпл`;
  `google` → `гугл`; `galaxy` → `галакси`; `XIAOMI` → `СЯОМИ`.

### 6.5 ЧПУ transliteration
### Web › Изменить › Символы - транслитерация в ЧПУ
- Handler: `––oa` (line 2749).
- Data: `chpuSym` = `abc!E10000:F10965` (966 rows: char → replacement; space → `-`; Cyrillic upper and lower as in
  6.2 but `ь`/`Ь` → empty, `ъ`→`y`; accented Latin → base letters, e.g. `á`→`a`, `Æ`→`AE`; ASCII letters map to
  themselves) plus digits `0`–`9`.
- Input / output: runner C (column 1); no license check.
- Algorithm: for each char of the cell: if it is a key → append its value; else drop it.
- Quirks: no lower-casing (`Купить` → `Kupit`); `-`, `_`, `.` and all other punctuation are dropped; each space
  becomes `-` (double spaces → `--`, leading/trailing spaces → leading/trailing `-`). Keys `cb`, `cp`, `II`, `IL` are
  2-char and never match.
- ADR 0005 deviation: none (keep as VBA). Possibly ask the Human about keeping `-`.
- Example: `Диван-кровать 2 м!` → `Divankrovat-2-m`; `Щётка  ёж` → `Schetka--ezh`.

### 6.6 Keyboard layout switch
### ИЗМЕНИТЬ › Символы › Замена en-ru-en › Сменить раскладку › Asdf -> Фыва; Фыва -> Asdf
- Handlers: `—··k` (line 2837, en→ru) → `okok` (1615); `sem_revr` (line 2838, ru→en) → `revraskl` (1616).
- Data: `arr1 = "f,dult`;pbqrkvyjghcnea[wxio]sm'.·o"`, `arr2 = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"`; only chars 1–33 are used.
- Input / output: runner A.
- Algorithm (en→ru): for `i = 1..33`: `Replace(s, arr1[i], arr2[i])`, then `Replace(s, UCase(arr1[i]), UCase(arr2[i]))`.
  ru→en is the same with the arrays swapped.
- Quirks:
  - The 33rd key char is `·` (U+00B7), not `z`: `z` is never converted to `я`, and `я` becomes `·`. The string is
    corrupted in the shipped add-in (the P-code has the same literal).
  - Shifted symbols are not handled (`<`→`Б`, `>`→`Ю`, `{`→`Х`, `}`→`Ъ`, `:`→`Ж`, `"`→`Э`, `~`→`Ё`).
  - Punctuation is always converted: `,`→`б`, `.`→`ю`, `;`→`ж`, `'`→`э`, `[`→`х`, `]`→`ъ`, `` ` ``→`ё`.
  - ru→en: upper-case `Б Ю Ж Э Х Ъ Ё` become `, . ; ' [ ] ``.
- ADR 0005 deviation: defect — map `z`↔`я`.
- Examples: `ghbdtn` → `привет`; `Ghbdtn, vbh` → `Приветб мир`; `zyltrc` → `zндекс` (fixed: `яндекс`); ru→en
  `привет` → `ghbdtn`.

### 6.7 Similar characters cyr ↔ lat
### ИЗМЕНИТЬ › Символы › Замена en-ru-en › Заменить похожие › Ru -> En; En -> Ru
- Handlers: `ao··` (line 2945) → `ok·a` (1896, Cyrillic → Latin); `ao·o` (line 1660) → `ok·—` (2146, Latin → Cyrillic).
- Data (19 pairs, Cyrillic ↔ Latin): `а a`, `А A`, `В B`, `е e`, `Е E`, `Н H`, `к k`, `К K`, `М M`, `о o`, `О O`,
  `р p`, `Р P`, `с c`, `С C`, `Т T`, `у y`, `х x`, `Х X`.
- Input / output: runner A.
- Algorithm: replace every char of the source set with its pair (case-sensitive), in the order above.
- Quirks: lowercase `в н м т` and uppercase `У` are not in the table; words become mixed-script.
- ADR 0005 deviation: none.
- Examples: Ru→En `Москва` → `Mockвa`; En→Ru `CTO` → `СТО`.

---

## 7. Match types (Yandex / Google operators)

Shared notes: stopword set = `stopwords()` (0.5). `k–` (runner B) is used unless stated.

### 7.1 Broad: A в Б (strip operators)
### Web › Изменить › Типы соотв-я › Широкое › A в Б
- Handler: `a—·1` (line 1610) → `k– "a·k"`; helpers: `a·k` (1325).
- Algorithm: delete every `+`, `!`, `[`, `]`, `"` anywhere in the cell.
- Quirks: minus-words are kept; `c++` → `c`; no space normalisation.
- ADR 0005 deviation: none.
- Example: `"[!купить +в москве]" -бесплатно` → `купить в москве -бесплатно`.

### 7.2 Plus on every word: +A +в +Б
### Web › Изменить › Типы соотв-я › Широкое › +A +в +Б
- Handler: `—·a·` (line 1891) → `k– "·—1"`; helpers: `·—1` (2658) = `a·ka(s, "+")` (2.1).
- Algorithm: as 2.1 "before each word" with `x = "+"`.
- Quirks: minus-words get a plus too (`-бесплатно` → `+-бесплатно`); existing modifiers are not checked
  (`!купить` → `+!купить`).
- ADR 0005 deviation: split on any whitespace.
- Example: `купить диван в москве` → `+купить +диван +в +москве`.

### 7.3 Plus on every word except stopwords: +A в +Б
### Web › Изменить › Типы соотв-я › Широкое › +A в +Б
- Handler: `—·a—` (line 1935) → `k– "·—1"` (7.2), then `oo·—` (2279, 7.8).
- Algorithm: 7.2 on every cell, then 7.8 on column 1.
- Quirks: columns 2+ keep `+в`; in "output right" mode the second step reads the unchanged source column.
- ADR 0005 deviation: as 7.8.
- Example: `купить диван в москве` → `+купить +диван в +москве`.

### 7.4 Modifier only on stopwords: A +в Б
### Web › Изменить › Типы соотв-я › Широкое › A +в Б
- Handler: `—·aa` (line 1846) → `oa–·` (1009).
- Input / output: InputBox «Введите модификатор (! или +)» (`m`, any text accepted); runner C (column 1).
- Algorithm: tokens `Split(s, " ")`; a token whose `UCase` is in `UCase(stopwords)` → `m & tok`; result
  `a·(Join)`.
- Quirks: `+в` already modified is not a stopword token and stays; `m` is not validated.
- ADR 0005 deviation: split on any whitespace.
- Example (`m = "+"`): `диван в москве для дачи` → `диван +в москве +для дачи`.

### 7.5 !A !в !Б and quoted variants
### Web › Изменить › Типы соотв-я › Широкое › !A !в !Б; Точное › Yandex › ''!А !в !Б''; ''[!А !в !Б]''
- Handlers: `a·11` (line 2747) → `оо··` (1318); `a·—1` (line 1800) → `oo—a` (1320); `a·–1` (line 2707) → `oo–·` (1321).
- Algorithm: `t = Join(Split(a·(s), " "), " !")`; then
  `!A`: `"!" & t`; `"!A"`: `"""!" & t & """"`; `"[!A]"`: `"""[!" & t & "]"""`.
- Quirks: empty cells become `!`, `"!"`, `"[!]"`; minus-words get `!` (`!-бесплатно`); existing modifiers are kept
  (`+в` → `!+в`).
- ADR 0005 deviation: defect — empty string stays empty.
- Example: `купить  диван` → `!купить !диван`; → `"!купить !диван"`; → `"[!купить !диван]"`.

### 7.6 Brackets and quotes around the cell
### Web › Изменить › Типы соотв-я › Фразовое › [A в Б] - Yandex; ''A в Б'' - Google; Точное › Google › [A в Б] - Google; Точное › Yandex › ''А в Б''
- Handlers: `a–·1` (line 2817) → `·1l` (1316): `"[" & s & "]"`; `–a·1` (line 2809) → `oo­` (1315): `"""" & s & """"`.
- Algorithm: wrap the whole cell; empty cell stays empty.
- Quirks: no trimming, minus-words end up inside (`[купить -бесплатно]`).
- ADR 0005 deviation: none.
- Example: `купить диван` → `[купить диван]` / `"купить диван"`.

### 7.7 Anti-semantic: [А] в [Б]
### Web › Изменить › Типы соотв-я › Анти-семантическое (Yandex) › [А] в [Б]
- Handler: `antisem` (line 1010).
- Input / output: runner C (column 1).
- Algorithm: tokens `Split(s, " ")`; each token whose `UCase` is **not** in `UCase(stopwords)` → `"[" & tok & "]"`;
  result `a·(Join)`.
- Quirks: an empty token from a double space becomes `[]`; minus-words get brackets (`[-бесплатно]`).
- ADR 0005 deviation: split on any whitespace (no `[]`).
- Example: `диван в москве` → `[диван] в [москве]`.

### 7.8 Remove modifiers from stopwords
### Web › Изменить › Типы соотв-я › Удалить модификаторы у стоп-слов
- Handler: `a·ak` (line 2680) → `oo·—` (2279); helpers: `a–l` (1008), `ka—·` (1681).
- Input / output: runner C (column 1).
- Algorithm: set `M = {"+" & w, "!" & w : w ∈ stopwords}` (lowercase, case-sensitive). Tokens
  `Split(a–l(s), " ")`; a token in `M` loses its first char; result `a·(Join(tokens) & ka—·(s))`.
- Quirks:
  - `a–l` was meant to cut the minus-word tail (`" -…"`) and `ka—·` to re-append it, but `Select Case InStr(...)`
    compares the position with `True` (−1), so it never matches: the whole cell is processed and nothing is
    re-appended. Net effect is the same for normal input.
  - Case-sensitive: `+В` (upper) is not stripped.
- ADR 0005 deviation: stopwords case-insensitive.
- Example: `+купить +в !москве +для дачи` → `+купить в !москве для дачи`.

### 7.9 Remove minus-words
### Web › Изменить › Типы соотв-я › Удалить минус-слова
- Handler: `a·ao` (line 1783) → `k– "–k–"`; helpers: `–k–` (2355).
- Algorithm: cut the cell before the first `" -"` (space + hyphen): `LeftB(s, InStrB(s & " -", " -") - 1)`.
- Quirks: a dash surrounded by spaces also cuts (`диван - кровать` → `диван`); a cell that starts with `-word`
  (no space before it) is kept whole; the result is not trimmed (`a  -b` → `a `). Byte-level `InStrB` can in theory
  match across char boundaries (practically never).
- ADR 0005 deviation: none (trim the result).
- Example: `купить диван -бесплатно -скачать` → `купить диван`.

---

## 8. URL and hashes

### 8.1 Remove UTM tags from URL
### Web › Удалить › Из URL › UTM-метки
- Handler: `a·aa` (line 2686) → `k– "—–1"`; helpers: `—–1` (2728), `RegExReplace`, `оk–a`.
- Algorithm:
  1. `s = RegExReplace(s, "(\?|&)utm_[^$#&]+", "")` (global, case-sensitive): drop every `?utm_…` / `&utm_…` up to the
     next `&`, `#` or end.
  2. If `s` has no `?` but has `&` → replace the first `&` with `?`.
- Quirks: `UTM_SOURCE` (upper) is kept; the parameter name only has to start with `utm_`.
- ADR 0005 deviation: none.
- Example: `https://site.ru/?utm_source=ya&utm_medium=cpc&id=5#top` → `https://site.ru/?id=5#top`.

### 8.2 Extract utm_* value
### Web › Извлечь › Из URL › utm_... › source; medium; campaign; term; content
- Handlers: `–aa—` (2139) → `a1·` (2652); `–ao—` (2598) → `—a1` (1861); `–—–·` (1754) → `a·–o` (2522);
  `–a·o` (2399) → `a·—o` (1908); `–—a–` (2313) → `a–1` (2241); all → `extrUTM(s, name)` (2763) via `k–`.
- Algorithm: first match of `utm_<name>=[^$#&]+` (case-sensitive); the whole match is returned; no match → `""`.
- Quirks: the result keeps the `utm_<name>=` prefix; the value is not URL-decoded; the cell is replaced in place
  (the URL is lost unless "output right" is on).
- ADR 0005 deviation: none (ask the Human whether to return the value only).
- Example (source): `https://site.ru/?utm_source=yandex&utm_medium=cpc` → `utm_source=yandex`.

### 8.3 Hashes md5 / SHA-256
### Web › Изменить › Шифровать md5 хешированием; Шифровать SHA-256 хешированием
- Handlers: `md5` (line 1912), `sha256` (1913) → `zHashSel` (1914–1920, runner B) → `zHash` (3259).
- Algorithm: UTF-8 bytes of `CStr(cell)` → .NET `MD5CryptoServiceProvider` / `SHA256Managed` → lower-case hex.
- Quirks: empty cells are hashed (`md5("")` = `d41d8cd98f00b204e9800998ecf8427e`); numbers go through `CStr`
  (locale decimal separator, e.g. `1,5`). Needs .NET 3.5 on Windows (error MsgBox otherwise).
- ADR 0005 deviation: none.
- Examples: `abc` → md5 `900150983cd24fb0d6963f7d28e17f72`, sha256
  `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`.
