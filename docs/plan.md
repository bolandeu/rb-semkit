# Plan: semkit

Draft. Built from `docs/brief.md`, `FEATURES.md`, `ribbon_menu.txt` (257 menu items) and the VBA.
Status of each line: **v1** = first version, **v2** = next, **later** = after the API settles, **out** = not ported.

## 1. Function tree

The add-in groups commands by *action* (find / remove / extract / change). semkit groups them by *object*
(chars, words, phrases, cells, dupes…), and each object gets the same verbs:
`find` → `bool` mask, `remove` → cleaned text, `extract` → found part. One matcher, three outputs.

### 1.1. Text core (`rb_semkit.text`)
| Object | Matchers | find | remove | extract | Phase |
|---|---|---|---|---|---|
| chars by type | latin, cyrillic, digits, letters+digits, punctuation, upper, UA | ✓ | ✓ | ✓ | v1 |
| spaces | all, left, right, both, extra | — | ✓ | — | v1 |
| chars by position | first/last N | — | ✓ | ✓ | v1 |
| around a pattern | before/after first/last occurrence, incl./excl. | — | ✓ | ✓ | v1 |
| regex | pattern; 1 match / all; match / NOT match | ✓ | ✓ | ✓ | v1 |
| ready patterns | domains, e-mails, RU phones, dates DDMMYYYY / YYYYMMDD | — | — | ✓ | v2 |
| whole words | 1 word, list (all / any; anywhere / start / end) | ✓ | ✓ | ✓ | v1 |
| words by content | starts / ends / contains pattern or pattern list; only-latin, has-latin, only-digits, has-digits, mixes | ✓ | ✓ | ✓ | v1 |
| words by case | lower, Capital, CAPS | ✓ | — | ✓ | v1 |
| words by position | first/last 1..N, N-th, up to middle, at most N | — | ✓ | ✓ | v1 |
| words by POS | noun, adj, verb, adverb | ✓ | ✓ | ✓ | v1 (needs lemmatizer) |
| word repeats | exact (all, en, ru, adjacent, numbers), by wordforms | ✓ | ✓ | — | v1 |
| stopwords | built-in + user list | — | ✓ | — | v1 |
| prepositions at phrase end, buy-markers at end | — | — | ✓ | — | v2 |
| phrases | user list (Aho-Corasick) | ✓ | ✓ | ✓ | v1 |
| prepositional complements («в Москве», «для детей») | — | — | — | ✓ | v2 |
| cells by content | contains / starts / ends with list item or preposition; regex; empty | ✓ | ✓ (row filter) | ✓ | v1 |
| cells by occurrence | unique, repeated, first, last | ✓ | ✓ | ✓ | v1 |

### 1.2. Markers (`rb_semkit.markers`) — v1
`find_markers / remove_markers / extract_markers(series, lists=[...], with_prepositions=False)`.
Lists: geo, mosmetro, districts, MO, citiesRu, questions, fun, DIY, edu, game, sale, rent, reviews,
color, material, origin, cars, names; plus user lists. Several lists in one pass. «Update lists» — out (frozen).

### 1.3. Duplicates (`rb_semkit.dupes`) — v1
| Kind | Rule |
|---|---|
| exact | equal strings |
| explicit | equal after normalization (case, ё→е, spaces) |
| implicit | equal word multiset (other word order) |
| implicit + wordforms | equal lemma multiset |
| vs. another column / table | same four kinds |

Modes: mark all except first / including first; remove; keep first.

### 1.4. Change (`rb_semkit.change`)
| Function | Phase |
|---|---|
| case: words, sentences, words with latin, list words, toponyms Capital, abbreviations (BMW, RGB) | v1 (abbr + toponyms need data) |
| insert text before/after each word, at start/end of cell | v1 |
| move word to start/end; replace word→word, list→list (keep or apply case); mass replace by substring / whole cell / regex | v1 |
| split text from digits; reverse chars / word order; sort words A–Z | v1 |
| quotes → «ёлочки» | v2 |
| translit ru→en, en→ru; ЧПУ translit (`chpuSym`) | v2 |
| phonetic en→ru («Dreamline → Дримлайн», `InitDicts` tables) | later |
| keyboard layout switch; similar chars cyr↔lat | v2 |
| match types: broad `+A`, `!A`, phrase `[A]`/`"A"`, exact, anti-semantic; drop modifiers on stopwords; drop minus-words | v2 |
| word order fix (`AdjToBeg`, `BKF/BKM/BKP`) | later |
| UTM: remove from URL, extract utm_* (string only, no network) | v2 |
| hashes md5 / sha256 | v2 |

