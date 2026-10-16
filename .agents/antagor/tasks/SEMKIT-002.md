---
id: SEMKIT-002
title: 'Text matchers and marker lists: every v1 find/remove/extract'
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
- src/rb_semkit/core/text/matchers/
- src/rb_semkit/core/markers/
- src/rb_semkit/data/markers/
- scripts/build_markers.py
- .gitattributes
- docs/plan.md
- pyproject.toml
- scripts/build_data.py
- scripts/build_data.toml
- src/rb_semkit/core/frame.py
- src/rb_semkit/core/text/base.py
- uv.lock
test_paths:
- tests/matchers/
- tests/markers/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-001
budget_usd: null
epic: E-001
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: 'Шаблоны текста и списки маркеров: все find/remove/extract v1. На каркасе
  ядра — все шаблоны v1 из плана §1.1 (символы, пробелы, позиции, вокруг шаблона,
  regex, слова по содержанию, регистру, позиции, части речи, повторы, стоп-слова,
  свой список фраз, ячейки по содержанию и вхождению) и 18 встроенных списков маркеров
  со сборкой из xlsx песочницы, автомат Aho-Corasick при первом использовании. Неподдерживаемый
  глагол — InvalidArguments со списком допустимых.'
---

All v1 matchers of the text core and the 18 bundled marker lists, on the frame and the three verbs of the core task. Each matcher works with find (bool mask), remove (cleaned text) and extract (found part) where the plan (§1.1) marks the verb; a verb the matcher does not support raises InvalidArguments naming the supported ones.

Matchers: chars (latin, cyrillic, digits, letters+digits, punctuation, upper, UA); spaces (all, left, right, both, extra); positions (first/last N chars); around (before/after the first/last occurrence of a pattern, incl./excl.); regex (one / all matches; match / NOT match); word_content (starts / ends / contains a pattern or list; only-latin, has-latin, only-digits, has-digits, mixed); word_case (lower, Capital, CAPS); word_position (first/last 1..N, N-th, up to the middle, at most N); pos (noun, adj, verb, adverb, through a Lemmatizer); repeats (exact: all, en, ru, adjacent, numbers; by wordforms); stopwords (bundled list + user list); phrases (user list, Aho-Corasick); cells (contains / starts / ends with a list item or a preposition; regex; empty; unique / repeated / first / last occurrence; remove filters rows); markers (lists by name, several in one pass, user lists; with_prepositions takes the toponym preposition before a marker).

Marker data: a build script reads the 18 xlsx of the sandbox (the brief, «Materials»), drops the 2nd sheet of DIY, takes column A of cars, strips and dedupes, keeps the display case, and writes compressed one-phrase-per-line files. The Aho-Corasick automaton is built on first use per list, thread-safe, cached.

Add a .gitattributes at the repo root that marks all built data as generated (src/rb_semkit/data/morph/**, data/lists/**, data/markers/** with linguist-generated), with a one-line comment naming the build scripts and ADR 0002: Antagor then counts these files by number, not by lines.

## Acceptance

- Given pd.Series(['Купить iPhone 15 в Москве']), When sk.extract with chars('latin'), chars('digits'), regex(r'\d+'), word_case('Capital'), word_position(first=1) run, Then they give 'iPhone', '15', '15', 'Купить Москве', 'Купить'; find gives True for each [check: tests/matchers/test_extract.py]
- Given pd.Series(['  купить  диван  в  москве ']), When sk.remove with spaces('extra'), stopwords(), around('в', after=True, include=True) run, Then they give 'купить диван в москве', 'купить диван москве' (spaces collapsed), 'купить диван' [check: tests/matchers/test_remove.py]
- Given pd.Series(['диван диван угловой', 'стол столы']), When find with repeats('exact') and repeats('wordforms') runs, Then exact gives [True, False] and wordforms gives [True, True] [check: tests/matchers/test_repeats.py]
- Given pd.Series(['красный диван', 'быстро купить']), When sk.extract(s, sk.pos('adj')) runs with the bundled lemmatizer, Then it gives ['красный', '']; with a fake lemmatizer it follows the fake [check: tests/matchers/test_pos.py]
- Given pd.Series(['диван', 'стол', 'диван', '']), When sk.find with cells('repeated'), cells('first'), cells('empty') runs, Then they give [True, False, True, False], [True, True, False, True], [False, False, False, True]; sk.remove(s, cells('empty')) drops the empty row [check: tests/matchers/test_cells.py]
- Given pd.Series(['диван в москве у метро таганская', 'диван купить']), When sk.extract(s, sk.markers(['geo', 'mosmetro'])) runs, Then it gives the markers spelled as the list spells them (not as the phrase does: geo gives 'Москве', and 'спб' gives 'СПб'), joined by ', ' in phrase order (sep= changes the separator), and '' for the second phrase; remove with with_prepositions=True gives ['диван у метро', 'диван купить']; matching is case-insensitive [check: tests/markers/test_markers.py]
- Given a user list ['угловой диван'] and an unknown list name 'nope', When markers/phrases run, Then the user list matches whole words only (not inside 'угловойдиван'); 'nope' raises InvalidArguments listing the 18 list names [check: tests/markers/test_markers.py]
- Given a regex '(', an unsupported verb (e.g. find with spaces), or N < 1, When called, Then InvalidArguments names the argument and the allowed values [check: tests/matchers/test_errors.py]
- Given the sandbox spiski folder, When the marker build runs twice, Then the files are byte-identical and all 18 lists load and match their own first item; a missing xlsx exits non-zero naming it [check: tests/markers/test_build_markers.py]

## How to test

Public library seam: import rb_semkit as sk, small Series in, exact Series out, index kept. Lemmatizer protocol with a fake for pos and repeats by wordforms. Build script on the sandbox sources (skip with a reason only when the sandbox is absent).

## Basis

Reuse the core task's frame, Matcher protocol, verbs, tokenizer, norm_phrase and lazy data loader; do not duplicate them. Plan §1.1, §1.2, §2 (D15 cleaning rules, preposition lists); pyahocorasick for phrases and markers; ADR 0004.

## Read first

- docs/plan.md
- CONTEXT.md
- docs/adr/0004-matcher-and-three-verbs.md

## Out of scope

- v2 patterns (domains, e-mails, phones, dates), prepositions at phrase end, prepositional complements, change functions (case, replace, insert, move).
- Updating marker lists from the network; dupes and n-grams (other blocks); CLI.

## Feedback

### Answer to question #1

> Acceptance 1 says sk.find gives True for word_position(first=1); plan 1.1 marks find for words-by-position as '—' (remove and extract only).
> Question: Which point wins for find on word_position?
> Options:
> 1. Acceptance: word_position supports find (True where the phrase has the chosen words)
> 2. Plan 1.1: word_position raises InvalidArguments on find
> Recommended: Acceptance: word_position supports find (True where the phrase has the chosen words)

Option 1: the acceptance wins. word_position supports find: True where the phrase has the chosen words (e.g. first=1 is True for any non-empty phrase, at_most=N is True where the phrase has at most N words). Update the words-by-position row of plan §1.1 to mark find ✓ (docs/plan.md is in your owns now).

### Blocked: needs_scope (entries [{'n': 1, 'text': "Acceptance 1 says sk.find gives True for word_position(first=1); plan 1.1 marks find for words-by-position as '—' (remove and extract only).\nQuestion: Which point wins for find on word_position?\nOptio"}])

### Attempt 1: file docstring

- update the docstring of src/rb_semkit/core/text/base.py: +bundled_list +choice +collapse +compiled +strip_edges +whole_number +word_list
