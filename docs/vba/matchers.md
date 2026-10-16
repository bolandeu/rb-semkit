# !SEMTools VBA reference: text matchers and markers

What the add-in does for each button of the find («Обнаружить»), remove («Удалить») and extract («Извлечь») menus that
work on text: chars, words, phrases, markers, cells. A Python port copies the algorithm from here and does not open the VBA.

Sources (read-only, traced by hand):
- `/Users/bolandau/Work/_sandbox/semtools/reverse/vba/RibbonCallbacks.vba` — all line numbers below point into this file.
  Most lines hold a whole procedure (statements joined by `: `); a line range is the first and the last physical line.
- `/Users/bolandau/Work/_sandbox/semtools/reverse/ribbon_full.txt` — menu paths and handler names.
- `/Users/bolandau/Work/_sandbox/semtools/reverse/vba/frmCombo.frm` — the multi-list form.
- `/Users/bolandau/Work/_sandbox/semtools/reverse/downloads/spiski/*.xlsx` — the marker lists (worked examples with markers use them).
- ADR 0005 (`docs/adr/0005-port-vba-fix-defects.md`): follow the VBA, deviate only for the listed defects.

Scope: 255 buttons. Excel-only buttons of the same menus (bold/italic, duplicates, sheets, columns, formulas, pictures,
attributes, counts) are not listed. Duplicates, n-grams and the lemmatizer are ported already (SEMKIT-003/004).

## How to read an entry

- **Handler** — the ribbon callback; **helpers** — the procedures it calls, with their lines. Obfuscated names are kept
  verbatim (`—`, `–`, `·` are em dash, en dash, middle dot; `­` is a soft hyphen; `о` in some names is Cyrillic).
- **Plain / Ignore-punctuation** — two variants chosen by the ribbon checkbox «Игнорировать пунктуацию» (S2).
  The default (checkbox off) is **plain**; port the plain variant, the other one is documented for completeness.
- **Token** — an item of `Split(text, " ")`: VBA splits on the single space only (S3).
- Case-insensitive in VBA means «both sides through `UCase`/`LCase`, then exact compare»; ё and е stay different.
- «ADR 0005 deviation» names the deviations from ADR 0005 that apply: ё = е; stopwords case-insensitive; split on any
  whitespace; no double spaces in results; markers in the list spelling joined by ', '; empty cells are never
  duplicates; lemmas in lower case. A «Fix:» there marks a VBA bug the port should not copy (a question for the Architect
  when it changes an existing acceptance line).

## Index

255 buttons. «Section» links to the group; inside it the entries follow the ribbon order.