### 1.5. Morphology (`rb_semkit.morph`)
| Function | Phase |
|---|---|
| `Lemmatizer` protocol; `SemtoolsLemmatizer` (dict + `lemmSuf` fallback + cache) | v1 |
| lemmatize words / phrases (unique-word map, then replace) | v1 |
| POS of a word (dict + verb endings + adj suffix rule) | v1 |
| all wordforms of a lemma (reverse trie) | v1 |
| decline nouns: 12 forms (`nounSuffixes`, `nounExclusions`, `nonDecl`) | v2 |
| decline adjectives: 16 forms (`adjSuffixes`, `adjExclusions`, `nounsLikeAdj`) | v2 |
| decline full names (`mSurn`, `fSurn`, `femSurSuf`, `names`) | later |
| `pymorphy3` backend, extra `[pymorphy]` | v2 |
| Mystem | out |

### 1.6. Analysis (`rb_semkit.analysis`)
| Function | Phase |
|---|---|
| n-gram frequency of words / lemmas, n = 1..N, count or sum by a weight column | v1 |
| bigrams ignoring word order (words / lemmas); bigrams without stopwords | v1 |
| word counts: words, chars per phrase; occurrence count, occurrence number, share of sum (cumulative), ABC | v1 |
| word permutations in a phrase; pairs from a list; linear combinations | v2 |
| parents (nearest, first) and children (first nested) | v2 |
| basis phrases | v2 |
| split the core by good / bad words (words or lemmas) → good, bad, rest + frequency of the rest | v2 |
| clustering by frequency dictionary | v2 |
| clustering by SERP top-10 (input table: phrase, position, url) | v2 |
| irrelevant-words search; synonym exclusion → minus-words | later |
| typos: is-typo, best correction (Levenshtein, `simScore`) | later |
| sentiment by user dictionary (mean / min / max) | later |
| conversion link matrix | later (needs spec) |

### 1.7. Out of scope
Excel-only (fonts, fill, borders, sheets, pictures, smart tables, formulas, connections, names, hotkeys, sudoku,
row/column ops, fill blanks, quick pivot, split sheet, merge files) — pandas/dataio do this.
Numbers (arithmetic, rounding, CBR rates, number to words). Network: URL parsing, response codes, suggests,
Yandex/Google APIs, XMLRiver, Pixel Tools, translation, LLM. Bukvarix → own package. CSV re-encode / ripgrep
samples → dataio. XML feed. License.

## 2. Reference data

All built by one script `scripts/build_data.py` from the sandbox sources into `src/rb_semkit/data/`.
The script is re-runnable; the built files are committed (private repo). Sources stay outside the repo.

