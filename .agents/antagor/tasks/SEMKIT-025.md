---
id: SEMKIT-025
title: 'Word lists: bundled Bukvarix and add-in lists with a manifest, the Human''s
  folders by any path, semkit lists, sk.word_list'
status: queue
attempts: 0
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
- src/rb_semkit/core/wordlists/
- src/rb_semkit/commands/lists.py
- src/rb_semkit/data/wordlists/
- scripts/build_parts/wordlists.py
- scripts/build_data.toml
- src/rb_semkit/core/services.py
- tests/test_services.py
- tests/core/test_build_data.py
- tests/conformance/test_cases.py
- .gitattributes
- tests/snapshots/help/lists.txt
- tests/snapshots/help/lists-show.txt
- tests/snapshots/help/lists-add.txt
- tests/snapshots/help/lists-rm.txt
- scripts/build_parts/wordlists.toml
- src/rb_semkit/commands/read.py
- src/rb_semkit/core/models.py
- src/rb_semkit/core/opencli.py
- src/rb_semkit/pipeline/commands.py
- src/rb_semkit/pipeline/items.py
test_paths:
- tests/wordlists/
- tests/conformance/data_manifest/wordlists.json
- tests/conftest.py
- tests/pipeline/test_lists.py
- tests/snapshots/describe.json
- tests/snapshots/help/read.txt
- tests/snapshots/help/steps/text/drop-cells.txt
- tests/snapshots/help/steps/text/drop-phrases.txt
- tests/snapshots/help/steps/text/drop-word-content.txt
- tests/snapshots/help/steps/text/drop-words.txt
- tests/snapshots/help/steps/text/extract-cells.txt
- tests/snapshots/help/steps/text/extract-phrases.txt
- tests/snapshots/help/steps/text/extract-word-content.txt
- tests/snapshots/help/steps/text/extract-words.txt
- tests/snapshots/help/steps/text/find-cells.txt
- tests/snapshots/help/steps/text/find-phrases.txt
- tests/snapshots/help/steps/text/find-word-content.txt
- tests/snapshots/help/steps/text/find-words.txt
- tests/snapshots/help/steps/text/keep-cells.txt
- tests/snapshots/help/steps/text/keep-phrases.txt
- tests/snapshots/help/steps/text/keep-word-content.txt
- tests/snapshots/help/steps/text/keep-words.txt
- tests/snapshots/help/steps/text/remove-cells.txt
- tests/snapshots/help/steps/text/remove-phrases.txt
- tests/snapshots/help/steps/text/remove-stopwords.txt
- tests/snapshots/help/steps/text/remove-word-content.txt
- tests/snapshots/help/steps/text/remove-words.txt
docs: none
tools: []
worker_args: null
class: standard
decision: false
visual: null
depends_on:
- SEMKIT-023
budget_usd: null
epic: E-003
spec_refs: []
checks:
- python3 scripts/check_command_docstrings.py
- uv run scripts/release.py --check
resident: null
tool: null
pr: null
translation: '**Списки слов.** 66 списков Букварикса (уже скачаны в sandbox) и списки
  надстройки встраиваются со сборкой и манифестом (имя, описание по-русски, источник);
  новый встроенный список — файл + строка манифеста, тест ловит рассинхрон. Имена:
  minus/cheap, stop/wordstat, combine/tourism/turkey, stop/semtools, markers/geo…
  Поиск @имени: проект .semkit/lists/ → папки из конфига lists = [пути] → SEMKIT_LISTS
  → встроенные; описание своего списка — первая строка «# …». sk.word_list(имя) для
  Python. Команды: semkit lists / show / add (--replace) / rm (встроенные не удаляются),
  --dry-run. Справка шагов, describe и --ai показывают доступные списки.'
---

