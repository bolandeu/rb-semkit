# End-to-end check of v0.1.20: findings

Source of E-004. The check ran semkit 0.1.20 (`semkit read …`) the way an SEO specialist or an agent does, on real data:

- core: 2000 Bukvarix phrases for «купить диван» (and its first 1000 and 100), csv / xlsx / parquet / jsonl;
- texts: 8 pages of ost-term.ru fetched by spider (a customs warehouse site), a core of 204 phrases «склад временного
  хранения» for them;
- a synthetic SERP table (100 phrases × top 10) for cluster-serp.

Ten runs were checked row by row against an independent recount (Python, pymorphy3, the reading of a Russian speaker);
four agents swept every step, option value and mode. Below: what is wrong, by layer. «Core» is the library
(`import rb_semkit as sk`): the CLI only calls it. «CLI» is the pipeline, the step table, the help and the errors.

## Correct (checked against a recount)

ngrams / bigrams (count, docs, sum, order: 3265 grams, 0 differences), dupes (every kind and action), drop-words /
drop-phrases by a list (1000 rows, the same rows as the recount), cluster-serp soft and hard (the rule holds for every
pair, common and center right), coverage by its own rule (200 of 204 the same; the 4 others are the punctuation rule
below), text-stats chars and words, bm25, compare-grams maths, split-by-words, basis-phrases, cluster-by-frequency,
hash-text, chpu, the csv / xlsx / parquet / jsonl round trip of text, --dry-run, --trace, OUTPUT_EXISTS.

## Core: algorithms

### Morphology

1. Lemmatizer: wrong lemmas from the bundled dictionary: кафе→кафа, купе→купа, мини→минь, ширина/шириной→ширин,
   спину→спин, экокожа→экокожи, подростка→подростковый, аскона→аскон, ножках→ножки, петушках→петушок, донецке→донецкий,
   вещей→вещий, временного→временной (in almost every phrase of a customs core), рус→русый; раскладывающийся and
   раскладывается swap their lemmas; вперед→вперёд (ё in a lemma while ё = е). `fallback pymorphy` changes none:
   the dictionary answers first. 14 of 542 distinct words of the sofa core (2.6%).
2. decline accusative: an inanimate noun takes the animate form («купить дивана»), and the adjective disagrees with it
   («кожаный дивана», «дивана углового»). decline-noun «диван» accusative → «дивана» is even in the help.
3. decline: a plural phrase does not decline at all («дизайнерские диваны», «угловые диваны» in every case, with
   `--number plural` too); half of a commercial core is plural.
4. decline: the first part of a hyphenated compound stays («диван-кровати», expected «дивана-кровати»); a feminine
   adjective in -ая after ш/ж/ч/щ/к/г/х («большей скидки», expected «большой»); an adjective with не- («нераскладной
   диване»).
5. decline-adjective: «синий» neuter → «синое», «третий» feminine → «третьи», plural accusative «третьих» / «лисие».
6. decline-noun plural: «стул» → «стулы», «человек» → «человеки»; «мебель» gets a plural.
7. decline-full-name: an indeclinable surname declines («Белых» → «Белыха»), a declinable one stays («Глинка»,
   «Королёва» with ё), accusative leaves the first name («Абрамовича Роман»), instrumental «Абрамовичом»; a row that is
   not three words stops the whole run.
8. wordforms: the input word is repeated (the help says it is not), odd forms («покрасно»), an unknown word gives a
   misleading error about a text column.
9. part-of-speech: an unknown word gives an empty code (double spaces in 263 of 2000 rows); the codes are not listed.
10. extract-complements takes words past the complement («в москве недорого распродажа»); fix-word-order uses it.
11. remove-phrase-end buy_markers leaves a hanging preposition («диван с»).

### Text

12. split-text cuts at a dash between subject and predicate («Склад временного хранения — это место» → two phrases),
    at an abbreviation point («г. Краснознаменск» → «г» | «Краснознаменск») and inside a phone or a date.
