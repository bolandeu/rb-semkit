# T320: `relate-phrases` — the linguistic class of each phrase of a topic

Design on paper, 2026-10-26. No code until the go of marketer (the Human agreed to the shape: one new step, no
workflow). Asked by marketer (T320, S319); the Human's rules: deterministic only (dictionaries and lemmas), nothing
leaves the machine at run time, no vector thresholds, no LLM.

semkit gives only the class of a phrase and the phrase it belongs to. Not here: SERP, roles, frequencies, the choice
of the main phrase (the caller sorts), vectors.

## 1. Interface

One new step. Not a `dupes --kind`: it has four classes, not "duplicate or not".

    semkit read topic.csv relate-phrases [--column COL] [--to PHRASE] [--synonyms FILE] [--keep WORDS] write out.csv

- Rows are read in order; each phrase is compared with every EARLIER phrase. The first phrase is the one kept.
- `--to PHRASE`: compare every row only with this phrase (as `nearest --to`); answers "X at Y" questions directly.
- `--synonyms FILE`: extra word links of the Human, the same table as `dupes --synonyms` (columns word, synonyms).
- `--keep WORDS`: extra words that are never dropped, as @FILE or @NAME of a list (see 3.1).
- Adds three columns:
  - `class`: `same`, `variation`, `refinement` or `other`.
  - `of`: the earlier phrase it is compared with; empty for `other`.
  - `reason`: the rule and the words: `lemmas`; `создание~создать (pos_synonymy)`, `сайт~веб-сайт (synset)`,
    `web~веб (latin)`; `+москва`, `+как`; for `other`: `unlinked: разработка | создание`, or `earlier has more: как`.
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

A **unit** is a word, or two adjacent words that RuWordNet knows as one sense when joined with a hyphen or glued
(«веб сайт» → веб-сайт, «интернет сайт» → интернет-сайт). Two units are **linked** when their lemmas are equal, or
they share a synset, or their synsets are a POS-synonymy pair, or they read the same in Cyrillic, or `--synonyms`
lists them. No chains: one link, never a link of a link (no polysemy drift).

Class of phrase C at an earlier phrase H, the first rule that fits:

1. `same`: the same lemmas in any order (case, number, word order).
2. `variation`: every unit of C pairs one-to-one with a unit of H, equal or linked, at least one pair linked.
3. `refinement`: every unit of H pairs with a unit of C (equal or linked) and C has units left over: C = H (or a
   variation of H) plus more words.
4. `other`: H has a unit that C does not explain (a different word, or a word C lacks).

C takes the best class over all earlier phrases (same, variation, refinement), the earliest phrase on a tie, so
«…bosch» goes to «…бош» as a variation, not to «…машин» as a refinement. No earlier phrase fits → `other`, and
`reason` names the nearest earlier phrase and the unlinked words. The relation has a direction: a shorter phrase after
a longer one is `other` (`earlier has more: как`); the caller sorts.

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
| ремонт стиральных машин бош | ремонт стиральных машин bosch | variation | bosch reads «бощ» = бош |
| ремонт стиральных машин | ремонт стиральных машин bosch | refinement | +bosch |
| сделать сайт | как сделать сайт | refinement | +как (question word) |
| разработка сайтов | разработка сайтов москва | refinement | +москва |
| разработка сайтов | разработка сайтов под ключ | refinement | +ключ («под» is dropped) |
| создание сайтов | разработка сайтов | other | разработка ≁ создание: RuWordNet has no link |
| ремонт стиральных машин | починить стиральную машину | other | починить ≁ ремонт, ремонтировать, починка ≁ ремонт: none (see 5) |
| как создать сайт на wordpress | как создать сайт на вордпресс | variation | wordpress reads вордпресс |
| как создать сайт на wordpress | как создать сайт на wordpress в москве | refinement | +москва («в» is dropped) |
| как создать сайт на wordpress | сайт на wordpress в москве | other | earlier has more: как, создать |

## 5. Gaps of the dictionary (checked, not guessed)

- **сделать ≁ создать**: «как сделать сайт» at «как создать сайт» is `other`. сделать ~ делать are one synset.
- **починить ≁ ремонт / ремонтировать / отремонтировать**: починить sits with чинить (and починка) only.
- **разработка ≁ создание**: as the task expected.
- «веб сайт» as two words is not a RuWordNet sense; the unit rule (hyphen or glued) covers it.
- Latin words that read differently from the spelling (hyundai → хендай, xiaomi → сяоми) are not matched by the
  reading; they go to `--synonyms` or to a small bundled list.

A small bundled list of the Human's domain links (сделать = создать, починить = ремонт, …) is the cheap fix; it is the
same table as `--synonyms`, kept in `scripts/build_parts` like the lemma fixes.

## 6. Questions

1. Direction: a shorter phrase after a longer one is `other` with `earlier has more: …`. Enough, or a fifth value?
2. `other` has an empty `of` and starts a new group (the reason names the nearest earlier phrase). Does Windmill want
   `of` = that nearest phrase instead?
3. `of` is the earlier phrase that explains C best, not always the first phrase of the group (a variation of a
   variation points at its own earlier phrase). Does the caller need the first phrase of the group in a column too?
4. The three gaps of section 5 (сделать/создать, починить/ремонт, разработка/создание): start the bundled link list
   with сделать = создать and починить = ремонтировать? (разработка ≁ создание stays `other` by the acceptance.)
5. The question-word list in 3.1: any word to add (сколько стоит, чем отличается)? A multi-word item is possible.

## 7. Tests (when the go comes)

The table of section 4 as a test (red first, as the Standard asks), the 200 labelled phrase pairs of
`tests/vectors/fixtures/phrase_pairs.tsv` as a precision check (a pair labelled "different intent" must never come out
`same` or `variation`), one run on the sofa core for the speed.
