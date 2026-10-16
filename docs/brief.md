# Brief: semkit

Read this file first. It is the hand-off from the session that created this repo.

## Goal
`semkit` is a Python port of the useful logic of the !SEMTools Excel add-in: processing Russian search phrases (semantic core): clean, find, extract, dedupe (incl. implicit duplicates), n-grams, bigrams, basis phrases, parents and children, clustering, marker lists (toponyms, questions, sales…), and morphology (lemmas, parts of speech, declension).

## Decided
1. Library first; a CLI comes after the API settles.
2. I/O goes through the sibling tool `dataio` (`~/Work/tools/dataio`): it reads any source into a `pandas.DataFrame` and writes any target. semkit does not read or write files itself.
3. Out of scope: LLM features, Excel-only features (fonts, sheets, pictures), SEO APIs. Bukvarix stays in its own package `bukvarix`.
4. Morphology lives inside semkit (no separate package). Everything is bundled in the package, no download:
   - lemma dictionary → marisa-trie (wordform → lemma, POS; plus lemma → wordforms). Measured: 5.8 MB, instant open (mmap), 2.7 µs per lookup;
   - marker lists → compressed lists, an Aho-Corasick automaton (`pyahocorasick`) built at load;
   - declension tables → small JSON → dicts.
5. Functions that need lemmas take an optional lemmatizer; without it they work on words as they are.
6. Private repo, private tool. The data belongs to the !SEMTools author; never publish it.
7. Repo state: cli-generator v1.15.0 scaffold, **no git yet**, no business logic. Names: dist `rb-semkit`, command `semkit`, import `rb_semkit`. Ask the Human whether to use the Antagor method here (it is off for dataio).

## Your first step
Run the interview below with the Human, in Russian, one block at a time. Each question has a recommendation (**R**); the Human can answer «R». Record the answers in this file, then write the plan, then code.

## Materials (absolute paths)
| What | Path |
|---|---|
| Catalog of all add-in functions, APIs, UDFs | `/Users/bolandau/Work/_sandbox/semtools/docs/FEATURES.md` |
| VBA source (obfuscated; main logic in RibbonCallbacks.vba) | `/Users/bolandau/Work/_sandbox/semtools/reverse/vba/` |
| Ribbon menu tree, short / with tooltips and handler names | `/Users/bolandau/Work/_sandbox/semtools/reverse/ribbon_menu.txt`, `/Users/bolandau/Work/_sandbox/semtools/reverse/ribbon_full.txt` |
| Lemma dictionary, TSV: wordform, lemma, pos (845k rows) | `/Users/bolandau/Work/_sandbox/semtools/reverse/data/lemms.tsv` |
| Add-in sheet `abc`: declension tables, stopwords, abbreviations (named ranges in `/Users/bolandau/Work/_sandbox/semtools/docs/FEATURES.md` and below) | `/Users/bolandau/Work/_sandbox/semtools/reverse/data/sheet_abc.tsv` |
| Marker lists (18 xlsx: geo, mosmetro, questions, sale…) | `/Users/bolandau/Work/_sandbox/semtools/reverse/downloads/spiski/` |
| Original files | `/Users/bolandau/Work/_sandbox/semtools/!SEMToolsPro.xlam`, `/Users/bolandau/Work/_sandbox/semtools/reverse/downloads/lemms.xlsb` |

Named ranges of sheet `abc` (rows and columns in `sheet_abc.tsv`): lemmSuf E50:G305 (fallback suffix → lemma suffix), nounSuffixes Q1:AB3331 (3-letter ending → 12 forms), nounExclusions Q3380:AB11089, adjSuffixes AD2:AS90 (16 forms), adjExclusions AD93:AS136, femSurSuf AD140:AI163, nonDecl B1:B1205, nounsLikeAdj J1:J417, abbrs M1:M1016, chpuSym E10000:F10965.