13. coverage exact: an occurrence never crosses punctuation («хранения — это» is not «хранения это»); the rule is not
    in the help. Decide: SEO tools count an exact occurrence across a dash or a comma.
14. Word counts disagree: text-stats counts 3899 words of a page, compare-grams and coverage 3775 (numbers such as
    31.03.2026 are one word in one place and several in the other); densities next to nausea do not agree.
15. text-stats / compare-grams: single-letter abbreviations (г, м, п) count as lemmas: top «г», nausea 47.8 on a page
    with addresses.
16. ngrams on a raw text keeps punctuation on words («руб.», «свх,», «★» on top); the help does not send to split-text.

### Analysis

17. is-typo / typo-correction: 263 of 2000 correct phrases marked as typos and rewritten («диван купить москва» →
    «москве», «угловые диваны» → «угловой диваны», «купить диван не дорого» → «не недорого»). Unusable on a real core.
18. add-minus-words adds the unsure synonyms (sure=False) too.
19. Rounding: coverage density and counts share unrounded, compare-grams 4 decimals, compare-stats integers as floats.

### Matching and lists

20. The bundled minus lists hold lemmas, the words / phrases matchers compare forms: «дешевые диваны», «недорогие
    диваны», «со скидкой» stay after drop-phrases @minus/cheap. The library has `lemmatizer` on the matchers; the
    CLI has no option for it.
21. @minus/universal holds «купить»: the "clean a core" pipeline of the guide drops 1996 of 2000 phrases of a
    commercial core; «бу» in *-cells contains matches «екатеринБУрге».
22. find-pos: a capitalised word is both adj and adverb; «лучше» a noun; «покрывало» a verb.
23. match-type glues operators to existing quotes and brackets (`+"купить +диван"`, `[[…]]`): invalid Direct syntax.
24. translit ru does not reverse translit en (ЖУК → ZHUK → ЗХУК, Цой → Тсой, Чайка → Чаыка, shchuka → шчука).
25. change-case toponyms misses hyphenated names and names before punctuation; phonetic IKEA → ИКИ; replace-words
    misses a word with punctuation attached; extract-utm reads the #fragment, remove-utm keeps it.
26. remove-chars punctuation breaks decimals and sizes («2.5 м» → «2 5 м»), split-digits «140х200» → «140 х 200».
27. remove-cells empty crashes on an empty cell (a shorter Series where the pipeline expects a change).

### Reading

28. An integer column with an empty cell comes back as float from xlsx and jsonl (5 → 5.0); csv and parquet keep it.

## CLI: the pipeline, the help, the errors

29. `--as NAME` over an existing column overwrites it silently (the frequencies replaced by URLs); a second `find-*`
    overwrites `<column>_find`. A step after `--as` works on the old working column, not on the new one, and several
    `--as` columns come in reverse order. `--as` counts «cells changed» against the working column.
30. The guide (`--ai`) disagrees with the CLI: `-q` does not exist; the `--json` success envelope has no `data`; an
    unknown list does not list the names that exist; text-stats is a change step, not a report; its "clean a core"
    pipeline is wrong for a commercial core (21); its pipelines name fixtures a user does not have.
31. `| head` gives BrokenPipeError and exit 1.
32. A missing second-input file (--against, --competitors, --freq, --pairs, --synonyms, IN) gives exit 1 and the
    Python hint «Pass format='text'»; CSV on stdin gives exit 1 and «pass encoding= or sep=». Expected: exit 2, the
    step and the option named, a CLI action.
33. Enum options of some steps (coverage --mode, cluster-serp --method, compare-lists --op) are checked after the
    input is read, not before.
34. Errors name Python arguments (`first_only`, `text_column`, `mode='fuzzy'`, `weight: 'f'`), not the step and the
    flag; an error on a list option echoes the whole list (825 KB for @markers/geo).
