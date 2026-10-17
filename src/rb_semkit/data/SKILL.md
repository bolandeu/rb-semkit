---
name: semkit
description: Drive the semkit CLI from an agent — one pipeline command that reads a semantic core or a text, runs library steps (clean, lemmas, n-grams, comparison, SERP clusters) and writes the table. Invoke when a task processes search phrases or SEO texts.
---

# semkit

semkit processes a semantic core (a list of search phrases) and SEO texts. The whole library runs from one command:
a pipeline of steps. `semkit --ai` prints this guide followed by every step with its kind and a one-line summary;
`semkit read IN STEP --help` shows one step with its options and an example.

## Install (if `semkit --version` fails)

```bash
uv tool install "rb-semkit @ git+https://github.com/bolandeu/rb-semkit.git@vX.Y.Z"
```

Replace `vX.Y.Z` with the latest release tag (install from a tag, never a branch). On an auth error run
`gh auth status`; if it passes, `gh auth setup-git` and retry; if not, ask the user to run `gh auth login`.

## The pipeline

    semkit [--json] [--quiet] [--dry-run] read IN [--column C] [--whole] [--trace FILE] STEP… write OUT [--overwrite]

- `IN` is a file of any format dataio reads (csv, xlsx, json, jsonl, parquet, txt…), or `-` for JSONL on stdin (CSV on
  stdin is refused: give its path). `OUT` is a file (its format by the extension), or `-` for JSONL on stdout. stdout
  holds data only; the summary and the errors go to stderr. A closed stdout (`| head`) ends quietly with exit 0.
- Columns keep the types of the file: numbers stay numbers, a text column is text (an empty cell is an empty text). A
  column of numbers with spaces around a cell is numbers too. The steps work on one column, the working column:
  `--column C`, by default the first text column; a column of numbers picked as the working column is text for the
  step and is written back as numbers. A text file read with `--whole` is one cell of the column `text` (an article).
- Steps run in the order written. After each one a line goes to stderr: the step, the rows before and after, the cells
  changed; the last line says how many rows were written and where (or that it was a dry run). Every step, every
  option, every file an option names and OUT are checked before the input is read: a wrong value is refused with
  exit 2, naming the step, the option and what to do.
- `write` comes once, last. An existing `OUT` is refused (exit 2, `OUTPUT_EXISTS`) unless `write OUT --overwrite`.
  The file is written whole or not at all.
- `--dry-run` runs every step and prints the summary, but writes nothing. `--trace FILE` writes every changed cell and
  every dropped row to FILE as JSONL (row, step, column, before, after; row 1 is the first row under the header): use
  it to see what a step did. An existing trace FILE is refused unless `write OUT --overwrite`.
- `--json`, `--quiet` and `--dry-run` go before the steps (`semkit --json read …`). With `--json` and a file OUT,
  stdout is one envelope `{"ok": true, "output", "rows", "written", "steps"}` (`steps`: one `{"step", "rows_before",
  "rows_after", "cells_changed"}` per step); with `write -` stdout is the JSONL of the rows. `--quiet` hides the lines
  on stderr, never the result.

## Step kinds

`semkit describe --json` gives each step its kind (`x-rb-kind`) and each option its accepted values.

- **change** — rewrites the working column (`chpu`, `lemmatize`, `decline`, `remove-words`). `--as NAME` writes the
  result to a new column NAME (refused when the table has it), keeps the working column, and makes NAME the working
  column of the next steps. Steps that give a value other than a phrase (`dupes`, `find-…`, `counts`, `is-typo`,
  `sentiment`, `bm25`, `first-parents`) write a new column `<column>_<suffix>` (a second one gets `_2`).
  `text-stats` adds its metric columns after the working column.
- **filter** — keeps or drops rows (`keep-…`, `drop-…`, `dupes --action drop`, `split-by-words --keep`,
  `remove-cells empty`).
- **report** — makes a new table the current one, and its first text column the working one (`ngrams`, `split-text`,
  `coverage`, `compare-grams`, `cluster-serp`, `compare-lists`, `permutations`).

The matchers (`words`, `phrases`, `stopwords`, `chars`, `spaces`, `regex`, `around`, `edges`, `positions`,
`word-case`, `word-content`, `word-position`, `pos`, `repeats`, `cells`, `markers`, `ready-pattern`, `complements`,
`phrase-end`) give a step for each verb they support: `find-`, `remove-`, `extract-`, and the filters `keep-`, `drop-`.

