# Conformance of the corpus area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/corpus/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [add_minus_words](#add_minus_words) | 6 | 4 | 2 | 0 |
| [basis_phrases](#basis_phrases) | 7 | 6 | 1 | 0 |
| [cluster_by_frequency](#cluster_by_frequency) | 6 | 4 | 2 | 0 |
| [first_children](#first_children) | 5 | 2 | 3 | 0 |
| [first_parents](#first_parents) | 6 | 3 | 3 | 0 |
| [is_typo](#is_typo) | 6 | 0 | 6 | 0 |
| [levenshtein](#levenshtein) | 7 | 5 | 2 | 0 |
| [linear_combinations](#linear_combinations) | 5 | 4 | 1 | 0 |
| [nearest_parents](#nearest_parents) | 7 | 2 | 5 | 0 |
| [ordered_pairs](#ordered_pairs) | 6 | 1 | 5 | 0 |
| [permutations](#permutations) | 6 | 5 | 1 | 0 |
| [sentiment](#sentiment) | 8 | 4 | 4 | 0 |
| [split_by_words](#split_by_words) | 6 | 4 | 2 | 0 |
| [synonyms](#synonyms) | 7 | 3 | 4 | 0 |
| [typo_correction](#typo_correction) | 5 | 0 | 5 | 0 |
| **All** | **93** | **47** | **46** | **0** |

## add_minus_words

add_minus_words. VBA (docs/vba/analysis.md §9): «Добавить в минус-слова» aa·· (L2466) → oo—– (L839–840): an InputBox asks for two columns, word | synonyms (separated by spaces); each phrase that does not start with a quote is lemmatized (oko of LCase, cut from its minus-words); for each lemma that is a word of the list, as compiled every synonym is appended as « -synonym», since the InStr/Case True test never matches. The phrase column comes from ydPhr (L1206), an empty stub: here the phrases are the input.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `add_minus_words` | 6 | 4 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| minus-held | `"купить диван -софа"` | `"купить диван -софа -софа -тахта"` | `"купить диван -софа -тахта"` | Минус-слово не добавляется, если синоним уже есть во фразе | the test of a synonym in the phrase never matches: every synonym is appended |
| minus-word-held | `"диван софа"` | `"диван софа -софа -тахта"` | `"диван софа -тахта"` | Минус-слово не добавляется, если синоним уже есть во фразе | the test of a synonym in the phrase never matches: every synonym is appended |

### xfail

None.

## basis_phrases

basis_phrases. VBA (docs/vba/analysis.md §6): «Найти базисы» semBasis (L3399–3450): two prompts (by lemmas, without stopwords); the key of a row is srt of its unique tokens of LCase(a·(cell)) split by one space, lemmatized by aaa on request, without the stopwords on request (all its tokens when none is left); the first row owns a key; a row stays when it owns its key and no smaller key has only words of it; the other rows are cleared.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `basis_phrases` | 7 | 6 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| basis-yo | `"ёлка \| елка купить"` | `"ёлка \| елка купить"` | `"ёлка \| "` | ё = е при сравнении | LCase keeps ё: «ёлка» is not «елка» |

### xfail

None.

## cluster_by_frequency

cluster_by_frequency. VBA (docs/vba/analysis.md §8): «По частотному словарю» ––o· (L2374) → O–—– (L1201): the stopwords removed (o–·o, L2588, exact); the words of each phrase sorted (srt), a repeated word dropped (a·o, L1649), counted with binary keys; the InputBox asks the threshold; in each phrase the words counted below it are dropped, the word order kept.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `cluster_by_frequency` | 6 | 4 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| cf-order | `"купить диван \| диван купить недорого \| диван угловой \| купить стол"` | `"купить диван \| диван купить \| диван \| купить"` | `"диван купить \| диван купить \| диван \| купить"` | Кластер по частотному словарю — набор слов, а не их порядок | the words keep the order of the phrase: «купить диван» and «диван купить» make two clusters |
| cf-case | `"Диван угловой \| диван"` | `" \| "` | `"диван \| диван"` | Слова сравниваются без учёта регистра | the counts have binary keys: «Диван» and «диван» are counted apart |

### xfail

None.

## first_children

first_children. VBA (docs/vba/analysis.md §6): «Первые вложенные фразы» –—·k (L2388) with firstChild (L1367): the first list item c with isChild(phrase, c) (L1366); an empty phrase is a parent of every item.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `first_children` | 5 | 2 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| fc-order | `"стол купить"` | `"купить стол"` | `"купить стол недорого"` | Фраза никогда не родитель самой себе | isChild compares the whole strings: the same words in another order make a child |
| fc-empty | `"диван \|  \| стол"` | `"купить диван \| купить диван \| стол угловой"` | `"купить диван \|  \| стол угловой"` | У пустой фразы нет родителя и ребёнка | an empty phrase has no word to miss, so the first item is its child |
| fc-case | `"Стол"` | `""` | `"купить стол"` | Слова сравниваются без учёта регистра | InStr is binary: «Стол» is not «стол» |

### xfail

None.

## first_parents

first_parents. VBA (docs/vba/analysis.md §6): «Первых родителей» –—·a (L2124) with firstParent (L1369): the first list item p with isChild (L1366): p <> phrase (binary) and each word of p, split by one space, stands in « phrase » as « word » (InStr, binary); an empty item is a parent of every phrase and gives "".

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `first_parents` | 6 | 3 | 3 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| fp-order | `"стол купить"` | `"купить стол"` | `"стол"` | Фраза никогда не родитель самой себе | isChild compares the whole strings: the same words in another order make a parent |
| fp-empty-item | `"купить стол"` | `""` | `"стол"` | Пустые ячейки списка пропускаются | an empty item has no word to miss, so it is the first parent of every phrase and gives "" |
| fp-case | `"Купить Стол"` | `""` | `"стол"` | Слова сравниваются без учёта регистра | InStr is binary: «Стол» is not «стол» |

### xfail

None.

## is_typo

is_typo. VBA (docs/vba/analysis.md §10): «Является ли опечаткой?» a–a— (L2484) → oo–a (L2451): a GET of suggest.yandex.ru for each cell (at most 500, 100 ms timeouts); the cell is a typo when « text » of the suggestions does not hold « cell ». No network in the cases: the request fails and the macro stops (#ERROR).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `is_typo` | 6 | 0 | 6 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| typo-core | `"диван \| диван угловой \| купить диавн"` | `"#ERROR"` | `"FALSE \| FALSE \| TRUE"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| typo-ratio | `"стол \| стол купить \| стул"` | `"#ERROR"` | `"FALSE \| FALSE \| FALSE"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| typo-ratio-2 | `"стол \| стол купить \| стул"` | `"#ERROR"` | `"FALSE \| FALSE \| TRUE"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| typo-short | `"кот \| кот черный \| кит \| кто"` | `"#ERROR"` | `"FALSE \| FALSE \| TRUE \| FALSE"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| typo-digit | `"диван \| диван угловой \| диван2"` | `"#ERROR"` | `"FALSE \| FALSE \| FALSE"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| typo-case | `"диван \| диван угловой \| купить Диавн"` | `"#ERROR"` | `"FALSE \| FALSE \| TRUE"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |

### xfail

None.

## levenshtein

levenshtein. VBA (docs/vba/analysis.md §10): the UDF Levenstein (L3338): unit costs, but it compares the low byte of each UTF-16 unit (bs1((i - 1) * 2)), so «а» (U+0430) equals «0» (U+0030). Input: «first | second».

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `levenshtein` | 7 | 5 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| lev-low-byte | `"а \| 0"` | `"0"` | `"1"` | Расстояние Левенштейна считается по целым символам | only the low byte is compared: U+0430 and U+0030 share 0x30 |
| lev-low-byte-word | `"кот \| к>т"` | `"0"` | `"1"` | Расстояние Левенштейна считается по целым символам | only the low byte is compared: «о» U+043E and «>» U+003E share 0x3E |

### xfail

None.

## linear_combinations

linear_combinations. VBA (docs/vba/analysis.md §5): «Генератор линейных комбинаций» ———o (L377–379): each column of the used range read from row 1 down to its first empty cell; the Cartesian product on a new sheet, the first column slowest, one column per list; a column with no items is a runtime error. Input: each item is one list, its values joined by «, »; a row renders as first=last column.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `linear_combinations` | 5 | 4 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| lin-gap | `"купить, , заказать \| диван"` | `"купить=диван"` | `"купить=диван \| заказать=диван"` | Пустые ячейки списка пропускаются | a column is read down to its first empty cell: the items below it are lost |

### xfail

None.

## nearest_parents

nearest_parents. VBA (docs/vba/analysis.md §6): «Ближайших родителей» –—·o (L3451): CreateAndPopulateNGramDicts (L3396) files each non-empty parent of up to 6 words by its sorted words (the first wins); GenNGrams (L3395) and GenerateCombinations (L3394) make the sorted combinations of the child's words of 1…min(n, 6), by size, then by positions; FindParentInDicts (L3398) takes the last one found. Binary compare: case and ё count.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `nearest_parents` | 7 | 2 | 5 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| near-basic | `"купить стол недорого \| стол"` | `"купить стол \| стол"` | `"купить стол \| "` | Фраза никогда не родитель самой себе | the combinations of the child hold the child itself, so a child that is in the list is its own parent |
| near-order | `"стол купить"` | `"купить стол"` | `"стол"` | Фраза никогда не родитель самой себе | the child's words sorted are the parent's words sorted: the same phrase in another order is its parent |
| near-case | `"Купить Стол"` | `""` | `"стол"` | Слова сравниваются без учёта регистра | the dictionary keys are binary: «Стол» is not «стол» |
| near-yo | `"ёлка искусственная"` | `""` | `"елка"` | ё = е при сравнении | the dictionary keys are binary: «ёлка» is not «елка» |
| near-long | `"a b c d e f g h"` | `"a"` | `"a b c d e f g"` | Родитель длиннее шести слов тоже находится | parents of more than 6 words are not filed, and the combinations stop at 6 words |

### xfail

None.

## ordered_pairs

ordered_pairs. VBA (docs/vba/analysis.md §5): «Комбинации по 2 элемента» a––· (L1862) → oa·k (L2361): for each row g and each row a ≠ g the key value_g\value_a, once; the writer —·a (L451) puts the keys in column A and FALSE in column B of a new sheet. vba renders a row as A=B.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `ordered_pairs` | 6 | 1 | 5 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| pairs-three | `"a \| b \| c"` | `"a\b=FALSE \| a\c=FALSE \| b\a=FALSE \| b\c=FALSE \| c\a=FALSE \| c\b=FALSE"` | `"a=b \| a=c \| b=a \| b=c \| c=a \| c=b"` | Таблица результата — по колонке на каждое значение | the add-in writes a pair as one text a\b and a column of FALSE |
| pairs-two | `"диван \| стол"` | `"диван\стол=FALSE \| стол\диван=FALSE"` | `"диван=стол \| стол=диван"` | Таблица результата — по колонке на каждое значение | the add-in writes a pair as one text a\b and a column of FALSE |
| pairs-case | `"Диван \| диван"` | `"Диван\диван=FALSE \| диван\Диван=FALSE"` | `"Диван=диван \| диван=Диван"` | Таблица результата — по колонке на каждое значение | the add-in writes a pair as one text a\b and a column of FALSE |
| pairs-repeated | `"a \| a \| b"` | `"a\a=FALSE \| a\b=FALSE \| b\a=FALSE"` | `"a=b \| b=a"` | Таблица результата — по колонке на каждое значение; Пары — из разных элементов списка | two equal rows make the pair a\a: an item with itself |
| pairs-empty | `"a \|  \| b"` | `"a\=FALSE \| a\b=FALSE \| \a=FALSE \| \b=FALSE \| b\a=FALSE \| b\=FALSE"` | `"a=b \| b=a"` | Таблица результата — по колонке на каждое значение; Пустые ячейки списка пропускаются | an empty cell is paired as an item "" |

### xfail

None.

## permutations

permutations. VBA, RibbonCallbacks.vba (docs/vba/analysis.md §5): «Все перестановки слов» —·—– (L2282) → oa–k (L1405): the sum of Permut(akk, akk) over the cells above 1 048 576 stops with a message; kaa— (L1406): a rest of fewer than 2 words (akk, L2414, a split by one space) writes prefix & rest, else each word g in turn (о·k, L1402) goes to the prefix with a space and the rest loses it (–··, L1404, Trim). Output: column A of a new sheet output.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `permutations` | 6 | 5 | 1 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| perm-spaces | `"a  b"` | `"a b \|  a b \|  b a \| b a"` | `"a b \| b a"` | фраза делится по любым пробелам, двойных пробелов в результатах нет | akk splits by one space: the empty word between the two spaces is permuted too, and Trim leaves a leading space |

### xfail

None.

## sentiment

sentiment. VBA (docs/vba/analysis.md §11): «Анализ тональности» NGB (L834) mean, NGBMin (L835) min, NGBMax (L836) max: an InputBox asks for two columns, marker | number, the first occurrence of a marker wins, binary keys; each phrase split by one space; the mean is sum / count (0 / 0 stops the macro), the min starts at 11111, the max at 0.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `sentiment` | 8 | 4 | 4 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| sent-mean-none | `"отличный диван \| стул"` | `"#ERROR"` | `"5 \| "` | Тональность фразы без маркера пустая | the mean of a phrase with no marker divides 0 by 0 and the macro stops |
| sent-min-none | `"стул"` | `"11111"` | `""` | Тональность фразы без маркера пустая | the min starts at 11111 and stays |
| sent-max-negative | `"плохой стол"` | `"0"` | `"-3"` | Максимум тональности может быть отрицательным | the max starts at 0 |
| sent-case | `"Отличный диван"` | `"#ERROR"` | `"5"` | Слова сравниваются без учёта регистра; Тональность фразы без маркера пустая | the keys are binary: «Отличный» is no marker, so the phrase has none and the mean divides 0 by 0 |

### xfail

None.

## split_by_words

split_by_words. VBA (docs/vba/analysis.md §7): «Работа с семантическим ядром» semWP (L319–328) and the helper workbook SEMToolsWordProcessor.xlsb: the lemma map TOOL_crLemmDict (L310–311) only when at least 3 words have another lemma; Tool_dictAtor (L315) counts the lemmas; findPhrWithWord (L316) moves the phrases with « word » to Bad case; TOOL_remPhrWithOnlyPlusWords (L312–313) moves the phrases whose lemmas are all plus-words to Good case. vba: the sheets after the good words, then the bad words are chosen: Good case || Bad case || the rest || the frequency dictionary. Without lemmas the core has fewer than 3 inflected words: the workbook builds no lemma map and compares words.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `split_by_words` | 6 | 4 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| split-few-forms | `"диваны бу \| купить диван \| диван \| диваны недорого"` | `"купить диван \| диван \|\| диваны бу \|\| диваны недорого \|\| диваны=1 \| недорого=1"` | `"купить диван \| диван \|\| диваны бу \|\| диваны недорого \|\| диван=1 \| недорогой=1"` | По леммам — всегда, без порога в три словоформы | with fewer than 3 inflected words the workbook builds no lemma map and compares the words as they stand |
| split-yo | `"ёлка купить \| ёлка"` | `" \|\|  \|\| ёлка купить \| ёлка \|\| ёлка=2 \| купить=1"` | `"ёлка купить \| ёлка \|\|  \|\|  \|\| "` | ё = е при сравнении | LCase keeps ё, and the plus-words compare by UCase: «ЁЛКА» is not «ЕЛКА» |

### xfail

None.

## synonyms

synonyms. VBA (docs/vba/analysis.md §9): «Составить список на основе отчета» aa·a (L2376) → o·k– (L654–747): the condition and the matched phrase cut from the first « -», «+» removed; ook (L1302): LCase, the stopwords out, equal word counts, lemmas, srt of all the words, the words unlike both neighbours, at most 2; as compiled, Select Case InStr/Case True always reverses the pair, so the initial word is the alphabetically later one. A row with the matched phrase «-» compares the condition with the search phrase, for the list to check. Output: the sheets Синонимы 100% and Синонимы проверить, keyword | synonyms. Input: each item «phrase / condition / matched»; vba renders the rows of the two sheets in that order as word=synonyms.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `synonyms` | 7 | 3 | 4 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| syn-initial | `"купить софу / купить диван / купить софа"` | `"софа=диван"` | `"диван=софа"` | Синоним считается от слова условия показа | the pair is always reversed: the initial word is the later one in sort order |
| syn-operators | `" / +купить !диваны -бу / купила софы"` | `"софа=!диваны"` | `"диван=софа"` | Синоним считается от слова условия показа; Операторы соответствия убираются все | only «+» is removed: «!диваны» is no word of the dictionary and stays as it is |
| syn-check | `"купить кушетку / купить диван / - \| купить софу / купить диван / купить софа"` | `"софа=диван \| кушетка=диван"` | `"диван=софа \| диван=кушетка"` | Синоним считается от слова условия показа | the pair is always reversed: the initial word is the later one in sort order |
| syn-stopwords | `" / диван в москве / софа москва"` | `"софа=диван"` | `"диван=софа"` | Синоним считается от слова условия показа | the pair is always reversed: the initial word is the later one in sort order |

### xfail

None.

## typo_correction

typo_correction. VBA (docs/vba/analysis.md §10): «Наиболее вероятное исправление» a–aa (L1620) → oo–— (L1511): the same request as «Является ли опечаткой?»; the suggestions split by «,»; every window of as many words as the cell counted; the window counted at least the current value wins, from the word count of the cell up. No network in the cases: the request fails and the macro stops (#ERROR).

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `typo_correction` | 5 | 0 | 5 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| fix-core | `"диван \| диван угловой \| купить диавн"` | `"#ERROR"` | `"диван \| диван угловой \| купить диван"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| fix-none | `"стол \| стол купить \| стул"` | `"#ERROR"` | `"стол \| стол купить \| стул"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| fix-ratio-2 | `"стол \| стол купить \| стул"` | `"#ERROR"` | `"стол \| стол купить \| стол"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| fix-short | `"кот \| кот черный \| кит"` | `"#ERROR"` | `"кот \| кот черный \| кот"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |
| fix-case | `"Диван \| диван угловой \| купить ДИАВН"` | `"#ERROR"` | `"Диван \| диван угловой \| купить диван"` | Опечатки ищутся без сети, по частотному словарю самого ядра | the add-in asks Yandex Suggest for each cell (100 ms timeouts); offline the request fails and the macro stops |

### xfail

None.