| # | Data | Source | Rows | Package format | Load | Used by |
|---|---|---|---|---|---|---|
| D1 | wordform → lemma, POS | `reverse/data/lemms.tsv` | 845 374 | `lemmas.marisa` (`marisa_trie.BytesTrie`, value = `lemma\tpos`) | mmap | lemmatize, POS, dupes by wordforms, n-gram lemmas |
| D2 | lemma → wordforms | same, reversed | 170 430 lemmas | `forms.marisa` (`BytesTrie`, multi-value) | mmap | all wordforms, remove/find by wordforms |
| D3 | lemma fallback suffixes | `abc` E50:G305 `lemmSuf` | 256 | `morph.json` → dict | at import of `morph` | lemmatizer for unknown words |
| D4 | noun endings, 12 forms | `abc` Q1:AB3331 `nounSuffixes` | 3 331 | `decline.json` | lazy | noun declension |
| D5 | noun exclusions | `abc` Q3380:AB11089 `nounExclusions` | 7 710 | `decline.json` | lazy | noun declension |
| D6 | adj endings, 16 forms | `abc` AD2:AS90 `adjSuffixes` | 89 | `decline.json` | lazy | adj declension, POS of unknown words |
| D7 | adj exclusions | `abc` AD93:AS136 `adjExclusions` | 44 | `decline.json` | lazy | adj declension |
| D8 | feminine surname suffixes | `abc` AD140:AI163 `femSurSuf` | 24 | `decline.json` | lazy | full-name declension |
| D9 | indeclinable words | `abc` B1:B1205 `nonDecl` | 1 205 | `decline.json` | lazy | declension |
| D10 | nouns that look like adj | `abc` J1:J417 `nounsLikeAdj` | 417 | `morph.json` | lazy | POS rule |
| D11 | abbreviations | `abc` M1:M1016 `abbrs` | 1 016 | `lists.json` | lazy | case: BMW, RGB |
| D12 | ЧПУ symbols | `abc` E10000:F10965 `chpuSym` | 966 | `translit.json` | lazy | ЧПУ translit |
| D13 | stopwords | VBA `Function stopwords` (string literal) | ~700 | `lists.json` | lazy | stopwords, n-grams, bigrams |
| D14 | words moved to phrase start (`где`, `купить`, `недорогой`, `готовый`…) | `abc` BA1:BA644 `charsPat` | 644 | `lists.json` | lazy | word order fix (`moveToBeg`) |
| D15 | 18 marker lists | `reverse/downloads/spiski/*.xlsx` (1 column, `cars` — 6) | 59 k total, geo 36 k | `markers/<name>.txt.gz` (one phrase per line) | lazy; Aho-Corasick built on first use, cached per list | markers |
| D16 | phonetic translit tables en→ru: whole words, suffixes (5–2 letters), prefixes (5–2), any n-grams (5–1) | VBA `InitDicts` (string literals, 14 pairs of lists) | 701 pairs (words 65) | `translit.json` | lazy | Dreamline → Дримлайн (later) |
| D17 | surname rules `mSurn` / `fSurn` | VBA functions (code, not data) | — | code | — | full names (later) |

Named ranges come from `xl/workbook.xml` of `!SEMToolsPro.xlam` (32 names). Not data: `BSR` (abc K1:K54) and
sheet `ggg` (marker cache, empty in the .xlam — the lists come from `spiski/`).

Lists D11, D13, D14 and the prepositions below go to one `lists.json`, keyed by name.

Prepositions are string literals in `RibbonCallbacks.vba`, two lists (→ `lists.json`):
- `prps()` (line 1322), 52 items: prepositions plus the conjunctions «а», «и», «или», «но». Used for cells
  starting / ending with a preposition, removing prepositions at the end, extracting prepositions. Junk to fix:
  «g» (stray latin) and «пo» (latin «o» inside).
- `preps` (inside the complements extractor), 17 items: «для с в из на к со о во у по под от после за над»;
  a second copy also has «без». Used to find prepositional complements («в Москве»).
- toponym prepositions (inside «remove / extract toponyms with prepositions»): ru «в во на по из до г и»,
  en «in at by to». The word before a toponym is removed with it when it is in this list.

`downloads/SEMToolsWordProcessor.xlsb` holds no reference data. It is the UI of «Работа с семантическим ядром»:
sheet `semHelper` (core phrases, frequency dictionary, plus-words, lemma map), sheets `Good case` / `Bad case`.
The user marks a word of the frequency dictionary as good or bad; phrases with it move to that sheet, the
dictionary is recounted. In semkit this is a function, not a UI: `split_by_words(phrases, good=, bad=,
lemmatizer=)` → good / bad / rest, plus the frequency dictionary of the rest (v2, section 1.6). `downloads/SEMToolsWordProcessor.xlsb`: a helper workbook with its own VBA,
to inspect before build.

Cleaning rules the build script applies (found in the sources):
- D1: drop header and junk rows (e.g. `0,0000001  1e-07  фыва`), empty POS, rare POS `nv`, `prt` → decide (see Q-D);
  lower-case, ё kept in source and a ё→е key added.
- D15: drop the 2nd sheet in `DIY.xlsx` (Google Sheets formula junk); `cars.xlsx` — take column A only
  (B..F is a brand table: ru, en); strip, dedupe, keep case for display, match case-insensitive.
