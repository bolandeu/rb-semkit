# !SEMTools VBA reference: morphology and analysis

This is the source of truth for porting these buttons. Everything below is traced from these sources:
- `/Users/bolandau/Work/_sandbox/semtools/reverse/vba/RibbonCallbacks.vba`, cited as `L<n>`. One VBA line holds a whole procedure joined by `:`.
- The forms `*.frm` in the same folder.
- The sheet `abc` (`reverse/data/sheet_abc.tsv`).
- The helper workbook `reverse/downloads/SEMToolsWordProcessor.xlsb`, its VBA extracted with `olevba`.
- Named ranges from `xl/workbook.xml` of `!SEMToolsPro.xlam`.

Already traced elsewhere and not repeated here:
- duplicates (`—kka`, `ako—`, `akoa`, `ako·`, SEMKIT-003);
- n-grams and bigrams (`ak—`, `–·ao`, SEMKIT-004);
- the lemma lookup `aaa` and the phrase lemmatizer `kok—`, summarised in §1.4 for reference only.

«As compiled» means the behaviour of the shipped code. Where the source looked wrong, I checked the P-code (`VBA_P-code.txt`): it matches the source.

## Index

| Menu path (ribbon) | Handler | Section |
|---|---|---|
| Web › Слова › Лемматизация › Словарь !SEMTools; Изменить › Слова › Просклонять › Все что склоняется › Лемматизация | `—ak–` | §2 |
| Web › Слова › Лемматизация › Mystem | `mystemLemm` | §2 |
| Обнаружить › Слова › Целые слова › Части речи › Сущ. / Прил. / Глаголы / Наречия | `—k–a`, `–···`, `—k—·`, `—kkk` | §2 |
| Удалить › Слова › Целые слова › Части речи › Сущ. / Прил. / Глаголы / Наречия | `ak··`, `—··a`, `ao——`, `—···` | §2 |
| Извлечь › Слова › Целые слова › Части речи › Сущ. / Прил. / Глаголы / Наречия | `–ao·`, `–—o—`, `–·ka`, `–—oa` | §2 |
| Web › Слова › Генерация всех словоформ | `––aa` | §2 |
| Изменить › Слова › Просклонять › Все что склоняется › 11 forms | `—aa—` … `—aa·` | §3 |
| Изменить › Слова › Просклонять › Существительные › 11 forms | `a–ka` … `—·ao` | §3 |
| Изменить › Слова › Просклонять › Прилагательные › м. / ж. / ср. / мн. (23 buttons) | `a–k·` … `—·a–` | §3 |
| Изменить › Слова › Просклонять › ФИО › 5 forms | `a–ok`, `––ao`, `a··o`, `aa—l`, `—·ak` | §3 |
| Извлечь › Атрибуты › Текста ячеек › Количество слов / символов / Длина в пикселях | `–·oa`, `–a·k`, `–a–·` | §4 |
| Извлечь › Посчитать › Количество повторений / Номер встречаемости / Долю от суммы / накопительным итогом / ABC | `––k—`, `–kko`, `–kok`, `–koo`, `ABCA` | §4 |
| Разбить/Сцепить › Комбинации › Слова › Все перестановки слов | `—·—–` | §5 |
| Разбить/Сцепить › Комбинации › Значения ячеек › Генератор линейных комбинаций | `———o` | §5 |
| Разбить/Сцепить › Комбинации › Значения ячеек › Комбинации по 2 элемента | `a––·` | §5 |
| Web › Извлечь › Из диапазона › Ближайших родителей / Первых родителей / Первые вложенные фразы | `–—·o`, `–—·a`, `–—·k` | §6 |
| Web › Семант.анализ › Найти базисы | `semBasis` | §6 |
| Web › Семант.анализ › Работа с семантическим ядром (good/bad split) | `semWP` + helper workbook | §7 |
| Web › Семант.анализ › Кластеризация › По частотному словарю / По топ-10 выдачи | `––o·`, `SERPClustering` | §8 |
| Web › Семант.анализ › Поиск нерелевантных слов | `—k–o` + `findIrr.frm` | §9 |
| Web › Семант.анализ › Исключение синонимов › Составить список / Добавить в минус-слова | `aa·a`, `aa··` | §9 |
| Web › Семант.анализ › Работа с опечатками › Является ли опечаткой? / Наиболее вероятное исправление | `a–a—`, `a–aa` | §10 |
| (UDF) `Levenstein`, `simScore` | — | §10 |
| Web › Семант.анализ › Анализ тональности › Среднее / Мин. / Макс. | `nGB`, `nGBMin`, `nGBMax` | §11 |
| Извлечь › Фразы › Дополнения с предлогами | `findCollocs` | §12 |
| Web › Удалить › Из текста › Предлоги в конце фраз | `remLWprps` | §12 |
| Обнаружить › Ячейки › Начинающиеся на / Заканчивающиеся на › Предлоги | `findFFWprps`, `findFLWprps` | §12 |

Not covered here, because they belong to other areas:
- word-order fix (`characs*`, `betterKeys*`);
- word repeats by wordforms (`aook`);
- markers and toponym removal, which are only summarised in §9 where the irrelevant-words tool calls them.

---

## 1. Shared helpers and conventions

### 1.1. Run frame (every handler)

| Helper | Lines | What it does |
|---|---|---|
| `·l` | L2753 | If a whole column is selected (1 048 576 rows), shrink the selection to the used part of that column. |
| `k–—` | L2150 | Same, but only for a 1-column selection. |
| `·——` | L2631 | Undo snapshot: copies the selection values to sheet `def`. It is skipped when «Выводить результат справа» is on and one column is selected. Side effect only. |
| `a–` / `—k` | L2667 / L2344 | Turn screen updating, calculation and alerts off / on. |
| `zSel` | L2752 | `Selection.Value2` as a 1-based 2-D array. A single cell is wrapped into a 1×1 array. |
| `k–k arr` | L2933 | Writes the result. If «Выводить результат справа» is on and the selection has 1 column, it inserts a new column to the right and writes there. Otherwise it overwrites the selection. The checkbox is `–aa`, cell `abc!AU4` (Checkbox1). |
| `oao rng, arr` | L2464 | Same as `k–k`, for one area. |
| `k– fn` | L1937 | Generic per-cell mapper: `cell = fn(CStr(cell))` for every cell of every area (a 1-cell area passes `cell.Value2`), then `oao`. |
| `·Oo` | L1952 | «Игнорировать пунктуацию» checkbox (Checkbox2, cell `abc!AU3`). |

