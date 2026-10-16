---
id: SEMKIT-001
title: 'Core: bundled dictionary, lemmatizer and the find/remove/extract frame'
status: queue
attempts: 1
blocked: false
blocked_reason: null
phase: null
tests_hash: null
publish_stage: null
created_by: architect
approved_by: human
worker: claude-code
type: feature
owns_paths:
- src/rb_semkit/__init__.py
- src/rb_semkit/core/frame.py
- src/rb_semkit/core/text/__init__.py
- src/rb_semkit/core/text/base.py
- src/rb_semkit/core/morph/
- src/rb_semkit/core/datastore.py
- src/rb_semkit/data/morph/
- src/rb_semkit/data/lists/
- scripts/build_data.py
- README.md
- pyproject.toml
- scripts/build_data.toml
- src/rb_semkit/core/text/matchers/__init__.py
- src/rb_semkit/core/text/matchers/words.py
- uv.lock
test_paths:
- tests/core/
docs:
- README.md
tools: []
worker_args: null
class: hard
decision: false
visual: null
depends_on: []
budget_usd: null
epic: E-001
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Ядро: встроенный словарь, лемматизатор и каркас find/remove/extract.
  После задачи работает import rb_semkit as sk: леммы, части речи, словоформы на словаре
  надстройки и find/remove/extract с шаблоном words над Series или колонкой таблицы.
  Задача фиксирует контракт для трёх параллельных блоков: корень пакета отдаёт все
  имена v1 через ленивую карту «имя → модуль». Состав: скрипт сборки данных (леммы,
  суффиксы, таблицы склонения, списки стоп-слов и предлогов; без маркеров), ленивая
  потокобезопасная загрузка, протокол Lemmatizer и SemtoolsLemmatizer, каркас ввода-вывода
  (NaN, column=, новая колонка, inplace, InvalidArguments), токенизатор и norm_phrase,
  протокол шаблона и три глагола, pipe, раздел README.'
---

The thin end-to-end path of the library. After this task `import rb_semkit as sk` works: sk.lemmatize / sk.part_of_speech / sk.wordforms on the bundled !SEMTools dictionary, and sk.find / sk.remove / sk.extract with one matcher, sk.words([...]), over a Series or a DataFrame column. It also fixes the public contract the three parallel blocks fill in: the root package exposes every v1 name through a lazy name → module map (matchers chars, spaces, positions, around, regex, word_content, word_case, word_position, pos, repeats, stopwords, phrases, cells, markers; dupes; ngrams, bigrams, counts); a name whose module does not exist yet raises AttributeError naming it.

Parts:
1. Data build script (re-runnable, sources read from the sandbox paths in docs/brief.md «Materials»): lemma tries (wordform → lemma+POS, lemma → wordforms, ё→е key added, junk rows dropped, POS nv/prt kept), lemmSuf fallback, nounsLikeAdj, declension tables (built, not used yet), lists (stopwords, three preposition lists with the junk «g», «пo» fixed, abbreviations, charsPat). Marker lists are NOT built here.
2. Lazy, thread-safe data loading: mmap tries, loaded once.
3. Lemmatizer protocol (lemma, pos, forms) and SemtoolsLemmatizer: the !SEMTools dictionary first; a word not in it goes to pymorphy3 (a regular dependency, not an extra); a word pymorphy3 does not know either gets the lemmSuf suffix fallback; lemmas are returned in lower case; a unique-word cache; POS rules from the add-in (verb endings -тся, -ться, -ают, -уют; adjective by adjSuffixes unless in nounsLikeAdj).
4. Frame: input Series or DataFrame + column=; NaN → empty string at entry; output Series with the input index, or the DataFrame with a new column <column>_<operation> to the right, inplace replaces; wrong input raises InvalidArguments naming the argument and allowed values.
5. Tokenizer (split on any run of whitespace, so double spaces never produce empty words; results never contain double spaces; ignore_punct flag) and comparison via the template's norm_phrase; output text keeps its original form.
6. Matcher protocol and the three verbs (ADR 0004); the words matcher (one word or a list; all / any; anywhere / start / end); a thin pipe(df, column) chaining verbs.
7. README: a short library usage section.

## Acceptance

- Given the built data, When sk.lemmatize(pd.Series(['москве', 'купила'])) runs, Then it returns ['москва', 'купить'] with the same index; sk.part_of_speech gives ['n', 'v']; 'москве' is in sk.wordforms('москва') [check: tests/core/test_morph.py]
- Given a word not in the !SEMTools dictionary but known to pymorphy3, When it is lemmatized, Then pymorphy3's normal form is returned; a nonsense word unknown to both (e.g. 'зюзюкалками') gets the lemmSuf fallback; no error is raised; 'Москве' gives 'москва' (lower case) [check: tests/core/test_morph.py]
- Given a fake Lemmatizer with two entries, When a lemma-dependent function gets lemmatizer=fake, Then it uses only the fake; with lemmatizer=None a lemma-optional function works on words as they are [check: tests/core/test_morph.py]
- Given pd.Series(['купить диван', 'Диван бу', None]), When sk.find(s, sk.words(['диван'])) / sk.remove(...) / sk.extract(...) run, Then find gives [True, True, False], remove gives ['купить', 'бу', ''], extract gives ['диван', 'Диван', '']; matching is case- and ё-insensitive, output keeps the original case [check: tests/core/test_frame.py]
- Given a DataFrame with column 'phrase', When sk.remove(df, sk.words(['бу']), column='phrase') runs, Then df gets a new column 'phrase_remove' right after 'phrase' and 'phrase' is unchanged; with inplace=True 'phrase' is replaced [check: tests/core/test_frame.py]
- Given column='nope', a numeric column, or words([]), When a verb is called, Then InvalidArguments is raised naming the argument and the allowed values, and the input is not changed [check: tests/core/test_frame.py]
- Given 8 threads calling sk.lemmatize at once on first use, When the data loads, Then all results are correct and the loader ran once [check: tests/core/test_datastore.py]
- Given the sandbox sources, When the build script runs twice, Then the produced files are byte-identical; with a source path missing it exits non-zero naming the file; row counts and 20 known lookups match [check: tests/core/test_build_data.py]
- Given the root package, When a name of a later block (e.g. sk.dupes) is accessed before its module exists, Then AttributeError names it; every name of the core resolves [check: tests/core/test_api.py]