How the add-in's morphology works (from the VBA, `RibbonCallbacks.vba`):
- **Lemma** (`aaa`): look up the wordform in the lemma dictionary. If it is missing, replace the last 4 letters by the `lemmSuf` table. The result is cached. For phrases the add-in first builds «unique word → lemma» (`semDict`), then replaces every word.
- **POS**: the 3rd dictionary column (`n`, `v`, `a`, `p`, `advb`, `prn`, `prep`). Verb also by the endings `-тся`, `-ться`, `-ают`, `-уют`. Adjective, when the word is not in the dictionary: the lemma ends with an `adjSuffixes` ending and is not in `nounsLikeAdj`.
- **Declension**: rules, not the dictionary (the dictionary has no cases). Noun: stem (word minus 3 letters) + ending from `nounSuffixes` (12 forms: 6 cases × 2 numbers); `nounExclusions` for whole words; `nonDecl` are indeclinable. Adjective: `adjSuffixes` (16 forms), `adjExclusions`. Surnames: `mSurn`, `fSurn`, `femSurSuf`.
- **All wordforms**: reverse index lemma → wordforms over the dictionary.
- **Mystem**: an external `mystem.exe -c -l` over a temp CSV (not ported).

## Сессия 2. semkit

### A. Объём первой версии
1. **Какие функции первыми?** Варианты из `FEATURES.md`:
   - а) чистка: удалить символы, слова, списки, пробелы, regex;
   - б) найти и извлечь (маски `bool`, извлечение);
   - в) дубли (точные и неявные) и повторы слов;
   - г) n-граммы, биграммы, частотный словарь;
   - д) базисы, родители и дети, кластеры;
   - е) маркеры (топонимы, вопросы, продажи…);
   - ж) морфология: леммы, части речи, склонение.

   **R:** а, в, г, е и леммы из ж; затем б и д; склонение — в конце.
2. **Как сверять поведение с надстройкой?** Повторять её точно (эталонные примеры из Excel) или делать «как правильно»? **R:** как правильно, но для ключевых функций снять примеры из надстройки и сверить.

### B. Данные на входе и выходе
3. **Единица обработки:** колонка фраз (`Series`), к ней параметр `column=` для таблицы? **R:** да.
4. **Куда писать результат:** на место колонки или новой колонкой справа (как в надстройке)? **R:** по умолчанию новой колонкой `<column>_<operation>`, флаг — на место.
5. **Цепочки операций:** `semkit.pipe(df).remove_markers(...).dedupe(...)` или отдельные функции? **R:** отдельные функции плюс тонкий `pipe`.

### C. Текст
6. **Разбиение на слова:** только по пробелу (как VBA) или регулярным выражением (дефисы, цифры, пунктуация)? **R:** по умолчанию по пробелу, режим «игнорировать пунктуацию» — флагом (как Checkbox2 в надстройке).
7. **Нормализация:** регистр, ё→е, лишние пробелы — до сравнения всегда? **R:** при сравнении — да, исходный текст в выводе не трогать.
8. **Стоп-слова:** брать список из надстройки (`stopwords`) или из другого источника? **R:** из надстройки, плюс свой список параметром.

### D. Морфология и данные
9. **Как упаковать данные.** Excel-таблицы не держим, переводим в быстрые форматы. Замер на словаре лемм (845 тыс. словоформ):

   | Формат | Размер | Открытие | Поиск слова | Память |
   |---|---|---|---|---|
   | marisa-trie (mmap) | 5.8 МБ | мгновенно | 2.7 мкс | почти ноль |
   | gzip TSV → dict | 3.7 МБ | 0.4 с | 1.1 мкс | ~200 МБ |
   | SQLite | 37.8 МБ | мгновенно | 4.3 мкс | мало |

   **R:**
   - словарь лемм — marisa-trie: «словоформа → лемма, часть речи» и обратный «лемма → словоформы»; поверх — кэш уникальных слов;
   - маркеры (топонимы и др.) — сжатые списки, при загрузке строится автомат Aho-Corasick (`pyahocorasick`): одна проходка по фразе находит все маркеры сразу;
   - таблицы склонения — маленькие JSON или TSV в словари Python.
