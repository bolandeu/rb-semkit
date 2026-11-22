# semkit

Обработка семантического ядра: чтение и запись фраз в любом формате, леммы, n-граммы, дубли

## Library

```python
import pandas as pd
import rb_semkit as sk

phrases = pd.Series(["купить диван", "Диван бу", None])
sk.find(phrases, sk.words(["диван"]))  # [True, True, False]
sk.remove(phrases, sk.words(["диван"]))  # ["купить", "бу", ""]
sk.extract(phrases, sk.words(["диван"]))  # ["диван", "Диван", ""]

sk.lemmatize(pd.Series(["купила диваны"]))  # ["купить диван"]
sk.part_of_speech(pd.Series(["москве"]))  # ["n"]
sk.wordforms("москва")  # [..., "москве", ...]
sk.decline(pd.Series(["купить красный диван"]), "genitive")  # ["купить красного дивана"]
sk.decline_full_name(pd.Series(["Петрова Анна Ивановна"]), "accusative")  # ["Петрову Анну Ивановну"]
sk.agree(pd.Series(["растаможить машина", "легковой машина"]))["agreed"]  # ["растаможить машину", "легковая машина"]

df = pd.DataFrame({"phrase": ["купить диван бу"], "freq": [10]})
sk.remove(df, sk.words("бу"), column="phrase")  # adds "phrase_remove" right after "phrase"
sk.remove(df, sk.words("бу"), column="phrase", inplace=True)  # replaces "phrase"
sk.pipe(df, "phrase").remove(sk.words("бу")).remove(sk.words("купить")).phrases
```

- Input: a Series of phrases, or a DataFrame with `column=`. NaN and None are empty strings.
- Output: a Series with the input index, or the input DataFrame itself with the new column
  `<column>_<operation>` (the function adds it to your object and returns that object; pass `df.copy()` to keep `df`).
- One matcher (`sk.words(...)`), three verbs: `find` (bool mask), `remove` (cleaned text), `extract` (found part).
  A phrase splits on any whitespace; words compare by case and ё = е; the output keeps the original text.
- `sk.words(items, mode="any"|"all", where="anywhere"|"start"|"end", ignore_punct=False, lemmatizer=None)`.
  With a `lemmatizer` it compares lemmas («диваны» = «диван»); without one, words as they are.
- Lemmas: the !SEMTools dictionary, then pymorphy3, then the add-in's suffix table; `fallback="pymorphy"` gives
  every word missing from the dictionary the pymorphy3 guess instead; any object with
  `lemma(word)`, `pos(word)` and `forms(lemma)` works as `lemmatizer=`.
- `sk.text_stats(data, lemmatizer=..., column=None)`: per text, `chars`, `chars_no_spaces`, `words`, `unique`, `water`,
  `nausea_classic`, `nausea_academic`, `top`, `ttr`, `mtld`, `zipf` (definitions in the docstring); with `column=` the
  metric columns follow `column`; `no_digits=True` and `exclude=[...]` leave words out of every count.
- `sk.summary(df)`: per numeric column, `count`, `mean`, `median`, `min`, `max`. `sk.compare_stats` and
  `sk.compare_grams` give a `mean` beside the median (`norm="mean"` sets the verdict by it); `compare_grams` also gives
  `need`, `have`, `add` and `med_count` (`words=` sets the size) and `per_text=True` a density column per competitor.
- Wrong input raises `sk.InvalidArguments`, naming the argument and the allowed values.

The bundled data (`src/rb_semkit/data/`) is built from the !SEMTools sources (paths in
`scripts/build_data.toml`) by `uv run scripts/build_data.py`; the same sources give byte-identical files.

## CLI

One command is a pipeline: `semkit read IN STEP… write OUT`. Every function of the library is a step with its own
`--help` (`semkit read IN STEP --help`); `semkit --ai` prints the guide for agents and the list of steps. A step
works on the working column (`--column`, by default the first text column), a second input is a file option
(`--against`, `--competitors`, `--freq`, `--dictionary`), and a list is `@name`, `@file` or `a,b`. Typical pipelines
(`src/rb_semkit/data/SKILL.md` shows their output; the tests run them):

