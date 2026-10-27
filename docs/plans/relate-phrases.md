# T320: `relate-phrases` — the linguistic class of each phrase of a topic

Design of 2026-10-26; the go came the same day (the Human approved, through marketer), with the answers of section 6.
Asked by marketer (T320, S319); the Human's rules: deterministic only (dictionaries and lemmas), nothing
leaves the machine at run time, no vector thresholds, no LLM.

semkit gives only the class of a phrase and the phrase it belongs to. Not here: SERP, roles, frequencies, the choice
of the main phrase (the caller sorts), vectors.

## 1. Interface

One new step. Not a `dupes --kind`: it has four classes, not "duplicate or not".

    semkit read topic.csv relate-phrases [--column COL] [--to PHRASE] [--synonyms FILE] [--keep WORDS] write out.csv

- Rows are read in order and the order is the caller's (by frequency, not by nesting). The first phrase of a group is
  the one kept. A phrase is compared with every other phrase of the table.
- `--to PHRASE`: compare every row only with this phrase (as `nearest --to`); answers "X at Y" questions directly.
- `--synonyms FILE`: the links of the topic, given per run by the caller (no bundled list). A table, read like
  `read` does, with the column `synonyms`: one group of synonyms per row, the items split by `|`, an item may be
  several words («стиральная машина | стиралка | стиральная машинка», «ремонт | починка | ремонтировать |
  починить»). Items are compared by lemmas, as runs of words. A table with the columns `word` and `synonyms` (the
  shape of `dupes --synonyms`, the synonyms split by spaces) is read too: a group of the word and its synonyms.
- `--keep WORDS`: extra words that are never dropped, as @FILE or @NAME of a list (see 3.1).
- Adds four columns:
  - `class`: `same`, `variation`, `refinement` or `other`.
  - `of`: the phrase it is `same`, a `variation` or a `refinement` of; empty for `other`.
  - `group`: the first (kept) phrase of its group (section 3).
  - `reason`: the rule and the words: `lemmas`; `создание~создать (pos_synonymy)`, `сайт~веб-сайт (synset)`,
    `web~веб (latin)`; `+москва`, `+как`; for `other`: `unlinked: разработка | создание`, or `base of: как сделать сайт`.
- Data: RuWordNet, already a semkit model (`semkit models pull ruwordnet` once on the prod worker). Same SQLite file,
  new tables read; no new download. No vectors extra needed for the step itself (to check on the worker).

## 2. Source of the part-of-speech and aspect links

Looked for ready solutions first (web search 2026-10-26; sizes and licences below come from the search summaries,
not from the files; semkit is not distributed, so a licence does not decide).

| source | what it gives | size | licence | pull | acceptance words | verdict |
|---|---|---|---|---|---|---|
| RuWordNet 2.0, tables `pos_synonymy_relation` and `derivation_relation` (already in semkit) | same meaning in another part of speech; aspect pairs sit in one synset | 59 905 synsets, 44 898 POS-synonymy pairs, 369 880 derivation pairs | not decisive | none: `models pull ruwordnet` is done | all POS, aspect and synonym words of the table; 3 gaps (section 5) | **pick** |
| DerivBase.Ru (LREC 2020) | derivational families by root | about 270 thousand words | Apache-2.0 | a new resource | not tried | no: a family joins agent nouns and prefixed verbs, like the derivation table below |
| DeriNet.RU | derivation trees | over 300 thousand words, 164 thousand relations | open (reported) | a new resource | not tried | no: the same noise, no meaning layer |
| aspect-pair lists (Zaliznyak 1987, the "empty prefixes" base with 1 426 verbs, a pilot base of Janssen and Borik) | verb aspect pairs | small | no bulk download found | — | — | not needed: RuWordNet holds the pairs checked |

The derivation table alone is too wide, checked by hand on typical query words: купить ~ покупатель, закупка,
подкупить; ремонт ~ ремонтник; заказ ~ заказчик; доставка ~ поставка. So a link is a **shared synset or a
POS-synonymy pair**; a derivation pair alone is not a link. With that rule: создание ~ создать, создавать;
разработка ~ разработать, разрабатывать; ремонт ~ отремонтировать, ремонтировать; купить ~ покупка, покупать;
заказ ~ заказать, заказывать; доставка ~ доставить; установка ~ установить; лечить ~ лечение; обучение ~ обучать
are all linked; сделать ~ делать are one synset. Known polysemy noise: купить ~ подкупить share a synset (the
"bribe" sense); `reason` names the link, so the caller can filter.