Named word lists the Human uses by name and extends without code.
1. Sources and build: the 66 Bukvarix lists were downloaded to /Users/bolandau/Work/_sandbox/semtools/reference/bukvarix/ (minus/, stop/, combiner/; UTF-8 with BOM, CRLF). Add that folder to the build sources; a build part cleans them (BOM, CRLF, trim, empty lines, duplicates in order) and bundles them. A manifest of the bundled lists holds, per list: name, description in Russian, source, file. Names: minus/universal, minus/computer, minus/free, minus/cheap, minus/handmade, minus/abusive, minus/adult-hard, minus/adult-soft, minus/countries, minus/world-cities, minus/ex-ussr-cities, minus/russia-cities, minus/moscow-region-cities, minus/ukraine-cities, minus/belarus-cities, minus/kazakhstan-cities, stop/wordstat, combine/shop, combine/review, combine/realty-service, combine/realty-object, combine/tourism, combine/russia-cities-500k, …-250k, …-100k, combine/moscow-region-villages, combine/leningrad-region-villages, combine/ukraine-cities-250k, …-100k, combine/kiev-region-towns, combine/moscow-hotels, combine/spb-hotels, combine/moscow-metro, combine/spb-metro, combine/tourism/<country> (austria, benelux, bulgaria, uk, hungary, germany, greece, egypt, israel, india, indonesia, spain, italy, canada, caribbean, cyprus, china, malaysia, mexico, uae, poland, portugal, baltic, scandinavia, usa, thailand, turkey, france, croatia, czech, montenegro, switzerland). The add-in's lists get names in the same scheme: stop/semtools (the bundled stopwords), markers/<name> for each marker list. A later bundled list is a source file plus a manifest line; a test fails when a source file has no manifest line or a manifest line has no file.
2. Resolution: resolve(name) looks in the project's .semkit/lists/, then the folders of the config key lists = [paths] (any absolute or ~ path), then the folders of SEMKIT_LISTS (os.pathsep separated), then the bundled lists; a name is a relative path without .txt (niche/mebel → niche/mebel.txt). A user list's description is its first line when it starts with '# ' (that line is not an item). names() gives every name with source (project, folder path, bundled), lines and description.
3. sk.word_list(name) -> Series of the items, for Python users; it is a public name of the package but not a step (list it as not-a-step / not cased in conformance: it is semkit's own).
4. Commands: semkit lists (all lists: name, source, lines, description; --json), semkit lists show NAME (the items), semkit lists add NAME FILE [--to project|PATH] [--replace] (copies a file into the project's .semkit/lists/ or the given folder; an existing name is refused without --replace), semkit lists rm NAME [--from …] (removes a list added there; a bundled list is never removed and the refusal says so). --dry-run shows what add or rm would do.
5. Help: the core's list resolver now names every list; a step that takes items shows the available names at the end of its --help, and describe and --ai (through the ai_section hook) list them with descriptions.

## Acceptance

- Given the bundled lists, When semkit lists --json runs, Then it holds minus/cheap (description, source bundled, lines > 0), stop/wordstat, combine/tourism/turkey, stop/semtools and markers/geo [check: tests/wordlists/]
- Given a folder ~/x/niche/mebel.txt starting with '# Мебель: минус-слова', When the config has lists = ['~/x'] (or SEMKIT_LISTS=~/x), Then @niche/mebel resolves to its items without the first line and semkit lists shows it with that description and source ~/x [check: tests/wordlists/]
- Given the same name in the project folder and in a user folder, When resolved, Then the project's list wins [check: tests/wordlists/]
- Given semkit lists add niche/x f.txt, When niche/x exists, Then it is refused naming --replace; with --replace it is overwritten; semkit lists rm minus/cheap is refused (bundled) [check: tests/wordlists/]
- Given semkit read core.csv drop-words --items @minus/cheap write -, When run, Then the phrases with «дешево» are dropped [check: tests/wordlists/]
- Given drop-words --help, When read, Then its end lists the available list names [check: tests/wordlists/]
- Given a source file without a manifest line, or a manifest line without a file, When the build test runs, Then it fails naming it [check: tests/wordlists/]
- Given sk.word_list('minus/free'), When called, Then it returns the items as a Series; an unknown name raises InvalidArguments with close names [check: tests/wordlists/]

## How to test

Unit tests of the resolver over tmp folders and env; CLI tests of the lists commands through CliRunner; the build part over a small fixture copy of the sources; help snapshots of the lists commands.

## Basis

Bundle the lists the way the marker lists are bundled (a build part, compact files loaded lazily, a manifest check in the build test). The core task's list-argument resolver calls rb_semkit.core.wordlists.resolve(name) and names() when the module exists: provide exactly those, plus describe(name) for the help. Project config and its loading: core/services.py; follow the cli-builder rule of project-local config, plus the SEMKIT_LISTS variable for folders shared across projects.

## Read first

- `scripts/build_data.toml`
- `src/rb_semkit/core/services.py`
- `src/rb_semkit/core/markers/__init__.py`

## Out of scope

- Downloading lists at run time or from the CLI; editing a list's items from the CLI (edit the file).
- The pipeline core and the other steps: SEMKIT-023 and SEMKIT-024.

## Feedback

### Answer to question #1

> Acceptance of SEMKIT-025 runs 'read core.csv drop-words --items @minus/cheap', but drop-words (core/text/matchers/words.py, SEMKIT-023/024) accepts single words only and minus/cheap holds phrases ('по дешевке', 'за копейки'), so the command exits 2.
> Question: How should the acceptance command work?
> Options:
> 1. Use drop-phrases in the acceptance and the test (phrases matcher takes multi-word items; I did this)
> 2. Make the words matcher accept multi-word items (a change of SEMKIT-024's matcher)
> Recommended: Use drop-phrases in the acceptance and the test (phrases matcher takes multi-word items; I did this)

Option 1: drop-phrases. A list with multi-word items goes to the phrases matcher; words stays for single words. Read the acceptance line as drop-phrases --items @minus/cheap.

### Blocked: needs_scope (entries [{'n': 1, 'text': "Acceptance of SEMKIT-025 runs 'read core.csv drop-words --items @minus/cheap', but drop-words (core/text/matchers/words.py, SEMKIT-023/024) accepts single words only and minus/cheap holds phrases ('по"}])

Inbox #1: option 1, use drop-phrases for lists with phrases; keep the words matcher as it is.