- `abc` ranges: read by the cell addresses above from `sheet_abc.tsv`; empty cells dropped.

Size estimate: D1+D2 ≈ 10 MB, the rest < 1 MB.

Checks after build (`tests/test_data.py`): row counts per file, 20 known lookups
(«москве → москва n», «купила → купить v»), every marker list loads and matches its own first item.

## 3. Interface with dataio

semkit takes and returns `pandas.Series` / `DataFrame`; it never reads files. The CLI (later) calls dataio for
input and output. Agreed with the dataio agent on 2026-10-16 (checked against dataio v0.1.21):
1. **API.** `rb_dataio.read(source, *, format, sheet, table, encoding, sep, header, credentials, as_text,
   dtypes, limit, query, source_column="_source", strict) -> DataFrame`;
   `rb_dataio.write(frame, target, *, format, sheet, …, mode="replace", overwrite, backup, dry_run, …)`.
   Errors: `rb_dataio.DataioError` (has `.action`) — the semkit CLI maps it to a `CliError`.
2. **Dependency.** Optional extra `[io]`, library use needs no dataio. Pin:
   `rb-dataio = { git = "https://github.com/bolandeu/rb-dataio.git", tag = "v0.1.21" }`.
3. **Types.** `read` infers types by default ("5" → Int64, dates → datetime). semkit CLI reads with
   `as_text=True` (or `dtypes={"<col>": "str"}`). Empty cells stay NaN: **semkit does `fillna("")`** itself,
   in the library too (any Series it gets). No `columns=`; select with `query="SELECT phrase FROM data"`.
4. **Pipes.** The dataio CLI is `dataio convert SRC DST` (no `read`/`write` commands). Stdin auto-detects
   JSON, JSONL, CSV or txt; stdout is CSV, or JSONL with `--out-format jsonl`. semkit stream format: **JSONL**
   on stdin/stdout. Parquet is not supported on pipes: for 1M+ rows pass a `.parquet` file path. Parquet on
   pipes would be a new dataio idea, not requested yet.
   Example: `dataio convert x.xlsx - --out-format jsonl | semkit dupes - | dataio convert - out.csv`.

## 3a. Spelling server (optional extra, from sysadmin 2026-10-16)

Typos: Levenshtein in the library; spelling check through LanguageTool on homeserver as an optional provider.
- LanguageTool 6.8, `https://homeserver.tailee01ab.ts.net:8010`, tailnet only, no auth. Owner: sysadmin.
  Docs: `~/Work/sysadmin/docs/services.md` «LanguageTool».
- `POST /v2/check`, form: `language=ru-RU`, `text=<one phrase per line>`,
  `enabledRules=MORFOLOGIK_RULE_RU_RU&enabledOnly=true`. Response `matches[]` (offset, length,
  `replacements[].value`, `rule.id`); semkit maps offsets back to lines.
- Started on demand: cold start ~15 s → client timeout ≥ 60 s.
- Limits: batches of ~1000 lines, at most 2 parallel requests, retry with backoff on 5xx/timeouts
  (`HttpProvider` does it). 1000 phrases ≈ 5 s → 1M ≈ 80+ min.
- Do not rely on a version bump (sitegen pins it). More throughput → a ticket to sysadmin with volume and frequency.
- Open: for 1M phrases a local dictionary check (hunspell-style) may be much faster; decide in the API design.

## 4. Work order

0. git init, this plan accepted, interview blocks B–F answered.
1. Data: `build_data.py` → D1–D15, data tests.
2. `morph`: Lemmatizer protocol, SemtoolsLemmatizer, POS, wordforms.
3. `text` core: tokenizer, normalizer, matchers, find/remove/extract over Series.
4. `markers`, `dupes`.
5. `analysis`: n-grams, bigrams, counts.
6. Reference examples from the add-in for key functions; compare.
7. v2 block; then CLI.

## 5. Open questions (interview)
Block A answered by this plan (order above) — confirm. Blocks B–F of the brief are still open.
Extra:
- Q-D: POS codes `nv` (3 rows), `prt` (1 row) — drop or keep?
- Q-D: built data in git (private) or built at install? **R:** in git.