| # | Menu path | Handler | Section |
|---|---|---|---|
| 1 | ОБНАРУЖИТЬ > Символы > По типу > Выделить цветом > Латиницу | `HL_Lat` | [F1](#f1) |
| 2 | ОБНАРУЖИТЬ > Символы > По типу > Выделить цветом > Кириллицу | `HL_Cyr` | [F1](#f1) |
| 3 | ОБНАРУЖИТЬ > Символы > По типу > Выделить цветом > Цифры | `HL_Num` | [F1](#f1) |
| 4 | ОБНАРУЖИТЬ > Символы > По типу > Вернуть ИСТИНА (шустрее) > Буквы-цифры | `—kko` | [F1](#f1) |
| 5 | ОБНАРУЖИТЬ > Символы > По типу > Вернуть ИСТИНА (шустрее) > Латиницу | `—·k—` | [F1](#f1) |
| 6 | ОБНАРУЖИТЬ > Символы > По типу > Вернуть ИСТИНА (шустрее) > Кириллицу | `—·k–` | [F1](#f1) |
| 7 | ОБНАРУЖИТЬ > Символы > По типу > Вернуть ИСТИНА (шустрее) > Цифры | `—·ka` | [F1](#f1) |
| 8 | ОБНАРУЖИТЬ > Символы > Заглавные | `—·ok` | [F1](#f1) |
| 9 | ОБНАРУЖИТЬ > Символы > UA символы/сочетания | `—·k·` | [F1](#f1) |
| 10 | ОБНАРУЖИТЬ > Слова > Целые слова > 1 слово | `–––o` | [F2](#f2) |
| 11 | ОБНАРУЖИТЬ > Слова > Целые слова > Все из списка | `–––k` | [F2](#f2) |
| 12 | ОБНАРУЖИТЬ > Слова > Целые слова > Любое из списка | `—k—k` | [F2](#f2) |
| 13 | ОБНАРУЖИТЬ > Слова > Целые слова > Части речи... > Существительные | `—k–a` | [F2](#f2) |
| 14 | ОБНАРУЖИТЬ > Слова > Целые слова > Части речи... > Прилагательные | `–···` | [F2](#f2) |
| 15 | ОБНАРУЖИТЬ > Слова > Целые слова > Части речи... > Глаголы | `—k—·` | [F2](#f2) |
| 16 | ОБНАРУЖИТЬ > Слова > Целые слова > Части речи... > Наречия | `—kkk` | [F2](#f2) |
| 17 | ОБНАРУЖИТЬ > Слова > Содержащие... > В начале > Паттерн | `—ka—` | [F2](#f2) |
| 18 | ОБНАРУЖИТЬ > Слова > Содержащие... > В начале > Список паттернов | `—kaa` | [F2](#f2) |
| 19 | ОБНАРУЖИТЬ > Слова > Содержащие... > В конце... > Паттерн | `—kao` | [F2](#f2) |
| 20 | ОБНАРУЖИТЬ > Слова > Содержащие... > В конце... > Список паттернов | `—ka–` | [F2](#f2) |
| 21 | ОБНАРУЖИТЬ > Слова > Содержащие... > Где угодно > Паттерн | `SEM_findCellsContainingPattern` | [F2](#f2) |
| 22 | ОБНАРУЖИТЬ > Слова > Содержащие... > Где угодно > Список паттернов | `—kk—` | [F2](#f2) |
| 23 | ОБНАРУЖИТЬ > Слова > По регистру > строчные | `aakL` | [F2](#f2) |
| 24 | ОБНАРУЖИТЬ > Слова > По регистру > 1 Заглавная | `aakP` | [F2](#f2) |
| 25 | ОБНАРУЖИТЬ > Слова > По регистру > ВСЕ КАПСОМ | `aakC` | [F2](#f2) |
| 26 | ОБНАРУЖИТЬ > Слова > По паттерну REGEX | `—kak` | [F2](#f2) |
| 27 | ОБНАРУЖИТЬ > Слова > Повторяющиеся слова | `—k—–` | [F2](#f2) |
| 28 | ОБНАРУЖИТЬ > Фразы > Свой список | `—k—k` | [F3](#f3) |
| 29 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Все | `—k——` | [F3](#f3) |
| 30 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Метро МСК | `—k—6` | [F3](#f3) |
| 31 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Районы МСК | `—k—7` | [F3](#f3) |
| 32 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Пункты МО | `—k—8` | [F3](#f3) |
| 33 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Населённые пункты РФ | `—k—9` | [F3](#f3) |
| 34 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > Маркеры вопросов | `—k—o` | [F3](#f3) |
| 35 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > Игры и развлечения | `—k—3` | [F3](#f3) |
| 36 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > DIY (самодеятельность) | `—k—4` | [F3](#f3) |
| 37 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > Образование | `—k—01` | [F3](#f3) |
| 38 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > Названия игр | `—k—02` | [F3](#f3) |
| 39 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > E-com > Продажи | `—k—l` | [F3](#f3) |
| 40 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > E-com > Аренда | `—k—00` | [F3](#f3) |
| 41 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > E-com > Отзывы | `—k—2` | [F3](#f3) |
| 42 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Характеристики > Цвет | `—k—0` | [F3](#f3) |
| 43 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Характеристики > Материал | `—k—03` | [F3](#f3) |
| 44 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Характеристики > Происхождение (страна) | `—k—04` | [F3](#f3) |
| 45 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Тематические > Марки и модели авто | `—k—5` | [F3](#f3) |
| 46 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Тематические > Имена (им.п) | `—k—05` | [F3](#f3) |
| 47 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Поиск по нескольким спискам | `RbnFind` | [F3](#f3) |
| 48 | ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Обновить все списки | `––kak` | [F3](#f3) |
| 49 | ОБНАРУЖИТЬ > Ячейки > По содержимому > Содержащие (указать список) | `—kk—` | [F4](#f4) |
| 50 | ОБНАРУЖИТЬ > Ячейки > По содержимому > Начинающиеся на > Указать список... | `—ko·` | [F4](#f4) |
| 51 | ОБНАРУЖИТЬ > Ячейки > По содержимому > Начинающиеся на > Предлоги | `findFFWprps` | [F4](#f4) |
| 52 | ОБНАРУЖИТЬ > Ячейки > По содержимому > Заканчивающиеся на > Указать список... | `—koo` | [F4](#f4) |
| 53 | ОБНАРУЖИТЬ > Ячейки > По содержимому > Заканчивающиеся на > Предлоги | `findFLWprps` | [F4](#f4) |
| 54 | ОБНАРУЖИТЬ > Ячейки > По паттерну REGEX | `—koa` | [F4](#f4) |
| 55 | ОБНАРУЖИТЬ > Ячейки > По встречаемости > Не повторяющиеся | `—k—a` | [F4](#f4) |
| 56 | ОБНАРУЖИТЬ > Ячейки > По встречаемости > Повторяющиеся | `—k–—` | [F4](#f4) |
| 57 | ОБНАРУЖИТЬ > Ячейки > По встречаемости > Первая | `—k–k` | [F4](#f4) |
| 58 | ОБНАРУЖИТЬ > Ячейки > По встречаемости > Последняя | `—k––` | [F4](#f4) |
| 59 | ОБНАРУЖИТЬ > Ячейки > Пустые ячейки | `—kk–` | [F4](#f4) |
| 60 | УДАЛИТЬ > Символы > По типу > Пунктуацию | `aok—` | [R1](#r1) |
| 61 | УДАЛИТЬ > Символы > По типу > Лишние пробелы > Все | `–aal` | [R1](#r1) |
| 62 | УДАЛИТЬ > Символы > По типу > Лишние пробелы > Слева | `—ako` | [R1](#r1) |
| 63 | УДАЛИТЬ > Символы > По типу > Лишние пробелы > Справа | `a–o—` | [R1](#r1) |
| 64 | УДАЛИТЬ > Символы > По типу > Лишние пробелы > Слева и справа | `a–k—` | [R1](#r1) |
| 65 | УДАЛИТЬ > Символы > По типу > Цифры | `aokk` | [R1](#r1) |
| 66 | УДАЛИТЬ > Символы > По типу > Латиницу | `ak·—` | [R1](#r1) |
| 67 | УДАЛИТЬ > Символы > По типу > Кириллицу | `ak–·` | [R1](#r1) |
| 68 | УДАЛИТЬ > Символы > По позиции... > С начала ячейки | `ak——` | [R1](#r1) |
| 69 | УДАЛИТЬ > Символы > По позиции... > С конца ячейки | `ak·k` | [R1](#r1) |
| 70 | УДАЛИТЬ > Символы > До вхожд-я... > Первого > Включительно | `––·a` | [R1](#r1) |
| 71 | УДАЛИТЬ > Символы > До вхожд-я... > Первого > Все что перед ним | `––·—` | [R1](#r1) |
| 72 | УДАЛИТЬ > Символы > До вхожд-я... > Последнего > Включительно | `–—kk` | [R1](#r1) |
| 73 | УДАЛИТЬ > Символы > До вхожд-я... > Последнего > Все что перед ним | `––··` | [R1](#r1) |
| 74 | УДАЛИТЬ > Символы > После вхожд-я... > Первого > Включительно | `––—–` | [R1](#r1) |
| 75 | УДАЛИТЬ > Символы > После вхожд-я... > Первого > Все что после | `––—o` | [R1](#r1) |
| 76 | УДАЛИТЬ > Символы > После вхожд-я... > Последнего > Включительно | `––—a` | [R1](#r1) |
| 77 | УДАЛИТЬ > Символы > После вхожд-я... > Последнего > Все что после | `––——` | [R1](#r1) |
| 78 | УДАЛИТЬ > Символы > по REGEX... > Все, попадающее под паттерн | `aoka` | [R1](#r1) |
| 79 | УДАЛИТЬ > Символы > по REGEX... > Все, НЕ попадающее под паттерн | `aok·` | [R1](#r1) |
| 80 | УДАЛИТЬ > Слова > Целые слова > 1 слово | `ao—a` | [R2](#r2) |
| 81 | УДАЛИТЬ > Слова > Целые слова > Указать список... > Удалить все | `aok–` | [R2](#r2) |
| 82 | УДАЛИТЬ > Слова > Целые слова > Указать список... > Только в начале строки | `dFWCustom` | [R2](#r2) |
| 83 | УДАЛИТЬ > Слова > Целые слова > Указать список... > Только в конце строки | `dLWCustom` | [R2](#r2) |
| 84 | УДАЛИТЬ > Слова > Целые слова > Части речи... > Существительные | `ak··` | [R2](#r2) |
| 85 | УДАЛИТЬ > Слова > Целые слова > Части речи... > Прилагательные | `—··a` | [R2](#r2) |
| 86 | УДАЛИТЬ > Слова > Целые слова > Части речи... > Глаголы | `ao——` | [R2](#r2) |
| 87 | УДАЛИТЬ > Слова > Целые слова > Части речи... > Наречия | `—···` | [R2](#r2) |
| 88 | УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Паттерн | `aoak` | [R2](#r2) |
| 89 | УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Список паттернов | `aoao` | [R2](#r2) |
| 90 | УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Только латиницу | `a·—–` | [R2](#r2) |
| 91 | УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Латиницу | `a·a–` | [R2](#r2) |
| 92 | УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Только цифры | `a·——` | [R2](#r2) |
| 93 | УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Цифры | `a·a—` | [R2](#r2) |
| 94 | УДАЛИТЬ > Слова > По содержимому... > Начинающиеся на... > Паттерн | `aoaa` | [R2](#r2) |
| 95 | УДАЛИТЬ > Слова > По содержимому... > Начинающиеся на... > Список паттернов | `aoa·` | [R2](#r2) |
| 96 | УДАЛИТЬ > Слова > По содержимому... > Заканчивающиеся на... > Паттерн | `aoa–` | [R2](#r2) |
| 97 | УДАЛИТЬ > Слова > По содержимому... > Заканчивающиеся на... > Список паттернов | `aoa—` | [R2](#r2) |
| 98 | УДАЛИТЬ > Слова > По паттерну REGEX | `––·k` | [R2](#r2) |
| 99 | УДАЛИТЬ > Слова > По порядку... > Первые... > 1 | `ak—k` | [R2](#r2) |
| 100 | УДАЛИТЬ > Слова > По порядку... > Первые... > 2 | `ak—o` | [R2](#r2) |
| 101 | УДАЛИТЬ > Слова > По порядку... > Первые... > 3 | `ak—–` | [R2](#r2) |
| 102 | УДАЛИТЬ > Слова > По порядку... > Первые... > N | `ak—a` | [R2](#r2) |
| 103 | УДАЛИТЬ > Слова > По порядку... > Последние... > 1 | `aka—` | [R2](#r2) |
| 104 | УДАЛИТЬ > Слова > По порядку... > Последние... > 2 | `akaa` | [R2](#r2) |
| 105 | УДАЛИТЬ > Слова > По порядку... > Последние... > 3 | `aka·` | [R2](#r2) |
| 106 | УДАЛИТЬ > Слова > По порядку... > Последние... > N | `ak·o` | [R2](#r2) |
| 107 | УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Все | `aala` | [R2](#r2) |
| 108 | УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Только англ. слов | `aal1` | [R2](#r2) |
| 109 | УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Только русских слов | `aall` | [R2](#r2) |
| 110 | УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Только идущие подряд | `remrepW` | [R2](#r2) |
| 111 | УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Только чисел | `aal·` | [R2](#r2) |
| 112 | УДАЛИТЬ > Слова > Повторы слов... > С учетом словоформ (Ru) | `aook` | [R2](#r2) |
| 113 | УДАЛИТЬ > Фразы > Свой список фраз | `aok–` | [R3](#r3) |
| 114 | УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Все > С предлогами | `a·—a` | [R3](#r3) |
| 115 | УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Все > Без предлогов | `a·–a` | [R3](#r3) |
| 116 | УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Метро МСК | `a·a6` | [R3](#r3) |
| 117 | УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Районы МСК | `a·a7` | [R3](#r3) |
| 118 | УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Пункты МО | `a·a8` | [R3](#r3) |
| 119 | УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Населённые пункты РФ | `a·a9` | [R3](#r3) |
| 120 | УДАЛИТЬ > Фразы > Удалить маркеры... > Минус-слова > Игры и развлечения | `a·a3` | [R3](#r3) |
| 121 | УДАЛИТЬ > Фразы > Удалить маркеры... > Минус-слова > DIY (самодеятельность) | `a·a4` | [R3](#r3) |
| 122 | УДАЛИТЬ > Фразы > Удалить маркеры... > Минус-слова > Образование | `a·a01` | [R3](#r3) |
| 123 | УДАЛИТЬ > Фразы > Удалить маркеры... > Минус-слова > Названия игр | `a·a02` | [R3](#r3) |
| 124 | УДАЛИТЬ > Фразы > Удалить маркеры... > E-com > Продажи | `a·al` | [R3](#r3) |
| 125 | УДАЛИТЬ > Фразы > Удалить маркеры... > E-com > Аренда | `a·a·` | [R3](#r3) |
| 126 | УДАЛИТЬ > Фразы > Удалить маркеры... > E-com > Отзывы | `a·a2` | [R3](#r3) |
| 127 | УДАЛИТЬ > Фразы > Удалить маркеры... > Характеристики > Цвет | `a·a0` | [R3](#r3) |
| 128 | УДАЛИТЬ > Фразы > Удалить маркеры... > Характеристики > Материал | `a·a03` | [R3](#r3) |
| 129 | УДАЛИТЬ > Фразы > Удалить маркеры... > Характеристики > Происхождение (страна) | `a·a04` | [R3](#r3) |
| 130 | УДАЛИТЬ > Фразы > Удалить маркеры... > Тематические > Марки и модели авто | `a·a5` | [R3](#r3) |
| 131 | УДАЛИТЬ > Фразы > Удалить маркеры... > Тематические > Имена | `a·a05` | [R3](#r3) |
| 132 | УДАЛИТЬ > Фразы > Удалить маркеры... > Удаление нескольких списков фраз | `RbnDelete` | [R3](#r3) |
| 133 | УДАЛИТЬ > Фразы > Удалить маркеры... > Обновить все списки | `––kak` | [R3](#r3) |
| 134 | УДАЛИТЬ > Ячейки > По содержимому > Пустые ячейки > Со смещением вверх | `remBlankCellsUp` | [R4](#r4) |
| 135 | УДАЛИТЬ > Ячейки > По содержимому > Пустые ячейки > Со смещением влево | `remBlankCellsLeft` | [R4](#r4) |
| 136 | УДАЛИТЬ > Ячейки > По содержимому > Содержащие любое из списка > Где угодно | `akok` | [R4](#r4) |
| 137 | УДАЛИТЬ > Ячейки > По содержимому > Содержащие любое из списка > В начале ячейки | `ak–a` | [R4](#r4) |
| 138 | УДАЛИТЬ > Ячейки > По содержимому > Содержащие любое из списка > В конце ячейки | `ak–k` | [R4](#r4) |
| 139 | УДАЛИТЬ > Ячейки > По содержимому > Содержащие слова > 1 слово | `akoo` | [R4](#r4) |
| 140 | УДАЛИТЬ > Ячейки > По содержимому > Содержащие слова > Любое из списка | `ako–` | [R4](#r4) |
| 141 | УДАЛИТЬ > Ячейки > По содержимому > По REGEX-паттерну | `akk·` | [R4](#r4) |
| 142 | УДАЛИТЬ > Ячейки > По встречаемости > Не повторяющиеся | `ao—–` | [R4](#r4) |
| 143 | УДАЛИТЬ > Ячейки > По встречаемости > Повторяющиеся | `ak·a` | [R4](#r4) |
| 144 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Ничего | `aooo` | [R5](#r5) |
| 145 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Букв или цифр | `ao–·` | [R5](#r5) |
| 146 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Латиницы | `ao—k` | [R5](#r5) |
| 147 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Цифр | `ao—o` | [R5](#r5) |
| 148 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Слов > Конкретного слова | `aoo·` | [R5](#r5) |
| 149 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Слов > Ни одного из списка | `ao–k` | [R5](#r5) |
| 150 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Латиницу | `aoo–` | [R5](#r5) |
| 151 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Цифры | `aoo—` | [R5](#r5) |
| 152 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Слова > Одно слово | `ao––` | [R5](#r5) |
| 153 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Слова > Любое из списка | `aooa` | [R5](#r5) |
| 154 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Слова > Слова из цифр | `ao–o` | [R5](#r5) |
| 155 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если длина содержимого... > Меньше | `ao–a` | [R5](#r5) |
| 156 | УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если длина содержимого... > Больше | `ao–—` | [R5](#r5) |
| 157 | ИЗВЛЕЧЬ > Символы > По порядку > Первые N | `–—·–` | [X1](#x1) |
| 158 | ИЗВЛЕЧЬ > Символы > По порядку > Последние N | `–ak·` | [X1](#x1) |
| 159 | ИЗВЛЕЧЬ > Символы > По типу > Английский (Латиницу) | `–ako` | [X1](#x1) |
| 160 | ИЗВЛЕЧЬ > Символы > По типу > Русский (Кириллицу) | `–—–a` | [X1](#x1) |
| 161 | ИЗВЛЕЧЬ > Символы > По типу > Любые буквы | `–·o–` | [X1](#x1) |
| 162 | ИЗВЛЕЧЬ > Символы > По типу > Цифры | `–·ko` | [X1](#x1) |
| 163 | ИЗВЛЕЧЬ > Символы > По типу > Любые буквы и цифры | `aok—` | [X1](#x1) |
| 164 | ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Ввести свой, 1 совпадение | `–a—–` | [X1](#x1) |
| 165 | ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Ввести свой, все совпадения | `–a——` | [X1](#x1) |
| 166 | ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > Домены (с субдоменами) | `a·k–` | [X1](#x1) |
| 167 | ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > Даты > в формате DDMMYYYY | `–a—a` | [X1](#x1) |
| 168 | ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > Даты > в формате YYYYMMDD | `–aa–` | [X1](#x1) |
| 169 | ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > e-mail-ы | `–a—·` | [X1](#x1) |
| 170 | ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > Номера телефона (RU) | `–aak` | [X1](#x1) |
| 171 | ИЗВЛЕЧЬ > Символы > Часть до... > Первого вхождения, включая | `–—–o` | [X1](#x1) |
| 172 | ИЗВЛЕЧЬ > Символы > Часть до... > Первого вхождения, не включая | `–—––` | [X1](#x1) |
| 173 | ИЗВЛЕЧЬ > Символы > Часть после... > Последнего вхождения, включая | `–—o·` | [X1](#x1) |
| 174 | ИЗВЛЕЧЬ > Символы > Часть после... > Последнего вхождения, не включая | `–—–k` | [X1](#x1) |
| 175 | ИЗВЛЕЧЬ > Слова > Целые слова > 1 слово | `–·oo` | [X2](#x2) |
| 176 | ИЗВЛЕЧЬ > Слова > Целые слова > Указать список | `–a–a` | [X2](#x2) |
| 177 | ИЗВЛЕЧЬ > Слова > Целые слова > Части речи... > Существительные | `–ao·` | [X2](#x2) |
| 178 | ИЗВЛЕЧЬ > Слова > Целые слова > Части речи... > Прилагательные | `–—o—` | [X2](#x2) |
| 179 | ИЗВЛЕЧЬ > Слова > Целые слова > Части речи... > Глаголы | `–·ka` | [X2](#x2) |
| 180 | ИЗВЛЕЧЬ > Слова > Целые слова > Части речи... > Наречия | `–—oa` | [X2](#x2) |
| 181 | ИЗВЛЕЧЬ > Слова > Паттерны из списка > Префиксы | `–a—k` | [X2](#x2) |
| 182 | ИЗВЛЕЧЬ > Слова > Паттерны из списка > Суффиксы | `–aa·` | [X2](#x2) |
| 183 | ИЗВЛЕЧЬ > Слова > Паттерны из списка > Любые вхождения | `—·—k` | [X2](#x2) |
| 184 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Список паттернов | `–·k·` | [X2](#x2) |
| 185 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Латиницу | `–—k—` | [X2](#x2) |
| 186 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Цифры | `–—k–` | [X2](#x2) |
| 187 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Буквы и цифры | `a·o–` | [X2](#x2) |
| 188 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Только... > кириллицу | `a·o—` | [X2](#x2) |
| 189 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Только... > цифры | `——·—` | [X2](#x2) |
| 190 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Только... > латиницу | `——·–` | [X2](#x2) |
| 191 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > И... > Латиницу и кириллицу | `–—ka` | [X2](#x2) |
| 192 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > И... > Латиницу и цифры | `–—k·` | [X2](#x2) |
| 193 | ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > И... > Кириллицу и цифры | `–—ko` | [X2](#x2) |
| 194 | ИЗВЛЕЧЬ > Слова > Содержащие > В начале... > Паттерн | `–·–a` | [X2](#x2) |
| 195 | ИЗВЛЕЧЬ > Слова > Содержащие > В начале... > Список паттернов | `–·–·` | [X2](#x2) |
| 196 | ИЗВЛЕЧЬ > Слова > Содержащие > В конце... > Паттерн | `–·––` | [X2](#x2) |
| 197 | ИЗВЛЕЧЬ > Слова > Содержащие > В конце... > Список паттернов | `–·–—` | [X2](#x2) |
| 198 | ИЗВЛЕЧЬ > Слова > По порядку... > Первые... > 1 | `–—a—` | [X2](#x2) |
| 199 | ИЗВЛЕЧЬ > Слова > По порядку... > Первые... > 2 | `–—aa` | [X2](#x2) |
| 200 | ИЗВЛЕЧЬ > Слова > По порядку... > Первые... > 3 | `–—a·` | [X2](#x2) |
| 201 | ИЗВЛЕЧЬ > Слова > По порядку... > Первые... > N | `–—·—` | [X2](#x2) |
| 202 | ИЗВЛЕЧЬ > Слова > По порядку... > Последние... > 1 | `–ak–` | [X2](#x2) |
| 203 | ИЗВЛЕЧЬ > Слова > По порядку... > Последние... > 2 | `–ak—` | [X2](#x2) |
| 204 | ИЗВЛЕЧЬ > Слова > По порядку... > Последние... > 3 | `–aka` | [X2](#x2) |
| 205 | ИЗВЛЕЧЬ > Слова > По порядку... > Последние... > N | `–aok` | [X2](#x2) |
| 206 | ИЗВЛЕЧЬ > Слова > По порядку... > N-е слово > 1-е | `–—a—` | [X2](#x2) |
| 207 | ИЗВЛЕЧЬ > Слова > По порядку... > N-е слово > 2-е | `–—oo` | [X2](#x2) |
| 208 | ИЗВЛЕЧЬ > Слова > По порядку... > N-е слово > 3-е | `–—o–` | [X2](#x2) |
| 209 | ИЗВЛЕЧЬ > Слова > По порядку... > N-е слово > N-е | `–a–k` | [X2](#x2) |
| 210 | ИЗВЛЕЧЬ > Слова > До позиции в строке... > До середины | `–·—k` | [X2](#x2) |
| 211 | ИЗВЛЕЧЬ > Слова > До позиции в строке... > Не более чем... | `–·—o` | [X2](#x2) |
| 212 | ИЗВЛЕЧЬ > Слова > По REGEX-паттерну | `–·–o` | [X2](#x2) |
| 213 | ИЗВЛЕЧЬ > Слова > Слова с заглавными | `–·ok` | [X2](#x2) |
| 214 | ИЗВЛЕЧЬ > Фразы > Свой список фраз | `–a–a` | [X3](#x3) |
| 215 | ИЗВЛЕЧЬ > Фразы > Дополнения с предлогами | `findCollocs` | [X3](#x3) |
| 216 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Все топонимы > С предлогами | `–·kk` | [X3](#x3) |
| 217 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Все топонимы > Без предлогов | `–a·a` | [X3](#x3) |
| 218 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Метро МСК | `——aa4` | [X3](#x3) |
| 219 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Районы МСК | `——aa5` | [X3](#x3) |
| 220 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Пункты МО | `——aa6` | [X3](#x3) |
| 221 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Населенные пункты РФ | `——aa7` | [X3](#x3) |
| 222 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > Маркеры вопросов | `–a—o` | [X3](#x3) |
| 223 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > Игры и развлечения | `——aa1` | [X3](#x3) |
| 224 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > DIY (самодеятельность) | `——aa2` | [X3](#x3) |
| 225 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > Образование | `——aa9` | [X3](#x3) |
| 226 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > Названия игр | `——aa0` | [X3](#x3) |
| 227 | ИЗВЛЕЧЬ > Фразы > Маркеры... > E-com > Продажи | `——·k` | [X3](#x3) |
| 228 | ИЗВЛЕЧЬ > Фразы > Маркеры... > E-com > Аренды | `——aa` | [X3](#x3) |
| 229 | ИЗВЛЕЧЬ > Фразы > Маркеры... > E-com > Отзывов | `——a·` | [X3](#x3) |
| 230 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Характеристики > Цвет | `——aa8` | [X3](#x3) |
| 231 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Характеристики > Материал | `——aa01` | [X3](#x3) |
| 232 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Характеристики > Происхождение (страна) | `——aa02` | [X3](#x3) |
| 233 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Тематические > Марки и модели авто | `——aa3` | [X3](#x3) |
| 234 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Тематические > Имена (Им.п) | `ruNames` | [X3](#x3) |
| 235 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Извлечение нескольких списков фраз | `RbnExtract` | [X3](#x3) |
| 236 | ИЗВЛЕЧЬ > Фразы > Маркеры... > Обновить все списки | `––kak` | [X3](#x3) |
| 237 | ИЗВЛЕЧЬ > Ячейки > Содержащие > Слова... > Указать слово | `–——o` | [X4](#x4) |
| 238 | ИЗВЛЕЧЬ > Ячейки > Содержащие > Слова... > Указать список слов | `–——–` | [X4](#x4) |
| 239 | ИЗВЛЕЧЬ > Ячейки > Содержащие > Слова... > Слова из латиницы | `—·o—` | [X4](#x4) |
| 240 | ИЗВЛЕЧЬ > Ячейки > Содержащие > Украинский | `—·–o` | [X4](#x4) |
| 241 | ИЗВЛЕЧЬ > Ячейки > Содержащие > Цифры | `—·oa` | [X4](#x4) |
| 242 | ИЗВЛЕЧЬ > Ячейки > Содержащие > Латиницу | `–aaa` | [X4](#x4) |
| 243 | ИЗВЛЕЧЬ > Ячейки > Содержащие > Заглавные буквы | `—·–k` | [X4](#x4) |
| 244 | ИЗВЛЕЧЬ > Ячейки > По REGEX-паттерну | `—·–a` | [X4](#x4) |
| 245 | ИЗВЛЕЧЬ > Ячейки > По списку критериев > Содержащие | `–——k` | [X4](#x4) |
| 246 | ИЗВЛЕЧЬ > Ячейки > По списку критериев > Начинающиеся с | `—·–·` | [X4](#x4) |
| 247 | ИЗВЛЕЧЬ > Ячейки > По списку критериев > Заканчивающиеся на | `—·––` | [X4](#x4) |
| 248 | ИЗВЛЕЧЬ > Ячейки > По встречаемости > Не повторяющиеся | `–·k—` | [X4](#x4) |
| 249 | ИЗВЛЕЧЬ > Ячейки > По встречаемости > Повторяющиеся | `–aoa` | [X4](#x4) |
| 250 | ИЗВЛЕЧЬ > Ячейки > Из другого диапазона | `—·–—` | [X4](#x4) |
| 251 | Web (Парсинг, SEO, PPC) > Удалить > Из текста > Стоп-слова | `a·–·` | [W1](#w1) |
| 252 | Web (Парсинг, SEO, PPC) > Удалить > Из текста > Предлоги в конце фраз | `remLWprps` | [W1](#w1) |
| 253 | Web (Парсинг, SEO, PPC) > Удалить > Из текста > Маркеры покупки в конце фраз | `remLWsales` | [W1](#w1) |
| 254 | Web (Парсинг, SEO, PPC) > Удалить > Из текста > Повторы слов во всем столбце (разделитель пробел) | `aoko` | [W1](#w1) |
| 255 | Web (Парсинг, SEO, PPC) > Удалить > Из текста > Повторы фраз во всем столбце (разделитель запятая с пробелом) | `aoko2` | [W1](#w1) |


## Shared helpers

<a id="s1"></a>
### S1. Handler frame: input and output

Most handlers are the same frame around one per-cell function.

1. `·l` (line 2753): when a whole column is selected (1 048 576 rows), shrink the selection to the data of that column
   (from the top to the last non-empty cell). `k–—` (line 2150) does the same in the area frame.
2. `·——` (line 2631): copy the selection to sheet `def` for the ribbon «Отмена» button (`retP`). Ignore in the port.
3. `a–` (line 2667) / `—k` (line 2344): screen updating and calculation off / on. Some handlers exit between the two and leave
   Excel with screen updating off (noted as «does nothing» in the entries).
4. Read: `zSel` (line 2752) = `Selection.Value2` as a 2-D array (one cell is wrapped into a 1×1 array).
   - **zSel frame**: every row × every column of the selection, one function call per cell.
   - **Area frame** (`k–` (line 1937), `·a` (line 441), `–1` (line 442) and the inline loops): every area of a multi-area selection,
     every column, every row; a one-cell area gets the function of its raw value.
   - **Column-1 handlers** read only column 1 (`a(g, 1)`): `o——`, `koo·`, `–la`, `la—`, `DeletePhrases`,
     `Del1DimArr`, `dLW*`, `dFW*`, `fFW`, `fLW`, `o——–`, `k—––`, `udalit_toponimy_s_pryedlogami`, `aoko*`, `—·–—`.
5. Write: `k–k` (line 2933) (zSel frame) and `oao` (line 2464) (area frame): when the checkbox «Выводить результат справа»
   (sheet `abc` cell AU4, read by `–aa` (line 1742), licensed users only) is on AND the selection is one column, insert a new
   column right of it and write there; otherwise overwrite the selection. The add-in ships with AU4 = False (in place).
   `DeletePhrases`, `aoko2` and `remLWprps` write `Selection` directly; `RunCombo` makes its own columns.
6. Licence: `—–(al(k—()), …)` (line 2006) checks the licence; when it fails, `c_h` (line 841) overwrites a random third of the rows
   with «Дoстyпнo в пoлнoй вeрcии !SЕМТооls» (`—aa` (line 1701)) and area frames process only random cells (`o–·` (line 2657)).
   Ignore in the port.
7. Apostrophe: many functions return `"'" & text`. Excel takes a leading apostrophe as the «text» prefix, not as content:
   the cell shows `text`. **Drop it in the port.** `"'" & ""` shows an empty cell.
8. Prompts: `Application.InputBox` with Type 1 (number), 2 (text) or 8 (range, the user selects cells). Cancel returns
   False and the handler exits — except where an entry says «Cancel is not checked».
9. A list taken with Type 8 is `range.Value2`: column 1, **every row of the chosen range, blanks included** (unless the
   entry says the list goes through BSR, S7). An empty pattern matches everything in the start/end/contains tests,
   so a blank list cell changes the result (noted per entry).

<a id="s2"></a>
### S2. Dispatchers and the «Игнорировать пунктуацию» mode

`·––(code1, code2, value)` (line 1858) (text prompt), `a—a(code1, code2, range)` (line 2677) (list prompt) and
`ao–(code1, code2)` (line 2650) (no prompt) read sheet `abc` cell AU3 through `·Oo` (line 1952) (the checkbox
«Игнорировать пунктуацию», ships False). AU3 True → `code1`, else `code2`. The chosen function name goes to the area
frame `·a`, `–1` or `k–`, which calls it per cell with `Application.Run(name, cell, value)`.

In the ignore-punctuation variants the predicate gets `oko(token)` (S3) instead of the token; what is kept or
removed is still the original token with its punctuation. A token such as «из-за» becomes «из за» (two words in one
token) for the test.

<a id="s3"></a>
### S3. Tokenizer and normalizers

| Name | VBA | Rule |
|---|---|---|
| split_raw | `Split(s, " ")` | Split on U+0020 only. Two spaces give an empty token; a leading/trailing space gives an empty first/last token; tabs, nbsp and line breaks stay inside tokens. |
| split_padded | `Split(s & " ")`, loop to `UBound − 1` | The same tokens as split_raw; the extra empty item is ignored. An empty cell has one empty token. Used by every word combinator (S6). |
| normalize `a·` | (line 1855) | `Trim$` (U+0020 only), then replace "  " by " " until none is left. Applied to almost every word-level result after `Join(tokens, " ")`, so blanked tokens vanish. |
| `oko` | (line 1332) | Per char: keep it if `InStr(" 1234567890", c) > 0` or `UCase(c) <> LCase(c)` (cased letter of any script), else write " "; then `a·`. Removes punctuation, symbols, tabs, newlines, nbsp and also uncased letters (CJK, Arabic). |
| `·–a` | (line 1331) | Like `oko` but digits also become spaces (letters and spaces only). |
| word count `akk` | (line 2414) | `UBound(Split(s, " ")) + 1`; empty tokens count; "" → 0. |
| first word `a—k` | (line 2175) | `Left(s, InStr(s & " ", " ") − 1)`: text before the first space ("" if s starts with a space). |
| last k words `eLW` | (line 2432) | Last k tokens of `Split(s)` joined by " ", `Trim`; k > count → s. |
| first k words `·k—` | (line 1644) | Tokens 1..k joined, `Trim`, "'" prefix; k > count → s. |
| last k words `·ka` | (line 2431) | Tokens count−k+1..count joined, `Trim`, "'" prefix; k > count → s. |

Worked examples: `a·("  купить   диван ")` = «купить диван»; `oko("Диван-кровать, 2 шт.!")` = «Диван кровать 2 шт»;
split_raw(«купить  диван») = [«купить», «», «диван»].

ADR 0005: semkit splits on any whitespace (`str.split()`), so empty tokens never exist and never count as words, and it
joins with one space. Every «empty token» quirk below disappears with this deviation.

<a id="s4"></a>
### S4. Character classes

VBA `Like` runs with `Option Compare Binary` (the module has no `Option Compare`/`Option Explicit`), so `[A-Za-z]` is
ASCII only and ranges are code-point ranges.

| Name | VBA | Notes |
|---|---|---|
| has_latin `a–—` | (line 2153) `Like "*[A-Za-z]*"` | ASCII letters. |
| has_digit `·kk` | (line 1619) `Like "*[0-9]*"` | ASCII digits. |
| has_cyrillic `—–o` | (line 2147) regex `[А-ӿЁё]` | А–я, ё/Ё, and U+0450–04FF (і ї є ґ Ґ, other scripts' Cyrillic). Not U+0400–040F except Ё: uppercase Є І Ї Ў Ђ… are NOT cyrillic. |
| `[А-Яа-я]` in Like masks | `ala`, `al–` masks | U+0410–044F only: Ё/ё are NOT in it. |
| only_latin `ala` | (line 1770) | has_latin and not `Like "*[0-9А-Яа-я]*"`. |
| only_cyrillic `о·k·` | (line 2654) | has_cyrillic and not `Like "*[0-9A-Za-z]*"`; punctuation allowed. |
| letters_and_digits `a·l1` | (line 2973) | has_digit and `UCase(x) <> LCase(x)`. |
| letter_or_digit `l–1` | (line 1926) | `StrComp(LCase(x), UCase(x)) <> 0` or has_digit. |
| has_upper `ooa` | (line 2655) | `LCase(x) <> x` and `LCase(x) <> UCase(x)`. |
| is_lower / is_proper / is_caps | (line 3387), (line 3388), (line 3389) | `LCase(x) = x` / `Application.Proper(x) = x` / `UCase(x) = x`, each and `LCase(x) <> UCase(x)`. |
| numeric `··—` | (line 2360) `IsNumeric(x)` | Locale-aware: «1,5» (ru), «1e3», «-5», «(5)», «$5», «&H10» are numeric. |
| Ukrainian `fua` | (line 1343) | See S11 for the list and the test. |

<a id="s5"></a>
### S5. String predicates

All case-insensitive by `UCase` on both sides, then a binary compare. ё ≠ е.

| Name | VBA | Rule |
|---|---|---|
| starts `—·–` | (line 1657) | `UCase(Left(x, Len(p))) = UCase(p)`; p = "" → TRUE. |
| ends `kok` | (line 2499) | `UCase(Right(x, Len(p))) = UCase(p)`; p = "" → TRUE. |
| contains `ao—` | (line 2443) | `InStr(1, UCase(x), UCase(p)) > 0`; p = "" → TRUE. |
| equals `–—a` | (line 2318) | `UCase(x) = UCase(p)`. |
| whole word `·a–` | (line 2573) | contains(" " & x & " ", " " & w & " "). w may hold spaces (works as a phrase). |
| whole word, ignore punctuation `oka` | (line 2460) | contains(" " & oko(x) & " ", " " & w & " "). |

<a id="s6"></a>
### S6. Word combinators

Every combinator splits with split_padded (S3), tests each token with a predicate called by name, and (for the text
results) returns `a·(Join(tokens, " "))`. The optional flag `—a` = True passes `oko(token)` to the predicate (S2).

| Combinator | Lines | Result |
|---|---|---|
| `aoo(pred, s)` | (line 1772) | TRUE if pred(token) for any token. |
| `·–o(pred, s, p)` | (line 2684) | TRUE if pred(token, p) for any token. |
| `a–o(pred, s, list)` | (line 2628) | TRUE if pred(token, list) for any token. |
| `aka(pred, s)` | (line 2731) | Blank tokens where pred(token). |
| `aao(pred, s, p)` | (line 1925) | Blank tokens where pred(token, p). |
| `–—k(pred, s, list)` | (line 1727) | Blank tokens where pred(token, list). |
| `—–·(pred, s, list)` | (line 2811) | Blank tokens where pred(token, item) for any list row. |
| `—·o(pred, s)` | (line 2964) | Keep only tokens where pred(token). |
| `·ko(pred, s, p)` | (line 2968) | Keep only tokens where pred(token, p). |
| `–—–(pred, s, list)` | (line 2719) | Keep only tokens where pred(token, item) for any list row. |
| `al–(s, m1, m2)` | (line 2584) | Keep tokens matching both `Like` masks (`Split(s, " ")`). |
| `—k—(pred, x, list)` | (line 1645) | TRUE if pred(x, item) for any list row (column 1, every row). |
| `k—–(pred, x, list)` | (line 1707) | TRUE if pred(x, item) for every list row. |
| `aa–(pred, x)` / `a1l(pred, x, p)` / `o·–(pred, x, list)` | (line 2448) / (line 1939) / (line 2765) | Whole cell: keep x if pred, else "". |
| `o–—(pred, x, p)` / `–k—(pred, x, list)` | (line 2271) / (line 2774) | Whole cell: "" if pred, else x. |

<a id="s7"></a>
### S7. BSR: exact word lookup through a sorted sheet range

`a–a(list)` (line 1686) copies column 1 of the list, `UCase`d and formatted as text, to sheet `abc` column K, sorts it
ascending and names `K1:K1.End(xlDown)` «BSR». `—a—(x, BSR)` (line 2675) is
`VLOOKUP(UCase(x), BSR, 1, TRUE) = UCase(x)`: a binary search plus an exact (binary) equality check, so it is exact
set membership, case-insensitive. `a–k` (line 2244) clears column K afterwards. Blank list cells sort to the end and fall out
of the named range. The same «approximate VLOOKUP + equality» trick is used by `—–` (line 2006) (membership) and `oa` (line 2208)
(returns column N, or the key itself when missing).

Port: a `set` of upper-cased (ADR: ё → е) items.

<a id="s8"></a>
### S8. Regex

`VBScript.RegExp` (ECMAScript-3-like): lookahead yes, lookbehind no, no named groups, no `\p{}`; `\d`, `\w` ASCII;
`\s` = `[ \f\n\r\t\v]`.

| Helper | Lines | Rule |
|---|---|---|
| `RegExMatch(s, p)` | (line 1646) | IgnoreCase False, Global True, `.Test` = search anywhere. Invalid pattern → run-time error. |
| `RegExExtract(s, p, global, sep)` | (line 2970) | Each match followed by sep, the trailing sep cut; no match → "". IgnoreCase reads an undeclared variable → False. |
| `RegExReplace(s, p, r)` | (line 2080) | Global True, IgnoreCase False. s or p empty → s. A bad pattern is swallowed → s. Then a dead guard: when the result starts with the literal «=+-», prefix "'". |

Port with Python `re`: use `re.ASCII` (VBScript `\d`/`\w`/`\s` are ASCII), `re.search` for a test, `re.finditer`
for extraction.

<a id="s9"></a>
### S9. Lemma `aaa` and parts of speech

Dictionary: workbook `lemms.xlsb`, range `lemmdict!slovarlyemm` (= `reverse/data/lemms.tsv`: wordform, lemma, POS; one
row per wordform; POS codes `n`, `v`, `a`, `p`, `advb`, `prn`, `prep`, `nv`, `prt`). `get_lemmdict` (line 2109)
downloads it next to the add-in when missing and opens it.

**`aaa(word)`** (line 1354) — the lemma function:
1. Cache: a Dictionary keyed by the exact word.
2. Evaluate the Excel formula `IF(VLOOKUP(w, slovarlyemm, 1, TRUE) = w, VLOOKUP(w, slovarlyemm, 2, TRUE), w)`.
   Excel `=` is case-insensitive. So: a known wordform → its lemma; **an unknown word → the word itself**.
3. Only when the formula returns an error (#N/A when w sorts before the first key, #REF! when `lemms.xlsb` is not
   reachable, a formula longer than 255 chars because of a long add-in path, a `"` inside w) the fallback runs:
   `Left(w, Len(w) − 4) & oa(Right(w, 4), lemmSuf, 2)` — replace the last 4 letters by column 2 of `lemmSuf`
   (abc E50:G305) when they are in column 1, else keep them. Words shorter than 4 letters: `Left` fails → w.
4. Callers lower-case the word first (`—··` (line 2395) lower-cases the phrase, `··o` passes `LCase`).

Note: `docs/brief.md` says the `lemmSuf` fallback runs for unknown words; in the VBA it runs only on lookup errors.

**POS predicates** — each looks up column 3 with `oa(word, slovarlyemm, 3)` (line 2208) (a missing word returns itself, so
it never equals a POS code):

| Predicate | Lines | Rule |
|---|---|---|
| noun `··–` | (line 2207) | POS(`LCase(w)`) = "n". |
| adverb `oa–` | (line 2154) | POS(`LCase(w)`) = "advb". |
| verb `·ok` | (line 1344) | `Right(LCase(w), 3)` ∈ {«тся», «ься», «ают»}, or = «уют» and w ≠ «уют» → TRUE without a lookup; else POS(`LCase(w)`) = "v". |
| adjective `··o` | (line 1439) | pt = POS(w) with w NOT lower-cased (the binary equality in `oa` fails for «Красный» → pt = the word). pt = "a" → TRUE. pt ∈ {n, v, advb, p, prep, conj, nv} → FALSE. Otherwise (prn, prt, unknown or capitalized): lemma = `aaa(LCase(w))`; TRUE when `Right(lemma, 3)` is in column 1 of `adjSuffixes` (abc AD2:AS90) and lemma is not in `nounsLikeAdj` (abc J1:J417). Participles (`p`) are not adjectives. |

Port: the semkit lemmatizer gives lemma and POS; keep the predicate rules above (ADR: ё = е, lemmas lower case).

<a id="s10"></a>
### S10. Phrase lists and toponyms

Marker lists live on the hidden sheet `ggg`, one column each, as named ranges (`def_*` procedures). They come from
`https://semtools.guru/dl/spiski/<file>.xlsx` (`upd` (lines 2001–2002)); the local copies are in `reverse/downloads/spiski/`.

| Ribbon caption | Named range | `ggg` column | File |
|---|---|---|---|
| Игры и развлечения | `markyeryFun` | A | fun |
| DIY (самодеятельность) | `markyeryDIY` | B | DIY |
| Марки и модели авто | `markyeryCars` | C | cars |
| Маркеры вопросов | `questions` | D | questions |
| Продажи | `markyerypokupki` | E | sale |
| Аренда | `markyeryRent` | F | rent |
| Отзывы | `markyeryReviews` | G | reviews |
| Метро МСК | `markyeryMosmetro` | H | mosmetro |
| Районы МСК | `markyeryMSKDistricts` | I | districts |
| Пункты МО | `markyeryMO` | J | MO |
| Имена | `names` | K | names |
| Населённые пункты РФ | `citiesRu` | L | citiesRu |
| Цвет | `color` | M | color |
| Образование | `edu` | N | edu |
| Названия игр | `game` | O | game |
| Материал | `material` | P | material |
| Происхождение (страна) | `origin` | Q | origin |
| Топонимы (все) | `GEO_Toponyms` | R | geo |

`chk(name)` (line 2511) offers to download all lists when the named range is missing or empty. Most per-list buttons call
`chk "edu"` instead of their own list name.

**First-word index** (used by `–la`, `la—`, `k—––`, `udalit…`): for each list item (original spelling, list order),
key = `UCase(a—k(item))` (text before the first space); value = the items with that key joined by TAB, in list order.
The geo list holds every case form («Москва», «Москве», «Москву»…), capitalized, and longer phrases of one first word
usually come first («Москве или области» … «Москве»).

<a id="find_phrases"></a>**find_phrases** — `–la(list)` (lines 645–646):
1. Selection column 1; a single selected cell → exit.
2. tokens = split_padded(cell). For each token in order: if `UCase(token)` is a key:
   - if `UCase(value) = UCase(token)` (the key holds one item and it is this one word) → TRUE;
   - else for each item of the value in list order: if `InStr(1, " " & cell & " ", " " & item & " ", vbTextCompare) > 0`
     → TRUE.
3. Otherwise FALSE.

The multi-word item is searched anywhere in the cell, not at the token position. A token glued to punctuation
(«москве,») is not a key.

<a id="extract_phrases"></a>**extract_phrases** — `la—(list)` (lines 647–648): as find_phrases, but each token becomes a slot:
the one-word item (list spelling), or the FIRST item in list order found in the cell (list spelling, not the longest),
or "". Result = the non-empty slots joined by "\" in token order; repeats are kept, and words inside an extracted phrase
that are keys themselves give extra slots.

**remove_phrases** — `DeletePhrases(list)` (lines 3452–3470):
1. For each list cell (column 1): phrase = `LCase(Trim(cell))`; skip "". n = its token count (split_raw). Keep a set of
   phrases per n; maxN = the largest n.
2. For each cell of the selection, column 1: phrase = `LCase(Trim(cell))`; "" → "".
3. words = split_raw(phrase); pos = 0. While pos ≤ last: for n = maxN down to 1, if words pos..pos+n−1 joined by " " is
   in set n, skip them (pos += n) and stop; if no n matched, output words(pos) and pos += 1.
4. Cell = output words joined by " " ("" when none). Greedy, longest phrase first at each position, left to right.

The output is **lower case** even when nothing was removed. Inner double spaces survive (empty words are output) and
block phrases across them. A one-cell selection fails silently.

<a id="toponyms"></a>**remove_toponyms_with_prepositions** — `udalit_toponimy_s_pryedlogami()` (lines 1194–1197):
1. Index over `GEO_Toponyms`. Prepositions (upper case): В, ВО, НА, ПО, ИЗ, ДО, Г, И (the optional en set IN, AT, BY,
   TO is never used from the ribbon).
2. For each cell (column 1): tokens = split_padded(cell); k = cell; padded = " " & cell & " ".
3. For a = 0 .. count−2 (token a+1 exists): if `UCase(token a)` is a preposition and `UCase(token a+1)` is a key:
   - the key has ONE item: padded = `Replace(padded, " " & token a & " " & token a+1 & " ", " ", vbTextCompare)` — only the
     preposition and the next word go, even when that one item has more words; k = `Trim(padded)`;
   - several items: candidate = token a & " " & item for each item; take the longest (by chars; ties → first) found by
     `InStr(padded, " " & candidate & " ", vbTextCompare)`; remove it with the same `Replace`; k = `Trim(padded)`.
4. Cell = `a·(k)`. Toponyms without a preposition stay. `Replace` removes every occurrence of the pair.

**extract_toponyms_with_prepositions** — `k—––(False)` (lines 1198–1199):
1. Same index and prepositions. tokens = `Split(cell & " ", " ")` (the extra empty item is kept as a slot).
2. For a = 0 .. last−1: if token a is a preposition and `UCase(token a+1)` is a key:
   - one-word item equal to token a+1 → slot = token a & " " & token a+1 (cell spelling);
   - else the first item in list order with `InStr(" " & cell & " ", " " & token a & " " & item & " ", vbTextCompare)`
     → slot = token a & " " & item (list spelling); none → "".
   Every other token → "".
3. Cell = `a·(Join(all slots, "\"))`: empty slots stay, so the separators pile up.

Worked examples (real geo list):

| Cell | find | extract (`la—`) | remove (`DeletePhrases`) | remove with preps | extract with preps |
|---|---|---|---|---|---|
| `купить диван в москве недорого` | TRUE | `Москве` | `купить диван в недорого` | `купить диван недорого` | `\\в Москве\\\` |
| `диван москва` | TRUE | `Москва` | `диван` | `диван москва` | `\\` |
| `доставка в нижний новгород` | TRUE | `Нижний Новгород\Новгород` | `доставка в` | `доставка` | `\в Нижний Новгород\\\` |
| `отели в хересе де ла фронтере` | TRUE | `Хересе де Ла Фронтере\Ла Фронтере` | `отели в` | `отели де ла фронтере` | `\в Хересе де Ла Фронтере\\\\\` |

<a id="s11"></a>
### S11. Built-in lists

- **Stopwords** `stopwords()` (lines 1374–1378): one string literal, 440 space-separated words, no duplicates even after
  `UCase`: English («a about all alled alling…») and Russian function words, pronoun and «быть/мочь/есть» forms, and
  the junk «g». Used case-SENSITIVELY by `Del1DimArr` and case-insensitively by `dLW`.
- **Prepositions** `prps()` (line 1322): 47 items «а без безо близ в вместо вне во для до за и из из-за из-под изо или к ко
  кроме меж между на над но g об обо от ото пo перед передо под подо пред предо при про ради с сквозь со среди у через
  чрез». «пo» has a LATIN o (so «по» is missing) and «g» is junk.
- **Complement prepositions** (inside `collocs` (line 1428)): « для с в из на к со о во у по под от после за над » (16).
- **Toponym prepositions**: ru В ВО НА ПО ИЗ ДО Г И; en IN AT BY TO (unused).
- **Ukrainian markers** (`fua` (line 1343)): «і» (U+0456), «ї» (U+0457), «є» (U+0454), «ння », «нню », « був », « ти », « це »,
  « з », «ковий », «сько», «ський », «учня », «ць», «цю», «ця», «що », « як », « ви », «тися », «ття », «лися »,
  «ярна », « цей », « цем », « може », «ити », «аних », «ною », «ють », «ати ». Test: s = " " & LCase(cell) & " ", then
  `InStr(1, " " & s & " ", item) > 0` for any item. Several items hit Russian words («кровати », «сити », «поють »).

<a id="s12"></a>
### S12. Cells by occurrence

`o——(unique, mode)` (lines 381–434) and `koo·(order)` (line 2929) work on column 1 of the selection, key = `UCase(CStr(value))`
(no trim, empty cells take part), and write the whole array back with `k–k`.

| Call | Cell gets |
|---|---|
| `o——(True, "find")` | TRUE if the key occurs once, else FALSE |
| `o——(False, "find")` | TRUE if the key occurs 2+ times (all occurrences) |
| `o——(True, "extr")` | the value if it occurs once, else "" |
| `o——(False, "extr")` | the value if it occurs 2+ times, else "" |
| `o——(True, "del")` | "" if it occurs once, else the value |
| `o——(False, "del")` | "" if it occurs 2+ times, else the value |
| `koo·("first")` | TRUE at the first occurrence of each key (top-down), else FALSE |
| `koo·("··1")` | TRUE at the last occurrence (bottom-up scan), else FALSE |

ADR 0005: empty cells are never duplicates — leave them out of the counts.

<a id="f1"></a>
## F1. Find › Chars (ОБНАРУЖИТЬ > Символы)

### ОБНАРУЖИТЬ > Символы > По типу > Выделить цветом > Латиницу
- Handler: `HL_Lat` (RibbonCallbacks.vba line 171); helpers: none
- Input / output: Selection, every cell. Writes nothing; colors the matching characters red (`Characters(i,1).Font.Color`). Excel-only.
- Algorithm:
  1. For each cell, for each character i = 1..Len: if `Mid(c, i, 1) Like "[A-Za-z]"` (binary compare) color it.
  2. Port as a find: TRUE when the cell has at least one such character (or return the char spans).
- Quirks: No `a–`/undo/licence frame. Font coloring is lost on the next write to the cell.
- ADR 0005 deviation that applies: none

### ОБНАРУЖИТЬ > Символы > По типу > Выделить цветом > Кириллицу
- Handler: `HL_Cyr` (RibbonCallbacks.vba line 172); helpers: none
- Input / output: Selection, every cell. Writes nothing; colors the matching characters magenta (`Characters(i,1).Font.Color`). Excel-only.
- Algorithm:
  1. For each cell, for each character i = 1..Len: if `Mid(c, i, 1) Like "[А-Яа-яЁё]"` (binary compare) color it.
  2. Port as a find: TRUE when the cell has at least one such character (or return the char spans).
- Quirks: No `a–`/undo/licence frame. Font coloring is lost on the next write to the cell. Here Ё/ё ARE in the class, unlike the other cyrillic tests (S4).
- ADR 0005 deviation that applies: none

### ОБНАРУЖИТЬ > Символы > По типу > Выделить цветом > Цифры
- Handler: `HL_Num` (RibbonCallbacks.vba line 173); helpers: none
- Input / output: Selection, every cell. Writes nothing; colors the matching characters blue (`Characters(i,1).Font.Color`). Excel-only.
- Algorithm:
  1. For each cell, for each character i = 1..Len: if `Mid(c, i, 1) Like "[0-9]"` (binary compare) color it.
  2. Port as a find: TRUE when the cell has at least one such character (or return the char spans).
- Quirks: No `a–`/undo/licence frame. Font coloring is lost on the next write to the cell.
- ADR 0005 deviation that applies: none

### ОБНАРУЖИТЬ > Символы > По типу > Вернуть ИСТИНА (шустрее) > Буквы-цифры
- Handler: `—kko` (RibbonCallbacks.vba line 2874); helpers: `k–` (line 1937), `l–1` (line 1926)
- Input / output: Selection, all cells of all areas (S1, area frame). Writes TRUE/FALSE in place or to the right.
- Algorithm:
  1. `l–1(cell)` = `StrComp(LCase(s), UCase(s)) <> 0 Or s Like "*[0-9]*"`.
  2. So TRUE when the cell has any cased letter of any script (latin, cyrillic, greek…) or an ASCII digit.
- Examples: `диван` → TRUE; `!!! ---` → FALSE; `2024` → TRUE.
- Quirks: «Letters» = any character whose upper and lower case differ; Chinese/Arabic letters do not count. A numeric cell is converted to text first ("12" → TRUE).
- ADR 0005 deviation that applies: none

### ОБНАРУЖИТЬ > Символы > По типу > Вернуть ИСТИНА (шустрее) > Латиницу
- Handler: `—·k—` (RibbonCallbacks.vba line 1824); helpers: `a–—` (line 2153)
- Input / output: Selection, every cell (S1, zSel frame). Writes TRUE/FALSE.
- Algorithm:
  1. TRUE when `cell Like "*[A-Za-z]*"` (S4 `has_latin`).
- Examples: `диван IKEA` → TRUE; `диван` → FALSE.
- Quirks: none found.
- ADR 0005 deviation that applies: none

### ОБНАРУЖИТЬ > Символы > По типу > Вернуть ИСТИНА (шустрее) > Кириллицу
- Handler: `—·k–` (RibbonCallbacks.vba line 2088); helpers: `—–o` (line 2147), `RegExMatch` (line 1646)
- Input / output: Selection, every cell. Writes TRUE/FALSE.
- Algorithm:
  1. TRUE when the regex `[\u0410-\u04FF\u0401\u0451]` finds a character (S4 `has_cyrillic`).
- Examples: `IKEA Эктроп` → TRUE; `IKEA` → FALSE.
- Quirks: Uppercase Є І Ї Ґ? Ґ (U+0490) is inside the range; Є (U+0404), І (U+0406), Ї (U+0407) are not, their lowercase forms are.
- ADR 0005 deviation that applies: none

### ОБНАРУЖИТЬ > Символы > По типу > Вернуть ИСТИНА (шустрее) > Цифры
- Handler: `—·ka` (RibbonCallbacks.vba line 1652); helpers: `k–` (line 1937), `·kk` (line 1619)
- Input / output: Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. TRUE when `cell Like "*[0-9]*"` (ASCII digits only).
- Examples: `диван 2 места` → TRUE; `диван` → FALSE.
- Quirks: none found.
- ADR 0005 deviation that applies: none

### ОБНАРУЖИТЬ > Символы > Заглавные
- Handler: `—·ok` (RibbonCallbacks.vba line 2756); helpers: `ooa` (line 2655)
- Input / output: Selection, every cell. Writes TRUE/FALSE.
- Algorithm:
  1. `ooa(s)` = `StrComp(LCase(s), s) <> 0 And StrComp(LCase(s), UCase(s)) <> 0` (binary).
  2. TRUE when the WHOLE cell has at least one uppercase letter.
- Examples: `диван IKEA` → TRUE; `купить Диван` → TRUE; `диван` → FALSE.
- Quirks: Tooltip says «words starting with a capital or in caps»; the code tests the whole cell for any uppercase letter, not word starts.
- ADR 0005 deviation that applies: none

### ОБНАРУЖИТЬ > Символы > UA символы/сочетания
- Handler: `—·k·` (RibbonCallbacks.vba line 1786); helpers: `fua` (line 1343)
- Input / output: Selection, every cell. Writes TRUE/FALSE.
- Algorithm:
  1. s = " " & LCase(cell) & " "; then test `InStr(1, " " & s & " ", item) > 0` (binary) for each item of the UA list (S11).
  2. TRUE on the first item found.
- Examples: `ціна дивана` → TRUE («і»); `купить кровати недорого` → TRUE (false positive, «ати »); `купить диван` → FALSE.
- Quirks: Many items are endings with a trailing space and hit Russian words: «ати » (кровати), «ити » (сити), «ють » (поють). Items without spaces («ць», «цю», «ця», «сько») match inside words.
- ADR 0005 deviation that applies: none

<a id="f2"></a>
## F2. Find › Words (ОБНАРУЖИТЬ > Слова)

### ОБНАРУЖИТЬ > Слова > Целые слова > 1 слово
- Handler: `–––o` (RibbonCallbacks.vba line 1927); helpers: `·––` (line 1858), `·a` (line 441), `·a–` (line 2573), `oka` (line 2460), `oko` (line 1332), `ao—` (line 2443)
- Input / output: InputBox «Введите слово» (Type 2, text). Selection, all cells of all areas (S2 `·a`). Writes TRUE/FALSE.
- Algorithm:
  1. Plain mode (default): `·a–(cell, w)` = `InStr(UCase(" " & cell & " "), UCase(" " & w & " ")) > 0` (binary on upper-cased strings).
  2. Ignore-punctuation mode: `oka(cell, w)` = same test on `" " & oko(cell) & " "` (S3 `oko`).
  3. w is used as typed: if it holds spaces it works as a phrase on space boundaries.
- Examples: cell `Купить Диван`, w `диван` → TRUE; cell `диван-кровать`, w `диван` → FALSE (ignore-punct: TRUE); cell `диваны`, w `диван` → FALSE.
- Quirks: Case-insensitive; ё ≠ е. In plain mode a word glued to punctuation does not match («диван,»).
- ADR 0005 deviation that applies: ё = е; split on any whitespace (pad/compare by tokens, not by single spaces).

### ОБНАРУЖИТЬ > Слова > Целые слова > Все из списка
- Handler: `–––k` (RibbonCallbacks.vba line 2805); helpers: `koao` (line 1844), `k—–` (line 1707), `·a–` (line 2573), `ao—` (line 2443)
- Input / output: InputBox for a range (Type 8): the word list, column 1, ALL rows of the chosen range including blanks. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. `k—–("·a–", cell, list)`: for each list row g, require `·a–(cell, list(g,1))` (whole-word test as in «1 слово»).
  2. TRUE only if every row passes (AND). Stops on the first failure.
- Examples: list [диван, москва]: `диван в москва` → TRUE; `диван в москве` → FALSE; list [диван, (blank)] → FALSE everywhere.
- Quirks: A blank cell in the chosen list range makes every result FALSE (`·a–(cell, "")` looks for a double space). There is no ignore-punctuation variant. List items are not deduplicated or trimmed.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items (fix).

### ОБНАРУЖИТЬ > Слова > Целые слова > Любое из списка
- Handler: `—k—k` (RibbonCallbacks.vba line 2218); helpers: `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: InputBox for a range (Type 8): the phrase list (column 1). Selection column 1; single-cell selection: nothing happens. Writes TRUE/FALSE.
- Algorithm:
  1. Phrase-list find, see S10 `find_phrases`.
- Examples: list [Нижний Новгород, Москва]: `доставка в нижний новгород` → TRUE; `нижний тагил` → FALSE; `в москва,` → FALSE.
- Quirks: Same handler as «Фразы > Свой список». Exits on a single selected cell after turning screen updating off. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Слова > Целые слова > Части речи... > Существительные
- Handler: `—k–a` (RibbonCallbacks.vba line 2266); helpers: `get_lemmdict` (line 2109), `ao–` (line 2650), `k–` (line 1937), `k—·–` (line 2254), `k—·—` (line 2905), `aoo` (line 1772), `··–` (line 2207)
- Input / output: No prompt. Opens `lemms.xlsb` (`get_lemmdict`; downloads it if missing). Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `k—·–` = `aoo("··–", cell)`: split the cell (S3 `split_padded`), TRUE if any token is a noun by `··–` (S9).
  2. Ignore-punctuation: `k—·—` = the same with each token passed through `oko` first.
- Examples: `купить красный диван` → TRUE for noun, adjective, verb; FALSE for adverb (dictionary tags assumed).
- Quirks: POS is looked up for the token as written (lower-cased inside the predicate, except the adjective test which looks up the token as is, see S9).
- ADR 0005 deviation that applies: split on any whitespace; ё = е when looking words up.

### ОБНАРУЖИТЬ > Слова > Целые слова > Части речи... > Прилагательные
- Handler: `–···` (RibbonCallbacks.vba line 2909); helpers: `get_lemmdict` (line 2109), `ao–` (line 2650), `k–` (line 1937), `k—aa` (line 2210), `k—·o` (line 1745), `aoo` (line 1772), `··o` (line 1439)
- Input / output: No prompt. Opens `lemms.xlsb` (`get_lemmdict`; downloads it if missing). Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `k—aa` = `aoo("··o", cell)`: split the cell (S3 `split_padded`), TRUE if any token is an adjective by `··o` (S9).
  2. Ignore-punctuation: `k—·o` = the same with each token passed through `oko` first.
- Examples: `купить красный диван` → TRUE for noun, adjective, verb; FALSE for adverb (dictionary tags assumed).
- Quirks: POS is looked up for the token as written (lower-cased inside the predicate, except the adjective test which looks up the token as is, see S9).
- ADR 0005 deviation that applies: split on any whitespace; ё = е when looking words up.

### ОБНАРУЖИТЬ > Слова > Целые слова > Части речи... > Глаголы
- Handler: `—k—·` (RibbonCallbacks.vba line 2494); helpers: `get_lemmdict` (line 2109), `ao–` (line 2650), `k–` (line 1937), `k—·a` (line 2469), `k—··` (line 2840), `aoo` (line 1772), `·ok` (line 1344)
- Input / output: No prompt. Opens `lemms.xlsb` (`get_lemmdict`; downloads it if missing). Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `k—·a` = `aoo("·ok", cell)`: split the cell (S3 `split_padded`), TRUE if any token is a verb by `·ok` (S9).
  2. Ignore-punctuation: `k—··` = the same with each token passed through `oko` first.
- Examples: `купить красный диван` → TRUE for noun, adjective, verb; FALSE for adverb (dictionary tags assumed).
- Quirks: POS is looked up for the token as written (lower-cased inside the predicate, except the adjective test which looks up the token as is, see S9).
- ADR 0005 deviation that applies: split on any whitespace; ё = е when looking words up.

### ОБНАРУЖИТЬ > Слова > Целые слова > Части речи... > Наречия
- Handler: `—kkk` (RibbonCallbacks.vba line 1663); helpers: `get_lemmdict` (line 2109), `ao–` (line 2650), `k–` (line 1937), `k—a·` (line 2152), `k—·k` (line 2328), `aoo` (line 1772), `oa–` (line 2154)
- Input / output: No prompt. Opens `lemms.xlsb` (`get_lemmdict`; downloads it if missing). Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `k—a·` = `aoo("oa–", cell)`: split the cell (S3 `split_padded`), TRUE if any token is an adverb by `oa–` (S9).
  2. Ignore-punctuation: `k—·k` = the same with each token passed through `oko` first.
- Examples: `купить красный диван` → TRUE for noun, adjective, verb; FALSE for adverb (dictionary tags assumed).
- Quirks: POS is looked up for the token as written (lower-cased inside the predicate, except the adjective test which looks up the token as is, see S9).
- ADR 0005 deviation that applies: split on any whitespace; ё = е when looking words up.

### ОБНАРУЖИТЬ > Слова > Содержащие... > В начале > Паттерн
- Handler: `—ka—` (RibbonCallbacks.vba line 2082); helpers: `·––` (line 1858), `·a` (line 441), `kaoo` (line 2633), `kaoa` (line 2771), `·–o` (line 2684), `—·–` (line 1657)
- Input / output: InputBox (Type 2) pattern p. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `kaoo` = `·–o("—·–", cell, p)`: TRUE if any token starts with p: `UCase(Left(token, Len(p))) = UCase(p)`.
  2. Ignore-punctuation: `kaoa` = same on `oko(token)`.
- Examples: p `диван`: `купить диванчик` → TRUE; `купить кресло` → FALSE.
- Quirks: Empty p → every cell with at least one token is TRUE (an empty cell too: it has one empty token).
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Слова > Содержащие... > В начале > Список паттернов
- Handler: `—kaa` (RibbonCallbacks.vba line 2225); helpers: `a—a` (line 2677), `–1` (line 442), `kao–` (line 2269), `kao—` (line 2590), `a–o` (line 2628), `–ok` (line 2474), `—k—` (line 1645), `—·–` (line 1657)
- Input / output: InputBox for a range (Type 8): pattern list, column 1, all rows. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `kao–` = `a–o("–ok", cell, list)`: TRUE if any token starts with any list item (`—·–`, case-insensitive).
  2. Ignore-punctuation: `kao—` = same on `oko(token)`.
- Examples: list [див, крес]: `купить диван` → TRUE; `стол` → FALSE.
- Quirks: A blank cell in the list range matches every token → TRUE for every cell.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### ОБНАРУЖИТЬ > Слова > Содержащие... > В конце... > Паттерн
- Handler: `—kao` (RibbonCallbacks.vba line 2670); helpers: `·––` (line 1858), `·a` (line 441), `kak—` (line 2668), `kaok` (line 2178), `·–o` (line 2684), `kok` (line 2499)
- Input / output: InputBox (Type 2) pattern p. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `kak—` = `·–o("kok", cell, p)`: TRUE if any token ends with p: `UCase(Right(token, Len(p))) = UCase(p)`.
  2. Ignore-punctuation: `kaok` = same on `oko(token)`.
- Examples: p `ный`: `красный диван` → TRUE; `красная кровать` → FALSE.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Слова > Содержащие... > В конце... > Список паттернов
- Handler: `—ka–` (RibbonCallbacks.vba line 2759); helpers: `a—a` (line 2677), `–1` (line 442), `kaka` (line 2461), `kak·` (line 1921), `a–o` (line 2628), `kaa` (line 2855), `—k—` (line 1645), `kok` (line 2499)
- Input / output: InputBox for a range (Type 8): pattern list, column 1, all rows. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `kaka` = `a–o("kaa", cell, list)`: TRUE if any token ends with any list item.
  2. Ignore-punctuation: `kak·` = same on `oko(token)`.
- Examples: list [ный, ая]: `красная кровать` → TRUE.
- Quirks: A blank cell in the list range → TRUE for every cell.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### ОБНАРУЖИТЬ > Слова > Содержащие... > Где угодно > Паттерн
- Handler: `SEM_findCellsContainingPattern` — NOT FOUND in the VBA; helpers: none
- Input / output: —
- Algorithm:
  1. The ribbon names the callback `SEM_findCellsContainingPattern`, but no such procedure exists in `RibbonCallbacks.vba`, the forms, the other modules or the p-code dump. Clicking it raises «macro not found».
  2. Nearest working analogue: «Где угодно > Список паттернов» (`—kk—`) with a one-item list: TRUE when the cell contains p as a substring, case-insensitive (`ao—`).
- Quirks: Not traceable: the handler is missing from the add-in.
- ADR 0005 deviation that applies: n/a (no VBA algorithm; derive from `—kk—`).

### ОБНАРУЖИТЬ > Слова > Содержащие... > Где угодно > Список паттернов
- Handler: `—kk—` (RibbonCallbacks.vba line 2556); helpers: `—––` (line 1831), `—k—` (line 1645), `ao—` (line 2443)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. `—––(cell, list)` = `—k—("ao—", cell, list)`: TRUE if any list item is a substring of the WHOLE cell: `InStr(1, UCase(cell), UCase(item)) > 0`.
  2. No word split: this is a cell-level substring test, though the button sits under «Слова > Содержащие > Где угодно».
- Examples: list [диван]: `диванчик` → TRUE; `кресло` → FALSE.
- Quirks: A blank list cell → TRUE for every cell (`InStr(x, "")` returns 1). Same handler for «Ячейки > По содержимому > Содержащие (указать список)».
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### ОБНАРУЖИТЬ > Слова > По регистру > строчные
- Handler: `aakL` (RibbonCallbacks.vba line 1665); helpers: `lifan` (line 1668), `aoo` (line 1772), `isLcase` (line 3387)
- Input / output: No prompt. Selection, every cell (zSel frame). Writes TRUE/FALSE.
- Algorithm:
  1. `lifan(cell)` = `aoo("isLcase", cell)`: split the cell (S3 `split_padded`), TRUE if any token is all lower case: `LCase(x) = x And LCase(x) <> UCase(x)`.
  2. Comparison `=` is binary (exact code points).
- Examples: `диван IKEA` → TRUE; `Диван IKEA` → FALSE; `3d` alone → TRUE (has a cased letter, already lower).
- Quirks: Tokens include punctuation; a token of only digits/punctuation is never lower/caps.
- ADR 0005 deviation that applies: split on any whitespace.

### ОБНАРУЖИТЬ > Слова > По регистру > 1 Заглавная
- Handler: `aakP` (RibbonCallbacks.vba line 1666); helpers: `peugeot` (line 1669), `aoo` (line 1772), `isProper` (line 3388)
- Input / output: No prompt. Selection, every cell (zSel frame). Writes TRUE/FALSE.
- Algorithm:
  1. `peugeot(cell)` = `aoo("isProper", cell)`: split the cell (S3 `split_padded`), TRUE if any token is proper case: `Application.Proper(x) = x And LCase(x) <> UCase(x)`.
  2. Comparison `=` is binary (exact code points).
- Examples: `купить Диван` → TRUE; `Ростов-на-Дону` → FALSE (Proper gives «Ростов-На-Дону»); `iPhone` → FALSE.
- Quirks: Excel PROPER capitalizes the letter after any non-letter: «из-за» → «Из-За», «3d» → «3D».
- ADR 0005 deviation that applies: split on any whitespace.

### ОБНАРУЖИТЬ > Слова > По регистру > ВСЕ КАПСОМ
- Handler: `aakC` (RibbonCallbacks.vba line 1667); helpers: `chery` (line 1670), `aoo` (line 1772), `isCaps` (line 3389)
- Input / output: No prompt. Selection, every cell (zSel frame). Writes TRUE/FALSE.
- Algorithm:
  1. `chery(cell)` = `aoo("isCaps", cell)`: split the cell (S3 `split_padded`), TRUE if any token is all caps: `UCase(x) = x And LCase(x) <> UCase(x)`.
  2. Comparison `=` is binary (exact code points).
- Examples: `диван IKEA` → TRUE; `диван Ikea` → FALSE; `2024` → FALSE (no cased letter).
- Quirks: Tokens include punctuation; a token of only digits/punctuation is never lower/caps.
- ADR 0005 deviation that applies: split on any whitespace.

### ОБНАРУЖИТЬ > Слова > По паттерну REGEX
- Handler: `—kak` (RibbonCallbacks.vba line 2482); helpers: `·––` (line 1858), `·a` (line 441), `kako` (line 2090), `kak–` (line 1956), `·–o` (line 2684), `RegExMatch` (line 1646)
- Input / output: InputBox (Type 2) pattern. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `kako` = `·–o("RegExMatch", cell, p)`: TRUE if the regex finds a match inside any token (S8: VBScript RegExp, IgnoreCase False, search not fullmatch).
  2. Ignore-punctuation: `kak–` = same on `oko(token)`.
- Examples: p `^\d+$`: `диван 2 места` → TRUE; p `^\d+$`: `диван 2х` → FALSE.
- Quirks: Not anchored: use ^…$ for a whole-token match. Case-sensitive.
- ADR 0005 deviation that applies: split on any whitespace.

### ОБНАРУЖИТЬ > Слова > Повторяющиеся слова
- Handler: `—k—–` (RibbonCallbacks.vba line 1731); helpers: `—la` (line 2938)
- Input / output: No prompt. Selection, every cell. Writes TRUE/FALSE.
- Algorithm:
  1. If the cell has no space → FALSE.
  2. Split `UCase(cell)` on " " (S3 `split_raw`); TRUE if any two tokens are equal (binary).
- Examples: `диван Диван` → TRUE; `диван диваны` → FALSE; `диван` → FALSE.
- Quirks: Empty tokens count: a cell with two double spaces («a  b  c») is TRUE. Case-insensitive, ё ≠ е, punctuation kept («диван, диван» → FALSE).
- ADR 0005 deviation that applies: ё = е; split on any whitespace (no empty tokens).

<a id="f3"></a>
## F3. Find › Phrases and markers (ОБНАРУЖИТЬ > Фразы)

### ОБНАРУЖИТЬ > Фразы > Свой список
- Handler: `—k—k` (RibbonCallbacks.vba line 2218); helpers: `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: InputBox for a range (Type 8): the phrase list (column 1). Selection column 1; single-cell selection: nothing happens. Writes TRUE/FALSE.
- Algorithm:
  1. Phrase-list find, see S10 `find_phrases`.
- Examples: list [Нижний Новгород, Москва]: `доставка в нижний новгород` → TRUE; `нижний тагил` → FALSE; `в москва,` → FALSE.
- Quirks: Same handler as «Фразы > Свой список». Exits on a single selected cell after turning screen updating off. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Все
- Handler: `—k——` (RibbonCallbacks.vba line 2520); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `GEO_Toponyms` = sheet `ggg` column R (`spiski/geo.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "GEO_Toponyms"` first (offers to download all lists when the named range `GEO_Toponyms` is missing or empty).
  2. Phrase-list find with list `GEO_Toponyms`, see S10 `find_phrases`.
- Quirks: Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Метро МСК
- Handler: `—k—6` (RibbonCallbacks.vba line 2047); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyeryMosmetro` = sheet `ggg` column H (`spiski/mosmetro.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `markyeryMosmetro`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Районы МСК
- Handler: `—k—7` (RibbonCallbacks.vba line 2048); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyeryMSKDistricts` = sheet `ggg` column I (`spiski/districts.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `markyeryMSKDistricts`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Пункты МО
- Handler: `—k—8` (RibbonCallbacks.vba line 2049); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyeryMO` = sheet `ggg` column J (`spiski/MO.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `markyeryMO`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Топонимы > Населённые пункты РФ
- Handler: `—k—9` (RibbonCallbacks.vba line 2050); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `citiesRu` = sheet `ggg` column L (`spiski/citiesRu.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `citiesRu`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > Маркеры вопросов
- Handler: `—k—o` (RibbonCallbacks.vba line 2040); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `questions` = sheet `ggg` column D (`spiski/questions.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `questions`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > Игры и развлечения
- Handler: `—k—3` (RibbonCallbacks.vba line 2044); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyeryFun` = sheet `ggg` column A (`spiski/fun.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `markyeryFun`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > DIY (самодеятельность)
- Handler: `—k—4` (RibbonCallbacks.vba line 2045); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyeryDIY` = sheet `ggg` column B (`spiski/DIY.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `markyeryDIY`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > Образование
- Handler: `—k—01` (RibbonCallbacks.vba line 2052); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `edu` = sheet `ggg` column N (`spiski/edu.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `edu`, see S10 `find_phrases`.
- Quirks: Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Минус-слова > Названия игр
- Handler: `—k—02` (RibbonCallbacks.vba line 2053); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `game` = sheet `ggg` column O (`spiski/game.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `game`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > E-com > Продажи
- Handler: `—k—l` (RibbonCallbacks.vba line 2042); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyerypokupki` = sheet `ggg` column E (`spiski/sale.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `markyerypokupki`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > E-com > Аренда
- Handler: `—k—00` (RibbonCallbacks.vba line 2041); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyeryRent` = sheet `ggg` column F (`spiski/rent.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. No `chk` call.
  2. Phrase-list find with list `markyeryRent`, see S10 `find_phrases`.
- Quirks: Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > E-com > Отзывы
- Handler: `—k—2` (RibbonCallbacks.vba line 2043); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyeryReviews` = sheet `ggg` column G (`spiski/reviews.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `markyeryReviews`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Характеристики > Цвет
- Handler: `—k—0` (RibbonCallbacks.vba line 2051); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `color` = sheet `ggg` column M (`spiski/color.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `color`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Характеристики > Материал
- Handler: `—k—03` (RibbonCallbacks.vba line 2054); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `material` = sheet `ggg` column P (`spiski/material.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `material`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Характеристики > Происхождение (страна)
- Handler: `—k—04` (RibbonCallbacks.vba line 2055); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `origin` = sheet `ggg` column Q (`spiski/origin.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `origin`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Тематические > Марки и модели авто
- Handler: `—k—5` (RibbonCallbacks.vba line 2046); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `markyeryCars` = sheet `ggg` column C (`spiski/cars.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `markyeryCars`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Тематические > Имена (им.п)
- Handler: `—k—05` (RibbonCallbacks.vba line 2056); helpers: `chk` (line 2511), `–la` (lines 645–646), `a—k` (line 2175)
- Input / output: No prompt. List: named range `names` = sheet `ggg` column K (`spiski/names.xlsx`). Selection column 1; a single selected cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. `chk "edu"` first (offers to download all lists when the named range `edu` is missing or empty).
  2. Phrase-list find with list `names`, see S10 `find_phrases`.
- Quirks: Checks the range `edu`, not the list it uses. Tokens glued to punctuation never match.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Поиск по нескольким спискам
- Handler: `RbnFind` (RibbonCallbacks.vba line 3172); helpers: `ShowCombo` (line 3178), `RunCombo` (lines 3175–3177), `ListCatalog` (line 3179), `–la` (lines 645–646)
- Input / output: Form `frmCombo` (frmCombo.frm): an action combo preset to «find» and one checkbox per list of `ListCatalog` (18 lists, S10 table). Selection must be one column. INSERTS A ROW above the selection for headers and inserts new columns to the right.
- Algorithm:
  1. `ShowCombo`: refuse if the selection is not one column; show the form; OK calls `RunCombo(action, chosen names)` in catalog order.
  2. `RunCombo` inserts a header row above the selection (the data shift down one row).
  3. delete: insert one column right of the data, copy the data there, run `DeletePhrases` (S10) on it once per chosen list, in catalog order; header «Очищено: name1, name2».
  4. find / extract: for list i insert a column at data column + 1 + i and write `–la` (TRUE/FALSE) or `la—` (markers joined by "\") for that list; header = the range name (e.g. `markyeryMosmetro`).
- Quirks: The form also runs `chk "edu"` only. Headers are the internal range names, not the Russian captions. Delete chains the lists, so a later list sees text already cleaned (and lower-cased) by the earlier ones.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ОБНАРУЖИТЬ > Фразы > Найти маркеры... > Обновить все списки
- Handler: `––kak` (RibbonCallbacks.vba line 2003); helpers: `upd` (lines 2001–2002), `Redefine` (line 1987)
- Input / output: No prompt. Downloads 18 lists from `https://semtools.guru/dl/spiski/<name>.xlsx` into sheet `ggg` columns A–R, re-creates the named ranges (`def_*`), saves the add-in.
- Algorithm:
  1. Not a matcher. semkit freezes the lists (plan §1.2: «Update lists» — out).
- Quirks: Network; overwrites sheet `ggg`.
- ADR 0005 deviation that applies: n/a (out of scope).

<a id="f4"></a>
## F4. Find › Cells (ОБНАРУЖИТЬ > Ячейки)

### ОБНАРУЖИТЬ > Ячейки > По содержимому > Содержащие (указать список)
- Handler: `—kk—` (RibbonCallbacks.vba line 2556); helpers: `—––` (line 1831), `—k—` (line 1645), `ao—` (line 2443)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. `—––(cell, list)` = `—k—("ao—", cell, list)`: TRUE if any list item is a substring of the WHOLE cell: `InStr(1, UCase(cell), UCase(item)) > 0`.
  2. No word split: this is a cell-level substring test, though the button sits under «Слова > Содержащие > Где угодно».
- Examples: list [диван]: `диванчик` → TRUE; `кресло` → FALSE.
- Quirks: A blank list cell → TRUE for every cell (`InStr(x, "")` returns 1). Same handler for «Ячейки > По содержимому > Содержащие (указать список)».
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### ОБНАРУЖИТЬ > Ячейки > По содержимому > Начинающиеся на > Указать список...
- Handler: `—ko·` (RibbonCallbacks.vba line 2172); helpers: `a—a` (line 2677), `–1` (line 442), `–ok` (line 2474), `—k—` (line 1645), `—·–` (line 1657)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `–ok(cell, list)` = `—k—("—·–", cell, list)`: TRUE if the WHOLE cell starts with any list item, case-insensitive (`UCase(Left(cell, Len(item))) = UCase(item)`).
  2. Ignore-punctuation: calls `startsWithAnyFromRngIgnorePunct`, which does not exist → run-time error, swallowed by the handler's `On Error Resume Next`: nothing is written.
- Examples: list [купить]: `купить диван` → TRUE; `купитьдиван` → TRUE; `диван купить` → FALSE.
- Quirks: Prefix, not word boundary: list [диван] marks «диванчик» TRUE. Blank list cell → TRUE everywhere. Broken when «Игнорировать пунктуацию» is on.
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### ОБНАРУЖИТЬ > Ячейки > По содержимому > Начинающиеся на > Предлоги
- Handler: `findFFWprps` (RibbonCallbacks.vba line 2304); helpers: `fFW` (line 2298), `prps` (line 1322), `a—k` (line 2175)
- Input / output: No prompt. Uses the built-in `prps` list (S11). Selection column 1; single cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. Keys = `UCase` of each prps item (Dictionary).
  2. First word = `Left(cell, InStr(cell & " ", " ") - 1)` (S3 `first_word`).
  3. TRUE if `UCase(first word)` is a key.
- Examples: `для дома диван` → TRUE; `по низкой цене` → FALSE (the «пo» bug); `диван для дома` → FALSE.
- Quirks: The list holds «пo» with a LATIN «o», so «по» is never found; it also holds the junk «g». A leading space gives an empty first word → FALSE.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; use the fixed preposition list (plan: 46 items, «по» fixed, «g» dropped).

### ОБНАРУЖИТЬ > Ячейки > По содержимому > Заканчивающиеся на > Указать список...
- Handler: `—koo` (RibbonCallbacks.vba line 2822); helpers: `a—a` (line 2677), `–1` (line 442), `kaa` (line 2855), `—k—` (line 1645), `kok` (line 2499)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes TRUE/FALSE.
- Algorithm:
  1. Plain: `kaa(cell, list)` = `—k—("kok", cell, list)`: TRUE if the whole cell ends with any list item, case-insensitive.
  2. Ignore-punctuation: calls the missing `endsWithAnyFromRngIgnorePunct` → nothing is written.
- Examples: list [москва]: `диван москва` → TRUE; `диван москвы` → FALSE.
- Quirks: Suffix, not word boundary. Blank list cell → TRUE everywhere. Broken when «Игнорировать пунктуацию» is on.
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### ОБНАРУЖИТЬ > Ячейки > По содержимому > Заканчивающиеся на > Предлоги
- Handler: `findFLWprps` (RibbonCallbacks.vba line 2305); helpers: `fLW` (line 2299), `prps` (line 1322), `eLW` (line 2432)
- Input / output: No prompt. Built-in `prps` list. Selection column 1; single cell does nothing. Writes TRUE/FALSE.
- Algorithm:
  1. Last word = `eLW(cell, 1)`: `Split(cell)` on " ", last token, `Trim` (S3 `last_words`).
  2. TRUE if `UCase(last word)` is a prps key.
- Examples: `диван для` → TRUE; `диван для ` (trailing space) → FALSE.
- Quirks: A trailing space makes the last token empty → FALSE. Same «пo»/«g» junk as above.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; fixed preposition list.

### ОБНАРУЖИТЬ > Ячейки > По паттерну REGEX
- Handler: `—koa` (RibbonCallbacks.vba line 2089); helpers: `RegExMatch` (line 1646)
- Input / output: InputBox «Введите RegEx паттерн» (Type 2). Selection, every cell. Writes TRUE/FALSE.
- Algorithm:
  1. `RegExMatch(cell, p)`: VBScript RegExp, IgnoreCase False, Global True, `.Test` (search anywhere in the cell).
- Examples: p `^купить`: `купить диван` → TRUE; `Купить диван` → FALSE.
- Quirks: Case-sensitive, not anchored. Invalid pattern → run-time error.
- ADR 0005 deviation that applies: none.

### ОБНАРУЖИТЬ > Ячейки > По встречаемости > Не повторяющиеся
- Handler: `—k—a` (RibbonCallbacks.vba line 2170); helpers: `o——` (lines 381–434)
- Input / output: No prompt. Selection column 1 (whole selection is written back). Writes TRUE/FALSE.
- Algorithm:
  1. Count key = `UCase(cell)` over column 1 (S12).
  2. TRUE when the key occurs exactly once in the selection, FALSE when 2+ times.
- Examples: [Диван, диван, кресло] → [FALSE, FALSE, TRUE].
- Quirks: Empty cells are values too: one empty cell → TRUE, two → both FALSE. No trimming (`"диван "` ≠ `"диван"`).
- ADR 0005 deviation that applies: empty cells are never duplicates; ё = е.

### ОБНАРУЖИТЬ > Ячейки > По встречаемости > Повторяющиеся
- Handler: `—k–—` (RibbonCallbacks.vba line 2214); helpers: `o——` (lines 381–434)
- Input / output: No prompt. Selection column 1. Writes TRUE/FALSE.
- Algorithm:
  1. Same counts as «Не повторяющиеся»; writes `Not unique`: TRUE for every occurrence (first included) of a value that occurs 2+ times.
- Examples: [Диван, диван, кресло] → [TRUE, TRUE, FALSE].
- Quirks: Two empty cells are marked TRUE.
- ADR 0005 deviation that applies: empty cells are never duplicates; ё = е.

### ОБНАРУЖИТЬ > Ячейки > По встречаемости > Первая
- Handler: `—k–k` (RibbonCallbacks.vba line 2846); helpers: `koo·` (line 2929)
- Input / output: No prompt. Selection column 1. Writes TRUE/FALSE.
- Algorithm:
  1. Scan top-down with a Dictionary of `UCase(cell)`: TRUE when the key is new (then add it), FALSE when seen.
- Examples: [Диван, диван, кресло, диван] → [TRUE, FALSE, TRUE, FALSE].
- Quirks: Empty cells take part (the first empty cell is TRUE). No license/demo check.
- ADR 0005 deviation that applies: empty cells are never duplicates (leave them out of the count); ё = е.

### ОБНАРУЖИТЬ > Ячейки > По встречаемости > Последняя
- Handler: `—k––` (RibbonCallbacks.vba line 2493); helpers: `koo·` (line 2929)
- Input / output: No prompt. Selection column 1. Writes TRUE/FALSE.
- Algorithm:
  1. Same as «Первая» but scanning bottom-up: TRUE on the LAST occurrence of each `UCase(cell)`.
- Examples: [Диван, диван, кресло, диван] → [FALSE, FALSE, TRUE, TRUE].
- Quirks: none found.
- ADR 0005 deviation that applies: empty cells are never duplicates; ё = е.

### ОБНАРУЖИТЬ > Ячейки > Пустые ячейки
- Handler: `—kk–` (RibbonCallbacks.vba line 1872); helpers: `l—1` (line 2875)
- Input / output: No prompt. Selection, every cell. Writes TRUE/FALSE.
- Algorithm:
  1. TRUE when `Len(cell) = 0`.
- Examples: `""` → TRUE; `" "` → FALSE.
- Quirks: A cell with only spaces is not empty. A formula returning "" is empty.
- ADR 0005 deviation that applies: none.

<a id="r1"></a>
## R1. Remove › Chars (УДАЛИТЬ > Символы)

### УДАЛИТЬ > Символы > По типу > Пунктуацию
- Handler: `aok—` (RibbonCallbacks.vba line 2404); helpers: `oko` (line 1332)
- Input / output: No prompt. Selection, every cell (must be a Range). Writes the cleaned text.
- Algorithm:
  1. For each character c: keep it if `InStr(" 1234567890", c) > 0` (space or ASCII digit) or `UCase(c) <> LCase(c)` (a cased letter); otherwise write a space.
  2. Then `a·` (S3): trim spaces, collapse runs of spaces to one.
- Examples: `Диван-кровать, 2 шт.!` → `Диван кровать 2 шт`; `«ИКЕА»` → `ИКЕА`.
- Quirks: «Punctuation» = everything that is not a space, ASCII digit or cased letter: hyphens, quotes, symbols, tabs, line breaks, nbsp, and also uncased letters (CJK, Arabic). «из-за» → «из за». Same handler as ИЗВЛЕЧЬ > Символы > Любые буквы и цифры.
- ADR 0005 deviation that applies: no double spaces (already); split on any whitespace (tabs/nbsp become spaces anyway).

### УДАЛИТЬ > Символы > По типу > Лишние пробелы > Все
- Handler: `–aal` (RibbonCallbacks.vba line 1941); helpers: `a·` (line 1855)
- Input / output: No prompt. Selection, every cell (must be a Range). Writes the result. No undo backup.
- Algorithm:
  1. `a·(s)`: `Trim$` (spaces only), then replace "  " by " " until none is left.
- Examples: `  купить   диван ` → `купить диван`.
- Quirks: Only U+0020 counts: tabs, nbsp and line breaks stay.
- ADR 0005 deviation that applies: split on any whitespace: collapse every whitespace run (tabs, nbsp, newlines) to one space.

### УДАЛИТЬ > Символы > По типу > Лишние пробелы > Слева
- Handler: `—ako` (RibbonCallbacks.vba line 2926); helpers: `k·—k` (line 2259)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `LTrim(s)`: drop leading U+0020 spaces only.
- Examples: `  купить  диван ` → `купить  диван `.
- Quirks: Inner double spaces stay.
- ADR 0005 deviation that applies: Open: ADR «no double spaces in results» would turn this into full normalization; keep VBA (leading spaces only) unless the Architect says otherwise.

### УДАЛИТЬ > Символы > По типу > Лишние пробелы > Справа
- Handler: `a–o—` (RibbonCallbacks.vba line 2230); helpers: `ook–` (line 1658)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `RTrim(s)`: drop trailing U+0020 spaces only.
- Examples: `  диван  ` → `  диван`.
- Quirks: none found.
- ADR 0005 deviation that applies: Open (see «Слева»).

### УДАЛИТЬ > Символы > По типу > Лишние пробелы > Слева и справа
- Handler: `a–k—` (RibbonCallbacks.vba line 1878); helpers: `ook—` (line 1702)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `Trim(s)`: drop leading and trailing U+0020 spaces.
- Examples: ` купить  диван ` → `купить  диван`.
- Quirks: VBA `Trim` does NOT collapse inner spaces (Excel TRIM does).
- ADR 0005 deviation that applies: Open (see «Слева»).

### УДАЛИТЬ > Символы > По типу > Цифры
- Handler: `aokk` (RibbonCallbacks.vba line 1924); helpers: `kk–—` (line 1923), `RegExReplace` (line 2080)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `RegExReplace(s, "[0-9]", "")` (global).
  2. If the result starts with the literal text "=+-", prefix "'" (never in practice).
- Examples: `диван 2 местный` → `диван  местный`; `120x200` → `x`.
- Quirks: No trim: removing a word made of digits leaves double/edge spaces. The «=+-» guard is a bug (meant: starts with = or + or -).
- ADR 0005 deviation that applies: no double spaces in results (collapse + trim).

### УДАЛИТЬ > Символы > По типу > Латиницу
- Handler: `ak·—` (RibbonCallbacks.vba line 1856); helpers: `ok––` (line 2607), `RegExReplace` (line 2080)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `RegExReplace(s, "[a-zA-Z]", "")`.
- Examples: `Диван IKEA Ektorp` → `Диван  ` (two trailing spaces).
- Quirks: No trim.
- ADR 0005 deviation that applies: no double spaces in results.

### УДАЛИТЬ > Символы > По типу > Кириллицу
- Handler: `ak–·` (RibbonCallbacks.vba line 1867); helpers: `ok–o` (line 2564), `RegExReplace` (line 2080)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `RegExReplace(s, "[\u0410-\u04FF\u0401\u0451]", "")`.
- Examples: `Диван IKEA` → ` IKEA`.
- Quirks: No trim. Uppercase Є І Ї (U+0404/0406/0407) are not removed.
- ADR 0005 deviation that applies: no double spaces in results.

### УДАЛИТЬ > Символы > По позиции... > С начала ячейки
- Handler: `ak——` (RibbonCallbacks.vba line 2702); helpers: `oaa` (line 1651)
- Input / output: InputBox «количество символов» (Type 1, number N). Selection, every cell. Writes the result.
- Algorithm:
  1. If N > Len(s) → "".
  2. Else `"'" & Mid(s, N + 1)` (S1: the apostrophe is Excel's text marker; drop it).
- Examples: N=2: `1. диван` → ` диван`; N=10: `диван` → "".
- Quirks: N < 0 → run-time error. N = 0 keeps the cell.
- ADR 0005 deviation that applies: none

### УДАЛИТЬ > Символы > По позиции... > С конца ячейки
- Handler: `ak·k` (RibbonCallbacks.vba line 2086); helpers: `–·—` (line 2375)
- Input / output: InputBox «Количество символов:» (Type 1). Selection, every cell. Writes the result.
- Algorithm:
  1. If N > Len(s) → "".
  2. Else `"'" & Left(s, Len(s) - N)`.
- Examples: N=1: `диван.` → `диван`.
- Quirks: none found.
- ADR 0005 deviation that applies: none

### УДАЛИТЬ > Символы > До вхожд-я... > Первого > Включительно
- Handler: `––·a` (RibbonCallbacks.vba line 2125); helpers: `kkoa` (line 1356)
- Input / output: InputBox «Паттерн для поиска(символ или последовательность)» (Type 2, literal text, not regex). Selection, every cell. Writes the result.
- Algorithm:
  1. pos = `InStr(1, s, p, vbTextCompare)` (first occurrence, case-insensitive).
  2. If pos = 0 (not found) → the cell is unchanged.
  3. Else result = `"'" & Mid(s, pos + Len(p))` (text after the pattern).
- Examples: p `:`: `Товар: диван: синий` → ` диван: синий`.
- Quirks: First-occurrence buttons compare case-insensitively, last-occurrence buttons case-sensitively.
- ADR 0005 deviation that applies: ё = е in the search; no double spaces in results (trim the cut edge).

### УДАЛИТЬ > Символы > До вхожд-я... > Первого > Все что перед ним
- Handler: `––·—` (RibbonCallbacks.vba line 2786); helpers: `kko—` (line 1357)
- Input / output: InputBox «Паттерн для поиска(символ или последовательность)» (Type 2, literal text, not regex). Selection, every cell. Writes the result.
- Algorithm:
  1. pos = `InStr(1, s, p, vbTextCompare)` (first occurrence, case-insensitive).
  2. If pos = 0 (not found) → the cell is unchanged.
  3. Else result = `"'" & Mid(s, pos)` (the pattern and what follows).
- Examples: p `диван`: `купить Диван синий` → `Диван синий`.
- Quirks: First-occurrence buttons compare case-insensitively, last-occurrence buttons case-sensitively.
- ADR 0005 deviation that applies: ё = е in the search; no double spaces in results (trim the cut edge).

### УДАЛИТЬ > Символы > До вхожд-я... > Последнего > Включительно
- Handler: `–—kk` (RibbonCallbacks.vba line 2923); helpers: `kk–k` (line 2921)
- Input / output: InputBox «Паттерн для поиска(символ или последовательность)» (Type 2, literal text, not regex). Selection, every cell. Writes the result.
- Algorithm:
  1. pos = `InStrRev(s, p) (binary)` (last occurrence, case-SENSITIVE).
  2. If pos = 0 (not found) → the cell is unchanged.
  3. Else result = `Right(s, Len(s) - pos - Len(p) + 1)` (text after the last pattern; no apostrophe).
- Examples: p `/`: `a/b/c` → `c`.
- Quirks: First-occurrence buttons compare case-insensitively, last-occurrence buttons case-sensitively. No apostrophe prefix: a result starting with «=» becomes a formula in Excel.
- ADR 0005 deviation that applies: ё = е in the search; no double spaces in results (trim the cut edge).

### УДАЛИТЬ > Символы > До вхожд-я... > Последнего > Все что перед ним
- Handler: `––··` (RibbonCallbacks.vba line 2389); helpers: `kko·` (line 1359)
- Input / output: InputBox «Паттерн для поиска(символ или последовательность)» (Type 2, literal text, not regex). Selection, every cell. Writes the result.
- Algorithm:
  1. pos = `InStrRev(s, p) (binary)` (last occurrence, case-SENSITIVE).
  2. If pos = 0 (not found) → the cell is unchanged.
  3. Else result = `Right(s, Len(s) - pos + 1)` (the last pattern and what follows; no apostrophe).
- Examples: p `/`: `a/b/c` → `/c`.
- Quirks: First-occurrence buttons compare case-insensitively, last-occurrence buttons case-sensitively. No apostrophe prefix: a result starting with «=» becomes a formula in Excel.
- ADR 0005 deviation that applies: ё = е in the search; no double spaces in results (trim the cut edge).

### УДАЛИТЬ > Символы > После вхожд-я... > Первого > Включительно
- Handler: `––—–` (RibbonCallbacks.vba line 1791); helpers: `kkok` (line 1360)
- Input / output: InputBox «Паттерн для поиска(символ или последовательность)» (Type 2, literal text, not regex). Selection, every cell. Writes the result.
- Algorithm:
  1. pos = `InStr(1, s, p, vbTextCompare)` (first occurrence, case-insensitive).
  2. If pos = 0 (not found) → the cell is unchanged.
  3. Else result = `"'" & Left(s, pos - 1)` (text before the pattern).
- Examples: p ` - `: `диван - синий - большой` → `диван`.
- Quirks: First-occurrence buttons compare case-insensitively, last-occurrence buttons case-sensitively.
- ADR 0005 deviation that applies: ё = е in the search; no double spaces in results (trim the cut edge).

### УДАЛИТЬ > Символы > После вхожд-я... > Первого > Все что после
- Handler: `––—o` (RibbonCallbacks.vba line 2721); helpers: `kkk·` (line 1342)
- Input / output: InputBox «Паттерн для поиска(символ или последовательность)» (Type 2, literal text, not regex). Selection, every cell. Writes the result.
- Algorithm:
  1. pos = `InStr(1, s, p, vbTextCompare)` (first occurrence, case-insensitive).
  2. If pos = 0 (not found) → the cell is unchanged.
  3. Else result = `"'" & Left(s, pos + Len(p) - 1)` (up to and including the pattern).
- Examples: p `диван`: `купить Диван синий` → `купить Диван`.
- Quirks: First-occurrence buttons compare case-insensitively, last-occurrence buttons case-sensitively.
- ADR 0005 deviation that applies: ё = е in the search; no double spaces in results (trim the cut edge).

### УДАЛИТЬ > Символы > После вхожд-я... > Последнего > Включительно
- Handler: `––—a` (RibbonCallbacks.vba line 2687); helpers: `kko–` (line 1362)
- Input / output: InputBox «Паттерн для поиска(символ или последовательность)» (Type 2, literal text, not regex). Selection, every cell. Writes the result.
- Algorithm:
  1. pos = `InStrRev(s, p) (binary)` (last occurrence, case-SENSITIVE).
  2. If pos = 0 (not found) → the cell is unchanged.
  3. Else result = `"'" & Left(s, pos - 1)`.
- Examples: p `/`: `a/b/c` → `a/b`.
- Quirks: First-occurrence buttons compare case-insensitively, last-occurrence buttons case-sensitively.
- ADR 0005 deviation that applies: ё = е in the search; no double spaces in results (trim the cut edge).

### УДАЛИТЬ > Символы > После вхожд-я... > Последнего > Все что после
- Handler: `––——` (RibbonCallbacks.vba line 2250); helpers: `kkoo` (line 1363)
- Input / output: InputBox «Паттерн для поиска(символ или последовательность)» (Type 2, literal text, not regex). Selection, every cell. Writes the result.
- Algorithm:
  1. pos = `InStrRev(s, p) (binary)` (last occurrence, case-SENSITIVE).
  2. If pos = 0 (not found) → the cell is unchanged.
  3. Else result = `"'" & Left(s, pos + Len(p) - 1)`.
- Examples: p `/`: `a/b/c` → `a/b/`.
- Quirks: First-occurrence buttons compare case-insensitively, last-occurrence buttons case-sensitively.
- ADR 0005 deviation that applies: ё = е in the search; no double spaces in results (trim the cut edge).

### УДАЛИТЬ > Символы > по REGEX... > Все, попадающее под паттерн
- Handler: `aoka` (RibbonCallbacks.vba line 2363); helpers: `ookk` (line 2807), `RegExReplace` (line 2080)
- Input / output: InputBox «Удалить все содержимое ячейки, удовлетворяющее паттерну:» (Type 2). Selection, every cell. Writes the result.
- Algorithm:
  1. `RegExReplace(s, p, "")`: VBScript RegExp, Global True, IgnoreCase False, MultiLine False.
  2. Empty s or empty p → s unchanged.
  3. If the result starts with the literal "=+-" → prefix "'" (dead guard).
- Examples: p `\d+`: `диван 2 места` → `диван  места`.
- Quirks: No trim after the replace. Invalid pattern → the error is swallowed and s is returned unchanged.
- ADR 0005 deviation that applies: no double spaces in results.

### УДАЛИТЬ > Символы > по REGEX... > Все, НЕ попадающее под паттерн
- Handler: `aok·` (RibbonCallbacks.vba line 1820); helpers: `ooko` (line 1871), `RegExExtract` (line 2970)
- Input / output: InputBox «Удалить все, кроме содержимого, удовлетворяющего паттерну:» (Type 2) into variable `—`. Selection, every cell.
- Algorithm:
  1. Intended: keep only the matches: `RegExExtract(s, p, Global=True)` (all matches concatenated, no separator).
  2. Actual: the call passes the undeclared variable `o—` instead of `—` (no `Option Explicit`), so the pattern is "". An empty pattern matches the empty string at every position: every cell becomes "".
- Examples: any input → "" (VBA); intended, p `\d+`: `диван 120x200` → `120200`.
- Quirks: BUG: the button empties every selected cell whatever the user types.
- ADR 0005 deviation that applies: Fix: implement the intended algorithm (concatenate all matches of p, no separator).

<a id="r2"></a>
## R2. Remove › Words (УДАЛИТЬ > Слова)

### УДАЛИТЬ > Слова > Целые слова > 1 слово
- Handler: `ao—a` (RibbonCallbacks.vba line 1835); helpers: `·––` (line 1858), `·a` (line 441), `k––—` (line 2735), `k––a` (line 1803), `aao` (line 1925), `–—a` (line 2318), `a·` (line 1855)
- Input / output: InputBox «Напишите слово для удаления(без пробелов)» (Type 2). Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `k––—` = `aao("–—a", s, w)`: tokens = `Split(s & " ")`; blank every token with `UCase(token) = UCase(w)`; join with " "; `a·`.
  2. Ignore-punctuation: `k––a`: compare `oko(token)` with w (a token «диван,» is removed whole, comma included).
- Examples: w `диван`: `Диван диван-кровать диван` → `диван-кровать`; w `диван`: `диван, кресло` → `диван, кресло` (ignore-punct: `кресло`).
- Quirks: Case-insensitive, ё ≠ е. The text is normalized by `a·` (trim + single spaces) even when nothing is removed.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Слова > Целые слова > Указать список... > Удалить все
- Handler: `aok–` (RibbonCallbacks.vba line 2733); helpers: `DeletePhrases` (lines 3452–3470)
- Input / output: InputBox «Выберите список фраз» (Type 8). Selection column 1 (≥ 2 cells). Overwrites the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. Remove list phrases, see S10 `remove_phrases`.
- Examples: list [купить, в москве]: `Купить диван в Москве` → `диван`; list [москве]: `Диван Москва` → `диван москва`.
- Quirks: The output is lower-cased. Same handler as «Фразы > Свой список фраз». A one-cell selection makes `Selection.value2` a scalar → error, swallowed: nothing happens.
- ADR 0005 deviation that applies: keep original case (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Слова > Целые слова > Указать список... > Только в начале строки
- Handler: `dFWCustom` (RibbonCallbacks.vba line 2309); helpers: `dFWrng` (line 2303), `a—k` (line 2175), `o––` (line 2429), `·ka` (line 2431), `akk` (line 2414)
- Input / output: InputBox for a range (Type 8): word list, column 1. Selection column 1; single cell does nothing. Writes the result.
- Algorithm:
  1. Keys: `UCase` of every list row, added with `Dictionary.Add`.
  2. For each cell: first word = `a—k(cell)` (text before the first space).
  3. If `UCase(first word)` is a key: cell = `o––(cell, 1)` = all words but the first (`·ka(cell, akk(cell) - 1)`, "'"-prefixed).
  4. One pass: only one leading word is removed.
- Examples: list [купить]: `Купить диван купить` → `диван купить`; `диван купить` → unchanged.
- Quirks: A duplicate or a second blank cell in the list makes `Dictionary.Add` fail; the error is swallowed by the caller → nothing is written and screen updating stays off. Words are split on single spaces.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; tolerate duplicate list items.

### УДАЛИТЬ > Слова > Целые слова > Указать список... > Только в конце строки
- Handler: `dLWCustom` (RibbonCallbacks.vba line 2308); helpers: `dLWrng` (line 2302), `eLW` (line 2432), `–·a` (line 2319), `·k—` (line 1644), `akk` (line 2414)
- Input / output: InputBox for a range (Type 8): word list, column 1. Selection column 1; single cell does nothing. Writes the result.
- Algorithm:
  1. Keys: `UCase` of every list row (`Dictionary.Add`).
  2. Last word = `eLW(cell, 1)`.
  3. If it is a key: cell = `–·a(cell, 1)` = the first (count − 1) words ("'"-prefixed). One pass.
- Examples: list [купить]: `диван купить` → `диван`.
- Quirks: Duplicates in the list → silent no-op (as above). A trailing space makes the last word empty → nothing removed.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; tolerate duplicate list items.

### УДАЛИТЬ > Слова > Целые слова > Части речи... > Существительные
- Handler: `ak··` (RibbonCallbacks.vba line 2642); helpers: `get_lemmdict` (line 2109), `ao–` (line 2650), `k–` (line 1937), `ok–—` (line 1741), `ok–a` (line 1958), `aka` (line 2731), `··–` (line 2207), `a·` (line 1855)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `ok–—` = `aka("··–", s)`: tokens = `Split(s & " ")`; blank every token that is a noun (`··–`, S9); join " "; `a·`.
  2. Ignore-punctuation: `ok–a`: test `oko(token)` instead of the token (the whole token, punctuation included, is removed).
- Examples: `купить красный диван быстро` → noun: `купить красный быстро`; adjective: `купить диван быстро`; verb: `красный диван быстро`; adverb: `купить красный диван` (dictionary tags assumed).
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace; ё = е in the lookup.

### УДАЛИТЬ > Слова > Целые слова > Части речи... > Прилагательные
- Handler: `—··a` (RibbonCallbacks.vba line 2697); helpers: `get_lemmdict` (line 2109), `ao–` (line 2650), `k–` (line 1937), `oko—` (line 1626), `ok–k` (line 2362), `aka` (line 2731), `··o` (line 1439), `a·` (line 1855)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `oko—` = `aka("··o", s)`: tokens = `Split(s & " ")`; blank every token that is an adjective (`··o`, S9); join " "; `a·`.
  2. Ignore-punctuation: `ok–k`: test `oko(token)` instead of the token (the whole token, punctuation included, is removed).
- Examples: `купить красный диван быстро` → noun: `купить красный быстро`; adjective: `купить диван быстро`; verb: `красный диван быстро`; adverb: `купить красный диван` (dictionary tags assumed).
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace; ё = е in the lookup.

### УДАЛИТЬ > Слова > Целые слова > Части речи... > Глаголы
- Handler: `ao——` (RibbonCallbacks.vba line 1897); helpers: `get_lemmdict` (line 2109), `ao–` (line 2650), `k–` (line 1937), `ok·k` (line 1902), `ok·–` (line 1768), `aka` (line 2731), `·ok` (line 1344), `a·` (line 1855)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `ok·k` = `aka("·ok", s)`: tokens = `Split(s & " ")`; blank every token that is a verb (`·ok`, S9); join " "; `a·`.
  2. Ignore-punctuation: `ok·–`: test `oko(token)` instead of the token (the whole token, punctuation included, is removed).
- Examples: `купить красный диван быстро` → noun: `купить красный быстро`; adjective: `купить диван быстро`; verb: `красный диван быстро`; adverb: `купить красный диван` (dictionary tags assumed).
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace; ё = е in the lookup.

### УДАЛИТЬ > Слова > Целые слова > Части речи... > Наречия
- Handler: `—···` (RibbonCallbacks.vba line 2563); helpers: `get_lemmdict` (line 2109), `ao–` (line 2650), `k–` (line 1937), `okoa` (line 2635), `oko·` (line 2907), `aka` (line 2731), `oa–` (line 2154), `a·` (line 1855)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `okoa` = `aka("oa–", s)`: tokens = `Split(s & " ")`; blank every token that is an adverb (`oa–`, S9); join " "; `a·`.
  2. Ignore-punctuation: `oko·`: test `oko(token)` instead of the token (the whole token, punctuation included, is removed).
- Examples: `купить красный диван быстро` → noun: `купить красный быстро`; adjective: `купить диван быстро`; verb: `красный диван быстро`; adverb: `купить красный диван` (dictionary tags assumed).
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace; ё = е in the lookup.

### УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Паттерн
- Handler: `aoak` (RibbonCallbacks.vba line 2901); helpers: `k–oo` (line 2743)
- Input / output: InputBox (Type 2) pattern p — Cancel is NOT checked (p becomes "False"). Selection, every cell. Writes the result.
- Algorithm:
  1. If s = "" → "". lp = LCase(p).
  2. If `InStr(LCase(s), lp) = 0` → s unchanged.
  3. Else walk the words split on " " (manual scan): keep words whose `LCase` does not contain lp; join kept words with one space.
- Examples: p `диван`: `диван диванчик кресло` → `кресло`; p `ДИВ`: `Диван кресло` → `кресло`.
- Quirks: Cancel removes words containing «false». Empty p removes every word. No ignore-punctuation variant. Empty words between double spaces are kept (a single space survives).
- ADR 0005 deviation that applies: ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Список паттернов
- Handler: `aoao` (RibbonCallbacks.vba lines 2183–2185); helpers: none
- Input / output: InputBox «Введите список паттернов» (Type 8): all rows AND all columns of the range. Selection, every cell. Writes the result.
- Algorithm:
  1. Skip empty cells. ls = LCase(cell).
  2. st = the first list row i that has a non-blank item which is a substring of ls. None → the cell is unchanged.
  3. Split the cell on " "; for each word, drop it if any non-blank item in rows st..end (any column) is a substring of `LCase(word)`.
  4. Join kept words with one space.
- Examples: list [див, крес]: `диван кресло стол` → `стол`.
- Quirks: A one-cell pattern range gives a scalar (`IsArray` False) → every cell is unchanged. Blank items are skipped (unlike most list handlers).
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Только латиницу
- Handler: `a·—–` (RibbonCallbacks.vba line 2456); helpers: `k–ka` (line 2167), `aka` (line 2731), `ala` (line 1770), `a·` (line 1855)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k–ka` = `aka("ala", s)`: tokens = `Split(s & " ")`; blank tokens that are only latin: `x Like "*[A-Za-z]*" And Not x Like "*[0-9А-Яа-я]*"`; join " "; `a·`.
- Examples: `диван IKEA 3d Ektorp` → `диван 3d`.
- Quirks: `[А-Яа-я]` misses Ё/ё: «Ёlka» counts as only-latin.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Латиницу
- Handler: `a·a–` (RibbonCallbacks.vba line 2336); helpers: `k–k–` (line 1853), `aka` (line 2731), `a–—` (line 2153), `a·` (line 1855)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k–k–` = `aka("a–—", s)`: tokens = `Split(s & " ")`; blank tokens that are contains latin (`Like "*[A-Za-z]*"`); join " "; `a·`.
- Examples: `диван IKEA 3d Ektorp` → `диван`.
- Quirks: Punctuation stays part of the token.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Только цифры
- Handler: `a·——` (RibbonCallbacks.vba line 2780); helpers: `k–ko` (line 2663), `aka` (line 2731), `··—` (line 2360), `a·` (line 1855)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k–ko` = `aka("··—", s)`: tokens = `Split(s & " ")`; blank tokens that are `IsNumeric(token)`; join " "; `a·`.
- Examples: `диван 2 120x200 1,5` → `диван 120x200` (ru locale: «1,5» is numeric).
- Quirks: `IsNumeric` is locale-aware: «1,5», «1e3», «-5», «(5)», «$5» and «&H10» count as numbers.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По содержимому... > Содержащие... > Цифры
- Handler: `a·a—` (RibbonCallbacks.vba line 1864); helpers: `k–k—` (line 1830), `aka` (line 2731), `·kk` (line 1619), `a·` (line 1855)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k–k—` = `aka("·kk", s)`: tokens = `Split(s & " ")`; blank tokens that are contains an ASCII digit; join " "; `a·`.
- Examples: `диван 2 120x200 3d` → `диван`.
- Quirks: Punctuation stays part of the token.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По содержимому... > Начинающиеся на... > Паттерн
- Handler: `aoaa` (RibbonCallbacks.vba line 2653); helpers: `·––` (line 1858), `·a` (line 441), `k––·` (line 2463), `k–—–` (line 2354), `aao` (line 1925), `—·–` (line 1657)
- Input / output: InputBox (Type 2) pattern p. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `k––·` = `aao("—·–", s, p)`: blank tokens that start with p (case-insensitive); join " "; `a·`.
  2. Ignore-punctuation: `k–—–` tests `oko(token)`.
- Examples: p `див`: `купить диван и диванчик` → `купить и`.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Слова > По содержимому... > Начинающиеся на... > Список паттернов
- Handler: `aoa·` (RibbonCallbacks.vba line 1762); helpers: `a—a` (line 2677), `–1` (line 442), `k–—k` (line 1944), `k–—o` (line 1773), `—–·` (line 2811), `—·–` (line 1657)
- Input / output: InputBox for a range (Type 8): pattern list, column 1, all rows. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `k–—k` = `—–·("—·–", s, list)`: tokens = `Split(s & " ")`; a token is blanked if it starts with any list item; join " "; `a·`.
  2. Ignore-punctuation: `k–—o` tests `oko(token)`.
- Examples: list [див, крес]: `купить диван кресло` → `купить`.
- Quirks: A blank list cell blanks every token (empty prefix matches).
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### УДАЛИТЬ > Слова > По содержимому... > Заканчивающиеся на... > Паттерн
- Handler: `aoa–` (RibbonCallbacks.vba line 1887); helpers: `·––` (line 1858), `·a` (line 441), `k–o—` (line 1934), `k––k` (line 1722), `aao` (line 1925), `kok` (line 2499)
- Input / output: InputBox (Type 2) pattern p. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `k–o—` = `aao("kok", s, p)`: blank tokens that end with p (case-insensitive); join; `a·`.
  2. Ignore-punctuation: `k––k` tests `oko(token)`.
- Examples: p `ый`: `красный большой диван` → `диван`.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Слова > По содержимому... > Заканчивающиеся на... > Список паттернов
- Handler: `aoa—` (RibbonCallbacks.vba line 2706); helpers: `a—a` (line 2677), `–1` (line 442), `k–oa` (line 2742), `k–o·` (line 1662), `–—k` (line 1727), `kaa` (line 2855), `—k—` (line 1645), `kok` (line 2499)
- Input / output: InputBox for a range (Type 8): pattern list, column 1. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `k–oa` = `–—k("kaa", s, list)`: blank tokens that end with any list item; join; `a·`.
  2. Ignore-punctuation: `k–o·` tests `oko(token)`.
- Examples: list [ый, ая]: `красный диван белая кровать` → `диван кровать`.
- Quirks: A blank list cell blanks every token.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### УДАЛИТЬ > Слова > По паттерну REGEX
- Handler: `––·k` (RibbonCallbacks.vba line 1804); helpers: `·––` (line 1858), `·a` (line 441), `k–k·` (line 1863), `k–ok` (line 2163), `aao` (line 1925), `RegExMatch` (line 1646)
- Input / output: InputBox (Type 2) regex p. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `k–k·` = `aao("RegExMatch", s, p)`: blank tokens where the regex finds a match (search, case-sensitive); join; `a·`.
  2. Ignore-punctuation: `k–ok` tests `oko(token)`.
- Examples: p `^\d+$`: `диван 2 места 2024` → `диван места`.
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По порядку... > Первые... > 1
- Handler: `ak—k` (RibbonCallbacks.vba line 2081); helpers: `o––` (line 2429), `·ka` (line 2431), `akk` (line 2414)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `o––(s, 1)` = `·ka(s, akk(s) - 1)`: keep the last (count − 1) words.
  2. `akk(s)` = number of tokens of `Split(s, " ")` (empty tokens counted).
  3. `·ka(s, k)`: tokens = `Split(s)`; if k > count → s; else join tokens count−k+1..count with " ", `Trim`, prefix "'".
  4. If the cell has ≤ 1 words → "".
- Examples: `купить диван в москве` → `диван в москве`.
- Quirks: Double spaces create empty tokens that count as words: `a  b c` minus 1 word → `b c`, minus 2 → `b c` too.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По порядку... > Первые... > 2
- Handler: `ak—o` (RibbonCallbacks.vba line 2659); helpers: `o––` (line 2429), `·ka` (line 2431), `akk` (line 2414)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `o––(s, 2)` = `·ka(s, akk(s) - 2)`: keep the last (count − 2) words.
  2. `akk(s)` = number of tokens of `Split(s, " ")` (empty tokens counted).
  3. `·ka(s, k)`: tokens = `Split(s)`; if k > count → s; else join tokens count−k+1..count with " ", `Trim`, prefix "'".
  4. If the cell has ≤ 2 words → "".
- Examples: `купить диван в москве` → `в москве`.
- Quirks: Double spaces create empty tokens that count as words: `a  b c` minus 1 word → `b c`, minus 2 → `b c` too.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По порядку... > Первые... > 3
- Handler: `ak—–` (RibbonCallbacks.vba line 2485); helpers: `o––` (line 2429), `·ka` (line 2431), `akk` (line 2414)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `o––(s, 3)` = `·ka(s, akk(s) - 3)`: keep the last (count − 3) words.
  2. `akk(s)` = number of tokens of `Split(s, " ")` (empty tokens counted).
  3. `·ka(s, k)`: tokens = `Split(s)`; if k > count → s; else join tokens count−k+1..count with " ", `Trim`, prefix "'".
  4. If the cell has ≤ 3 words → "".
- Examples: `купить диван в москве` → `москве`.
- Quirks: Double spaces create empty tokens that count as words: `a  b c` minus 1 word → `b c`, minus 2 → `b c` too.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По порядку... > Первые... > N
- Handler: `ak—a` (RibbonCallbacks.vba line 2939); helpers: `o––` (line 2429), `·ka` (line 2431), `akk` (line 2414)
- Input / output: InputBox «количество слов» (Type 1). Selection, every cell. Writes the result.
- Algorithm:
  1. `o––(s, N)` = `·ka(s, akk(s) - N)`: keep the last (count − N) words.
  2. `akk(s)` = number of tokens of `Split(s, " ")` (empty tokens counted).
  3. `·ka(s, k)`: tokens = `Split(s)`; if k > count → s; else join tokens count−k+1..count with " ", `Trim`, prefix "'".
  4. If the cell has ≤ N words → "".
- Examples: `купить диван в москве` → `диван в москве` (N=1).
- Quirks: Double spaces create empty tokens that count as words: `a  b c` minus 1 word → `b c`, minus 2 → `b c` too.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По порядку... > Последние... > 1
- Handler: `aka—` (RibbonCallbacks.vba line 1940); helpers: `–·a` (line 2319), `·k—` (line 1644), `akk` (line 2414)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `–·a(s, 1)` = `·k—(s, akk(s) - 1)`: keep the first (count − 1) words.
  2. `·k—(s, k)`: tokens = `Split(s)`; if k > count → s; else join tokens 1..k with " ", `Trim`, prefix "'".
  3. If the cell has ≤ 1 words → "".
- Examples: `купить диван в москве` → `купить диван в`.
- Quirks: Empty tokens from double spaces count as words.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По порядку... > Последние... > 2
- Handler: `akaa` (RibbonCallbacks.vba line 2357); helpers: `–·a` (line 2319), `·k—` (line 1644), `akk` (line 2414)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `–·a(s, 2)` = `·k—(s, akk(s) - 2)`: keep the first (count − 2) words.
  2. `·k—(s, k)`: tokens = `Split(s)`; if k > count → s; else join tokens 1..k with " ", `Trim`, prefix "'".
  3. If the cell has ≤ 2 words → "".
- Examples: `купить диван в москве` → `купить диван`.
- Quirks: Empty tokens from double spaces count as words.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По порядку... > Последние... > 3
- Handler: `aka·` (RibbonCallbacks.vba line 2962); helpers: `–·a` (line 2319), `·k—` (line 1644), `akk` (line 2414)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `–·a(s, 3)` = `·k—(s, akk(s) - 3)`: keep the first (count − 3) words.
  2. `·k—(s, k)`: tokens = `Split(s)`; if k > count → s; else join tokens 1..k with " ", `Trim`, prefix "'".
  3. If the cell has ≤ 3 words → "".
- Examples: `купить диван в москве` → `купить`.
- Quirks: Empty tokens from double spaces count as words.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > По порядку... > Последние... > N
- Handler: `ak·o` (RibbonCallbacks.vba line 2270); helpers: `–·a` (line 2319), `·k—` (line 1644), `akk` (line 2414)
- Input / output: InputBox «количество слов» (Type 1). Selection, every cell. Writes the result.
- Algorithm:
  1. `–·a(s, N)` = `·k—(s, akk(s) - N)`: keep the first (count − N) words.
  2. `·k—(s, k)`: tokens = `Split(s)`; if k > count → s; else join tokens 1..k with " ", `Trim`, prefix "'".
  3. If the cell has ≤ N words → "".
- Examples: `купить диван в москве` → `купить диван в` (N=1).
- Quirks: Empty tokens from double spaces count as words.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Все
- Handler: `aala` (RibbonCallbacks.vba line 2514); helpers: `ao–` (line 2650), `k–` (line 1937), `a·o` (line 1649), `ok—a` (line 1311), `oko` (line 1332)
- Input / output: No prompt. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `a·o(s)`: U = `Split(UCase(s), " ")`, W = `Split(s, " ")`.
  2. For g = 0..n−1, for a = g+1..n: if U(g) = U(a) → W(a) = "" (later repeats go; the first occurrence stays with its case).
  3. Join W with " ", `a·`.
  4. Ignore-punctuation: `ok—a` compares `oko(U(g))` with `oko(U(a))` but blanks in `Split(a·(s))` — see quirks.
- Examples: `Купить диван купить диван недорого` → `Купить диван недорого`; `диван  диван` → `диван`.
- Quirks: Ignore-punctuation variants (`ok—a`, `okak`, `okao`, `ok—·`) split the raw text for comparison and the `a·`-normalized text for output: with double spaces the indexes drift and the wrong word is removed (or an index error occurs).
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Только англ. слов
- Handler: `aal1` (RibbonCallbacks.vba line 2257); helpers: `ao–` (line 2650), `k–` (line 1937), `ok——` (line 1308), `okak` (line 1312), `a–—` (line 2153)
- Input / output: No prompt. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `ok——`: as «Все», but a later token is blanked only when it equals an earlier token U(g) AND U(g) contains latin (`a–—`).
  2. Ignore-punctuation: `okak` (same with `oko`, same index drift bug).
- Examples: `iphone 13 iphone 13` → `iphone 13 13`.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Только русских слов
- Handler: `aall` (RibbonCallbacks.vba line 2703); helpers: `ao–` (line 2650), `k–` (line 1937), `oka—` (line 1309), `okao` (line 1313), `—–o` (line 2147)
- Input / output: No prompt. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `oka—`: as «Все», only for earlier tokens that contain a cyrillic char (`—–o`, S4).
  2. Ignore-punctuation: `okao`.
- Examples: `диван 2 диван 2` → `диван 2 2`.
- Quirks: A mixed token («wi-fi-роутер») counts as Russian.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Только идущие подряд
- Handler: `remrepW` (RibbonCallbacks.vba line 1697); helpers: `k–` (line 1937), `RCD` (line 177)
- Input / output: No prompt. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. W = `Split(s, " ")`.
  2. For i = last down to 1: if `StrComp(W(i), W(i-1), vbTextCompare) = 0` → W(i) = "" (W(i-1) is still the original word).
  3. Result = Excel `TRIM(Join(W, " "))` (trim + collapse inner spaces).
- Examples: `диван диван Диван кресло диван` → `диван кресло диван`.
- Quirks: No ignore-punctuation variant. Text compare (case-insensitive). Repeats split by a double space are not adjacent (the empty token sits between them).
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Слова > Повторы слов... > Точные повторы... > Только чисел
- Handler: `aal·` (RibbonCallbacks.vba line 2569); helpers: `ao–` (line 2650), `k–` (line 1937), `ok—–` (line 1310), `ok—·` (line 1314), `··—` (line 2360)
- Input / output: No prompt. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. Plain: `ok—–`: as «Все», only for earlier tokens with `IsNumeric(U(g))`.
  2. Ignore-punctuation: `ok—·`.
- Examples: `диван 2 места 2 шт` → `диван 2 места шт`.
- Quirks: IsNumeric is locale-aware (see «Только цифры»).
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Слова > Повторы слов... > С учетом словоформ (Ru)
- Handler: `aook` (RibbonCallbacks.vba line 2371); helpers: `get_lemmdict` (line 2109), `k–` (line 1937), `oka–` (line 1874), `—··` (line 2395), `aaa` (line 1354)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. L = `Split(UCase(—··(LCase(s))), " ")` where `—··` lemmatizes every token with `aaa` (S9) and `a·`-normalizes.
  2. W = `Split(s, " ")` (raw).
  3. For g < a: if L(g) = L(a) → W(a) = "".
  4. Join W, `a·`.
- Examples: `диван диваны диванов` → `диван`; `купить диван купила` → `купить диван`.
- Quirks: L comes from normalized text, W from raw text: double spaces shift the indexes and the wrong words are blanked. The first wordform stays.
- ADR 0005 deviation that applies: lemmas lower case; ё = е; split on any whitespace (fixes the index drift).

<a id="r3"></a>
## R3. Remove › Phrases and markers (УДАЛИТЬ > Фразы)

### УДАЛИТЬ > Фразы > Свой список фраз
- Handler: `aok–` (RibbonCallbacks.vba line 2733); helpers: `DeletePhrases` (lines 3452–3470)
- Input / output: InputBox «Выберите список фраз» (Type 8). Selection column 1 (≥ 2 cells). Overwrites the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. Remove list phrases, see S10 `remove_phrases`.
- Examples: list [купить, в москве]: `Купить диван в Москве` → `диван`; list [москве]: `Диван Москва` → `диван москва`.
- Quirks: The output is lower-cased. Same handler as «Фразы > Свой список фраз». A one-cell selection makes `Selection.value2` a scalar → error, swallowed: nothing happens.
- ADR 0005 deviation that applies: keep original case (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Все > С предлогами
- Handler: `a·—a` (RibbonCallbacks.vba line 2967); helpers: `udalit_toponimy_s_pryedlogami` (lines 1194–1197), `chk` (line 2511), `a—k` (line 2175), `a·` (line 1855)
- Input / output: No prompt. List `GEO_Toponyms` (ggg!R, `spiski/geo.xlsx`); prepositions ru `В ВО НА ПО ИЗ ДО Г И` (the en list `IN AT BY TO` is never used from the ribbon). Selection column 1; single cell does nothing. Writes the result.
- Algorithm:
  1. See S10 `remove_toponyms_with_prepositions`.
- Examples: `купить диван в москве недорого` → `купить диван недорого`; `диван москва` → `диван москва`; `отели в хересе де ла фронтере` → `отели де ла фронтере` (bug).
- Quirks: Only toponyms preceded by a preposition are removed; a toponym without one stays. When the first word of a toponym has ONE list entry, only "prep + first word" is removed even if the entry is multi-word. `Replace` removes every occurrence of the found pair in the cell.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; no double spaces; remove the full multi-word entry (fix).

### УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Все > Без предлогов
- Handler: `a·–a` (RibbonCallbacks.vba line 2204); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `GEO_Toponyms` (sheet `ggg` column R, `spiski/geo.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "GEO_Toponyms"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Метро МСК
- Handler: `a·a6` (RibbonCallbacks.vba line 2030); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyeryMosmetro` (sheet `ggg` column H, `spiski/mosmetro.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Районы МСК
- Handler: `a·a7` (RibbonCallbacks.vba line 2031); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyeryMSKDistricts` (sheet `ggg` column I, `spiski/districts.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Пункты МО
- Handler: `a·a8` (RibbonCallbacks.vba line 2032); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyeryMO` (sheet `ggg` column J, `spiski/MO.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Топонимы > Населённые пункты РФ
- Handler: `a·a9` (RibbonCallbacks.vba line 2033); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `citiesRu` (sheet `ggg` column L, `spiski/citiesRu.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Минус-слова > Игры и развлечения
- Handler: `a·a3` (RibbonCallbacks.vba line 2027); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyeryFun` (sheet `ggg` column A, `spiski/fun.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Минус-слова > DIY (самодеятельность)
- Handler: `a·a4` (RibbonCallbacks.vba line 2028); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyeryDIY` (sheet `ggg` column B, `spiski/DIY.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Минус-слова > Образование
- Handler: `a·a01` (RibbonCallbacks.vba line 2035); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `edu` (sheet `ggg` column N, `spiski/edu.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Минус-слова > Названия игр
- Handler: `a·a02` (RibbonCallbacks.vba line 2036); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `game` (sheet `ggg` column O, `spiski/game.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > E-com > Продажи
- Handler: `a·al` (RibbonCallbacks.vba line 2025); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyerypokupki` (sheet `ggg` column E, `spiski/sale.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > E-com > Аренда
- Handler: `a·a·` (RibbonCallbacks.vba line 2024); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyeryRent` (sheet `ggg` column F, `spiski/rent.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > E-com > Отзывы
- Handler: `a·a2` (RibbonCallbacks.vba line 2026); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyeryReviews` (sheet `ggg` column G, `spiski/reviews.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Характеристики > Цвет
- Handler: `a·a0` (RibbonCallbacks.vba line 2034); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `color` (sheet `ggg` column M, `spiski/color.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Характеристики > Материал
- Handler: `a·a03` (RibbonCallbacks.vba line 2037); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `material` (sheet `ggg` column P, `spiski/material.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Характеристики > Происхождение (страна)
- Handler: `a·a04` (RibbonCallbacks.vba line 2038); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `origin` (sheet `ggg` column Q, `spiski/origin.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Тематические > Марки и модели авто
- Handler: `a·a5` (RibbonCallbacks.vba line 2029); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `markyeryCars` (sheet `ggg` column C, `spiski/cars.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Тематические > Имена
- Handler: `a·a05` (RibbonCallbacks.vba line 2039); helpers: `chk` (line 2511), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. List: `names` (sheet `ggg` column K, `spiski/names.xlsx`). Selection column 1 (needs ≥ 2 cells). Writes the cleaned text over the selection (ignores «Выводить результат справа»).
- Algorithm:
  1. `chk "edu"`, then remove the list phrases, see S10 `remove_phrases`.
- Quirks: The whole result is LOWER-CASED, also cells where nothing was removed. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: keep the original case of the remaining words (fix); ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Удаление нескольких списков фраз
- Handler: `RbnDelete` (RibbonCallbacks.vba line 3173); helpers: `ShowCombo` (line 3178), `RunCombo` (lines 3175–3177), `ListCatalog` (line 3179), `DeletePhrases` (lines 3452–3470)
- Input / output: Form `frmCombo` (frmCombo.frm): an action combo preset to «delete» and one checkbox per list of `ListCatalog` (18 lists, S10 table). Selection must be one column. INSERTS A ROW above the selection for headers and inserts new columns to the right.
- Algorithm:
  1. `ShowCombo`: refuse if the selection is not one column; show the form; OK calls `RunCombo(action, chosen names)` in catalog order.
  2. `RunCombo` inserts a header row above the selection (the data shift down one row).
  3. delete: insert one column right of the data, copy the data there, run `DeletePhrases` (S10) on it once per chosen list, in catalog order; header «Очищено: name1, name2».
  4. find / extract: for list i insert a column at data column + 1 + i and write `–la` (TRUE/FALSE) or `la—` (markers joined by "\") for that list; header = the range name (e.g. `markyeryMosmetro`).
- Quirks: The form also runs `chk "edu"` only. Headers are the internal range names, not the Russian captions. Delete chains the lists, so a later list sees text already cleaned (and lower-cased) by the earlier ones.
- ADR 0005 deviation that applies: keep original case; ё = е; split on any whitespace; no double spaces.

### УДАЛИТЬ > Фразы > Удалить маркеры... > Обновить все списки
- Handler: `––kak` (RibbonCallbacks.vba line 2003); helpers: `upd` (lines 2001–2002), `Redefine` (line 1987)
- Input / output: No prompt. Downloads 18 lists from `https://semtools.guru/dl/spiski/<name>.xlsx` into sheet `ggg` columns A–R, re-creates the named ranges (`def_*`), saves the add-in.
- Algorithm:
  1. Not a matcher. semkit freezes the lists (plan §1.2: «Update lists» — out).
- Quirks: Network; overwrites sheet `ggg`.
- ADR 0005 deviation that applies: n/a (out of scope).

<a id="r4"></a>
## R4. Remove › Cells (УДАЛИТЬ > Ячейки)

### УДАЛИТЬ > Ячейки > По содержимому > Пустые ячейки > Со смещением вверх
- Handler: `remBlankCellsUp` (RibbonCallbacks.vba line 178); helpers: none
- Input / output: Selection. Deletes the blank cells with Excel `SpecialCells(xlCellTypeBlanks).Delete Shift:=xlUp`.
- Algorithm:
  1. Port: drop empty cells from the column (values below move up).
- Quirks: No blank cells → `SpecialCells` raises a run-time error. Formulas returning "" are not blank for Excel.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Ячейки > По содержимому > Пустые ячейки > Со смещением влево
- Handler: `remBlankCellsLeft` (RibbonCallbacks.vba line 179); helpers: none
- Input / output: Selection. `SpecialCells(xlCellTypeBlanks).Delete Shift:=xlToLeft`.
- Algorithm:
  1. Port: within each row, drop empty cells (values to the right move left).
- Quirks: Same as «Со смещением вверх».
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Ячейки > По содержимому > Содержащие любое из списка > Где угодно
- Handler: `akok` (RibbonCallbacks.vba line 1868); helpers: `ko–·` (line 2462), `–k—` (line 2774), `—––` (line 1831)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes "" or the cell.
- Algorithm:
  1. `ko–·` = `–k—("—––", cell, list)`: the cell becomes "" when the WHOLE cell contains any list item as a substring (`ao—`), case-insensitive; else unchanged.
- Examples: `диванчик` with list [диван] → "".
- Quirks: A blank list cell clears every cell.
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### УДАЛИТЬ > Ячейки > По содержимому > Содержащие любое из списка > В начале ячейки
- Handler: `ak–a` (RibbonCallbacks.vba line 2613); helpers: `ko—a` (line 2934), `–k—` (line 2774), `–ok` (line 2474)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes "" or the cell.
- Algorithm:
  1. `ko—a` = `–k—("–ok", cell, list)`: the cell becomes "" when the WHOLE cell starts with any list item (`—·–`), case-insensitive; else unchanged.
- Examples: `купить диван` with list [куп] → "".
- Quirks: A blank list cell clears every cell.
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### УДАЛИТЬ > Ячейки > По содержимому > Содержащие любое из списка > В конце ячейки
- Handler: `ak–k` (RibbonCallbacks.vba line 2248); helpers: `ko—–` (line 1870), `–k—` (line 2774), `kaa` (line 2855)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes "" or the cell.
- Algorithm:
  1. `ko—–` = `–k—("kaa", cell, list)`: the cell becomes "" when the WHOLE cell ends with any list item (`kok`), case-insensitive; else unchanged.
- Examples: `диван москва` with list [москва] → "".
- Quirks: A blank list cell clears every cell.
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### УДАЛИТЬ > Ячейки > По содержимому > Содержащие слова > 1 слово
- Handler: `akoo` (RibbonCallbacks.vba line 2943); helpers: `ko—k` (line 2274), `o–—` (line 2271), `·a–` (line 2573), `ao—` (line 2443)
- Input / output: InputBox «Удалить содержимое ячеек, если содержит слово:» (Type 2). Selection, every cell. Writes "" or the cell.
- Algorithm:
  1. `ko—k` = `o–—("·a–", cell, w)`: clear the cell when `·a–(cell, w)` (whole word on space boundaries, case-insensitive).
- Examples: w `диван`: `купить диван` → ""; `диваны` → unchanged.
- Quirks: No ignore-punctuation variant: «диван,» does not count.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Ячейки > По содержимому > Содержащие слова > Любое из списка
- Handler: `ako–` (RibbonCallbacks.vba lines 1682–1683); helpers: `a–a` (line 1686), `ko—o` (line 2312), `–k—` (line 2774), `–ao` (line 2726), `a–o` (line 2628), `—a—` (line 2675), `a–k` (line 2244)
- Input / output: InputBox for a range (Type 8): word list. The list is copied to `abc!K` (S7 BSR). Selection, all cells of all areas. Writes "" or the cell.
- Algorithm:
  1. Build BSR: column 1 of the list, `UCase`, text, sorted ascending, named `BSR`.
  2. `ko—o` = `–k—("–ao", cell, BSR)`: `–ao` = `a–o("—a—", cell, BSR)`: tokens = `Split(cell & " ")`; a token hits when `VLOOKUP(UCase(token), BSR, 1, TRUE) = UCase(token)` (exact, via binary search).
  3. Clear the cell when any token hits. Finally clear `abc!K`.
- Examples: list [Купить]: `купить диван` → ""; `покупка дивана` → unchanged.
- Quirks: Exact word match, case-insensitive; punctuation stays in the token.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Ячейки > По содержимому > По REGEX-паттерну
- Handler: `akk·` (RibbonCallbacks.vba line 2969); helpers: `ko——` (line 1712), `o–—` (line 2271), `RegExMatch` (line 1646)
- Input / output: InputBox «Очистить содержимое ячеек, если удовлетворяют паттерну» (Type 2). Selection, every cell. Writes "" or the cell.
- Algorithm:
  1. Clear the cell when `RegExMatch(cell, p)` (search, case-sensitive).
- Examples: p `\d`: `диван 2` → "".
- Quirks: none found.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Ячейки > По встречаемости > Не повторяющиеся
- Handler: `ao—–` (RibbonCallbacks.vba line 2074); helpers: `o——` (lines 381–434)
- Input / output: No prompt. Selection column 1. Writes "" or the cell.
- Algorithm:
  1. Counts of `UCase(cell)` over column 1 (S12).
  2. unique = True, mode "del": a value that occurs ONCE is cleared; repeated values stay (all occurrences).
- Examples: [Диван, диван, кресло] → [Диван, диван, ""].
- Quirks: One empty cell counts as unique (stays empty anyway).
- ADR 0005 deviation that applies: empty cells are never duplicates; ё = е.

### УДАЛИТЬ > Ячейки > По встречаемости > Повторяющиеся
- Handler: `ak·a` (RibbonCallbacks.vba line 2358); helpers: `o——` (lines 381–434)
- Input / output: No prompt. Selection column 1. Writes "" or the cell.
- Algorithm:
  1. unique = False, mode "del": every occurrence (first included) of a value that occurs 2+ times is cleared.
- Examples: [Диван, диван, кресло] → ["", "", кресло].
- Quirks: none found.
- ADR 0005 deviation that applies: empty cells are never duplicates; ё = е.

<a id="r5"></a>
## R5. Remove › Rows by the selected column (УДАЛИТЬ > Диапазоны)

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Ничего
- Handler: `aooo` (RibbonCallbacks.vba line 2478); helpers: `l—1` (line 2875)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when the cell is empty (`Len = 0`).
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Букв или цифр
- Handler: `ao–·` (RibbonCallbacks.vba line 2192); helpers: `о·oa` (line 2486)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when the cell is non-empty and has no cased letter and no ASCII digit (`cell <> "" And Not l–1(cell)`).
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Латиницы
- Handler: `ao—k` (RibbonCallbacks.vba line 2789); helpers: `о··–` (line 2695)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when the cell has no latin letter (`Not Like "*[A-Za-z]*"`; empty cells too).
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Цифр
- Handler: `ao—o` (RibbonCallbacks.vba line 2554); helpers: `о··—` (line 2377)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when the cell has no ASCII digit (empty cells too).
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Слов > Конкретного слова
- Handler: `aoo·` (RibbonCallbacks.vba line 1621); helpers: `–·1` (line 2587), `о···` (line 2956), `·a–` (line 2573), `okkk` (line 1698), `oka` (line 2460)
- Input / output: InputBox «Удалить строку, если ячейка не содержит слово:» (Type 2). Selection one column, > 1 row. Deletes rows.
- Algorithm:
  1. Plain (`–·1 "о···"`): delete the row when NOT `·a–(cell, w)` (whole word, space boundaries, case-insensitive).
  2. Ignore-punctuation: `okkk` = NOT `oka(cell, w)` (on `oko(cell)`).
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейки НЕ содержит... > Слов > Ни одного из списка
- Handler: `ao–k` (RibbonCallbacks.vba line 2679); helpers: `a–a` (line 1686), `ka·–` (line 1954), `a–o` (line 2628), `—a—` (line 2675), `a–k` (line 2244)
- Input / output: InputBox for a range (Type 8): word list → BSR (S7). Selection one column, > 1 row. Deletes rows.
- Algorithm:
  1. Delete the row when NO token of the cell is in the list: `ka·–` = `Not a–o("—a—", cell, BSR)`.
- Quirks: Empty cells have one empty token, not in the list → their rows are deleted.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Латиницу
- Handler: `aoo–` (RibbonCallbacks.vba line 2699); helpers: `a–—` (line 2153)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when the cell has a latin letter.
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Цифры
- Handler: `aoo—` (RibbonCallbacks.vba line 2889); helpers: `·kk` (line 1619)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when the cell has an ASCII digit.
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Слова > Одно слово
- Handler: `ao––` (RibbonCallbacks.vba line 1752); helpers: `–·1` (line 2587), `·a–` (line 2573), `oka` (line 2460)
- Input / output: InputBox «Удалить строку, если содержит конкретное слово:» (Type 2). Selection one column, > 1 row. Deletes rows.
- Algorithm:
  1. Plain (`–·1 "·a–"`): delete the row when `·a–(cell, w)`.
  2. Ignore-punctuation: `oka(cell, w)`.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Слова > Любое из списка
- Handler: `aooa` (RibbonCallbacks.vba line 1640); helpers: `a–a` (line 1686), `–ao` (line 2726), `a–o` (line 2628), `—a—` (line 2675), `a–k` (line 2244)
- Input / output: InputBox for a range (Type 8): word list → BSR. Selection one column, > 1 row. Deletes rows.
- Algorithm:
  1. Delete the row when any token of the cell is in the list (exact, case-insensitive): `–ao(cell, BSR)`.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если ячейка содержит... > Слова > Слова из цифр
- Handler: `ao–o` (RibbonCallbacks.vba line 2296); helpers: `a—l` (line 2946)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when any token is `IsNumeric` (`aoo("··—", cell)`).
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: split on any whitespace.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если длина содержимого... > Меньше
- Handler: `ao–a` (RibbonCallbacks.vba line 1838); helpers: `о·–k` (line 1705)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when `Len(cell) < N` (InputBox «…короче:», Type 1).
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: none.

### УДАЛИТЬ > Диапазоны > Строки на листе по выд. столбцу > Если длина содержимого... > Больше
- Handler: `ao–—` (RibbonCallbacks.vba line 1840); helpers: `о·o–` (line 1692)
- Input / output: Selection must be ONE column and more than one row (else MsgBox). Deletes whole sheet rows.
- Algorithm:
  1. Walk the selected rows bottom-up; delete the sheet row when `Len(cell) > N` (InputBox «…длиннее:», Type 1).
  2. Port: filter the table, keep rows where the condition is false.
- Quirks: Deletes entire rows (other columns go too). No undo of deleted rows.
- ADR 0005 deviation that applies: none.

<a id="x1"></a>
## X1. Extract › Chars (ИЗВЛЕЧЬ > Символы)

### ИЗВЛЕЧЬ > Символы > По порядку > Первые N
- Handler: `–—·–` (RibbonCallbacks.vba line 2369); helpers: `k–a–` (line 2888)
- Input / output: InputBox «количество символов» (Type 1). Selection, every cell. Writes the result.
- Algorithm:
  1. `Left(s, N)`.
- Examples: N=5: `диван-кровать` → `диван`.
- Quirks: N < 0 → run-time error.
- ADR 0005 deviation that applies: none

### ИЗВЛЕЧЬ > Символы > По порядку > Последние N
- Handler: `–ak·` (RibbonCallbacks.vba line 1687); helpers: `k—k–` (line 2615)
- Input / output: InputBox «количество символов» (Type 1). Selection, every cell. Writes the result.
- Algorithm:
  1. `Right(s, N)`.
- Examples: N=6: `диван-кровать` → `ровать`.
- Quirks: none found.
- ADR 0005 deviation that applies: none

### ИЗВЛЕЧЬ > Символы > По типу > Английский (Латиницу)
- Handler: `–ako` (RibbonCallbacks.vba line 2441); helpers: `k—k—` (line 2599), `RegExExtract` (line 2970), `a·` (line 1855)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. Concatenate all matches of `[a-zA-Z\s]` (keeps latin letters and whitespace), then `a·`.
- Examples: `Диван IKEA Ektorp 3-местный` → `IKEA Ektorp`.
- Quirks: `\s` in VBScript = [ \f\n\r\t\v]; tabs/newlines survive `a·` (it collapses only spaces).
- ADR 0005 deviation that applies: split on any whitespace (collapse all whitespace).

### ИЗВЛЕЧЬ > Символы > По типу > Русский (Кириллицу)
- Handler: `–—–a` (RibbonCallbacks.vba line 2350); helpers: `k–ak` (line 2844), `RegExExtract` (line 2970), `a·` (line 1855)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. Concatenate all matches of `[\u0410-\u04FF\u0401\u0451\s]`, then `a·`.
- Examples: `Диван IKEA 3-местный` → `Диван местный`.
- Quirks: Uppercase Є І Ї are dropped.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Символы > По типу > Любые буквы
- Handler: `–·o–` (RibbonCallbacks.vba line 1696); helpers: `·–a` (line 1331), `a·` (line 1855)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. Keep a character if it is a space or a cased letter (`UCase(c) <> LCase(c)`), else write a space; then `a·`.
- Examples: `Диван-кровать 2х IKEA` → `Диван кровать х IKEA`.
- Quirks: Digits are replaced by spaces.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Символы > По типу > Цифры
- Handler: `–·ko` (RibbonCallbacks.vba line 2594); helpers: `a—1` (line 2397), `RegExExtract` (line 2970), `a·` (line 1855)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. Concatenate all matches of `[0-9\s]`, then `a·`.
- Examples: `тел 8 (999) 123-45` → `8 999 12345`; `120x200` → `120200`.
- Quirks: Numbers that were apart stay apart, numbers glued by letters merge: «120x200» → «120200».
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Символы > По типу > Любые буквы и цифры
- Handler: `aok—` (RibbonCallbacks.vba line 2404); helpers: `oko` (line 1332)
- Input / output: No prompt. Selection, every cell (must be a Range). Writes the cleaned text.
- Algorithm:
  1. For each character c: keep it if `InStr(" 1234567890", c) > 0` (space or ASCII digit) or `UCase(c) <> LCase(c)` (a cased letter); otherwise write a space.
  2. Then `a·` (S3): trim spaces, collapse runs of spaces to one.
- Examples: `Диван-кровать, 2 шт.!` → `Диван кровать 2 шт`; `«ИКЕА»` → `ИКЕА`.
- Quirks: «Punctuation» = everything that is not a space, ASCII digit or cased letter: hyphens, quotes, symbols, tabs, line breaks, nbsp, and also uncased letters (CJK, Arabic). «из-за» → «из за». Same handler as ИЗВЛЕЧЬ > Символы > Любые буквы и цифры.
- ADR 0005 deviation that applies: no double spaces (already); split on any whitespace (tabs/nbsp become spaces anyway).

### ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Ввести свой, 1 совпадение
- Handler: `–a—–` (RibbonCallbacks.vba line 2712); helpers: `–—o` (line 2517), `RegExExtract` (line 2970)
- Input / output: InputBox (Type 2) regex p. Selection, every cell. Writes the first match or "".
- Algorithm:
  1. `RegExExtract(s, p, Global=False)`: the first match (VBScript RegExp, IgnoreCase False — the code reads an undeclared `IgnoreCase` variable, which is Empty = False).
- Examples: p `\d+`: `диван 120x200` → `120`.
- Quirks: none found.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Ввести свой, все совпадения
- Handler: `–a——` (RibbonCallbacks.vba lines 2877–2878); helpers: `a1a` (line 1690), `RegExExtract` (line 2970)
- Input / output: InputBox 1: regex p (Type 2). InputBox 2: separator (Type 2; Cancel is not checked → separator "False"). Selection, all cells of all areas. Writes the joined matches.
- Algorithm:
  1. All matches (Global True), each followed by the separator; the trailing separator is cut.
- Examples: p `\d+`, sep `;`: `диван 120x200` → `120;200`.
- Quirks: Cancelling the separator prompt joins the matches with the text «False».
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > Домены (с субдоменами)
- Handler: `a·k–` (RibbonCallbacks.vba line 2863); helpers: `a1a` (line 1690), `RegExExtract` (line 2970)
- Input / output: No prompt. Selection, all cells of all areas. Writes the domains joined by " ".
- Algorithm:
  1. All matches of `(?!\-)(?:(?:[a-zA-Z\d][a-zA-Z\d\-]{0,61})?[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z\d]{1,63}` joined by " ".
- Examples: `сайт www.example.com и mail.ru` → `www.example.com mail.ru`.
- Quirks: ASCII only: кириллические домены (.рф) are not found. Plan: ready patterns — v2.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > Даты > в формате DDMMYYYY
- Handler: `–a—a` (RibbonCallbacks.vba line 2960); helpers: `–—o` (line 2517), `RegExExtract` (line 2970)
- Input / output: No prompt. Selection, every cell. Writes the first date or "".
- Algorithm:
  1. First match of `([0-3][0-9]-[0-1][0-9]-[12]\d{3}|[0-3][0-9]\.[0-1][0-9]\.[12]\d{3}|[0-3][0-9]/[0-1][0-9]/[12]\d{3})`.
- Examples: `заказ от 05.11.2023` → `05.11.2023`.
- Quirks: No validation (39.19.2999 passes). Plan: v2.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > Даты > в формате YYYYMMDD
- Handler: `–aa–` (RibbonCallbacks.vba line 1765); helpers: `–—o` (line 2517), `RegExExtract` (line 2970)
- Input / output: No prompt. Selection, every cell. Writes the first date or "".
- Algorithm:
  1. First match of `([12]\d{3}-[0-1][0-9]-[0-3][0-9]|[12]\d{3}\.[0-1][0-9]\.[0-3][0-9]|[12]\d{3}/[0-1][0-9]/[0-3][0-9])`.
- Examples: `2023-11-05 заказ` → `2023-11-05`.
- Quirks: Plan: v2.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > e-mail-ы
- Handler: `–a—·` (RibbonCallbacks.vba line 2845); helpers: `–—o` (line 2517), `RegExExtract` (line 2970)
- Input / output: No prompt. Selection, every cell. Writes the first e-mail or "".
- Algorithm:
  1. First match of `[A-z0-9._%+-]+@[A-z0-9.-]+\.[A-z]{2,4}`.
- Examples: `пишите: info@site.ru` → `info@site.ru`.
- Quirks: `[A-z]` also admits the characters [ \ ] ^ _ and the backtick; TLDs longer than 4 letters are cut («.travel» → «.trav»). Plan: v2.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Символы > По REGEX-паттерну > Готовые паттерны: > Номера телефона (RU)
- Handler: `–aak` (RibbonCallbacks.vba line 2714); helpers: `l–a` (line 1330), `a1a` (line 1690), `RegExExtract` (line 2970)
- Input / output: No prompt. Selection, every cell. Writes "\" + phones joined by "|".
- Algorithm:
  1. m = all matches of `(\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}` joined by "|".
  2. The code computes m twice and keeps the longer (they are equal); result = "\" & m.
- Examples: `звоните 8 (999) 123-45-67` → `\8 (999) 123-45-67`; `нет телефона` → `\`.
- Quirks: Every result starts with a backslash, and a cell without a phone becomes "\". Plan: v2.
- ADR 0005 deviation that applies: Fix: drop the leading "\"; join phones with ', '.

### ИЗВЛЕЧЬ > Символы > Часть до... > Первого вхождения, включая
- Handler: `–—–o` (RibbonCallbacks.vba line 2775); helpers: `a·l` (line 1346)
- Input / output: InputBox (prompt `pp`, Type 2) pattern p. Selection, every cell. Writes the result.
- Algorithm:
  1. If Len(p) > Len(s) → "".
  2. pos = `InStr(1, s, p)` (binary, case-sensitive). Not found → "".
  3. Else `Left(s, pos + Len(p) - 1)` (up to and including the first p).
- Examples: p `,`: `диван, кресло, стол` → `диван,`; p `;`: `диван` → "".
- Quirks: Not found gives "" (the Remove buttons keep the cell instead). Case-sensitive.
- ADR 0005 deviation that applies: ё = е.

### ИЗВЛЕЧЬ > Символы > Часть до... > Первого вхождения, не включая
- Handler: `–—––` (RibbonCallbacks.vba line 1794); helpers: `a·ok` (line 1345)
- Input / output: InputBox (prompt `pp`, Type 2) pattern p. Selection, every cell. Writes the result.
- Algorithm:
  1. Intended: `Left(s, InStr(1, s, p) - 1)` (before the first p).
  2. Actual: the whole search sits inside `Case Len(p) > Len(s)`; when p is shorter than s (the normal case) the function returns Empty. The result is always "".
- Examples: p `,`: `диван, кресло` → "" (VBA); intended `диван`.
- Quirks: BUG: always empties the cells.
- ADR 0005 deviation that applies: Fix: implement the intended algorithm (case-sensitive, not found → "").

### ИЗВЛЕЧЬ > Символы > Часть после... > Последнего вхождения, включая
- Handler: `–—o·` (RibbonCallbacks.vba line 2767); helpers: `aal` (line 1348)
- Input / output: InputBox (prompt `pp`, Type 2) pattern p. Selection, every cell. Writes the result.
- Algorithm:
  1. If Len(p) > Len(s) → "".
  2. pos = `InStrRev(s, p)` (binary). Not found → "".
  3. Else `Right(s, Len(s) - pos + 1)` (the last p and what follows).
- Examples: p `/`: `a/b/c` → `/c`.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е.

### ИЗВЛЕЧЬ > Символы > Часть после... > Последнего вхождения, не включая
- Handler: `–—–k` (RibbonCallbacks.vba line 1602); helpers: `a·1` (line 1349)
- Input / output: InputBox (prompt `pp`, Type 2) pattern p. Selection, every cell. Writes the result.
- Algorithm:
  1. Intended: `Right(s, Len(s) - InStrRev(s, p) - Len(p) + 1)` (after the last p).
  2. Actual: same structure bug as «Первого вхождения, не включая»: always "".
- Examples: p `/`: `a/b/c` → "" (VBA); intended `c`.
- Quirks: BUG: always empties the cells.
- ADR 0005 deviation that applies: Fix: implement the intended algorithm.

<a id="x2"></a>
## X2. Extract › Words (ИЗВЛЕЧЬ > Слова)

### ИЗВЛЕЧЬ > Слова > Целые слова > 1 слово
- Handler: `–·oo` (RibbonCallbacks.vba line 2567); helpers: `k—ak` (line 2138), `·ko` (line 2968), `–—a` (line 2318)
- Input / output: InputBox «Напишите извлекаемое слово (без пробелов)» (Type 2). Selection, every cell. Writes the result.
- Algorithm:
  1. `·ko("–—a", s, w)`: tokens = `Split(s & " ")`; keep tokens with `UCase(token) = UCase(w)`, blank the rest; join " "; `a·`.
- Examples: w `диван`: `Купить Диван и диван` → `Диван диван`; `диваны` → "".
- Quirks: Every occurrence is kept, in the cell spelling: «Диван диван» → «Диван диван». No ignore-punctuation variant.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Целые слова > Указать список
- Handler: `–a–a` (RibbonCallbacks.vba line 1736); helpers: `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: InputBox «Выберите список фраз» (Type 8). Selection column 1; single cell does nothing. Writes the found phrases joined by "\".
- Algorithm:
  1. Phrase-list extract, see S10 `extract_phrases`.
- Examples: list [Нижний Новгород, Москва]: `доставка нижний новгород москва` → `Нижний Новгород\Москва`.
- Quirks: Same handler as «Фразы > Свой список фраз». Output uses the list spelling.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Целые слова > Части речи... > Существительные
- Handler: `–ao·` (RibbonCallbacks.vba line 2891); helpers: `get_lemmdict` (line 2109), `k—ok` (line 2710), `—·o` (line 2964), `··–` (line 2207)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `k—ok` = `—·o("··–", s)`: tokens = `Split(s & " ")`; keep tokens that are nouns (S9), blank the rest; join; `a·`.
- Examples: `купить красный диван быстро` → noun `диван`; adjective `красный`; verb `купить`; adverb `быстро` (dictionary tags assumed).
- Quirks: No ignore-punctuation variant: «диван,» is looked up with the comma.
- ADR 0005 deviation that applies: split on any whitespace; ё = е in the lookup.

### ИЗВЛЕЧЬ > Слова > Целые слова > Части речи... > Прилагательные
- Handler: `–—o—` (RibbonCallbacks.vba line 1948); helpers: `get_lemmdict` (line 2109), `k–—a` (line 1866), `—·o` (line 2964), `··o` (line 1439)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `k–—a` = `—·o("··o", s)`: tokens = `Split(s & " ")`; keep tokens that are adjectives (S9), blank the rest; join; `a·`.
- Examples: `купить красный диван быстро` → noun `диван`; adjective `красный`; verb `купить`; adverb `быстро` (dictionary tags assumed).
- Quirks: No ignore-punctuation variant: «диван,» is looked up with the comma.
- ADR 0005 deviation that applies: split on any whitespace; ё = е in the lookup.

### ИЗВЛЕЧЬ > Слова > Целые слова > Части речи... > Глаголы
- Handler: `–·ka` (RibbonCallbacks.vba line 2246); helpers: `get_lemmdict` (line 2109), `k—–—` (line 2574), `—·o` (line 2964), `·ok` (line 1344)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `k—–—` = `—·o("·ok", s)`: tokens = `Split(s & " ")`; keep tokens that are verbs (S9), blank the rest; join; `a·`.
- Examples: `купить красный диван быстро` → noun `диван`; adjective `красный`; verb `купить`; adverb `быстро` (dictionary tags assumed).
- Quirks: No ignore-punctuation variant: «диван,» is looked up with the comma.
- ADR 0005 deviation that applies: split on any whitespace; ё = е in the lookup.

### ИЗВЛЕЧЬ > Слова > Целые слова > Части речи... > Наречия
- Handler: `–—oa` (RibbonCallbacks.vba line 2480); helpers: `get_lemmdict` (line 2109), `k–—·` (line 2627), `—·o` (line 2964), `oa–` (line 2154)
- Input / output: No prompt. Opens `lemms.xlsb`. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `k–—·` = `—·o("oa–", s)`: tokens = `Split(s & " ")`; keep tokens that are adverbs (S9), blank the rest; join; `a·`.
- Examples: `купить красный диван быстро` → noun `диван`; adjective `красный`; verb `купить`; adverb `быстро` (dictionary tags assumed).
- Quirks: No ignore-punctuation variant: «диван,» is looked up with the comma.
- ADR 0005 deviation that applies: split on any whitespace; ё = е in the lookup.

### ИЗВЛЕЧЬ > Слова > Паттерны из списка > Префиксы
- Handler: `–a—k` (RibbonCallbacks.vba lines 2724–2725); helpers: `k—o·` (line 1730), `k—oa` (line 1653), `·a·` (lines 1218–1301), `—·–` (line 1657)
- Input / output: InputBox for a range (Type 8): pattern list, column 1, all rows. MsgBox «Извлечь все из списка? (нет = только первый найденный в списке)». Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `·a·(s, list, "begin", all)`: tokens = `Split(s, " ")`.
  2. No («first»): for each token, scan the list top-down; the first item the token starts with (case-insensitive) REPLACES the token (list spelling); no item → "".
  3. Yes («all»): for each token append " " & item for every matching item, then cut the original token off the front → the items in LIST order.
  4. Join " ", `a·`.
- Examples: list [див, дива, крес], No: `диваны и кресла` → `див крес`; Yes: `див дива крес`.
- Quirks: Output is the PATTERN (list spelling), not the word. A blank list cell matches every token (in «first» mode a blank before the real items replaces the token by ""). A one-cell list → scalar → error swallowed, cells unchanged.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### ИЗВЛЕЧЬ > Слова > Паттерны из списка > Суффиксы
- Handler: `–aa·` (RibbonCallbacks.vba lines 2899–2900); helpers: `k—–o` (line 2348), `k—–k` (line 2331), `·a·` (lines 1218–1301), `kok` (line 2499)
- Input / output: InputBox for a range (Type 8): pattern list, column 1, all rows. MsgBox «Извлечь все из списка? (нет = только первый найденный в списке)». Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `·a·(s, list, "end", all)`: tokens = `Split(s, " ")`.
  2. No («first»): for each token, scan the list top-down; the first item the token ends with (case-insensitive) REPLACES the token (list spelling); no item → "".
  3. Yes («all»): for each token PREPEND item & " " for every matching item, then cut the original token off the end → the items in REVERSE list order.
  4. Join " ", `a·`.
- Examples: list [ый, ный], No: `красный диван` → `ый`; Yes: `ный ый`.
- Quirks: Output is the PATTERN (list spelling), not the word. «All» mode lists the items in reverse list order. A blank list cell matches every token (in «first» mode a blank before the real items replaces the token by ""). A one-cell list → scalar → error swallowed, cells unchanged.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### ИЗВЛЕЧЬ > Слова > Паттерны из списка > Любые вхождения
- Handler: `—·—k` (RibbonCallbacks.vba lines 2220–2221); helpers: `k—o—` (line 2195), `k—o–` (line 2004), `·a·` (lines 1218–1301), `ao—` (line 2443)
- Input / output: InputBox for a range (Type 8): pattern list, column 1, all rows. MsgBox «Извлечь все из списка? (нет = только первый найденный в списке)». Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `·a·(s, list, "contain", all)`: tokens = `Split(s, " ")`.
  2. No («first»): for each token, scan the list top-down; the first item the token contains (case-insensitive) REPLACES the token (list spelling); no item → "".
  3. Yes («all»): for each token PREPEND item & " " for every matching item, then cut the original token off the end → the items in REVERSE list order.
  4. Join " ", `a·`.
- Examples: list [ив, ван], No: `диван` → `ив`; Yes: `ван ив`.
- Quirks: Output is the PATTERN (list spelling), not the word. «All» mode lists the items in reverse list order. A blank list cell matches every token (in «first» mode a blank before the real items replaces the token by ""). A one-cell list → scalar → error swallowed, cells unchanged.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Список паттернов
- Handler: `–·k·` (RibbonCallbacks.vba line 2156); helpers: `o——–` (line 2918)
- Input / output: InputBox «Выделите список слов для поиска» (Type 8): list, column 1. Selection column 1. Writes the result.
- Algorithm:
  1. For each token of `Split(s & " ")`: scan the list; keep the token at the first item with `InStr(UCase(token), UCase(item)) > 0`; if the scan reaches the last row without a hit, blank it.
  2. Join " ", `a·`.
- Examples: list [див]: `купить диван и диванчик` → `диван диванчик`.
- Quirks: A blank list cell keeps every token.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Латиницу
- Handler: `–—k—` (RibbonCallbacks.vba line 2442); helpers: `k—–·` (line 1811), `—·o` (line 2964), `a–—` (line 2153)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k—–·` = `—·o("a–—", s)`: tokens = `Split(s & " ")`; keep tokens that contain latin; join; `a·`.
- Examples: `диван IKEA 3d` → `IKEA 3d`.
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Цифры
- Handler: `–—k–` (RibbonCallbacks.vba line 2416); helpers: `o—––` (line 2952), `—·o` (line 2964), `·kk` (line 1619)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `o—––` = `—·o("·kk", s)`: tokens = `Split(s & " ")`; keep tokens that contain an ASCII digit; join; `a·`.
- Examples: `диван 2 120x200` → `2 120x200`.
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Буквы и цифры
- Handler: `a·o–` (RibbonCallbacks.vba line 2916); helpers: `a·ll` (line 2974), `—·o` (line 2964), `a·l1` (line 2973)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `a·ll` = `—·o("a·l1", s)`: tokens = `Split(s & " ")`; keep tokens that contain a digit AND a cased letter; join; `a·`.
- Examples: `диван 2 120x200 3d` → `120x200 3d`.
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Только... > кириллицу
- Handler: `a·o—` (RibbonCallbacks.vba line 2672); helpers: `k——o` (line 1688), `—·o` (line 2964), `о·k·` (line 2654)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k——o` = `—·o("о·k·", s)`: tokens = `Split(s & " ")`; keep tokens that contain cyrillic and no `[0-9A-Za-z]`; join; `a·`.
- Examples: `диван-кровать IKEA 2х` → `диван-кровать`.
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Только... > цифры
- Handler: `——·—` (RibbonCallbacks.vba line 2127); helpers: `k—oo` (line 2324), `—·o` (line 2964), `··—` (line 2360)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k—oo` = `—·o("··—", s)`: tokens = `Split(s & " ")`; keep tokens that are `IsNumeric`; join; `a·`.
- Examples: `диван 2 1,5 120x200` → `2 1,5`.
- Quirks: IsNumeric is locale-aware.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > Только... > латиницу
- Handler: `——·–` (RibbonCallbacks.vba line 2107); helpers: `k——–` (line 2063), `—·o` (line 2964), `ala` (line 1770)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k——–` = `—·o("ala", s)`: tokens = `Split(s & " ")`; keep tokens that are only latin (latin, no digit, no `[А-Яа-я]`); join; `a·`.
- Examples: `диван IKEA 3d` → `IKEA`.
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > И... > Латиницу и кириллицу
- Handler: `–—ka` (RibbonCallbacks.vba line 2095); helpers: `k—ka` (line 1611), `al–` (line 2584)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `al–(s, "*[A-Za-z]*", "*[А-Яа-я]*")`: tokens = `Split(s, " ")`; keep tokens matching both `Like` masks; join; `a·`.
- Examples: `Wi-Fi-роутер TP-Link` → `Wi-Fi-роутер`.
- Quirks: `[А-Яа-я]` misses Ё/ё.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > И... > Латиницу и цифры
- Handler: `–—k·` (RibbonCallbacks.vba line 2394); helpers: `k—k·` (line 1650), `al–` (line 2584)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `al–(s, "*[A-Za-z]*", "*[0-9]*")`: tokens = `Split(s, " ")`; keep tokens matching both `Like` masks; join; `a·`.
- Examples: `диван 3d 120x200` → `3d 120x200`.
- Quirks: `[А-Яа-я]` misses Ё/ё.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > Где угодно... > И... > Кириллицу и цифры
- Handler: `–—ko` (RibbonCallbacks.vba line 2624); helpers: `k–ao` (line 2959), `al–` (line 2584)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `al–(s, "*[0-9]*", "*[А-Яа-я]*")`: tokens = `Split(s, " ")`; keep tokens matching both `Like` masks; join; `a·`.
- Examples: `2-местный диван` → `2-местный`.
- Quirks: `[А-Яа-я]` misses Ё/ё.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > В начале... > Паттерн
- Handler: `–·–a` (RibbonCallbacks.vba line 1903); helpers: `o———` (line 2352), `·ko` (line 2968), `—·–` (line 1657)
- Input / output: InputBox «Извлечь слова, начинающиеся с:» (Type 2). Selection, every cell. Writes the result.
- Algorithm:
  1. `·ko("—·–", s, p)`: keep tokens starting with p (case-insensitive); join; `a·`.
- Examples: p `див`: `купить диван и диванчик` → `диван диванчик`.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > В начале... > Список паттернов
- Handler: `–·–·` (RibbonCallbacks.vba line 2513); helpers: `k—ao` (line 2077), `–—–` (line 2719), `—·–` (line 1657)
- Input / output: InputBox for a range (Type 8): pattern list, column 1. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `–—–("—·–", s, list)`: keep tokens that start with any list item; join; `a·`.
- Examples: list [див, крес]: `диван и кресло` → `диван кресло`.
- Quirks: A blank list cell keeps every token.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### ИЗВЛЕЧЬ > Слова > Содержащие > В конце... > Паттерн
- Handler: `–·––` (RibbonCallbacks.vba line 1816); helpers: `k——a` (line 1715), `·ko` (line 2968), `kok` (line 2499)
- Input / output: InputBox «Извлечь слова, заканчивающиеся на:» (Type 2). Selection, every cell. Writes the result.
- Algorithm:
  1. `·ko("kok", s, p)`: keep tokens ending with p; join; `a·`.
- Examples: p `ый`: `красный большой диван` → `красный большой`.
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Содержащие > В конце... > Список паттернов
- Handler: `–·–—` (RibbonCallbacks.vba line 2330); helpers: `k——·` (line 2479), `–—–` (line 2719), `kok` (line 2499)
- Input / output: InputBox for a range (Type 8): pattern list, column 1. Selection, all cells of all areas. Writes the result.
- Algorithm:
  1. `–—–("kok", s, list)`: keep tokens that end with any list item; join; `a·`.
- Examples: list [ый, ая]: `красный диван белая кровать` → `красный белая`.
- Quirks: A blank list cell keeps every token.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; ignore blank list items.

### ИЗВЛЕЧЬ > Слова > По порядку... > Первые... > 1
- Handler: `–—a—` (RibbonCallbacks.vba line 1877); helpers: `tfw` (line 1829)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. Skip cells where `Trim(s) = ""`.
  2. p = `Split(s, " ")`.
  3. If the token count > 1: s = "'" & p(0) … p(1−1) joined by " ".
  4. Cells with ≤ 1 tokens are left as they are (no trim).
- Examples: `купить диван в москве` → `купить`; `диван` → `диван`.
- Quirks: Empty tokens from double or leading spaces count as words: ` диван кресло` first 1 → "". The ribbon wires «N-е слово > 1-е» to this same handler.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > Первые... > 2
- Handler: `–—aa` (RibbonCallbacks.vba line 1680); helpers: `tfw` (line 1829)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. Skip cells where `Trim(s) = ""`.
  2. p = `Split(s, " ")`.
  3. If the token count > 2: s = "'" & p(0) … p(2−1) joined by " ".
  4. Cells with ≤ 2 tokens are left as they are (no trim).
- Examples: `купить диван в москве` → `купить диван`; `диван` → `диван`.
- Quirks: Empty tokens from double or leading spaces count as words: ` диван кресло` first 1 → "".
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > Первые... > 3
- Handler: `–—a·` (RibbonCallbacks.vba line 1632); helpers: `tfw` (line 1829)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. Skip cells where `Trim(s) = ""`.
  2. p = `Split(s, " ")`.
  3. If the token count > 3: s = "'" & p(0) … p(3−1) joined by " ".
  4. Cells with ≤ 3 tokens are left as they are (no trim).
- Examples: `купить диван в москве` → `купить диван в`; `диван` → `диван`.
- Quirks: Empty tokens from double or leading spaces count as words: ` диван кресло` first 1 → "".
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > Первые... > N
- Handler: `–—·—` (RibbonCallbacks.vba line 1828); helpers: `tfw` (line 1829)
- Input / output: InputBox «Количество слов» (Type 1; Cancel or N < 1 exits). Selection, every cell. Writes the result.
- Algorithm:
  1. Skip cells where `Trim(s) = ""`.
  2. p = `Split(s, " ")`.
  3. If the token count > N: s = "'" & p(0) … p(N−1) joined by " ".
  4. Cells with ≤ N tokens are left as they are (no trim).
- Examples: `купить диван в москве` → `купить диван` (N=2); `диван` → `диван`.
- Quirks: Empty tokens from double or leading spaces count as words: ` диван кресло` first 1 → "".
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > Последние... > 1
- Handler: `–ak–` (RibbonCallbacks.vba line 1778); helpers: `·ka` (line 2431)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `·ka(s, 1)`: tokens = `Split(s)`; if 1 > token count → s unchanged; else the last 1 tokens joined by " ", `Trim`, "'"-prefixed.
- Examples: `купить диван в москве` → `москве`.
- Quirks: Empty tokens count (a trailing space makes the last word "").
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > Последние... > 2
- Handler: `–ak—` (RibbonCallbacks.vba line 1711); helpers: `·ka` (line 2431)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `·ka(s, 2)`: tokens = `Split(s)`; if 2 > token count → s unchanged; else the last 2 tokens joined by " ", `Trim`, "'"-prefixed.
- Examples: `купить диван в москве` → `в москве`.
- Quirks: Empty tokens count (a trailing space makes the last word "").
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > Последние... > 3
- Handler: `–aka` (RibbonCallbacks.vba line 1661); helpers: `·ka` (line 2431)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `·ka(s, 3)`: tokens = `Split(s)`; if 3 > token count → s unchanged; else the last 3 tokens joined by " ", `Trim`, "'"-prefixed.
- Examples: `купить диван в москве` → `диван в москве`.
- Quirks: Empty tokens count (a trailing space makes the last word "").
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > Последние... > N
- Handler: `–aok` (RibbonCallbacks.vba line 2137); helpers: `·ka` (line 2431)
- Input / output: InputBox «количество слов:» (Type 1). Selection, every cell. Writes the result.
- Algorithm:
  1. `·ka(s, N)`: tokens = `Split(s)`; if N > token count → s unchanged; else the last N tokens joined by " ", `Trim`, "'"-prefixed.
- Examples: `купить диван в москве` → `в москве` (N=2).
- Quirks: Empty tokens count (a trailing space makes the last word "").
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > N-е слово > 1-е
- Handler: `–—a—` (RibbonCallbacks.vba line 1877); helpers: `tfw` (line 1829)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. Skip cells where `Trim(s) = ""`.
  2. p = `Split(s, " ")`.
  3. If the token count > 1: s = "'" & p(0) … p(1−1) joined by " ".
  4. Cells with ≤ 1 tokens are left as they are (no trim).
- Examples: `купить диван в москве` → `купить`; `диван` → `диван`.
- Quirks: Empty tokens from double or leading spaces count as words: ` диван кресло` first 1 → "". The ribbon wires «N-е слово > 1-е» to this same handler.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > N-е слово > 2-е
- Handler: `–—oo` (RibbonCallbacks.vba line 2847); helpers: `k·k` (line 1851)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `k·k(s, 2)`: tokens = `Split(s & " ", " ")`; if 2 > UBound (i.e. fewer than 2 words) → ""; else token 2−1 (0-based).
- Examples: `купить диван в москве` → `диван`.
- Quirks: Empty tokens count: `купить  диван` 2nd word → "".
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > N-е слово > 3-е
- Handler: `–—o–` (RibbonCallbacks.vba line 2133); helpers: `k·k` (line 1851)
- Input / output: Selection, every cell. Writes the result.
- Algorithm:
  1. `k·k(s, 3)`: tokens = `Split(s & " ", " ")`; if 3 > UBound (i.e. fewer than 3 words) → ""; else token 3−1 (0-based).
- Examples: `купить диван в москве` → `в`.
- Quirks: Empty tokens count: `купить  диван` 2nd word → "".
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По порядку... > N-е слово > N-е
- Handler: `–a–k` (RibbonCallbacks.vba line 1850); helpers: `k·k` (line 1851)
- Input / output: InputBox «№ слова в строке:» (Type 1). Selection, every cell. Writes the result.
- Algorithm:
  1. `k·k(s, N)`: tokens = `Split(s & " ", " ")`; if N > UBound (i.e. fewer than N words) → ""; else token N−1 (0-based).
- Examples: `купить диван в москве` → `москве` (N=4).
- Quirks: Empty tokens count: `купить  диван` 2nd word → "". N ≤ 0 → index error (run-time error).
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > До позиции в строке... > До середины
- Handler: `–·—k` (RibbonCallbacks.vba line 1599); helpers: `k—a–` (line 2802), `o·—` (line 1403)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `o·—(s, RoundDown(Len(s) / 2))`.
  2. `o·—(s, k)`: tokens = `Split(s & " ", " ")`; result = token 0 (always, whatever its length); total = Len(token 0).
  3. For each next token: total += Len(token) + 1; if total > k stop; else append " " & token.
- Examples: `купить диван недорого москва` (28 chars, k = 14) → `купить диван`; `диван-кровать недорого` → `диван-кровать`.
- Quirks: The first word is always returned, even when it is longer than half the cell. No trim.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > До позиции в строке... > Не более чем...
- Handler: `–·—o` (RibbonCallbacks.vba line 1612); helpers: `o·—` (line 1403)
- Input / output: InputBox «Извлечь слова с начала ячейки, чтобы общая длина результата не превышала:» (Type 1). Selection, every cell. Writes the result.
- Algorithm:
  1. `o·—(s, N)` as in «До середины».
- Examples: N=12: `купить диван недорого` → `купить диван`; N=3: `купить диван` → `купить`.
- Quirks: The first word is returned even when longer than N.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > По REGEX-паттерну
- Handler: `–·–o` (RibbonCallbacks.vba line 2871); helpers: `k———` (line 2076), `·ko` (line 2968), `RegExMatch` (line 1646)
- Input / output: InputBox (prompt `pt`, Type 2) regex. Selection, every cell. Writes the result.
- Algorithm:
  1. `·ko("RegExMatch", s, p)`: keep tokens where the regex finds a match (case-sensitive search); join; `a·`.
- Examples: p `^\d+$`: `диван 2 места 2024` → `2 2024`.
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Слова > Слова с заглавными
- Handler: `–·ok` (RibbonCallbacks.vba line 2709); helpers: `k——k` (line 1815), `—·o` (line 2964), `ooa` (line 2655)
- Input / output: No prompt. Selection, every cell. Writes the result.
- Algorithm:
  1. `k——k` = `—·o("ooa", s)`: tokens = `Split(s & " ")`; keep tokens that contain an uppercase letter; join; `a·`.
- Examples: `купить Диван IKEA` → `Диван IKEA`.
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

<a id="x3"></a>
## X3. Extract › Phrases and markers (ИЗВЛЕЧЬ > Фразы)

### ИЗВЛЕЧЬ > Фразы > Свой список фраз
- Handler: `–a–a` (RibbonCallbacks.vba line 1736); helpers: `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: InputBox «Выберите список фраз» (Type 8). Selection column 1; single cell does nothing. Writes the found phrases joined by "\".
- Algorithm:
  1. Phrase-list extract, see S10 `extract_phrases`.
- Examples: list [Нижний Новгород, Москва]: `доставка нижний новгород москва` → `Нижний Новгород\Москва`.
- Quirks: Same handler as «Фразы > Свой список фраз». Output uses the list spelling.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Дополнения с предлогами
- Handler: `findCollocs` (RibbonCallbacks.vba line 448); helpers: `k–` (line 1937), `collocs` (line 1428), `k—·—` (line 2905), `aoo` (line 1772), `··–` (line 2207), `oko` (line 1332)
- Input / output: No prompt. `lemms.xlsb` must already be OPEN in Excel (else it offers to download and exits). Selection, all cells of all areas. Writes the complements joined by ", ".
- Algorithm:
  1. preps = « для с в из на к со о во у по под от после за над » (16, S11). words = `Split(s, " ")`.
  2. For each word i that is in preps (case-SENSITIVE `InStr(preps, " " & w & " ")`):
  3.   scan j = i+1 .. min(i+5, last): stop at the next preposition; remember v = the last j whose word is a noun (`k—·—` = `aoo("··–", word, True)`: the word after `oko`).
  4.   If a noun was found: add words i..v joined by " " to the result; continue after v.
  5. Join the found complements with ", ".
- Examples: `купить диван для дачи недорого` → `для дачи`; `диван в гостиную с ящиками` → `в гостиную, с ящиками` (dictionary tags assumed).
- Quirks: Case-sensitive prepositions: «В Москве» is skipped. The complement runs to the LAST noun in the window (up to 5 words, before the next preposition). Plan: v2.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; prepositions case-insensitive (fix, by analogy with stopwords).

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Все топонимы > С предлогами
- Handler: `–·kk` (RibbonCallbacks.vba line 2674); helpers: `k—––` (lines 1198–1199), `chk` (line 2511), `a—k` (line 2175), `a·` (line 1855)
- Input / output: No prompt. List `GEO_Toponyms`; prepositions ru `В ВО НА ПО ИЗ ДО Г И`. Selection column 1; single cell does nothing. Writes the result.
- Algorithm:
  1. See S10 `extract_toponyms_with_prepositions`.
- Examples: `купить диван в москве` → `\\в Москве\\` (4 backslashes: 5 slots); `диван москва` → `\\` (2 backslashes: 3 empty slots).
- Quirks: The output keeps one slot per token, joined by "\": «купить диван в москве» → «\\в Москве\\». Toponyms without a preposition are not extracted.
- ADR 0005 deviation that applies: markers joined by ', ' (no empty slots); ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Все топонимы > Без предлогов
- Handler: `–a·a` (RibbonCallbacks.vba line 2823); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `GEO_Toponyms` (sheet `ggg` column R, `spiski/geo.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "GEO_Toponyms"`, then phrase-list extract with list `GEO_Toponyms`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Метро МСК
- Handler: `——aa4` (RibbonCallbacks.vba line 2014); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyeryMosmetro` (sheet `ggg` column H, `spiski/mosmetro.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `markyeryMosmetro`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Районы МСК
- Handler: `——aa5` (RibbonCallbacks.vba line 2015); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyeryMSKDistricts` (sheet `ggg` column I, `spiski/districts.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `markyeryMSKDistricts`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Пункты МО
- Handler: `——aa6` (RibbonCallbacks.vba line 2016); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyeryMO` (sheet `ggg` column J, `spiski/MO.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `markyeryMO`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Топонимы > Населенные пункты РФ
- Handler: `——aa7` (RibbonCallbacks.vba line 2017); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `citiesRu` (sheet `ggg` column L, `spiski/citiesRu.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `citiesRu`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > Маркеры вопросов
- Handler: `–a—o` (RibbonCallbacks.vba line 2409); helpers: `chk` (line 2511), `la—` (lines 647–648), `ao–` (line 2650), `k–` (line 1937), `a·o` (line 1649), `DeletePhrases` (lines 3452–3470)
- Input / output: No prompt. Lists `questions` (ggg!D, `spiski/questions.xlsx`) and `markyerypokupki`. Selection column 1. Writes the result.
- Algorithm:
  1. `chk "questions"`.
  2. `la—(questions)`: extract question markers joined by "\" (S10).
  3. Then `ao– "ok—a", "a·o"` over the same selection: remove repeated words (as «Повторы слов > Все»; tokens are split on spaces, so "\"-joined markers are one token).
  4. Then `DeletePhrases(markyerypokupki)` over the same selection: remove sale markers and LOWER-CASE everything.
- Examples: `Где Купить диван как сделать` → `где\как` (real lists: «как» is taken, not «как сделать», because «как» comes first in the list; no sale phrase left to delete; then lower case).
- Quirks: Unlike the other extract buttons, the result is lower-cased and sale words are cut out of it. With «Выводить результат справа» on, steps 3–4 run on the source column, not on the extracted one.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; keep case; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > Игры и развлечения
- Handler: `——aa1` (RibbonCallbacks.vba line 2011); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyeryFun` (sheet `ggg` column A, `spiski/fun.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `markyeryFun`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > DIY (самодеятельность)
- Handler: `——aa2` (RibbonCallbacks.vba line 2012); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyeryDIY` (sheet `ggg` column B, `spiski/DIY.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `markyeryDIY`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > Образование
- Handler: `——aa9` (RibbonCallbacks.vba line 2019); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `edu` (sheet `ggg` column N, `spiski/edu.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `edu`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Минус-слова (обычно нерелевантные) > Названия игр
- Handler: `——aa0` (RibbonCallbacks.vba line 2020); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `game` (sheet `ggg` column O, `spiski/game.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `game`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > E-com > Продажи
- Handler: `——·k` (RibbonCallbacks.vba line 2685); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyerypokupki` (sheet `ggg` column E, `spiski/sale.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "markyerypokupki"`, then phrase-list extract with list `markyerypokupki`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > E-com > Аренды
- Handler: `——aa` (RibbonCallbacks.vba line 2010); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyeryRent` (sheet `ggg` column F, `spiski/rent.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `markyeryRent`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > E-com > Отзывов
- Handler: `——a·` (RibbonCallbacks.vba line 2009); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyeryReviews` (sheet `ggg` column G, `spiski/reviews.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `markyeryReviews`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Характеристики > Цвет
- Handler: `——aa8` (RibbonCallbacks.vba line 2018); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `color` (sheet `ggg` column M, `spiski/color.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `color`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Характеристики > Материал
- Handler: `——aa01` (RibbonCallbacks.vba line 2021); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `material` (sheet `ggg` column P, `spiski/material.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `material`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Характеристики > Происхождение (страна)
- Handler: `——aa02` (RibbonCallbacks.vba line 2022); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `origin` (sheet `ggg` column Q, `spiski/origin.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `origin`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Тематические > Марки и модели авто
- Handler: `——aa3` (RibbonCallbacks.vba line 2013); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `markyeryCars` (sheet `ggg` column C, `spiski/cars.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `markyeryCars`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Тематические > Имена (Им.п)
- Handler: `ruNames` (RibbonCallbacks.vba line 2023); helpers: `chk` (line 2511), `la—` (lines 647–648), `a—k` (line 2175)
- Input / output: No prompt. List: `names` (sheet `ggg` column K, `spiski/names.xlsx`). Selection column 1; single cell does nothing. Writes the found markers joined by "\".
- Algorithm:
  1. `chk "edu"`, then phrase-list extract with list `names`, see S10 `extract_phrases`.
- Quirks: Markers are written in the list spelling, in token order, joined by a backslash; repeats are kept. Checks the range `edu`, not the list it uses.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Извлечение нескольких списков фраз
- Handler: `RbnExtract` (RibbonCallbacks.vba line 3174); helpers: `ShowCombo` (line 3178), `RunCombo` (lines 3175–3177), `ListCatalog` (line 3179), `la—` (lines 647–648)
- Input / output: Form `frmCombo` (frmCombo.frm): an action combo preset to «extract» and one checkbox per list of `ListCatalog` (18 lists, S10 table). Selection must be one column. INSERTS A ROW above the selection for headers and inserts new columns to the right.
- Algorithm:
  1. `ShowCombo`: refuse if the selection is not one column; show the form; OK calls `RunCombo(action, chosen names)` in catalog order.
  2. `RunCombo` inserts a header row above the selection (the data shift down one row).
  3. delete: insert one column right of the data, copy the data there, run `DeletePhrases` (S10) on it once per chosen list, in catalog order; header «Очищено: name1, name2».
  4. find / extract: for list i insert a column at data column + 1 + i and write `–la` (TRUE/FALSE) or `la—` (markers joined by "\") for that list; header = the range name (e.g. `markyeryMosmetro`).
- Quirks: The form also runs `chk "edu"` only. Headers are the internal range names, not the Russian captions. Delete chains the lists, so a later list sees text already cleaned (and lower-cased) by the earlier ones.
- ADR 0005 deviation that applies: markers as the list spelling joined by ', '; ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Фразы > Маркеры... > Обновить все списки
- Handler: `––kak` (RibbonCallbacks.vba line 2003); helpers: `upd` (lines 2001–2002), `Redefine` (line 1987)
- Input / output: No prompt. Downloads 18 lists from `https://semtools.guru/dl/spiski/<name>.xlsx` into sheet `ggg` columns A–R, re-creates the named ranges (`def_*`), saves the add-in.
- Algorithm:
  1. Not a matcher. semkit freezes the lists (plan §1.2: «Update lists» — out).
- Quirks: Network; overwrites sheet `ggg`.
- ADR 0005 deviation that applies: n/a (out of scope).

<a id="x4"></a>
## X4. Extract › Cells (ИЗВЛЕЧЬ > Ячейки)

### ИЗВЛЕЧЬ > Ячейки > Содержащие > Слова... > Указать слово
- Handler: `–——o` (RibbonCallbacks.vba line 1951); helpers: `k–a·` (line 1841), `a1l` (line 1939), `·a–` (line 2573)
- Input / output: InputBox «Оставить содержимое ячеек, если содержит слово:» (Type 2). Selection, every cell. Writes the cell or "".
- Algorithm:
  1. Keep the cell when `·a–(cell, w)` (whole word on spaces, case-insensitive), else "".
- Examples: w `диван`: `купить диван` → kept; `диваны` → "".
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Ячейки > Содержащие > Слова... > Указать список слов
- Handler: `–——–` (RibbonCallbacks.vba lines 2953–2954); helpers: `a–a` (line 1686), `k–·k` (line 2720), `o·–` (line 2765), `–ao` (line 2726), `a–o` (line 2628), `—a—` (line 2675), `a–k` (line 2244)
- Input / output: InputBox for a range (Type 8): word list → BSR (S7). Selection, all cells of all areas. Writes the cell or "".
- Algorithm:
  1. Keep the cell when any token is in the list (`–ao`, exact, case-insensitive), else "".
- Examples: list [диван]: `купить диван` → kept; `купить диваны` → "".
- Quirks: none found.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### ИЗВЛЕЧЬ > Ячейки > Содержащие > Слова... > Слова из латиницы
- Handler: `—·o—` (RibbonCallbacks.vba line 2603); helpers: `k–·–` (line 2120), `aa–` (line 2448), `l—·` (line 1943)
- Input / output: No prompt. Selection, every cell. Writes the cell or "".
- Algorithm:
  1. `k–·–` = `aa–("l—·", cell)`: keep the cell when any token is only latin (`aoo("ala", cell)`), else "".
- Examples: `диван IKEA` → kept; `диван 3d` → "".
- Quirks: none found.
- ADR 0005 deviation that applies: split on any whitespace.

### ИЗВЛЕЧЬ > Ячейки > Содержащие > Украинский
- Handler: `—·–o` (RibbonCallbacks.vba line 2407); helpers: `k—ko` (line 1888), `aa–` (line 2448), `fua` (line 1343)
- Input / output: No prompt. Selection, every cell. Writes the cell or "".
- Algorithm:
  1. `k—ko` = `aa–("fua", cell)`: keep the cell when the UA test is TRUE (see «UA символы/сочетания»), else "".
- Examples: `ціна` → kept.
- Quirks: none found.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Ячейки > Содержащие > Цифры
- Handler: `—·oa` (RibbonCallbacks.vba line 2467); helpers: `k–·—` (line 2351), `aa–` (line 2448), `··—` (line 2360)
- Input / output: No prompt. Selection, every cell. Writes the cell or "".
- Algorithm:
  1. `k–·—` = `aa–("··—", cell)`: keep the cell when the WHOLE cell is `IsNumeric`, else "".
- Examples: `120` → kept; `диван 2` → "".
- Quirks: Button says «Цифры», the code keeps only cells that are entirely a number (`IsNumeric`), not cells that contain a digit.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Ячейки > Содержащие > Латиницу
- Handler: `–aaa` (RibbonCallbacks.vba line 2914); helpers: `k–a—` (line 2656), `aa–` (line 2448), `a–—` (line 2153)
- Input / output: No prompt. Selection, every cell. Writes the cell or "".
- Algorithm:
  1. `k–a—` = `aa–("a–—", cell)`: keep the cell when the cell contains a latin letter, else "".
- Examples: `диван IKEA` → kept.
- Quirks: none found.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Ячейки > Содержащие > Заглавные буквы
- Handler: `—·–k` (RibbonCallbacks.vba line 2776); helpers: `k–aa` (line 2592), `aa–` (line 2448), `ooa` (line 2655)
- Input / output: No prompt. Selection, every cell. Writes the cell or "".
- Algorithm:
  1. `k–aa` = `aa–("ooa", cell)`: keep the cell when the cell contains an uppercase letter, else "".
- Examples: `купить Диван` → kept; `диван` → "".
- Quirks: none found.
- ADR 0005 deviation that applies: none.

### ИЗВЛЕЧЬ > Ячейки > По REGEX-паттерну
- Handler: `—·–a` (RibbonCallbacks.vba line 1847); helpers: `k–··` (line 2662), `aa–` (line 2448), `RegExMatch` (line 1646)
- Input / output: No prompt at all. Selection, every cell.
- Algorithm:
  1. `k–··` = `aa–("RegExMatch", cell)` calls `RegExMatch` with ONE argument; it needs two (text, pattern). `Application.Run` fails on the first cell with a run-time error.
  2. Intended (by analogy with «Удалить > Ячейки > По REGEX»): ask for a regex, keep the cell when it matches, else "".
- Quirks: BROKEN: no pattern prompt; the button stops with an error.
- ADR 0005 deviation that applies: n/a: derive from `akk·` (keep instead of clear).

### ИЗВЛЕЧЬ > Ячейки > По списку критериев > Содержащие
- Handler: `–——k` (RibbonCallbacks.vba line 2101); helpers: `——l` (line 2748), `o·–` (line 2765), `—––` (line 1831)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes the cell or "".
- Algorithm:
  1. Keep the cell when the WHOLE cell contains any list item (substring), case-insensitive; else "".
- Examples: list [диван]: `диванчик` → kept; `кресло` → "".
- Quirks: A blank list cell keeps every cell.
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### ИЗВЛЕЧЬ > Ячейки > По списку критериев > Начинающиеся с
- Handler: `—·–·` (RibbonCallbacks.vba line 2935); helpers: `k—kk` (line 2525), `o·–` (line 2765), `–ok` (line 2474)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes the cell or "".
- Algorithm:
  1. Keep the cell when the WHOLE cell starts with any list item, case-insensitive; else "".
- Examples: list [куп]: `купить диван` → kept.
- Quirks: A blank list cell keeps every cell.
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### ИЗВЛЕЧЬ > Ячейки > По списку критериев > Заканчивающиеся на
- Handler: `—·––` (RibbonCallbacks.vba line 2645); helpers: `k–·o` (line 2151), `o·–` (line 2765), `kaa` (line 2855)
- Input / output: InputBox for a range (Type 8): list, column 1, all rows. Selection, all cells of all areas. Writes the cell or "".
- Algorithm:
  1. Keep the cell when the WHOLE cell ends with any list item, case-insensitive; else "".
- Examples: list [москва]: `диван москва` → kept.
- Quirks: A blank list cell keeps every cell.
- ADR 0005 deviation that applies: ё = е; ignore blank list items.

### ИЗВЛЕЧЬ > Ячейки > По встречаемости > Не повторяющиеся
- Handler: `–·k—` (RibbonCallbacks.vba line 2942); helpers: `o——` (lines 381–434)
- Input / output: No prompt. Selection column 1. Writes the cell or "".
- Algorithm:
  1. Counts of `UCase(cell)` (S12). unique = True, mode "extr": keep values that occur once; clear values that occur 2+ times.
- Examples: [Диван, диван, кресло] → ["", "", кресло].
- Quirks: none found.
- ADR 0005 deviation that applies: empty cells are never duplicates; ё = е.

### ИЗВЛЕЧЬ > Ячейки > По встречаемости > Повторяющиеся
- Handler: `–aoa` (RibbonCallbacks.vba line 2911); helpers: `o——` (lines 381–434)
- Input / output: No prompt. Selection column 1. Writes the cell or "".
- Algorithm:
  1. unique = False, mode "extr": keep every occurrence of values that occur 2+ times; clear unique values.
- Examples: [Диван, диван, кресло] → [Диван, диван, ""].
- Quirks: none found.
- ADR 0005 deviation that applies: empty cells are never duplicates; ё = е.

### ИЗВЛЕЧЬ > Ячейки > Из другого диапазона
- Handler: `—·–—` (RibbonCallbacks.vba line 2524); helpers: none
- Input / output: InputBox «Выделите список ячеек» (Type 8): the other range, column 1. Selection column 1. Writes the cell or "".
- Algorithm:
  1. Dictionary of `UCase(value)` over the other range.
  2. Keep a selected cell when `UCase(cell)` is in it, else "".
- Examples: other [ДИВАН]: `диван` → kept; `диван ` → "".
- Quirks: Exact whole-cell match, case-insensitive, no trim.
- ADR 0005 deviation that applies: ё = е.

<a id="w1"></a>
## W1. Web › Remove from text (Web (Парсинг, SEO, PPC) > Удалить > Из текста)

### Web (Парсинг, SEO, PPC) > Удалить > Из текста > Стоп-слова
- Handler: `a·–·` (RibbonCallbacks.vba line 2285); helpers: `Del1DimArr` (line 2284), `stopwords` (lines 1374–1378)
- Input / output: No prompt. Built-in stopword list (S11). Selection column 1. Writes the result.
- Algorithm:
  1. Dictionary of the stopwords exactly as written (case-SENSITIVE keys).
  2. tokens = `Split(cell, " ")`; keep tokens that are not keys: rs = rs & token & " ".
  3. Result = `Trim(rs)`.
- Examples: `диван для дачи и сада` → `диван дачи сада`; `Диван В Москве` → `Диван В Москве`.
- Quirks: Case-sensitive: «В», «Для» are not removed. Empty tokens are kept, so double spaces survive inside the text. The list has 440 entries incl. the junk «g» and many English/archaic forms.
- ADR 0005 deviation that applies: stopwords case-insensitive; ё = е; split on any whitespace; no double spaces; drop «g» (plan D13: 439).

### Web (Парсинг, SEO, PPC) > Удалить > Из текста > Предлоги в конце фраз
- Handler: `remLWprps` (RibbonCallbacks.vba line 2306); helpers: `dLW` (line 2301), `stopwords` (lines 1374–1378), `prps` (line 1322), `eLW` (line 2432), `–·a` (line 2319)
- Input / output: No prompt. Selection column 1; single cell does nothing. Writes the result (4 times).
- Algorithm:
  1. Four passes: `dLW(stopwords)`, `dLW(prps)`, `dLW(stopwords)`, `dLW(prps)`.
  2. `dLW(list)`: keys = `UCase` of the list; if `UCase(eLW(cell, 1))` (last word) is a key, cell = `–·a(cell, 1)` (drop the last word).
  3. So up to four trailing stopwords/prepositions are dropped.
- Examples: `диван для` → `диван`; `диван для и` → `диван`; `диван с подъемным механизмом для` → `диван с подъемным механизмом`.
- Quirks: Case-insensitive here (unlike `a·–·`). Each pass writes the selection; with «Выводить результат справа» on, every pass inserts its own column and reads the unchanged source. «пo» (latin o) in prps.
- ADR 0005 deviation that applies: ё = е; split on any whitespace; fixed preposition list.

### Web (Парсинг, SEO, PPC) > Удалить > Из текста > Маркеры покупки в конце фраз
- Handler: `remLWsales` (RibbonCallbacks.vba line 2307); helpers: `chk` (line 2511), `dLWrng` (line 2302), `eLW` (line 2432), `–·a` (line 2319)
- Input / output: No prompt. List `markyerypokupki` (ggg!E, `spiski/sale.xlsx`). Selection column 1. Writes the result.
- Algorithm:
  1. One pass of `dLWrng(list)`: if `UCase(last word)` is a list item, drop the last word.
- Examples: `диван угловой купить` → `диван угловой` (if «купить» is in the list).
- Quirks: Only one-word list items can match (the test compares one word). Duplicates in the list → silent no-op (Dictionary.Add).
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### Web (Парсинг, SEO, PPC) > Удалить > Из текста > Повторы слов во всем столбце (разделитель пробел)
- Handler: `aoko` (RibbonCallbacks.vba line 2117); helpers: `a·` (line 1855)
- Input / output: No prompt. Selection column 1. Writes the result.
- Algorithm:
  1. One Dictionary for the whole column.
  2. For each cell top-down, for each token of `Split(cell & " ", " ")`: if `UCase(token)` is already in the Dictionary (from an earlier cell or earlier in this cell) blank it, else add it.
  3. Cell = `a·(Join(tokens, " "))`.
- Examples: [`купить диван`, `диван угловой`, `купить кресло`] → [`купить диван`, `угловой`, `кресло`].
- Quirks: A word survives only at its first occurrence in the whole column.
- ADR 0005 deviation that applies: ё = е; split on any whitespace.

### Web (Парсинг, SEO, PPC) > Удалить > Из текста > Повторы фраз во всем столбце (разделитель запятая с пробелом)
- Handler: `aoko2` (RibbonCallbacks.vba line 2118); helpers: none
- Input / output: No prompt. Selection column 1. Overwrites the selection directly.
- Algorithm:
  1. As «Повторы слов во всем столбце», but items are split on ", " and rejoined with ", " (blank items skipped).
- Examples: [`диван, кресло`, `кресло, стол`] → [`диван, кресло`, `стол`].
- Quirks: No trim of items: «диван » ≠ «диван».
- ADR 0005 deviation that applies: ё = е.


## Buttons that do not work as labelled

| Button | Handler | What happens |
|---|---|---|
| ОБНАРУЖИТЬ > Слова > Содержащие... > Где угодно > Паттерн | `SEM_findCellsContainingPattern` | The procedure does not exist in the VBA (nor in the p-code dump): «macro not found». |
| ИЗВЛЕЧЬ > Ячейки > По REGEX-паттерну | `—·–a` | No pattern prompt; `RegExMatch` is called with one argument → run-time error. |
| УДАЛИТЬ > Символы > по REGEX... > Все, НЕ попадающее под паттерн | `aok·` | Uses an undeclared variable as the pattern → "" → every cell becomes "". |
| ИЗВЛЕЧЬ > Символы > Часть до... > Первого вхождения, не включая | `–—––` | `a·ok` only works when the pattern is longer than the text → always "". |
| ИЗВЛЕЧЬ > Символы > Часть после... > Последнего вхождения, не включая | `–—–k` | `a·1`, same bug → always "". |
| ОБНАРУЖИТЬ > Ячейки > Начинающиеся на / Заканчивающиеся на > Указать список... (with «Игнорировать пунктуацию» on) | `—ko·`, `—koo` | Call the missing `startsWithAnyFromRngIgnorePunct` / `endsWithAnyFromRngIgnorePunct` → nothing is written. |
| Обновить все списки | `––kak` | Works, but downloads from the network; out of scope (lists are frozen). |

## Main quirks to keep in mind

1. Words are `Split(text, " ")`: double, leading and trailing spaces create empty tokens that count as words in
   positions, word counts and repeats (ADR: split on any whitespace).
2. `DeletePhrases` (remove phrase lists, remove markers, «Удалить все» from a word list) lower-cases the whole cell,
   even when nothing is removed.
3. `aaa` returns an unknown word unchanged; the `lemmSuf` suffix fallback runs only when the Excel lookup errors.
4. Marker extraction joins with "\" and takes the first item in LIST order, not the longest («как», not «как сделать»);
   «extract toponyms with prepositions» keeps one slot per token («\\в Москве\\\»).
5. «Remove toponyms with prepositions» removes only toponyms that follow a preposition, and for a first word with one
   multi-word entry removes only «preposition + first word».
6. A blank cell in a Type 8 list matches everything in the start/end/contains tests (and fails «all words»).
7. Stopwords are matched case-sensitively in «Стоп-слова», case-insensitively in «Предлоги в конце фраз»; `prps` has a
   latin «пo», so «по» is never a preposition.
8. «Around a pattern»: first-occurrence buttons are case-insensitive, last-occurrence buttons case-sensitive; Remove
   keeps a cell without the pattern, Extract empties it.