Licence gate (ignore in the port): `—–(al(k—()), …)` checks a machine hash. Without a licence:
- `k–` writes «Дoстyпнo в пoлнoй вeрcии !SЕМТооls» (`—aa`, L1701) into a column-1 cell with probability 1/3 (`o–·`, L2657), and into every cell of columns 2 and higher;
- `c_h` (L841) overwrites a random third of the rows.

### 1.2. Text helpers

| Helper | Lines | Exact behaviour |
|---|---|---|
| `a·(s)` | L1855 | `Trim`, then collapse each run of U+0020 spaces into one. |
| `oko(s)` | L1332 | Ignore-punctuation normaliser. It keeps a char if it is a space, a digit `0-9`, or a letter (`UCase(ch) <> LCase(ch)`). Any other char becomes a space, then `a·`. Example: `из-за` → `из за`. |
| `akk(s)` | L2414 | Word count = `UBound(Split(s, " ")) + 1`. `""` gives 0. Every extra space adds a word. |
| `a—k(s)` | L2175 | First word. |
| `eLW(s, n)` | L2432 | Last `n` words, trimmed. The whole string if it has ≤ n words. |
| `·k—(s, n)` | L1644 | First `n` words, prefixed with `'` (the Excel text marker, invisible when it is the first char of a cell). |
| `srt(s)` | L2951 | Sorts the words with quick sort `kkka` (L1015), using binary `<` (code-point order, case-sensitive), then `a·`. |
| `·–—(w)` | L1350 | Case class: `"UP"` if `w = UCase(w)` (also true for digits and empty), `"Pr"` if `w = a·a(w)`, else `"lc"`. |
| `a·a(s)` | L1721 | Proper case: lower-case all, then upper-case the first letter of every run of letters (`'дмитрия` → `'Дмитрия`). |
| `root(w)` / `———(w)` | L2161 / L1849 | `———` = last 3 chars. `root` = `w` minus its last 3 chars. |
| `kok(s, e)` | L2499 | `s` ends with `e`, case-insensitive. |
| `a—o(x, arr)` | L1306 | `x` equals an element of `arr` (binary). |
| `al·(w)` | L2634 | Abbreviation test: `Len(w) < 5` and no lower-case vowel `[аоуиыеёэюя]`. |
| `stopwords()` | L1374–1378 | One string of 440 words separated by spaces (ru + en, includes the junk word `g`). |
| `prps()` | L1322 | 47 items: `а без безо близ в вместо вне во для до за и из из-за из-под изо или к ко кроме меж между на над но g об обо от ото пo перед передо под подо пред предо при про ради с сквозь со среди у через чрез`. Junk: `g`, and `пo` has a latin `o`. |

### 1.3. Table lookups (VLOOKUP emulation)

Both helpers work in two steps:
1. `Application.VLookup(key, range, …, TRUE)`: approximate match on a sorted first column, case-insensitive.
2. A check with VBA `=`, which is binary and **case-sensitive**.

The net effect is an exact, case-sensitive lookup.
- `—–(key, range)` (L2006) returns True when `key` is in column 1.
- `oa(key, range, col)` (L2208) returns column `col` of the matching row. When the key is missing or there is any error, it returns **the key itself**. A found row with an empty cell returns `""`.
- The tables are sorted, except that `ё` is sorted like `е`. Port: use a dict.

### 1.4. Lemma `aaa(word)` (L1354), already traced

The formula is `IF(VLOOKUP(word, lemms!slovarlyemm, 1, TRUE) = word, VLOOKUP(…, 2, TRUE), word)`, run through `Evaluate`, with a memo dict.
- An unknown word is returned as is.
- The suffix table `lemmSuf` (`abc!E50:G305`) is used only when `Evaluate` returns an error: `Left(word, Len-4) & oa(Right(word, 4), lemmSuf, 2)`.
- `get_lemmdict` (L2109) and `openLD` (L2826) make sure `lemms.xlsb` exists (offering a download) and is open.

### 1.5. Part-of-speech predicates (one token)

The POS is column 3 of the lemma dictionary. The values in `lemms.tsv` are `n`, `v`, `a`, `p`, `advb`, `prn`, `prep`, `nv`, `prt`.

| Predicate | Lines | Rule |
|---|---|---|
| noun `··–(w)` | L2207 | `pos(LCase(w)) = "n"`. |
| verb `·ok(w)` | L1344 | `e = Right(LCase(w), 3)`. True if `e` is `тся` or `ься`, or `e = "уют"` and the word is not `уют`, or `e = "ают"`. Otherwise `pos = "v"`. The `ться` case is covered by `ься`. |
| adverb `oa–(w)` | L2154 | `pos(LCase(w)) = "advb"`. |
| adjective `··o(w)` | L1439 | `pt = pos(w)` **without lower-casing**, so a capitalised word is not found and `pt` = the word. `pt = "a"` → true. `pt` in {n, v, advb, p, prep, conj, nv} → false. Otherwise (unknown, `prn`, `prt`, capitalised): `lemma = aaa(LCase(w))`, and the word is an adjective iff `Right(lemma, 3)` is a key of `adjSuffixes` (AD2:AD90) and `lemma` is not in `nounsLikeAdj` (J1:J417, mostly male names in -ий). |

### 1.6. Per-word filters over a phrase

The phrase is `phrase & " "`, split by a single space; the last, empty token is dropped. The predicate is called by name through `Application.Run`. With `strip = True` the predicate gets `oko(token)`, but the original token is what is kept or removed.

| Helper | Lines | Result |
|---|---|---|
| `aoo(pred, phrase, strip)` | L1772 | True if any token satisfies `pred`. |
| `aka(pred, phrase, strip)` | L2731 | Tokens that satisfy `pred` are dropped, then joined and `a·`. |
| `—·o(pred, phrase, strip)` | L2964 | Tokens that do not satisfy `pred` are dropped, then joined and `a·`. |
| `ao–(fnStrip, fnPlain)` | L2650 | Runs `k– fnStrip` if «Игнорировать пунктуацию» is on, else `k– fnPlain`. |