## 3. The rules

A phrase: lowercase, ё = е, lemmas from the bundled lemmatizer. Prepositions, conjunctions and particles are dropped
(the list `stop/semtools`), except the question words (3.1). A Latin word is read as Cyrillic (the `translit` table
en→ru; ш and щ count as one sound: bosch → «бощ» = «бош»; web → веб; wordpress → вордпресс).

A **unit** is a word, or a run of adjacent words (a bigram, a trigram, … up to the longest sense of RuWordNet) that
RuWordNet knows as one sense: by the lemmas of the run («стиральная машина», «ремонтные работы»), or joined with a
hyphen or glued («веб сайт» → веб-сайт, «интернет сайт» → интернет-сайт). Every n-gram of a phrase is looked up, as
`synonym-candidates` does; all the ways to cut a phrase into units are tried and the pairing that explains the most
words wins. Two units are **linked** when their lemmas are equal, or
they share a synset, or their synsets are a POS-synonymy pair, or they read the same in Cyrillic, or `--synonyms`
lists them. No chains: one link, never a link of a link (no polysemy drift).

Class of phrase C at another phrase H, the first rule that fits:

1. `same`: the same lemmas in any order (case, number, word order).
2. `variation`: every unit of C pairs one-to-one with a unit of H, equal or linked, at least one pair linked.
3. `refinement`: every unit of H pairs with a unit of C (equal or linked) and C has units left over: C = H (or a
   variation of H) plus more words. The cuts into single words take part here, and only here: a run of C can take a
   word of H («мастер по ремонту» takes «ремонт»), or hold the words of H apart («стиральных и посудомоечных машин»).
4. `other`: no phrase of the table gives C one of the three.

`same` and `variation` look only at EARLIER rows: the later phrase is the duplicate of the kept one. `refinement`
looks at all rows and decides by words, not by order: a longer phrase that holds all units of a shorter one is a
refinement of it even when it comes earlier («как сделать сайт» may be more frequent than «сделать сайт»).

C takes the best relation over the table: `same`, then `variation`, then `refinement`; among phrases of the same
class, for a refinement the base with most units (the closest), then the earliest row. So «…bosch» goes to «…бош» as
a variation, not to «…машин» as a refinement. No relation → `other`, `of` is empty, and `reason` names the nearest
phrase and the unlinked words (`unlinked: разработка | создание`) or what hangs on it (`base of: как сделать сайт`).
Every relation points to a phrase that is before it by (the number of units, the row), so the chains of `of` end.

`group`: the phrases whose chains of `of` end in the same phrase make a group; `group` is the first row of it. The
phrase at the end of a chain is `other`, and its `group` is the first row among the phrases that end in it.

### 3.1 Question words

A short bundled list, `meaning/question`, about 20 words: как, где, сколько, почему, зачем, что, какой, какая,
какое, какие, когда, куда, откуда, чем, кто, ли, можно. They stay in the phrase although the lemmatizer calls «как»
a conjunction. The marker list `questions` is not this list: it has 603 items (`10 букв`, `будет`, `больше`).

### 3.2 Speed

Lemmas and links are computed once per word of the topic, then the phrases go through an inverted index (the units
of the phrase and their linked units), not all pairs. RuWordNet loads once (about the load of `synonym-candidates`).
Expected: 1000 phrases in seconds; to measure on the sofa core in the task.

## 4. The acceptance table on paper

Word links checked by hand against the RuWordNet in the cache (`ruwordnet-2021.db`); lemma equality (rows 1, 2) is the
lemmatizer's, not run by hand; the Latin reading was run with `translit`. "H" is the earlier phrase.

