# semkit

Обработка семантического ядра: чтение и запись фраз в любом формате, леммы, n-граммы, дубли

## Словарь

**Проект**:
Каталог с `.rb_semkit/config.toml`, созданный `semkit init`; даёт командам настройки по умолчанию.
_Избегать_: workspace, рабочая папка

**Гейт**:
Полная проверка, которую код проходит перед коммитом и релизом: сборка, линтер, типы, тесты и контракты.
_Избегать_: CI, линт

**Phrase** (фраза):
One search query as a user typed it, e.g. «купить диван в москве». The unit semkit processes.
_Avoid_: keyword, query, ключ

**Semantic core** (семантическое ядро, ядро):
A list of phrases for one site or project, usually a table column.
_Avoid_: keyword list, база

**Wordform** (словоформа):
A word as it stands in a phrase: «москве», «купила».
_Avoid_: token

**Lemma** (лемма):
The dictionary form of a wordform: «москве» → «москва», «купила» → «купить».
_Avoid_: stem, normal form

**Lemmatizer** (лемматизатор):
What gives the lemma and the part of speech of a wordform. The default one uses the !SEMTools dictionary.
_Avoid_: morph analyzer, backend

**Marker list** (список маркеров):
A named list of phrases of one kind: toponyms, metro stations, question words, sale words.
_Avoid_: dictionary, словарь

**Marker** (маркер):
An item of a marker list found in a phrase.

**Stopword** (стоп-слово):
A function word that carries no search intent: prepositions, conjunctions, particles.

**Duplicate** (дубль):
A phrase that repeats an earlier one. Kinds: exact (same string), explicit (same after normalization:
case, ё→е, spaces), implicit (same words in another order), implicit by wordforms (same lemmas), by meaning (close phrase vectors, and the words that differ are only
non-refining words or synonyms).
_Avoid_: double, повтор (a repeat is a word repeated inside one phrase)

**Phrase vector** (вектор фразы, эмбеддинг):
A list of numbers a language model gives a phrase; phrases of close meaning get close vectors. The ground of the
steps by meaning; they give candidates, the Human decides.
_Avoid_: embedding in product text (say vector), semantics (the semantic core is the phrase list)

**Encoder** (модель векторов):
The model that turns a phrase into its phrase vector, chosen by name; downloaded once into the cache.
_Avoid_: LLM, neural net

**Word data** (данные слов):
The thesaurus RuWordNet and the word vectors navec; models of the same cache as the encoders, pulled once. The ground
of `synonym-candidates`: a candidate is a word they propose as a synonym, for the Human to pick.
_Avoid_: dictionary, словарь (a dictionary is a marker list or the bundled lemma dictionary)

**Non-refining word** (неуточняющее слово):
A word that does not change what a phrase asks for: a commercial word (недорого, распродажа, от производителя,
с доставкой, цены). A refining word (type, mechanism, size, material, room, brand, used, another city) makes
another intent, so two phrases that differ by it are not duplicates.
_Avoid_: modifier (too broad), stopword (a stopword is a preposition or a particle)

**Intent** (интент):
What a phrase asks for; two phrases have one intent when one landing page serves both.
_Avoid_: meaning (vague), тема

**N-gram** (n-грамма):
A run of N words of a phrase; counted over a semantic core to build a frequency dictionary.

**Text** (текст):
Prose to analyse (an article, a review); a table of one cell, cut into phrases before the phrase steps.

**Step** (шаг):
One operation of the CLI over the current table: one library function with its arguments.

**Pipeline** (конвейер):
One command line: read, then any steps in the order written, then write. Built from steps.
_Avoid_: recipe

**Workflow** (воркфлоу):
A named, saved pipeline of semkit's own steps with parameters and their defaults, run by `semkit run NAME`;
bundled or in the folder `.rb_semkit/workflows/` where semkit runs (ADR 0010, the name: ADR 0011). It records a chain,
it is not a step: each of its steps runs alone too.
_Avoid_: scenario (сценарий), run (as a noun: `run` is the command), composite step, flow (a chain over other CLIs is
built outside semkit)

**Word list** (список слов, список):
A named list of words or phrases (minus-words, stopwords, items to combine, a niche list), one per line; bundled,
or the Human's own in any folder the config names.
_Avoid_: dictionary (a dictionary is the lemma data)

<!-- Формат термина:

**Термин**:
Что это (одно-два предложения), а не что оно делает.
_Избегать_: синонимы, которые не используем

Только понятия этого проекта, без общих программистских. Без деталей реализации: это словарь, не спека. -->