## Items and lists

An option that takes items takes a comma list `a,b`, `@FILE` (one item per line, or the first column of a table
without its header) or `@NAME` of a list (`@minus/universal`, `@stop/wordstat`, `@markers/geo`). `semkit lists`
shows every list with its source and size, `semkit lists show NAME` its items. A name that is neither a file nor a
list is refused with the closest names that exist. The lists `minus/*` hold phrases: they go to `drop-phrases`
(`keep-phrases`…), not to `drop-words`, which takes single words only (`@stop/wordstat`); a words step given a phrase
names it and sends you to the phrases step. The lists hold lemmas: add `--lemmas` to a words or phrases step to compare
the lemmas («дешевые диваны» is «дешевый диван»). `find-markers --lists` takes a bundled marker list (`geo` or
`@markers/geo`) and a list of your own (`@FILE` or `@NAME`).

The lists of your own are `.txt` files, one item per line, in a folder: set `SEMKIT_LISTS=DIR` (folders separated as
in PATH; a relative one is from the current folder) or the config key `lists` (`semkit config set lists '["DIR"]'`);
`@sub/name` is the file `DIR/sub/name.txt`. The order: the project lists, `SEMKIT_LISTS`, the config `lists`, the
bundled lists. The first required argument of a step may be given without its flag: `remove-chars punctuation` is
`remove-chars --kind punctuation`.

## A second table

A step that needs a second input reads it from a file, like `read` does (any format; `-` is refused here):

- `--against FILE`: `coverage` (the texts), `compare-lists` (the second list).
- `--competitors FILE`: `compare-grams`, `compare-stats` (the texts of the competitors, one per row, in the first
  text column).
- `--freq FILE`: `cluster-serp` (the phrases and their frequencies; `--freq-column` names the column of numbers).
  `--dictionary FILE`: `sentiment` (word, score; «5,5» and «1 000» are numbers). `--synonyms FILE`: `add-minus-words`
  (the table `synonyms` gives). `--pairs FILE`: `replace-text`, `replace-words` (what to find, its replacement). The
  first row of such a file is its header.

## Typical pipelines

Each command line below runs on small files of the kind a user has: `core.csv` (columns `phrase`, `freq`),
`phrases.csv` and `second.csv` (a column `phrase`), `article.txt` and `mine.txt` (a text), `competitors.csv` (a column
`text`, a text per row), `serp.csv` (`phrase`, `position`, `url`). The lines under a command are what it writes to
stdout (JSONL, one row per line).

Clean a core: drop the phrases with the universal minus-words by lemmas (a list of phrases, so `drop-phrases`; it
holds no buy words, so a commercial core keeps its phrases), remove punctuation and extra spaces, drop the duplicates
by lemmas.

```console
$ semkit read core.csv drop-phrases @minus/universal --lemmas remove-chars punctuation remove-spaces extra dupes --kind lemmas --action drop write -
{"phrase": "Диван кровать 2 м", "freq": 5}
{"phrase": "купить диван", "freq": 4}
{"phrase": "купить диван в москве", "freq": 2}
{"phrase": "углы", "freq": 1}
{"phrase": "диван www sofa ru диван", "freq": 7}
{"phrase": "отличный диван Лион", "freq": 3}
{"phrase": "диван120см", "freq": 2}
{"phrase": "чехол на диван", "freq": 1}
{"phrase": "диавн купить", "freq": 1}
{"phrase": "угловой диван", "freq": 2}
{"phrase": "диван недорого", "freq": 1}
```

The same with a list of your own: a folder `lists/` with the file `lists/niche/minus.txt` (single words, one per line)
is `@niche/minus` once `SEMKIT_LISTS=lists` is set. Single words go to `drop-words`.

```console
$ SEMKIT_LISTS=lists semkit read core.csv drop-words @niche/minus --lemmas remove-chars punctuation remove-spaces extra dupes --kind lemmas --action drop write -
{"phrase": "Диван кровать 2 м", "freq": 5}
{"phrase": "купить диван", "freq": 4}
{"phrase": "купить диван в москве", "freq": 2}
{"phrase": "углы", "freq": 1}
{"phrase": "диван www sofa ru диван", "freq": 7}
{"phrase": "отличный диван Лион", "freq": 3}
{"phrase": "диван120см", "freq": 2}
{"phrase": "чехол на диван", "freq": 1}
{"phrase": "диавн купить", "freq": 1}
{"phrase": "угловой диван", "freq": 2}
```

