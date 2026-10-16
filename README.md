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
- Lemmas: the !SEMTools dictionary, then pymorphy3, then the add-in's suffix table; any object with
  `lemma(word)`, `pos(word)` and `forms(lemma)` works as `lemmatizer=`.
- Wrong input raises `sk.InvalidArguments`, naming the argument and the allowed values.

The bundled data (`src/rb_semkit/data/`) is built from the !SEMTools sources (paths in
`scripts/build_data.toml`) by `uv run scripts/build_data.py`; the same sources give byte-identical files.

## Development

```bash
uv sync
uv run semkit --help
uv run scripts/release.py --check   # the full gate (run before every commit; CI runs it too)
uv run pytest --snapshot-update  # after changing a command's help; review tests/snapshots/help/
```

`pytest` fails below the coverage floor in `pyproject.toml`; `ruff` includes
the security (`S`) rules; the gate also scans `uv.lock` for known
vulnerabilities when `osv-scanner` is installed (`brew install osv-scanner`),
and says it skipped the scan otherwise. CI is optional and only repeats
`release.py --check`.

## Release

The version is the git tag (`vX.Y.Z`) — `pyproject.toml` has no `version =`.
Work goes through Antagor tickets (`.agents/antagor/`); a release (run by the Human) is

```bash
antagor publish --bump   # SemVer; at 0.x: patch = fix/feature, minor = breaking
```

It tags the release, builds `CHANGELOG.md` from the ticket titles and runs
`scripts/deploy.sh`: push `main` with tags, then report the release to the
root tools agent. Nobody tags or pushes by hand.

## Install

**On this machine, from a local checkout:**

```bash
uv tool install .
```

**On any other machine (any OS), once this repo is pushed to GitHub — no
PyPI publish needed:**

```bash
uv tool install "rb-semkit @ git+https://github.com/bolandeu/rb-semkit.git@vX.Y.Z"
```

Replace `vX.Y.Z` with the latest release tag (a tag cut by
`antagor publish`; never install a branch). This is also how an AI agent
bootstraps this CLI on a fresh machine/sandbox where it isn't installed
yet — see `src/rb_semkit/data/SKILL.md`.

**Private repo?** The command above is unchanged — `uv` runs git under the
hood, so it authenticates the same way `git clone` does. On a machine
where the install is refused with an auth error, do one of these once:

```bash
gh auth login          # interactive login also sets up git's credential helper
gh auth setup-git      # only needed if gh was logged in with --with-token / in CI
```

or use the SSH form instead of HTTPS:

```bash
uv tool install "rb-semkit @ git+ssh://git@github.com/bolandeu/rb-semkit.git@vX.Y.Z"
```

**Update** an installed copy to the latest commit:

```bash
uv tool upgrade rb-semkit
```

After install, the command `semkit` is available globally, on
macOS, Linux and Windows alike (see `architecture.md` in the cli-generator
plugin for why: no shelling out, no hardcoded POSIX paths).

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
(`[cli] min_version = "..."`); an older install refuses with exit 6 and
`uv tool upgrade rb-semkit` fixes it.

See `src/rb_semkit/data/SKILL.md` for the agent-facing usage guide
bundled with this package — install it into an AI tool with
`semkit skill install`, or get it as plain text with
`semkit --ai` (works even without file access).