35. Help: many options say only «See the description above.» with no values; `describe --json` has no accepted values
    for most enum options and no step kinds; positional names `positional_kind`; help paragraphs leak into the next
    option; Python internals (Series, DataFrame, sk.*, InvalidArguments, ADR 0005, "as in the add-in") in product
    help; options described that the CLI does not have (provider, against, lemmatizer, user).
36. Examples that do nothing or harm on a real core: remove-around '\d+' (the pattern is literal), remove-edges with no
    characters (a no-op, exit 0), linear-combinations / ordered-pairs / permutations over a whole core (millions of
    rows), split-by-words good with no --good (0 rows), parents with @minus/universal.
37. find-markers --lists @markers/geo fails (it takes bundled names only); @FILE of a CSV reads the header as an item;
    cluster-serp --freq wants a column named freq exactly; weights «5,5» and «1 000» are refused; options that do not
    apply are ignored silently (find-cells empty --items x); `--help` of an unknown step exits 0; an empty input says
    «no text column … ([])».
38. --trace: row is 0-based and undocumented; an existing trace file is overwritten without --overwrite.

## CLI: top-level commands, config, lists

39. Global `--dry-run` is ignored outside `read`: `config set` and `skill install` write for real; `init --dry-run`
    is refused.
40. `config set cli.min_version 0.2.0` (the Example of its help) locks the project, and `config set` cannot lower it
    (exit 6); the version gate is applied to some commands only (`read` with an @list, not without).
41. `config set lists …` and `config set version abc` crash with a raw pydantic error (exit 1); the documented
    `lists = [paths]` cannot be set from the CLI.
42. `init` creates `.rb_semkit/`, its help and the guide say `.semkit/`.
43. A relative SEMKIT_LISTS resolves against the project root, not the current folder; the config `lists` wins over
    SEMKIT_LISTS (undocumented); `lists add --to` a folder outside the search path gives no warning.
44. `lists show @minus/cheap` prints an error and exits 0; `lists list` does not exist though the help names it.
45. `--quiet` hides the result itself (`status`, `doctor`, `lists show`), not only the extra lines.
46. `read` in human mode never says what it wrote; `--dry-run` does not say it was one; `read` with no arguments
    exits 0; `run` is listed and is not implemented.
47. The output format, a txt target with several columns and the trace folder are checked after the steps ran (exit 1,
    temp paths in the message), not before the input is read.
48. A number column becomes text when it is the working column, or when one cell is space-padded; in an all-number
    table the first column silently becomes the working one.
49. `--json`: shapes differ between commands (`data`, `result`, top level), `doctor` unhealthy exits 0, Cyrillic is
    escaped in envelopes, `--json` after the steps is refused, `--version --json` is text; the guide's exit 3
    `auth login` does not exist.
50. The guide: «every column is read as text» (no longer true), step summaries cut at a colon, help text hard-wrapped
    mid-sentence; `dupes` needs `--action` though the guide calls it a change step.

## dataio (another tool)

51. Writing xlsx is quadratic: 10k rows 3.8 s, 100k rows 326 s, 1M rows did not end; a killed write leaves its temp
    folder. Reading the same file takes 1.3 s. This is rb_dataio's writer: an idea for dataio, and semkit's benchmark
    of a write to xlsx guards it.

## Not taken

- Real competitor texts: all texts came from one site; compare-grams was checked for its maths, not for a market.

Correct in run D: introspection (`describe` and `--ai` name the same 122 steps), doctor / init / status / auth /
config get, lists add / rm / show and the @name order, every input format (csv `,` `;` cp1251 BOM, tsv, xlsx,
parquet, json, jsonl, stdin, txt, --whole), `write -` only JSONL, OUTPUT_EXISTS, a failed step keeps the old OUT,
136 of 137 Example lines, 1M rows through 5 steps to parquet in 11.1 s (790 MB).