10. **Бэкенды:** SemtoolsDict по умолчанию, pymorphy3 и mystem — опционально? Bukvarix уже использует pymorphy3 — выравнивать с ним? **R:** SemtoolsDict по умолчанию, pymorphy3 — дополнением `[pymorphy]`, mystem не делать.
11. **Склонение по правилам листа `abc`:** переносить таблицы надстройки или склонять только через pymorphy3? **R:** переносить таблицы (быстро и без зависимостей), pymorphy3 — запасной вариант.
12. ~~Лицензия данных~~ — решено: semkit и dataio — частные закрытые инструменты, репозитории приватные.
13. **Обновление списков маркеров** (в надстройке их скачивают с semtools.guru): заморозить версию внутри пакета или дать команду обновления? **R:** заморозить; свои списки — параметром.

### E. Анализ
14. **Кластеризация:** по частотному словарю и по выдаче (вход — готовые URL топ-10)? Какой формат входа для выдачи? **R:** обе; выдача — таблица «фраза, позиция, url».
15. **Опечатки:** только расстояние Левенштейна или ещё что-то? **R:** только Левенштейн.

### F. Производительность и интерфейс
16. **Целевой объём:** до 1 млн фраз за минуты? **R:** да; если pandas не справится — векторизация, DuckDB.
17. **Команды CLI:** по группам ленты (`find`, `remove`, `extract`, `change`, `ngrams`, `dupes`, `basis`, `cluster`, `morph`)? Имена английские? **R:** да, английские.
18. **Antagor для semkit:** тоже без него? **R:** как для dataio.
19. **Импорт `rb_semkit`** (стандарт tools) или `semkit` для удобства в скриптах? **R:** `rb_semkit` по стандарту; при желании — алиас.

### Ответы Человека (2026-10-16)
Все **R** приняты, кроме:
- **10. Бэкенды:** свой словарь по умолчанию, pymorphy3 — дополнением `[pymorphy]`. mystem не берём.
- **11. Склонение:** режим `auto` по умолчанию: pymorphy3 установлен и знает слово → pymorphy3; иначе таблицы надстройки. Явные режимы `table` и `pymorphy`.
- **13 (POS `nv`, `prt`):** оставить как есть, отдавать коды без изменений, в справке — «значение неизвестно».
- **15. Опечатки:** Левенштейн; проверка орфографии — дополнением `[spell]`: LanguageTool на homeserver (план §3a) и локальный словарь для больших объёмов — выбор в проекте API.
- **17–19:** команда CLI — `semkit`.
- **18. Antagor:** используется (проект SEMKIT).

## Ход работы (обновлять в конце сессии)

**Сессия 3 (2026-10-16).** Человек решил: сначала детальное планирование, код — только после него.
- Готов `docs/plan.md`: дерево функций с этапами (v1 / v2 / later / out), каталог справочников D1–D17 (источник, строки, формат, загрузка, где используются), правила очистки, договор с dataio (4 вопроса), порядок работ.
- Блок A интервью закрыт порядком работ в `docs/plan.md` §4 — Человеку осталось подтвердить.
- Справочники собраны в каталог полностью: именованные диапазоны (из `xl/workbook.xml` в `.xlam`), три списка предлогов, транслит `InitDicts`, `SEMToolsWordProcessor.xlsb` (данных нет, это экран «Работы с ядром»).
- dataio разрабатывается параллельно; его агент — отдельная сессия Claude Code (в `ListAgents` — `dataio-…`). Договор с ним (§3 плана) согласован 2026-10-16.

**Дальше:**
1. Интервью, блоки B–F (вопросы 3–19 выше), ответы — сюда.
2. Проект API в `docs/plan.md`: модули, сигнатуры v1, общие параметры.
3. ~~Отправить агенту dataio вопросы §3~~ — согласовано, см. план §3.
4. Список эталонных примеров для снятия в Excel (снимает Человек).
5. Только потом: git init, `scripts/build_data.py`, код.
