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
case, ё→е, spaces), implicit (same words in another order), implicit by wordforms (same lemmas).
_Avoid_: double, повтор (a repeat is a word repeated inside one phrase)

**N-gram** (n-грамма):
A run of N words of a phrase; counted over a semantic core to build a frequency dictionary.

**Text** (текст):
Prose to analyse (an article, a review); a table of one cell, cut into phrases before the phrase steps.

**Step** (шаг):
One operation of the CLI over the current table: one library function with its arguments.

**Pipeline** (конвейер):
One command line: read, then any steps in the order written, then write. Built from steps, never a built-in scenario.
_Avoid_: scenario, recipe (a saved pipeline is the Human's shell line, not a semkit object)

**Word list** (список слов, список):
A named list of words or phrases (minus-words, stopwords, items to combine, a niche list), one per line; bundled,
or the Human's own in any folder the config names.
_Avoid_: dictionary (a dictionary is the lemma data)

<!-- Формат термина:

**Термин**:
Что это (одно-два предложения), а не что оно делает.
_Избегать_: синонимы, которые не используем

Только понятия этого проекта, без общих программистских. Без деталей реализации: это словарь, не спека. -->