---

## 2. Lemmatization, POS, wordforms

### Web › Слова › Лемматизация › Словарь !SEMTools (also Просклонять › Все что склоняется › Лемматизация)
- **Handler:** `—ak–` (L1960). Helpers: `kok—` (L2835), `aaa`, `get_lemmdict`. Data: `lemms.xlsb!slovarlyemm`, `lemmSuf`.
- **Input / output:** reads column 1 of the selection and writes through `k–k`. Other columns are written back unchanged.
- **Algorithm (already traced):**
  1. For each row, `Split(LCase(cell), " ")`.
  2. Map each unique token through `aaa`, cached per run.
  3. Replace the tokens and join them with a space.
- **Quirks:** dictionary lemmas may keep capitals (`москве` → `Москва`). Double spaces survive. There is no licence noise in this handler.
- **ADR 0005:** lemmas lower case; split by any whitespace.

### Web › Слова › Лемматизация › Mystem
- **Handler:** `mystemLemm` (L1594).
- **What it does:**
  1. A file picker asks for `mystem.exe`.
  2. The selection is written to `tmp.csv` (commas are stripped by `k–kk`, L1597).
  3. It runs `mystem.exe tmp.csv tmp2.csv -c -l`.
  4. It waits a fixed 2 seconds, then imports `tmp2.csv` as UTF-8.
- **Not ported** (ADR 0003).

### Обнаружить › Слова › Целые слова › Части речи › Существительные / Прилагательные / Глаголы / Наречия
- **Handler:** `—k–a` (L2266), `–···` (L2909), `—k—·` (L2494), `—kkk` (L1663). Each runs `get_lemmdict`, then `ao–(<pos>Strip, <pos>Plain)` with these wrappers:
  - noun: `k—·—` / `k—·–`;
  - adjective: `k—·o` / `k—aa`;
  - verb: `k—··` / `k—·a`;
  - adverb: `k—·k` / `k—a·`.
- **Input / output:** every selected cell gets `TRUE`/`FALSE`, in place or to the right.
- **Algorithm:** `aoo(pred, cell, strip = checkbox)`.
- **Quirks:**
  - With the checkbox off, `диван,` is not found, because the punctuation stays on the token.
  - A capitalised word skips the dictionary in the adjective test: `Красный` goes through the suffix rule and is TRUE.
  - The four tests are independent, so one word can be several POS.
- **ADR 0005:** split by any whitespace.

### Удалить › Слова › Целые слова › Части речи › Сущ. / Прил. / Глаголы / Наречия
- **Handler:** `ak··` (L2642), `—··a` (L2697), `ao——` (L1897), `—···` (L2563). Wrappers: `ok–a`/`ok–—`, `ok–k`/`oko—`, `ok·–`/`ok·k`, `oko·`/`okoa`, which call `aka`.
- **Output:** the text without the tokens of that POS, in place or to the right.
- **ADR 0005:** split by any whitespace.

### Извлечь › Слова › Целые слова › Части речи › Сущ. / Прил. / Глаголы / Наречия
- **Handler:** `–ao·` (L2891), `–—o—` (L1948), `–·ka` (L2246), `–—oa` (L2480). They call `—·o("··–" / "··o" / "·ok" / "oa–", cell)` with `strip = False`.
- **Output:** only the tokens of that POS.
- **Quirk:** extraction ignores the «Игнорировать пунктуацию» checkbox.

**Examples:**
- Find noun in `купил красные диваны` → TRUE.
- Remove adjectives → `купил диваны`.
- Extract verbs → `купил`.

### Web › Слова › Генерация всех словоформ
- **Handler:** `––aa` (L380). Helpers: `aaa`, `·la` (L651, unpivot).
- **Input:** the selection. The last selected column holds the word.
- **Output:** a new sheet named `Morphs`, two columns from A2, no header.
- **Algorithm:**
  1. Build `lemma → wordforms` over all dictionary rows, in file order. Rows with POS `ll` are skipped (there are none). Keys are the lemma as stored.
  2. For each row: `key = col1\col2\…\colN`, and `lemma = aaa(LCase(colN))`.
  3. Emit `(key, colN)`, then `(key, form)` for every form of the lemma.
- **Example:** `диван` → `(диван, диван), (диван, диван), (диван, дивана), …`.
- **Quirks:** the input word appears twice; forms listed twice in the dictionary repeat; the macro fails if a sheet named `Morphs` already exists.

---

## 3. Declension

Data on sheet `abc`, using the named ranges from `workbook.xml`:

| Range | Address | Layout |
|---|---|---|
| `nounSuffixes` | Q1:AB3331 | Column 1 = key, the last 3 letters of the nominative (there are also 39 two-letter keys and 1 one-letter key, which only match whole short words). Columns 2–12 = the endings that replace the key: Р Д В Т П, then МН И Р Д В Т П. `ko` = column number (2 = gen sg … 12 = prep pl). 2 285 rows are sparse: only В and МН-В are filled. |
| `nounExclusions` / `nounExclusions2` | Q3380:Q11089 / Q3380:AB11089 | Whole words, with 11 full forms in columns 2–12. |
| `nonDecl` | B1:B1205 | Indeclinable words. |
| `adjSuffixes` | AD2:AS90 | Key = last 3 letters; the gender is encoded in the key (`ный`, `ная`, `ное`). Columns 2–6: Р Д В Т П (sg, in the gender of the key). Columns 7–12: МН И Р Д В Т П. Column 13: `и-ж`. Column 14: `рдтп-ж`. Column 15: `в-ж`. Column 16: `и-ср`. No empty cells. |
| `adjExclusions` / `adjExclusions2` | AD93:AD136 / AD93:AS136 | Whole adjectives and pronouns (`весь`, `мой`, `бычий`…), with 16 forms. |
| `femSurSuf` | AD140:AI163 | **Not used by any button.** Only the dead functions `—–a` (L1582) and `–––` (L1583) read it. |

Default endings by `ko` (the module has `Option Base 1`):

| `ko` | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `o` (after т р н с м д з л б п в ф) | а | у | а | ом | е | ы | ов | ам | "" | ами | ах |
| `arr2` (after г к х) | а | у | а | ом | е | и | ов | ам | "" | ами | ах |
| `arr3` (after ж ш ч щ) | а | у | а | ем | е | и | ей | ам | "" | ами | ах |