```bash
# clean a core: drop the phrases with the universal minus-words by lemmas (a list of phrases: drop-phrases; single
# words go to drop-words), remove punctuation and extra spaces, drop duplicates by lemmas
semkit read core.csv drop-phrases @minus/universal --lemmas remove-chars punctuation remove-spaces extra \
  dupes --kind lemmas --action drop write clean.csv

# the same with your own list: lists/niche/minus.txt (one word per line) is @niche/minus; `semkit lists` shows the names
SEMKIT_LISTS=lists semkit read core.csv drop-words @niche/minus --lemmas remove-chars punctuation remove-spaces extra \
  dupes --kind lemmas --action drop write clean.csv

# the frequency dictionary of an article
semkit read --whole article.txt split-text ngrams -n 1 --lemmas write words.csv

# my text against the texts of the competitors
semkit read --whole mine.txt compare-grams --competitors competitors.csv write verdicts.csv

# a quick try: phrases from the command line, the result as a table in the terminal (no write)
semkit read --text "растаможка авто" synonym-candidates --all

# which core phrases stand in the texts
semkit read core.csv coverage --against texts.csv write coverage.csv

# SERP clusters (the table has phrase, position, url)
semkit read serp.csv cluster-serp --method hard --common 3 write clusters.csv

# the phrases only the second list has
semkit read first.csv compare-lists --against second.csv --op second write only-second.csv

# a core from word variants (one column per list): combine them into phrases, agree the words, match them to the
# pages by meaning (the extra vectors)
semkit read variants.csv linear-combinations agree nearest --against page_texts.csv --top 2 write matches.csv
```

A topic's phrases get a class at each other (`relate-phrases`): `same`, `variation` (another word of the same meaning),
`refinement` (the phrase of another plus more words) or `other`, with `of` (the phrase it belongs to), `group` (the
first phrase of its group) and `reason` (the rule and the link). It works by lemmas and the dictionary
(`semkit models pull ruwordnet` once), with no network and no vectors; 1000 phrases run in seconds. `--synonyms FILE`
adds the links of your topic: a column `synonyms`, a group in each row, items split by `|`
(`ремонт | починка | починить`), or the columns `word` and `synonyms` (split by spaces) as `dupes --synonyms` has.
The dictionary has gaps, and a gap is `other` (сделать ≁ создать, починить ≁ ремонт): the file fills them.

```bash
semkit read --text "купить диван" --text "диван купить" --text "купить угловой диван" --text "диван" relate-phrases write -
# купить диван: refinement of диван (+купить); диван купить: same as купить диван (lemmas);
# купить угловой диван: refinement of купить диван (+угловой); диван: other, group купить диван
semkit read topic.csv relate-phrases --synonyms links.csv write classes.csv
```

Columns keep the types of the file (numbers stay numbers). Every step, option and file an option names is checked
before the input is read; a refusal exits 2 and names the step and the option. `--as NAME` writes a change to a new
column NAME, which the next steps work on. `--lemmas` on a words or phrases step compares lemmas, as the bundled
lists hold them. `--json`, `--quiet` and `--dry-run` go before the steps: `semkit --json read …` prints one envelope
`{"ok": true, "output", "rows", "written", "steps"}` (`steps`: one summary per step, with a `note` when the step tells
more), `--quiet` hides the lines on stderr, `--dry-run` runs the steps and writes nothing (it also keeps `init`, `config set`, `skill install`, `lists add` and `lists rm` from writing).
`--trace FILE` records every cell a step changed (row 1 is the first row under the header), `write OUT --overwrite`
replaces an existing file (and an existing trace). `write OUT --columns NAME,NAME --rename OLD=NEW` chooses, orders and
renames the output columns (`… nearest --to Q write - --columns phrase,similarity --rename similarity=сходство`); an
unknown name or a clash exits 2 and lists the columns there are. `read --text TEXT` (repeatable) takes the phrases from the command
line instead of IN: a table with the column `phrase`, a row for each `--text`. A pipeline without `write` prints the
result as a table (every column, every row) in the terminal; with `--json`, or when stdout is not a terminal, it writes
JSONL to stdout as `write -` does.