## How to test

Unit and integration at the public library seam (import rb_semkit, small Series/DataFrames), the Lemmatizer protocol with a fake, and the build script run on the sandbox sources (skip with a clear reason only when the sandbox is absent, e.g. in CI).

## Basis

docs/plan.md §1, §2 (data catalog D1–D14, cleaning rules), §3; ADR 0002, 0003, 0004; template core/normalize.py norm_phrase and core/errors.py InvalidArguments; marisa-trie BytesTrie measured in docs/brief.md.

## Read first

- `docs/plan.md`
- `docs/brief.md`
- `CONTEXT.md`
- `src/rb_semkit/core/normalize.py`
- `src/rb_semkit/core/errors.py`

## Out of scope

- Other matchers, marker lists and their build, dupes, n-grams, the benchmark (the three blocks).
- Declension functions (v2; pymorphy3 here is only the lemma fallback); CLI commands and dataio (next epic).

## Feedback

### Blocked: diff_too_large (lines 162055 > 4000)

diff_too_large came from generated data, not code (decline.json 158k lines, lists.json 2.2k, morph.json 0.7k). Decision: (1) do NOT build the declension tables now — remove decline.json and its build step; declension is v2 and will build its own data. (2) Write every generated JSON compact: json.dumps(..., ensure_ascii=False, separators=(',', ':'), sort_keys=True) on one line, so the data files add a few lines each; keep the build byte-reproducible. Binary .marisa files are fine as they are. Keep the rest of the work.

### Attempt 1: the Architect's verdict

The review found blockers; close each:

- [blocker] C11 docs/plan.md: the diff stops building the declension tables (feedback: "do NOT build the declension tables now — remove decline.json and its build step"), but the data catalog §2 still lists D4–D9 with package format `decline.json`, load «lazy». Nothing in `src/rb_semkit/data/` holds them. A reader of the plan expects files that do not exist. Mark D4–D9 as «not built in v1; v2 builds its own data», or move them out of the catalog table. The same table says D3 loads «at import of `morph`»; the code loads it lazily through `datastore.table` (`core/morph/lemmatizer.py`). D13 says «~700» stopwords; `lists.json` holds 439 (unchecked whether the source has more or the build dedupes; the plan or the build should say which).

Minor remarks of the review: optional, if they do not widen the task:

- [minor] C3 src/rb_semkit/core/morph/lemmatizer.py: `_ye()` repeats the ё→е rule of `norm_phrase` (core/normalize.py) and of `yo_to_ye` in scripts/build_data.py. A script may not import the package, so the script copy is fine; the package copy should reuse `norm_phrase` or one shared helper.
- [minor] C7 src/rb_semkit/core/morph/lemmatizer.py: `VERB_ENDINGS`, `NOT_VERBS` and `PYMORPHY_POS` are rule lists in code. They are add-in rules, not tunable values, so this is a judgement call; the build could ship them in `morph.json` with the other add-in tables.
- [minor] C7 scripts/build_data.toml: the source paths are absolute paths of one machine (`/Users/bolandau/...`). This is settings, as C7 asks, and the tests skip when the sandbox is absent. Allow an env var or a CLI override later if the build must run elsewhere.
- [minor] C5 src/rb_semkit/core/frame.py: `Frame.put` changes the caller's DataFrame in place also when `inplace=False` (it adds the column to the input object). It matches the acceptance wording, but the docstring of `put`/README should say it.
- [minor] [extra] none beyond the task: `Pipe.find` returns a Series and ends the chain, which the task's «thin pipe(df, column) chaining verbs» allows.
- [minor] [wrong] the adjective POS rule runs only in the suffix fallback (`_from_suffixes`); a word found in the dictionary or in pymorphy3 keeps its source POS. The task line is «POS rules from the add-in (verb endings …; adjective by adjSuffixes unless in nounsLikeAdj)». The test `test_pos_rules_of_the_add_in` only covers unknown words. Confirm that the add-in applies the adjective rule to unknown words only.
- [minor] [missing] «Given the sandbox sources … row counts and 20 known lookups match» — `KNOWN_LEMMAS` + `KNOWN_FORMS` give 17 lookups, not 20 (the count may include the list and morph lookups at the end of `test_known_lookups`; unchecked).

### Attempt 1 (not counted): main moved and conflicts with the work

`main` changed since your work began, and merging it conflicts in:

- `docs/plan.md`

Merge it into your branch (`git merge main`), resolve each file keeping both behaviours, `git add` it and run the checks; do not commit: Antagor commits the merge with your work when the round ends (IDEA-201).