### 3.0. Core functions

**Noun, one word: `l–(w, ko)`** (L1518–1520)
1. If `ko` is 4 or 10: when `w` is in `nounExclusions`, return its exclusions row; otherwise return `root(w) & oa(last3, nounSuffixes, ko)`.
2. If `al·(w)` or `w` is in `nonDecl`, return `w`.
3. If `w` is in `nounExclusions`, return its exclusions row.
4. Intended: if the last letter is in `трнсмдзлбпвф` / `гкх` / `жшчщ`, take `s = oa(last3, nounSuffixes, ko)`. When `s = ""`, return `w & o/arr2/arr3(ko)`; otherwise return `root & s`.
5. Otherwise return `root(w) & oa(last3, nounSuffixes, ko)`.

**As compiled, step 4 never runs.** The code is `Select Case True … Case InStr(1, "трн…", Right(w, 1))`, and True (-1) never equals a position ≥ 1. So a consonant-final word goes to step 5:
- key found with an empty cell → `root` only, a truncated word;
- key not found → the word is unchanged.

`aoa` writes the same logic with `If/ElseIf InStr(...) Then`, and that version works.

**Adjective, one word: `l­(w, ko)`** (L2470)
- If `LCase(w)` is in `adjExclusions`, return its `adjExclusions2` row.
- Otherwise return `root(w) & oa(last3(LCase w), adjSuffixes, ko)`. An unknown ending leaves the word unchanged; the original case of the root is kept.

**Phrase: `aoa(phrase, ko)`** (L1521–1581), used by «Все что склоняется»:
1. `W = Split(" " & phrase & " ", " ")`. Loop over the inner tokens `g = 1…n`.
2. For each token `t`: take `cc = ·–—(t)` and `k = LCase(t)`. The first matching branch wins:
   1. `pos = oa(k, dictRange, 3)`; skip if `pos` is `ll` or `advb`, or `k` is in `nonDecl`. **As compiled, `dictRange` is never Set**, so `pos = k` and only the `nonDecl` test works. Verbs, adverbs and prepositions get declined.
   2. Skip if `k` ends with `ой`, the next token is not a lemma (`aaa(next) <> next`), and the next token is a real word.
   3. Skip if `g > 2` (the 3rd word or later) and the lower-cased previous token is in `arrPron`. `arrPron` has 56 entries: `без в во вместо для до за из или их ли после своего моего кроме вследствие своим моим твоим своей моей твоей своими моими твоими твоего своей моей твоей своих моих мой мои мою на над наш о об от по под подо про с со свой свои свою сквозь твою твои твоих твой у через`.
   4. If `l­(k, ko) <> k` and not `al·(k)`, the token becomes `l­(k, ko)` (adjective).
   5. Skip if `aaa(k) <> k`, meaning the word is already an inflected form in the dictionary.
   6. If `ko` is 4 or 10: use the exclusions row, or `root & oa(last3, nounSuffixes, ko)`.
   7. If the last letter is in a consonant group: use the exclusions row; else `s = oa(…)`. When `s = ""`, the result is `k & o/arr2/arr3(ko)`; otherwise `root & s`.
   8. Otherwise: the exclusions row, or `root & oa(…)`.
3. Restore the case from `cc`: `lc` keeps the token as is, `Pr` applies `a·a`, `UP` applies `UCase`. A declined mixed-case token ends up lower case.
4. Return `a·(Join(W, " "))`.

### Изменить › Слова › Просклонять › Все что склоняется › ЕД Род … МН Предл
- **Handler and `ko`:** `—aa—` (L1774, 2), `—a·k` (L2568, 3), `—a·o` (L2295, 4), `—a·–` (L2297, 5), `—a·—` (L2205, 6), `—a·a` (L2579, 7), `—a··` (L2795, 8), `—·kk` (L2876, 9), `—·ko` (L2858, 10), `—aaa` (L2332, 11), `—aa·` (L2673, 12).
- **How it runs:** each handler calls `get_lemmdict`, then `k–` with the wrapper `aoa(cell, ko)` (`ook·` L1622 … `okk·` L2913).
- **Input / output:** every cell, in place or to the right.
- **Quirks:**
  - Verbs and adverbs are declined like nouns.
  - A word after a preposition is protected only from the 3rd word on.
  - Noun forms come only from the 3-letter ending table.
- **ADR 0005:**
  - split by any whitespace;
  - restore the intended POS skip (decline only nouns and adjectives).

**Examples** (traced with the real tables):
- Род `купить красный диван` → `купити красного дивана`.
- МН Род → `купитей красных диванов`.
- Род `чехол для телефон` → `чехла для телефон`.
- Дат `Москва` → `Москве`.

### Изменить › Слова › Просклонять › Существительные › ЕД Род … МН Предл
- **Handler and `ko`:** `a–ka` (L2841, 2), `––—·` (L2824, 3), `a··1` (L1643, 4), `aal—` (L2644, 5), `—·—a` (L2843, 6), `—a—·` (L2219, 7), `a–oo` (L1604, 8), `––a–` (L1693, 9), `a··k` (L2114, 10), `a–al` (L2950, 11), `—·ao` (L2864, 12).
- **How it runs:** the wrapper is `ka("l–", cell, ko)`. `ka` (L2669) maps `l–` over the space-separated tokens, then applies `a·`. There is no `get_lemmdict`, no lemma check, no preposition rule and no `LCase`.
- **Quirks:**
  - **As compiled, consonant-final nouns are truncated or unchanged** for all cases except the accusative.
  - Capitalised words are not found in the tables.
  - Every token is declined, prepositions included.
- **ADR 0005 deviation:** port the intended consonant fallback (step 4).

**Examples (ЕД Род):**
- `диван` → as compiled `ди`; intended `дивана`.
- `парк` → as compiled `п`; intended `парка`.
- `книга` → `книги` in both versions.

