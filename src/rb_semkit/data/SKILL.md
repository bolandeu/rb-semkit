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
  "rows_after", "cells_changed"}` per step, and `"note"` after them when the step tells more, as `index: exact`); with
  `write -` stdout is the JSONL of the rows. `--quiet` hides the lines on stderr, never the result.

## Step kinds

`semkit describe --json` gives each step its kind (`x-rb-kind`) and each option its accepted values.

- **change** — rewrites the working column (`chpu`, `lemmatize`, `decline`, `remove-words`). `--as NAME` writes the
  result to a new column NAME (refused when the table has it), keeps the working column, and makes NAME the working
  column of the next steps. Steps that give a value other than a phrase (`dupes`, `find-…`, `counts`, `is-typo`,
  `sentiment`, `bm25`, `first-parents`) write a new column `<column>_<suffix>` (a second one gets `_2`).
  `text-stats` and `parse-html` (a column of HTML → text, links, all, main, title, description, h1) add their columns
  after the working column; a text step takes one of them with `semkit read IN --column all`.
- **filter** — keeps or drops rows (`keep-…`, `drop-…`, `dupes --action drop`, `split-by-words --keep`,
  `remove-cells empty`).
- **report** — makes a new table the current one, and its first text column the working one (`ngrams`, `split-text`,
  `headings`, `coverage`, `compare-grams`, `cluster-serp`, `compare-lists`, `permutations`, `summary`).

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
(`below`, `within`, `above`) against the median (`--norm mean` for the mean), and the occurrences to reach it: `need`
for the size of my text (`--words N` for another size), `have`, `add` (negative: remove) and `med_count`, the median count
in the competitors. `--per-text` adds the density of each competitor, `--no-digits` and `--exclude LIST` leave numbers
and listed words out of every count (also in `text-stats` and `compare-stats`). `summary` reports the mean, median, min
and max of every numeric column, e.g. after `text-stats`.

```console
$ semkit read --whole mine.txt compare-grams --competitors competitors.csv write -
{"ngram": "диван", "docs": 2, "docs_share": 0.6667, "median": 0.2857, "mean": 0.2381, "min": 0.0, "max": 0.4286, "mine": 0.3333, "verdict": "within", "need": 2, "have": 2, "add": 0, "med_count": 2}
{"ngram": "кресло", "docs": 3, "docs_share": 1.0, "median": 0.1429, "mean": 0.2619, "min": 0.1429, "max": 0.5, "mine": 0.0, "verdict": "below", "need": 1, "have": 0, "add": 1, "med_count": 1}
{"ngram": "купить", "docs": 2, "docs_share": 0.6667, "median": 0.1429, "mean": 0.2143, "min": 0.0, "max": 0.5, "mine": 0.1667, "verdict": "within", "need": 1, "have": 1, "add": 0, "med_count": 1}
{"ngram": "угловой", "docs": 2, "docs_share": 0.6667, "median": 0.1429, "mean": 0.0952, "min": 0.0, "max": 0.1429, "mine": 0.1667, "verdict": "within", "need": 1, "have": 1, "add": 0, "med_count": 1}
{"ngram": "кожаный", "docs": 1, "docs_share": 0.3333, "median": 0.0, "mean": 0.0476, "min": 0.0, "max": 0.1429, "mine": 0.1667, "verdict": "above", "need": 0, "have": 1, "add": -1, "med_count": 0}
{"ngram": "недорогой", "docs": 1, "docs_share": 0.3333, "median": 0.0, "mean": 0.0476, "min": 0.0, "max": 0.1429, "mine": 0.1667, "verdict": "above", "need": 0, "have": 1, "add": -1, "med_count": 0}
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

## Steps by meaning

The steps by meaning (`cluster-meaning`, `dupes --kind meaning`) compare phrases by their phrase vectors: phrases of close meaning get close
vectors. They need the optional extra `vectors` and an encoder pulled once; a step never downloads one.