| H | C | class | why |
|---|---|---|---|
| ремонт стиральных машин | ремонт стиральной машины | same | lemmas |
| ремонт стиральных машин | стиральная машина ремонт | same | lemmas, order |
| создание сайтов | создание сайта | same | lemmas |
| создание сайтов | создать сайт | variation | создание ~ создать (POS-synonymy) |
| создание сайтов | создавать сайты | variation | создание ~ создавать (POS-synonymy) |
| разработка сайтов | разработать сайт | variation | разработка ~ разработать (POS-synonymy) |
| ремонт стиральных машин | отремонтировать стиральную машину | variation | ремонт ~ отремонтировать (POS-synonymy) |
| разработка сайтов | разработка веб сайтов | variation | unit «веб сайт» = веб-сайт, one synset with сайт |
| разработка сайтов | разработка интернет сайтов | variation | unit «интернет сайт» = интернет-сайт, one synset with сайт |
| разработка веб сайтов | разработка web сайтов | variation | web reads веб |
| разработка сайтов | разработка web сайтов | variation | web reads веб, then the unit as above |
| ремонт стиральных машин | ремонтные работы стиральных машин | variation | the bigram «ремонтные работы» is a sense in the synset of ремонт |
| ремонт стиральных машин | ремонт стиралок | variation | стиралка is in the synset of the bigram «стиральная машина» (checked) |
| ремонт стиральных машин бош | ремонт стиральных машин bosch | variation | bosch reads «бощ» = бош |
| ремонт стиральных машин | ремонт стиральных машин bosch | refinement | +bosch |
| сделать сайт | как сделать сайт | refinement | +как (question word) |
| разработка сайтов | разработка сайтов москва | refinement | +москва |
| (row 1) как сделать сайт | (row 2) сделать сайт | row 1: refinement of row 2, group row 1; row 2: other, group row 1 | order does not matter: the longer phrase refines the shorter |
| разработка сайтов | разработка сайтов под ключ | refinement | +ключ («под» is dropped) |
| создание сайтов | разработка сайтов | other | разработка ≁ создание: RuWordNet has no link |
| ремонт стиральных машин | починить стиральную машину | other | починить ≁ ремонт, ремонтировать, починка ≁ ремонт: none (see 5) |
| как создать сайт на wordpress | как создать сайт на вордпресс | variation | wordpress reads вордпресс |
| как создать сайт на wordpress | как создать сайт на wordpress в москве | refinement | +москва («в» is dropped) |
| как создать сайт на wordpress | сайт на wordpress в москве | other | no phrase explains it: unlinked как, создать |

## 5. Gaps of the dictionary (checked, not guessed)

- **сделать ≁ создать**: «как сделать сайт» at «как создать сайт» is `other`. сделать ~ делать are one synset.
- **починить ≁ ремонт / ремонтировать / отремонтировать**: починить sits with чинить (and починка) only.
- **разработка ≁ создание**: as the task expected.
- «веб сайт» as two words is not a RuWordNet sense; the unit rule (hyphen or glued) covers it.
- Latin words that read differently from the spelling (hyundai → хендай, xiaomi → сяоми) are not matched by the
  reading; they go to `--synonyms` or to a small bundled list.

Looked for another dictionary that joins them (2026-10-26); none does, and they are not synonyms without context:
- RuWordNet at the level of phrases: it has the sense «разработка веб-сайта» (synset: разработка веб-сайта,
  веб-разработка) and no «создание сайта» anywhere. «разработка X» and «создание X» share a synset only for other
  objects (бренд, вооружения). The unit rule catches such phrase senses by itself, but not for сайт.
- The synset of «сделать» holds делать, выполнить, реализовать, изготовить, произвести… not «создать».
- The word vectors (navec, `synonym-candidates`): сделать → деланный, нужный; создать → формируть, создавая;
  починить → отремонтировать 0.79, ремонтировать 0.60; ремонт → капитальный, … починка 0.48. Only починить helps, and
  a vector is a candidate, not a link.
- No open file of the synonym dictionary of Abramov or similar was found (the old 1911 edition in mythes format with
  dated words; the modern ones are printed or sold).
- Linguistically «сделать сайт» = «создать сайт» holds in this collocation only («сделать ремонт» ≠ «создать ремонт»):
  a link of intent, not of the dictionary. The caller's SERP check decides it; a confirmed pair goes to the own list.

The links of a topic that the dictionaries lack come with each run in `--synonyms` (from Windmill: the LLM grouping and
the right column of Wordstat); no list is bundled (marketer, 2026-10-26).

## 6. Answers of marketer (2026-10-26)

1. Refinement is decided by words, not by order (section 3).
2. `of` stays empty for `other`.
3. The column `group` is added: the first (kept) phrase of the group.
4. No bundled link list; the links of a topic come per run in `--synonyms`, groups of synonyms with items of several
   words (the shape is in section 1).
5. The question-word list (3.1) is enough.

## 7. Tests (when the go comes)

The table of section 4 as a test (red first, as the Standard asks), the 200 labelled phrase pairs of
`tests/vectors/fixtures/phrase_pairs.tsv` as a precision check (a pair labelled "different intent" must never come out
`same` or `variation`), one run on the sofa core for the speed.