### Изменить › Слова › Просклонять › Прилагательные
**Handlers and `ko`:**
- м. род: Род `a–k·` (L1822, 2), Дат `––ak` (L2713, 3), Вин `a··l` (L2730, 4), Твор `aa–l` (L2957, 5), Предл `—·—·` (L2641, 6).
- ж. род: Им `———–` (L2468, 13); Род, Дат, Твор and Предл all call `—··–` (L2311, 14); Вин `a···` (L1744, 15).
- ср. род: Им and Вин both call `————` (L2384, 16). **Род, Дат, Твор and Предл are the noun handlers** `a–ka`, `––—·`, `aal—`, `—·—a`.
- мн. ч.: Им `—aak` (L1671, 7), Род `a–o–` (L1953, 8), Дат `––a—` (L2425, 9), Вин `a·1–` (L2130, 10), Твор `a—al` (L2919, 11), Предл `—·a–` (L2160, 12).
- The wrapper is `ka("l­", cell, ko)`.

**Algorithm:** `l­` per token. A masculine key gives masculine forms; columns 13–16 convert to feminine or neuter.

**Quirks:**
- Neuter oblique cases go through the noun table: `красное` Род comes back unchanged.
- A noun whose last 3 letters equal an adjective key gets changed (`зной`, key `ной`).
- The table has `синий` → и-ср `синое`.

**ADR 0005 deviation:** neuter Род/Дат/Твор/Предл should use the adjective columns 2, 3, 5, 6.

**Example `красный`:** Род `красного`, Твор `красным`, МН Род `красных`, ж. Им `красная`, ж. Род `красной`, ж. Вин `красную`, ср. `красное`.

### Изменить › Слова › Просклонять › ФИО › Род / Дат / Вин / Твор / Предл
- **Handler:** `a–ok` (L2894, ko 2), `––ao` (L1624, 3), **`a··o` (L1642, Вин, which uses ko 3, the dative)**, `aa—l` (L2223, 5), `—·ak` (L2102, 6).
- **Helpers:** `oak` (L1593), `fSurn` (L1586), `mSurn` (L1592), `·a—` (L1584), `––o` (L1585), `о·o·` (L2410), `–·—` (L2375), `l–`.
- **Input / output:** every selected cell, written through `k–k`. The input format is «Фамилия Имя Отчество».
- **`oak(s, ko)`:**
  1. Split `LCase(s)` by a single space. Anything other than exactly 3 tokens returns `!!!Это не ФИО, ФИО это 3 слова`.
  2. The person is female if the whole input ends with `зы` or `на`.
  3. Female: name via `·a—`, surname via `fSurn`. Male: name via `––o`, surname via `mSurn`.
  4. The patronymic goes through `l–`.
  5. The result is `a·a(sur & " " & name & " " & patr)`.
- **`fSurn(x, p)`:** the first matching ending, in this order, is replaced by element p-1 of its list (a 0-based split):
  - `ая` → `ая ой ой ую ой ой`
  - `ина` → `ина иной иной ину иной иной`
  - `ева` → `ева евой евой еву евой евой`
  - `ова` → `ова овой овой ову овой овой`
- **`mSurn(x, p)`:** the same, with these endings in order:
  - `ев` → `ев ева еву ева евым еве`
  - `ов` → `ов ова ову ова овым ове`
  - `ый` → `ый ого ому ого ым ом`
  - `ин` → `ин ина ину ина иным ине`
  - `кий` → `кий кого кому кого ким ком`
  - `а` and `о` → unchanged

  If nothing matches, it falls back to `––o`.
- **Female name `·a—`:**
  - `любовь` uses a fixed list.
  - An `-ая` name becomes `–·—(w, 2)` + `аи / ае / аю / аей / ае`.
  - An `-а` or `-я` name goes through `l–`.
  - Anything else is unchanged.
- **Male name `––o`:**
  - An `-ий` name becomes `–·—(w, 2)` + `ия / ию / ия / ием / ии`.
  - Otherwise the `nounExclusions` row.
  - Otherwise, for a final consonant of `трнсмдзлбпвфгкхжшчщ`, `w & o(ko)`.
  - Otherwise `root & oa(last3, nounSuffixes, ko)`.
- **`–·—(w, n)`** = `"'" & Left(w, Len-n)`: the apostrophe stays visible inside the full name.
- **Quirks:**
  - The Вин button gives the dative.
  - The patronymic suffers from the noun bug.
  - `-ий` names get a visible `'`.
  - An empty cell gets the error text.
- **ADR 0005 deviation:** Вин uses ko 4; no apostrophe; the patronymic uses the fixed noun rule.

**Examples:**
- Род `Иванов Сергей Петрович` → as compiled `Иванова Сергея Петро`; fixed `Иванова Сергея Петровича`.
- Дат `Петрова Анна Ивановна` → `Петровой Анне Ивановне`.
- Род `Толстой Дмитрий Ильич` → `Толстоя 'Дмитрия Ильича`.

---

## 4. Counts

**Количество слов**
- **Handler:** `–·oa` (L2229), using `akk` on every cell, written through `k–k`.
- **Quirks:** empty → 0; `" a  b "` → 5.
- **ADR 0005:** count real words.

**Количество символов**
- **Handler:** `–a·k` (L1933), which returns `Len(cell)`. Spaces count.