1. Install semkit with the extra: the command of «Install» above with `rb-semkit[vectors]` in place of `rb-semkit`
   and `--force` (uv must reinstall an installed semkit). The error `VECTORS_NOT_INSTALLED` gives the exact command.
2. Pull an encoder once: `semkit models pull e5-small` (the default; `bge-m3` is better and 7 times slower, for small
   cores; `potion` is 20 times faster, for very large ones; `hf:<id>` is any model of the Hugging Face hub with an ONNX
   export or a model2vec model). The files are checked against pinned checksums; a failed pull keeps nothing (exit 5,
   run it again). `semkit models list` shows each encoder, pulled or not, with its size and default threshold;
   `semkit models remove NAME` takes one out. The cache is the system cache (`~/Library/Caches/semkit/models` on macOS,
   `~/.cache/semkit/models` on Linux) or the folder of the config key `models.dir`.
3. Run a step by meaning in a pipeline:

```bash
semkit read core.csv cluster-meaning --freq freq write clusters.csv
```

`--model NAME` names the encoder (default `e5-small`); `--threshold` is the similarity from 0 to 1 of one intent, by
default the threshold of the model (a hub model has none: give it). The steps add columns and drop no row: their
columns are candidates, the user decides. `cluster-meaning` gives every phrase a `cluster`, a `cluster_name` (its most
frequent phrase with `--freq COLUMN`, else the phrase nearest its centre) and the `similarity` of the phrase to that
name; a phrase without close phrases is a cluster of one. The summary line of the step names the vector index it
searched (`index: exact`, or `index: hnsw` above about 300 000 phrases; both give the same result every run); with
`--json` it is the `note` of the step's summary. A model not pulled is `MODEL_NOT_PULLED` (exit 1, the action is the
pull command); an unknown `--model` or a `--threshold` out of 0–1 is exit 2.

`ad-groups` gives every phrase an `ad_group` number and an `ad_group_name`: phrases that are duplicates by meaning of
each other (the rule of `dupes --kind meaning`, with its `--neutral`, `--synonyms`, `--home`) share a group, taken
transitively. `--max-size N` (1 or more) splits a larger group by vector, the nearest phrases together; the name is the
most frequent phrase with `--freq COLUMN`, else the first one.

`dupes --kind meaning` marks a phrase as a duplicate of an earlier one when their vectors are close and the words that
differ are only non-refining words (the bundled list `@meaning/neutral`, plus your own `--neutral @FILE`), synonyms
(`--synonyms FILE` of word and synonyms, as the step `synonyms` gives), another form or order of a word, or the home
city (`--home NAME`). A refinement (type, size, material, brand, another city) is another intent, however close the
vectors. It adds `<column>_dupes`, `dupe_of` (the first phrase of the group) and `similarity` (the cosine to it);
`--action drop` keeps the first row of each group.

### Synonym candidates

`synonym-candidates` proposes synonyms for the words of the core (by lemmas; stopwords and words with digits are
skipped), for you to pick. It needs two word data, pulled once like an encoder: `semkit models pull ruwordnet` (the
thesaurus RuWordNet) and `semkit models pull navec` (word vectors); `models list` and `models remove` handle them too.

```bash
semkit read core.csv synonym-candidates write candidates.csv
semkit read core.csv synonym-candidates --source ruwordnet --as-synonyms write synonyms.csv
```

The report has the columns `word`, `candidate`, `source` (`ruwordnet` or `navec`), `score` (1 for a thesaurus
synonym, the cosine for navec) and `in_core`. By default only candidates that occur in the core are given; `--all`
gives every candidate. `--source ruwordnet|navec|both` picks the data, `--top` limits the navec candidates per word.
`--as-synonyms` gives the file of synonyms instead (`word`, `synonyms`) that `--synonyms` of the steps reads
(`add-minus-words`): edit it down to the picked words first. A data not pulled is `MODEL_NOT_PULLED` (exit 1, the
action is the pull command).

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