The frequency dictionary of an article: read it whole, cut it into phrases, count the lemmas (`docs` counts the cells
of the cut text: all phrases of one article come from one).

```console
$ semkit read --whole article.txt split-text ngrams -n 1 --lemmas write -
{"ngram": "диван", "count": 4, "docs": 1, "forms": "диван, дивана"}
{"ngram": "в", "count": 1, "docs": 1, "forms": "в"}
{"ngram": "и", "count": 1, "docs": 1, "forms": "и"}
{"ngram": "кресло", "count": 1, "docs": 1, "forms": "кресла"}
{"ngram": "купить", "count": 1, "docs": 1, "forms": "купить"}
{"ngram": "москва", "count": 1, "docs": 1, "forms": "москве"}
{"ngram": "недорогой", "count": 1, "docs": 1, "forms": "недорогой"}
{"ngram": "угловой", "count": 1, "docs": 1, "forms": "угловой"}
{"ngram": "угол", "count": 1, "docs": 1, "forms": "углы"}
```

My text against the competitors: the density of each lemma in the competitors' texts and in mine, with a verdict
(`below`, `within`, `above`).

```console
$ semkit read --whole mine.txt compare-grams --competitors competitors.csv write -
{"ngram": "диван", "docs": 2, "docs_share": 0.6667, "median": 0.2857, "min": 0.0, "max": 0.4286, "mine": 0.3333, "verdict": "within"}
{"ngram": "кресло", "docs": 3, "docs_share": 1.0, "median": 0.1429, "min": 0.1429, "max": 0.5, "mine": 0.0, "verdict": "below"}
{"ngram": "купить", "docs": 2, "docs_share": 0.6667, "median": 0.1429, "min": 0.0, "max": 0.5, "mine": 0.1667, "verdict": "within"}
{"ngram": "угловой", "docs": 2, "docs_share": 0.6667, "median": 0.1429, "min": 0.0, "max": 0.1429, "mine": 0.1667, "verdict": "within"}
{"ngram": "кожаный", "docs": 1, "docs_share": 0.3333, "median": 0.0, "min": 0.0, "max": 0.1429, "mine": 0.1667, "verdict": "above"}
{"ngram": "недорогой", "docs": 1, "docs_share": 0.3333, "median": 0.0, "min": 0.0, "max": 0.1429, "mine": 0.1667, "verdict": "above"}
```

Core phrases in a text: how often each phrase stands in the texts and where it first starts.

```console
$ semkit read phrases.csv coverage --against competitors.csv write -
{"phrase": "купить диван", "count": 1, "docs": 1, "density": 0.125, "first": 5}
{"phrase": "кресло", "count": 3, "docs": 3, "density": 0.1875, "first": 4}
{"phrase": "диван недорого", "count": 1, "docs": 1, "density": 0.125, "first": 6}
```

SERP clusters: the SERP table has the columns `phrase`, `position`, `url` (semkit never fetches a SERP).

```console
$ semkit read serp.csv cluster-serp --method hard --common 3 write -
{"phrase": "диван купить", "cluster": 1, "center": "диван купить", "common": 3}
{"phrase": "купить диван", "cluster": 1, "center": "диван купить", "common": 3}
{"phrase": "кресло", "cluster": 2, "center": "кресло", "common": 3}
```

Compare two lists: the phrases only the second list has (`--op` is `both`, `either`, `first` or `second`).

```console
$ semkit read phrases.csv compare-lists --against second.csv --op second write -
{"phrase": "диван купить"}
```

## Errors

Error envelope with `--json`: `{"ok": false, "error": {"code", "message", "action"}}`. Read the exit code, then
`error.code`, then `error.action` (the next command).

    0  ok
    1  general (UNEXPECTED = a bug: re-run with --verbose, report; ABORTED = user said no; UNHEALTHY = doctor found a problem)
    2  invalid arguments (the message names the step, the option and what to do)
    3  credentials (semkit itself needs none; `semkit status` shows them)
    4  project not initialized → semkit init
    5  provider error (network / external service; already retried) → retry later
    6  CLI too old for this project → uv tool upgrade rb-semkit

Only exit 5 is worth an automatic retry. `semkit doctor --json` reports the environment when something looks off;
`semkit describe --json` is the whole CLI, every step and option, as one machine-readable document. The global
`--dry-run` also keeps `init`, `config set`, `skill install`, `lists add` and `lists rm` from writing.