A frequent chain runs by its name: `semkit run NAME` runs a workflow, a named chain of semkit's own steps, as one read
pipeline. `semkit run --help` lists the workflows, `semkit run NAME --help` shows the parameters with their defaults
and the steps. A project adds its own as `.rb_semkit/workflows/NAME.toml` (one of the same name overrides the bundled
one).

```bash
# phrase synonyms of one intent: every variation of the phrase by the thesaurus, scored by meaning against it
semkit run intent-synonyms --text "растаможка авто"

# a parameter, and an option of one of the steps
semkit run intent-synonyms core.csv --set threshold=0.85 --set nearest.model=e5-small write synonyms.csv
```

Your own lists: `SEMKIT_LISTS=DIR` (a relative folder is from the current one) or `semkit config set lists '["DIR"]'`;
`SEMKIT_LISTS` wins over the config. `semkit lists` shows every list, `semkit lists show @NAME` its items.

## Development

```bash
uv sync
uv run semkit --help
# the full gate (run before every commit; CI runs it too), at the template tag of .copier-answers.yml
uvx --from "git+https://github.com/bolandeu/cli-generator.git@v1.27.3#subdirectory=gate" gate check
uv run pytest -m speed    # the timed tests, left out of the gate: run on an idle machine
uv run pytest --snapshot-update  # after changing a command's help; review tests/snapshots/help/
```

`pytest` fails below the coverage floor in `pyproject.toml`; `ruff` includes
the security (`S`) rules; the gate also scans the git history for committed
secrets when `gitleaks` is installed (`brew install gitleaks`) and `uv.lock`
for known vulnerabilities when `osv-scanner` is installed (`brew install
osv-scanner`), and says it skipped a scan otherwise. CI is optional and only repeats
`gate check`.

## Release

The version is the git tag (`vX.Y.Z`) — `pyproject.toml` has no `version =`.
Work and releases go through Antagor. Nobody tags or pushes by hand.

## Install

**On this machine, from a local checkout:**

```bash
uv tool install .
```

**From the Gitea registry** (the package is released there):

```bash
```

**Or from the git tag, on any other machine (any OS):**

```bash
uv tool install "rb-semkit @ git+https://github.com/bolandeu/rb-semkit.git@vX.Y.Z"
```

Replace `vX.Y.Z` with the latest release tag (never install a branch). This is also how an AI agent
bootstraps this CLI on a fresh machine/sandbox where it isn't installed
yet — see `src/rb_semkit/data/SKILL.md`.

**Update** an installed copy to the latest commit:

```bash
uv tool upgrade rb-semkit
```

After install, the command `semkit` is available globally, on
macOS, Linux and Windows alike (no shelling out, no hardcoded POSIX paths).

To pick up later architecture changes from the `cli-generator` template
itself, run `copier update` in this repo (requires this repo and the
template to both be git repos; see the `cli-generator` plugin's README).

## Architecture

This project follows a fixed CLI architecture:

- `src/rb_semkit/commands/` — argument parsing only, no business logic.
- `src/rb_semkit/core/` — services, models, errors: the real logic.
- `src/rb_semkit/providers/` — external APIs/integrations.
- `src/rb_semkit/credentials/` — secrets via the OS keychain (`keyring`)
  and environment variables. Secrets never live in `.rb_semkit/config.toml`.
- `src/rb_semkit/output/` — human (`rich`) and `--json` rendering.

Run `semkit doctor` to check environment/config/auth readiness, and
`semkit --help` for the full command surface. Every command supports
`--json` for machine/agent consumption; errors are structured (`error.code`,
fixed exit codes, `error.action` telling you what to do next) and go to
stderr in human mode, so stdout is always safe to pipe.

A project can require a minimum CLI version in its `.rb_semkit/config.toml`
(`[cli] min_version = "..."`, set or lowered by `semkit config set cli.min_version X`); every command checks it, an
older install refuses with exit 6 and `uv tool upgrade rb-semkit` fixes it.

See `src/rb_semkit/data/SKILL.md` for the agent-facing usage guide
bundled with this package — install it into an AI tool with
`semkit skill install`, or get it as plain text with
`semkit --ai` (works even without file access).