**Длина в пикселях (Arial 18)**
- **Handler:** `–a–·` (L2646) → `o—o` (L444–445) → `o··–` (L1397–1401).
- It sums per-character widths from tables at L1398–1400 (regular or bold, depending on each character's font). An unknown character counts 0. Excel-specific.

**Количество повторений элемента**
- **Handler:** `––k—` (L1875). Works on column 1.
- **Algorithm:** the key is `UCase(value)`. The first pass counts the keys; the second writes each row's total count.
- **Quirk:** empty cells are counted as one key.
- **ADR 0005:** ё = е; empty cells get no count.

**Номер встречаемости**
- **Handler:** `–kko` (L2166). Same key; writes the running count (1, 2, 3…).

**Долю от суммы**
- **Handler:** `–kok` (L1607). `value / SUM(column 1)`.
- **Quirks:** a text cell → type mismatch and the macro stops; a sum of 0 → division error.

**Накопительным итогом**
- **Handler:** `–koo` (L2489). The running sum in selection order (unsorted), divided by the total.

**ABC-анализ**
- **Handler:** `ABCA` (L3497). It colours the cells and writes no values.
- **Algorithm:**
  1. `T = SUM`; if `T = 0`, exit.
  2. Sort the cells descending, with an exchange sort that swaps only on strict `<` (not stable).
  3. Compute the cumulative share `p` per cell: `p ≤ 0.8` → A, **red**; `p ≤ 0.95` → B, yellow; otherwise C, green.
- **Example:** `50 30 15 5` → `A A B C`.
- **Port:** return an A/B/C column.

---

## 5. Combinations

### Перестановки слов
- **Handler:** `—·—–` (L2282) → `oa–k` (L1405). Helpers: `kaa—` (L1406), `о·k` (L1402), `–··` (L1404).
- **Input / output:** column 1; output on a new sheet named `output`, column A from A1.
- **Algorithm:**
  1. If `Σ words!` > 1 048 576, show a message and stop.
  2. Recursion: if the rest has fewer than 2 words, write `prefix & rest`. Otherwise, for each word `g`, recurse with `prefix & word_g & " "` and the rest without word `g`.
- **Order:** `a b c` → `abc, acb, bac, bca, cab, cba`.
- **Quirks:** no dedupe; an empty phrase gives an empty row; the macro fails if a sheet `output` exists.

### Генератор линейных комбинаций
- **Handler:** `———o` (L377–379).
- **Input:** active-sheet columns 1…`UsedRange.Columns.Count`, each read from row 1 down to its first empty cell.
- **Output:** the Cartesian product on a new sheet. The first column changes slowest, as in `itertools.product`. Each source column stays a separate column, not joined.
- **Example:** A = `купить, заказать`, B = `диван, стол` → 4 rows.
- **Quirk:** an empty column → runtime error.

### Комбинации по 2 элемента
- **Handler:** `a––·` (L1862) → `oa·k` (L2361). Writer: `—·a` (L451–498).
- **Algorithm:** all ordered pairs of rows `g ≠ a`, keyed `v_g\v_a`, deduplicated. The output goes to a new sheet: A = `x\y`, B = `FALSE`.
- **Example:** `a, b, c` → `a\b a\c b\a b\c c\a c\b`.
- **Quirks:** equal values give `x\x`; column B is a useless `FALSE`.

---

## 6. Hierarchy

**`isChild(p, c)`** (L1366) is true when:
- `p <> c` (binary), and
- every token of `p` appears in `" " & c & " "` as `" " & token & " "` (case-sensitive).

Word order and repeated words are ignored. An empty `p` is a parent of everything.

### Ближайших родителей
- **Handler:** `–—·o` (L3451). Helpers: `CreateAndPopulateNGramDicts` (L3396), `GenNGrams` (L3395), `GenerateCombinations` (L3394), `QuickSort` (L3393), `FindParentInDicts` (L3398).
- **Input / output:** an InputBox asks for the parent range; the selection holds the children. Column 1 is **overwritten in place**.
- **Algorithm:**
  1. Index the parents: for each phrase with ≤ 6 words, sort its words and store `sorted → original` in a dict per word count. The first occurrence wins.
  2. For each child, generate every combination of its words of size 1…min(n, 6). The order is by size, and within a size by lexicographic word positions. Each combination is sorted.
  3. Scan the combinations from the last back to the first. The first one found gives the parent's original text; if none is found, the result is `""`.
- **Quirks:**
  - The child itself counts: a child equal to a parent (in any word order) returns that parent.
  - Parents with more than 6 words are ignored.
  - The match is case-sensitive.
  - A child with no parent becomes an empty cell.
- **Example:** parents `стол`, `купить стол`; child `купить стол недорого` → `купить стол`.

### Первых родителей / Первые вложенные фразы (детей)
- **Handler:** `–—·a` (L2124) with `firstParent` (L1369); `–—·k` (L2388) with `firstChild` (L1367).
- **Algorithm:** an InputBox asks for a list. For each cell, scan the list top-down:
  - parent: the first `p` with `isChild(p, cell)`;
  - child: the first `c` with `isChild(cell, c)`.
  If nothing matches, the result is `""`. Output in place or to the right.
- **Quirk:** an empty source cell returns the first non-empty list item as its child.

### Найти базисы
- **Handler:** `semBasis` (L3399–3450).
- **Input:** two Yes/No prompts («по леммам?» and «без стоп-слов?»), then column 1 of the selection.
- **Algorithm:**
  1. For each row: take the tokens of `LCase(a·(cell))`, lemmatized if asked. `set` = the unique tokens that are not stopwords. If that set is empty, use all unique tokens.
  2. `key = srt(set)`. The first row with a given key owns it.
  3. A row is a basis iff it owns its key and no other key is a proper subset of its set.
  4. Rows that are not a basis are cleared to `""`. Empty rows stay as they are.
- **Output:** through `k–k`, plus a message with the count.
- **Example:** `купить диван`, `диван`, `купить диван недорого`, `стол`, `диван купить` → `""`, `диван`, `""`, `стол`, `""`.
- **ADR 0005:** stopwords case-insensitive; split by any whitespace.

---

## 7. Good / bad split (Работа с семантическим ядром)

- **Handler:** `semWP` (L319–328) opens `SEMToolsWordProcessor.xlsb`, downloading it if needed. That workbook calls these add-in procedures: `Tool_countWords` (L314), `Tool_dictAtor` (L315), `TOOL_crLemmDict` (L310–311), `TOOL_lemmatizeArr` (L2585), `findPhrWithWord` (L316), `findPhrWithOutWord` (L317–318), `TOOL_remPhrWithOnlyPlusWords` (L312–313).
- **Sheet `semHelper`:** A = core phrases, C:D = frequency dictionary, F = phrases containing the selected word, H = plus-words, J:K = lemma map `semDict`. Sheets `Good case` and `Bad case` (B = the word) hold the results.
- **Algorithm:**
  1. Lemma map, built once while J1 is empty: `token → aaa(token)` for tokens with a different lemma (case kept). It is written only if it has ≥ 3 entries.
  2. Lemmatize: lower-case the phrase, split it by spaces, and map each token through `semDict[UCase(token)]`.
  3. Frequency dictionary: count every lemma occurrence (occurrences, not phrases), sorted descending.
  4. **Bad word:** phrases whose lemmatized form contains `" " & word & " "` (binary) move to `Bad case` together with the word.
  5. **Good word:** the word is appended to the plus-words. A phrase moves to `Good case` only when **all** its lemmas are plus-words (`UCase` compare).
  6. After each step the dictionary is recounted, and the cursor moves to the next word that is not a plus-word.
- **Quirk:** fewer than 3 inflected words → no lemma map at all.
- **Port:** `split_by_words(phrases, good, bad, lemmatizer)` → good / bad / rest + the frequency dictionary of the rest.

---

## 8. Clustering

### По частотному словарю
- **Handler:** `––o·` (L2374) → `O–—–` (L1201). Helpers: `o–·o` (L2588), `a·o` (L1649).
- **Input / output:** column 1; an InputBox asks for the threshold `wc`; the result is written to `Selection.Offset(0, 1)`, with no insert.
- **Algorithm:**
  1. Remove stopwords (exact, case-sensitive).
  2. Count document frequency: sort each phrase's words, drop repeated words (case-insensitive), then count.
  3. Ask for `wc`. The prompt shows the max, mean and median count.
  4. In each phrase, drop the words with count < `wc`. The original word order is kept.
- **Example (`wc = 2`):** `купить диван`, `диван купить недорого`, `диван угловой`, `купить стол` → `купить диван`, `диван купить`, `диван`, `купить`.
- **Quirk:** the word order is kept, so `купить диван` and `диван купить` look like separate clusters.

### По топ-10 выдачи
- **Handler:** `SERPClustering` (L182) → `Clustering.frm` → `calculateScore` (L3261–3278). It uses `simScore` (L3260).
- **Input:** active sheet from row 2: column A = keyword, column B = its URLs separated by spaces, top first (the format of `xmlRiver2`, L258).
- **Settings** (saved in `abc`): AZ1–AZ5 = `bonus1…5` (defaults 5 4 3 2 1), AZ6 = `bonus10` (1), AZ7 = threshold (24).
- **`simScore(x, y)`:** for each URL `x[i]` (0-based):
  - if `i > 4` and the URL is anywhere in `y`: add `bonus10`;
  - if `i ≤ 4`: take `j` = its last index in `y`. If found, add `bonus10`, plus `sb[max(i, j)]` when `max(i, j) ≤ 4`. `sb[k] = bonus_{k+1} + … + bonus5`, which gives `15 10 6 3 1` with the defaults.
- **Algorithm:**
  1. Draw an edge between two rows when their score is ≥ the threshold.
  2. Find connected components by BFS, starting from the lowest unvisited row; neighbours are visited in row order.
  3. Sort the clusters **ascending** by size (zero-padded size + text).
  4. Drop keywords already printed in an earlier cluster.
  5. Output on a new sheet `Clusters`: `Keywords` header, then one cluster per row, joined by `", "` and truncated to 32 767 chars.
- **Example:** two tops sharing positions 0, 1 and 7 → `16 + 11 + 1 = 28`, so they are linked. Identical tops score 45.
- **Quirks:**
  - The linking is single linkage, so clusters can chain.
  - The same keyword twice inside one component → error 457.
  - A comma inside a keyword miscounts the cluster size.
- **Port:** the input is the table `phrase, position, url`.

---

## 9. Minus-words

### Поиск нерелевантных слов
- **Handler:** `—k–o` (L2887) → `findIrr.frm`.
- **Input:** an InputBox asks for the main word in the nominative. The form shows its 12 forms, computed with the noun handlers (`l–`). They are editable and all must be filled.
- **Algorithm:**
  1. **The selection is modified in place:** `udalit_toponimy_s_pryedlogami` (L1194) removes toponyms together with their preposition; `DeletePhrases` (L3452) removes the geo and purchase-marker phrases and lower-cases the cells.
  2. For each word triple `(w[g-2], w[g-1], w[g])`: if `w[g]` is one of the 12 forms and `w[g-1]` is in that case's preposition list, `w[g-2]` is a candidate, unless it is a stopword. The lists are:
     - **Им:** `ли или если свой мой твой своя моя твоя свое мое твое своё моё твоё свои мои твои`
     - **Род:** `без вследствие вместо для до из кроме моей моих от после своего моего твоего своей с у твоей своих твоих`
     - **Дат:** `по к своему моему твоему своей моей твоей своим моим твоим`
     - **Вин:** `про подо под в во за на через по о об с сквозь ли или свою мою твою свои мои твои свой мой твой наш их`
     - **Твор:** `над под подо между за с со перед своим моим твоим своей моей твоей своими моими твоими`
     - **Предл:** `о об при в на по своём моём твоём своем моем твоем своей моей твоей своих моих твоих`
  3. Count the candidates and collect unique examples.
- **Output:** a new sheet `Минус-слова` with columns Слово, Употреблений, Примеры.
- **Example:** `чехол для телефона` → candidate `чехол`.
- **Quirks:**
  - The input data is changed.
  - The default forms carry the noun bug (`телефон` Род → `теле`).
  - The match is case-sensitive.
- **ADR 0005:** do not modify the input; use the fixed noun forms.

### Исключение синонимов › Составить список на основе отчета
- **Handler:** `aa·a` (L2376) → `o·k–` (L654–747). Helpers: `ook` (L1302), `a––` (L1380), `–k–` (L2355), `ka––` (L1819), `—··` (L2395).
- **Input:** a Yandex.Direct search-query report with the columns `Поисковый запрос`, `Условие показа`, `Подобранная фраза`.
- **Output:** two new sheets, `Синонимы 100%` and `Синонимы проверить`, with columns keyword | synonyms.
- **Algorithm:**
  1. Clean the condition and the matched phrase: cut everything from the first `" -"`, and remove `+`.
  2. If the matched phrase is not `-`: `pair = ook(cond, match)`. Otherwise: `pair2 = ook(cond, query)`.
  3. `ook(a, b)`:
     1. Lower-case both, and remove stopwords outside `[…]`.
     2. If the word counts differ, return `""`.
     3. Lemmatize both, then `srt` all the words together.
     4. Collect the tokens that differ from both neighbours. More than 2 → `""`.
     5. Intended: keep the order when the first token is a word from `a`; otherwise reverse it.
  4. `initial` = first word of the pair, `syn` = last word. `pair` feeds the 100% list; `pair2` feeds the «проверить» list unless the synonym is already in the 100% list.
- **Quirk:** **as compiled, `Select Case InStr/Case True` always reverses**, so `initial` is the alphabetically later word. Example: `купить диван` / `купить софа` → `софа: диван`.
- **ADR 0005 deviation:** `initial` = the word from the condition.

### Исключение синонимов › Добавить в минус-слова
- **Handler:** `aa··` (L2466) → `oo—–` (L839–840).
- **Input:** an InputBox asks for two columns, word | synonyms (space-separated).
- **Phrase column:** found by `Find(ydPhr())`. `ydPhr` (L1206) is an empty stub; I believe this ends up as column B from row 2, but I could not confirm it.
- **Algorithm:** for each phrase that does not start with `"`, lemmatize `oko(cut-minus(LCase))`. For each lemma that is a dictionary key, intended behaviour: append ` -syn` for each synonym that is not already in the phrase.
- **Quirk:** **as compiled, every synonym is appended**, because the `InStr/Case True` test never matches.
- **ADR 0005 deviation:** skip synonyms already in the phrase; take the phrase column as an explicit argument.

---

## 10. Typos and similarity

### Является ли опечаткой?
- **Handler:** `a–a—` (L2484) → `oo–a` (L2451). Max 500 cells.
- **Algorithm:**
  1. GET `suggest.yandex.ru/suggest-ya.cgi?part=<cell> &ll=2&lr=213` (not URL-encoded, 100 ms timeouts).
  2. Take the first match of `\[.+\]`, drop its outer characters, and keep the text after the first `"],"`.
  3. The cell is a typo if `" " & oko(text) & " "` does not contain `" " & cell & " "` (case-insensitive).
- **Quirks:** depends on the network; a cell with punctuation is always a typo.
- **Port:** Levenshtein only, as the plan says (a different algorithm).

### Наиболее вероятное исправление
- **Handler:** `a–aa` (L1620) → `oo–—` (L1511).
- **Algorithm:**
  1. Same request as above.
  2. Suggestions = the text split by `,`, with quotes removed.
  3. Count every window of k words in every suggestion, where k = the cell's word count (`ok–`, L1391).
  4. Pick in insertion order: a window wins when its count is ≥ the current value, starting from `current = k`. Ties go to the later window.
- **Quirk:** when no window reaches k, the result is the last window computed (often `""`).

### UDFs
- **`Levenstein`** (L3338): unit edit costs, but it compares only the low byte of each UTF-16 unit. So, for example, `а` (U+0430) equals `0` (U+0030).
- **`БлижайшееПоЛевенштейну`** (L1364): private and never called.
- **`simScore`:** see §8.
- **ADR 0005:** compare full code points.

---

## 11. Sentiment (Среднее / Мин. / Макс.)

- **Handler:** `NGB` (L834), `NGBMin` (L835), `NGBMax` (L836).
- **Input:** the selection holds the phrases. An InputBox asks for two columns, marker | number; the first occurrence wins and keys are binary.
- **Output:** written in place.
- **Algorithm:** split each phrase by spaces; only single-word markers can match, exactly.
  - Mean: `sum / count` of the matched scores (repeated words count again).
  - Min: starts at `11111`.
  - Max: starts at `0`.
- **Quirks:**
  - The mean with no marker divides 0 by 0, and the macro stops.
  - The mean does not handle Cancel.
  - The min with no marker is `11111`.
  - The max can never be negative.
- **ADR 0005 deviation:**
  - no marker → empty;
  - max starts at −∞;
  - case-insensitive markers, with ё = е.

---

## 12. Prepositions

### Дополнения с предлогами
- **Handler:** `findCollocs` (L448) → `k– "collocs"` (L1428). The noun test is `k—·—`, i.e. `aoo("··–", w, True)`.
- **Algorithm:**
  1. `preps` = `для с в из на к со о во у по под от после за над` (16 items, no `без`, case-sensitive).
  2. For each preposition token, scan the next ≤ 5 tokens, stopping at the next preposition. `v` = the last noun among them.
  3. If there is one, emit `prep … v` and continue after `v`.
  4. Join the results with `", "`.
- **Examples:**
  - `купить диван в москве недорого` → `в москве`
  - `диван для детей с доставкой` → `для детей, с доставкой`
- **Quirks:**
  - It runs only if `lemms.xlsb` is already open.
  - Capitalised `В` is not treated as a preposition.
- **Related:** `prepCollocsToEnd` (L1426) is a UDF version that moves the complements to the end of the phrase.

### Предлоги в конце фраз
- **Handler:** `remLWprps` (L2306) → `dLW` (L2301), called four times: stopwords, `prps`, stopwords, `prps`.
- **Algorithm:** in each pass, if the last word (`UCase` compare) is in the list, drop it (`·k—`).
- **Example:** `диван в и` → `диван`.
- **Quirks:**
  - A one-cell selection does nothing.
  - A phrase that is only a preposition becomes empty.
  - With «Выводить результат справа», each pass inserts its own column computed from the **original** text, so the passes are not chained.
- **ADR 0005 deviation:**
  - loop until the last word is clean;
  - one output;
  - clean the list (`g`, `пo`).

### Ячейки, начинающиеся / заканчивающиеся на предлоги
- **Handler:** `findFFWprps` (L2304) → `fFW` (L2298), using the first word; `findFLWprps` (L2305) → `fLW` (L2299), using the last word.
- **Output:** TRUE/FALSE when the word is in `prps()` (`UCase` compare).
- **Quirk:** a one-cell selection does nothing.

---

## 13. Top quirks to keep in mind when porting

1. **`Select Case True / Case InStr(…)` and `Select Case InStr / Case True` never match**, because True is -1; the P-code confirms this. Affected:
   - noun declension: consonant-final words are truncated or unchanged, and so are patronymics and the forms in the irrelevant-words form;
   - synonym orientation;
   - synonym minus-words.
2. **`dictRange` is never set**, so «Все что склоняется» declines verbs and adverbs.
3. **ФИО:** Вин gives the dative; `-ий` names get a visible `'`; neuter adjective oblique cases run the noun table.
4. **«Поиск нерелевантных слов» changes the input in place** before it starts.
5. **Sentiment:** the mean crashes when a phrase has no marker; the max cannot be negative; the min defaults to 11111.
