---
id: SEMKIT-007
title: 'Markers and phrase lists: extract the longest match'
status: queue
attempts: 3
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
- src/rb_semkit/core/markers/
- src/rb_semkit/core/text/matchers/phrases.py
test_paths:
- tests/markers/
- tests/matchers/
- tests/matchers_vba/
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
review: true
depends_on: []
budget_usd: null
epic: E-001
spec_refs: []
checks:
- uv run pytest tests/markers tests/matchers tests/matchers_vba -q --no-cov
resident: null
tool: null
pr: null
translation: 'Маркеры и списки фраз: извлекать самое длинное совпадение («как сделать»,
  а не «как»), при равной длине — порядок списка; find/remove на тех же участках.
  Отход от VBA la— записан в ADR 0005.'
---

The marker extraction follows the VBA `la—` (docs/vba/matchers.md S10): for each word that starts a list item it takes the first item, in list order, that the phrase holds, so a short item hides a longer one: questions on 'как сделать диван своими руками' gives 'как', not 'как сделать'. ADR 0005 now asks for the longest match.

1. For each word that starts one or more items, take the longest item (in words, then in characters) that the phrase holds from that word; a tie keeps the list order.
2. Matched words are consumed: a later word inside a taken item does not start another one.
3. The same rule for sk.markers (every list, with_prepositions too) and sk.phrases extract; find and remove give the same spans.
4. Update the docstrings (the ADR 0005 line) and the rows of tests/matchers_vba that change, with the VBA value in a comment.

## Acceptance

- Given the questions list and 'как сделать диван своими руками', When sk.extract with sk.markers('questions'), Then the result is 'как сделать' [check: tests/markers/test_longest.py]
- Given sk.phrases(['нижний', 'нижний новгород']) and 'купить диван нижний новгород', When extract, Then 'нижний новгород'; When remove, Then 'купить диван' [check: tests/markers/test_longest.py]
- Given two items of equal length from one word, When extract, Then the one earlier in the list [check: tests/markers/test_longest.py]

## How to test

Public library seam (import rb_semkit as sk): pytest cases in tests/markers/test_longest.py with the bundled lists.

## Basis

docs/vba/matchers.md S10 (la—, DeletePhrases), ADR 0005, the SEMKIT-005 code of core/markers/matcher.py and phrases.py.

## Read first

- `docs/adr/0005-port-vba-fix-defects.md`
- `docs/vba/matchers.md`

## Out of scope

- Other matchers; the marker lists themselves.

## Feedback

### Attempt 1: checks failed

- `uv run pytest tests/markers tests/matchers tests/matchers_vba -q` (exit 4)

```
no tests ran in 0.00s
ERROR: file or directory not found: tests/matchers_vba
```

### Answer to question #1

> Branch antagor/SEMKIT-007 starts from main, which lacks the SEMKIT-005 work (status publish, not merged): no tests/matchers_vba, and markers/matcher.py is the pre-005 code, so the check cannot pass and the task would change the wrong code.
> Question: How does SEMKIT-007 get the SEMKIT-005 code?
> Options:
> 1. Publish SEMKIT-005 first, then restart SEMKIT-007 from the new main (add depends_on: SEMKIT-005)
> 2. Merge antagor/SEMKIT-005 into antagor/SEMKIT-007 now, then the worker continues
> 3. Drop tests/matchers_vba from the checks and work on the pre-005 code
> Recommended: Publish SEMKIT-005 first, then restart SEMKIT-007 from the new main (add depends_on: SEMKIT-005)

Option 2. SEMKIT-005 is accepted (status publish) but not on main yet: its publish waits for the Human. Merge its branch into yours now: git merge --no-edit antagor/SEMKIT-005 (no rebase, no force), then continue; the code and tests of SEMKIT-005 (tests/matchers_vba, core/markers/matcher.py, matchers, lemmatizer looks_like_adjective) are the base. Do not edit the SEMKIT-005 files outside your owns.

### Blocked: scope_held (holders ['SEMKIT-005'], paths ['docs/plan.md', 'src/rb_semkit/core/morph/lemmatizer.py', 'src/rb_semkit/core/text/matchers/around.py', 'src/rb_semkit/core/text/matchers/cells.py', 'src/rb_semkit/core/text/matchers/chars.py', 'src/rb_semkit/core/text/matchers/classes.py', 'src/rb_semkit/core/text/matchers/pos.py', 'src/rb_semkit/core/text/matchers/positions.py', 'src/rb_semkit/core/text/matchers/regex.py', 'src/rb_semkit/core/text/matchers/repeats.py', 'src/rb_semkit/core/text/matchers/spaces.py', 'src/rb_semkit/core/text/matchers/stopwords.py', 'src/rb_semkit/core/text/matchers/word_case.py', 'src/rb_semkit/core/text/matchers/word_content.py', 'src/rb_semkit/core/text/matchers/word_position.py', 'src/rb_semkit/core/text/matchers/words.py'])

### Attempt 2: file docstring

- update the docstring of src/rb_semkit/core/text/matchers/phrases.py: +longest

### Attempt 3: checks failed

- `uv run pytest tests/markers tests/matchers tests/matchers_vba -q` (exit 1)

```
7
src/rb_semkit/core/data_files.py                 8      8     0%   8-20
src/rb_semkit/core/deps.py                      88     88     0%   14-166
src/rb_semkit/core/dupes/__init__.py             2      2     0%   3-5
src/rb_semkit/core/dupes/functions.py           43     43     0%   6-81
src/rb_semkit/core/errors.py                    73     33    55%   44-47, 52, 62, 72-73, 98-109, 124, 141-148, 151-155, 160, 170, 181, 193, 208
src/rb_semkit/core/frame.py                     61     11    82%   25, 40, 47-48, 50, 56, 58, 60, 79, 83, 93
src/rb_semkit/core/models.py                    14     14     0%   1-23
src/rb_semkit/core/morph/functions.py           19      8    58%   23-27, 40, 51, 56
src/rb_semkit/core/morph/lemmatizer.py          55      4    93%   68-69, 93, 122
src/rb_semkit/core/normalize.py                 20     11    45%   34-40, 49-52
src/rb_semkit/core/opencli.py                  141    141     0%   18-256
src/rb_semkit/core/services.py                  44     44     0%   1-78
src/rb_semkit/core/text/base.py                 84      8    90%   33, 106, 124, 160, 163, 166, 169, 174
src/rb_semkit/core/text/matchers/around.py      39      1    97%   26
src/rb_semkit/core/text/matchers/cells.py       73      2    97%   30, 43
src/rb_semkit/core/text/matchers/spans.py       22      2    91%   19, 22
src/rb_semkit/core/text/matchers/words.py       34      1    97%   39
src/rb_semkit/core/version.py                   40     18    55%   20-22, 32-35, 52-53, 57, 62-65, 75-78
src/rb_semkit/output/__init__.py                94     94     0%   1-224
src/rb_semkit/output/human.py                   18     18     0%   1-32
src/rb_semkit/output/json.py                     5      5     0%   1-9
--------------------------------------------------------------------------
TOTAL                                         1758    906    48%

23 files skipped due to complete coverage.
FAIL Required test coverage of 90.0% not reached. Total coverage: 48.46%
318 passed in 3.16s
```

### Blocked: attempts (max_attempts 3)
