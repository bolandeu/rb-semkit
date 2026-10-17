# Conformance of the declension area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/declension/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [decline](#decline) | 22 | 7 | 15 | 0 |
| [decline_adjective](#decline_adjective) | 20 | 8 | 12 | 0 |
| [decline_full_name](#decline_full_name) | 14 | 2 | 12 | 0 |
| [decline_noun](#decline_noun) | 16 | 5 | 11 | 0 |
| [irrelevant_words](#irrelevant_words) | 7 | 2 | 5 | 0 |
| **All** | **79** | **24** | **55** | **0** |

## decline

decline. VBA, RibbonCallbacks.vba: «Просклонять › Все что склоняется» —aa— (L1774, ko 2) … —aa· (L2673, ko 12), each k– with the wrapper aoa(cell, ko) (L1521–1581): W = Split(" " & cell & " "); per word, the first branch wins: dictRange is never Set, so the part-of-speech skip tests the word itself (only nonDecl works); a word in «ой» before a word that is not a lemma stays; from the 3rd word on, a word after arrPron stays; l­ <> word (not an abbreviation) → the adjective form; aaa (L1354) <> word → stays; else the noun form (ko 4/10 by the table; a consonant with an empty cell → the usual ending). Case restored by ·–— (L1350). Docs: docs/vba/analysis.md §3.0, §3 «Все что склоняется».

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `decline` | 22 | 7 | 15 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| decline-verb-stays | `"купить красный диван"` | `"купити красного дивана"` | `"купить красного дивана"` | «Все что склоняется» склоняет только существительные, прилагательные и местоимения по таблице прилагательных | dictRange is never Set, so aoa declines the verb as a noun: «купити» |
| decline-plural | `"купить красный диван"` | `"купитей красных диванов"` | `"купить красных диванов"` | «Все что склоняется» склоняет только существительные, прилагательные и местоимения по таблице прилагательных | dictRange is never Set, so aoa declines the verb as a noun: «купитей» |
| decline-noun-like-adjective | `"зной"` | `"зного"` | `"зноя"` | «Все что склоняется» склоняет только существительные, прилагательные и местоимения по таблице прилагательных | aoa tests the adjective ending first and the noun skip never works: «ной» gives «зного» |
| decline-inflected | `"диваны для дачи"` | `"диваны для дачи"` | `"диванов для дачи"` | Фраза во множественном числе склоняется во множественном числе | aoa leaves a word that is not its lemma: диваны |
| decline-accusative-inanimate | `"купить кожаный диван"` | `"купить кожаный дивана"` | `"купить кожаный диван"` | Винительный падеж неодушевлённого существительного — именительный | aoa takes the accusative from nounSuffixes, whose «ван» is animate («Иван») |
| decline-accusative-oj | `"угловой диван"` | `"углового дивана"` | `"угловой диван"` | Винительный падеж неодушевлённого существительного — именительный | aoa takes the accusative from nounSuffixes, whose «вой» and «ван» are animate |
| decline-accusative-adjective | `"красный диван"` | `"красный дивана"` | `"красный диван"` | Винительный падеж неодушевлённого существительного — именительный | aoa takes the accusative from nounSuffixes, whose «ван» is animate («Иван») |
| decline-plural-genitive | `"угловые диваны"` | `"угловые диваны"` | `"угловых диванов"` | Фраза во множественном числе склоняется во множественном числе | aoa leaves a word that is not its lemma, and «вые» is no ending of adjSuffixes |
| decline-plural-instrumental | `"угловые диваны"` | `"угловые диваны"` | `"угловыми диванами"` | Фраза во множественном числе склоняется во множественном числе | aoa leaves a word that is not its lemma, and «вые» is no ending of adjSuffixes |
| decline-plural-ie-genitive | `"дизайнерские диваны"` | `"дизайнерские диваны"` | `"дизайнерских диванов"` | Фраза во множественном числе склоняется во множественном числе | aoa leaves a word that is not its lemma, and «кие» is no ending of adjSuffixes |
| decline-plural-ie-instrumental | `"дизайнерские диваны"` | `"дизайнерские диваны"` | `"дизайнерскими диванами"` | Фраза во множественном числе склоняется во множественном числе | aoa leaves a word that is not its lemma, and «кие» is no ending of adjSuffixes |
| decline-compound-genitive | `"диван-кровать угловой"` | `"диван-кровати углового"` | `"дивана-кровати углового"` | Сложное существительное через дефис склоняется целиком | aoa changes the last three letters of the word only |
| decline-compound-prepositional | `"диван-кровать угловой"` | `"диван-кровати угловом"` | `"диване-кровати угловом"` | Сложное существительное через дефис склоняется целиком | aoa changes the last three letters of the word only |
| decline-feminine-genitive | `"большая скидка"` | `"большей скидки"` | `"большой скидки"` | Прилагательное женского рода, среднего рода и множественного числа склоняется от своей леммы | aoa declines «большая» by the ending «шая» of adjSuffixes, as «хорошая» |
| decline-feminine-prepositional | `"большая скидка"` | `"большей скидке"` | `"большой скидке"` | Прилагательное женского рода, среднего рода и множественного числа склоняется от своей леммы | aoa declines «большая» by the ending «шая» of adjSuffixes, as «хорошая» |

### xfail

None.

## decline_adjective

decline_adjective. VBA, RibbonCallbacks.vba: «Просклонять › Прилагательные», the wrapper ka("l­", cell, ko) (L2669) with l­ (L2470): adjExclusions2 for a word of adjExclusions (LCase), else root & oa(last3(LCase), adjSuffixes, ko). м. род Род a–k· (L1822, 2) … Предл —·—· (L2641, 6); мн. ч. Им —aak (L1671, 7) … Предл —·a– (L2160, 12); ж. род Им ———– (L2468, 13), Род/Дат/Твор/Предл —··– (L2311, 14), Вин a··· (L1744, 15); ср. род Им and Вин ———— (L2384, 16), Род/Дат/Твор/Предл the noun handlers a–ka, ––—·, aal—, —·—a (l–). Docs: docs/vba/analysis.md §3 «Прилагательные».

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `decline_adjective` | 20 | 8 | 12 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| adj-neuter-genitive | `"красный"` | `"красный"` | `"красного"` | Средний род прилагательного в косвенных падежах — формы прилагательного | the ср. род Род button runs the noun handler a–ka: «ный» is no noun ending, so the word stays |
| adj-neuter-soft | `"синий"` | `"синое"` | `"синее"` | Ошибки таблиц склонения исправлены | the neuter of the ending «ний» in adjSuffixes is «ное» |
| adj-feminine-third | `"третий"` | `"третьи"` | `"третья"` | Ошибки таблиц склонения исправлены | the feminine nominative of «третий» in adjExclusions2 is «третьи» |
| adj-plural-accusative-third | `"третий"` | `"третьих"` | `"третьи"` | Ошибки таблиц склонения исправлены | the plural accusative of «третий» in adjExclusions2 is the animate «третьих» |
| adj-plural-possessive | `"лисий"` | `"лисие"` | `"лисьи"` | Ошибки таблиц склонения исправлены | the plural of the ending «сий» in adjSuffixes is «сие» |
| adj-feminine-second | `"второй"` | `"вторые"` | `"вторая"` | Ошибки таблиц склонения исправлены | the feminine nominative of «второй» in adjExclusions2 is «вторые» |
| adj-accusative-second | `"второй"` | `"второго"` | `"второй"` | Ошибки таблиц склонения исправлены | the masculine accusative of «второй» in adjExclusions2 is the animate «второго» |
| adj-plural-accusative-second | `"второй"` | `"вторых"` | `"вторые"` | Ошибки таблиц склонения исправлены | the plural accusative of «второй» in adjExclusions2 is the animate «вторых» |
| adj-dative-blue | `"голубой"` | `"голубого"` | `"голубому"` | Ошибки таблиц склонения исправлены | the dative of «голубой» in adjExclusions2 is «голубого» |
| adj-dative-pockmarked | `"рябой"` | `"рябого"` | `"рябому"` | Ошибки таблиц склонения исправлены | the dative of «рябой» in adjExclusions2 is «рябого» |
| adj-plural-genitive-blue | `"голубой"` | `"голубыъ"` | `"голубых"` | Ошибки таблиц склонения исправлены | the plural genitive of «голубой» in adjExclusions2 is the typo «голубыъ» |
| adj-plural-genitive-pockmarked | `"рябой"` | `"рябыъ"` | `"рябых"` | Ошибки таблиц склонения исправлены | the plural genitive of «рябой» in adjExclusions2 is the typo «рябыъ» |

### xfail

None.

## decline_full_name

decline_full_name. VBA, RibbonCallbacks.vba: «Просклонять › ФИО» a–ok (L2894, ko 2), ––ao (L1624, 3), a··o (L1642, Вин, ko 3), aa—l (L2223, 5), —·ak (L2102, 6), each k– with oak (L1593): Split(LCase(cell)) must give 3 words, else «!!!Это не ФИО, ФИО это 3 слова»; a woman when the cell ends in «зы» or «на»: the name by ·a— (L1584), the surname by fSurn (L1586); a man: ––o (L1585) and mSurn (L1592); the patronymic by l– (L1518–1520, with its consonant bug); a·a (L1721) on the whole. –·— (L2375) puts «'» before a cut name. Docs: docs/vba/analysis.md §3 «ФИО».

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `decline_full_name` | 14 | 2 | 12 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| fio-genitive-man | `"Иванов Сергей Петрович"` | `"Иванова Сергея Петро"` | `"Иванова Сергея Петровича"` | Существительное на согласную получает обычное окончание своей группы | the patronymic goes through l–, whose consonant bug leaves «Петро» |
| fio-accusative-woman | `"Петрова Анна Ивановна"` | `"Петровой Анне Ивановне"` | `"Петрову Анну Ивановну"` | Винительный падеж ФИО — винительный | the Вин button a··o calls oak with ko 3, the dative |
| fio-accusative-man | `"Иванов Сергей Петрович"` | `"Иванову Сергею Петро"` | `"Иванова Сергея Петровича"` | Винительный падеж ФИО — винительный; Существительное на согласную получает обычное окончание своей группы | a··o calls oak with ko 3 (the dative), and l– leaves the patronymic «Петро» |
| fio-ij-oj | `"Толстой Дмитрий Ильич"` | `"Толстоя 'Дмитрия Ильича"` | `"Толстого Дмитрия Ильича"` | В ФИО нет апострофа; Мужская фамилия на «-ой» склоняется как прилагательное | ––o cuts «Дмитрий» by –·—, which puts «'» in front; mSurn has no «ой» and declines «Толстой» by the noun table |
| fio-empty | `""` | `"!!!Это не ФИО, ФИО это 3 слова"` | `""` | Пустая ячейка ФИО остаётся пустой | oak writes its error text into an empty cell too |
| fio-indeclinable | `"Белых Никита Юрьевич"` | `"Белыха Никиты Юрье"` | `"Белых Никиты Юрьевича"` | Фамилия на «-ых» и «-их» не склоняется; Существительное на согласную получает обычное окончание своей группы | mSurn has no «ых» and gives «Белых» the consonant ending; l– leaves the patronymic «Юрье» |
| fio-indeclinable-dative | `"Черных Иван Петрович"` | `"Черныху Ивану Петро"` | `"Черных Ивану Петровичу"` | Фамилия на «-ых» и «-их» не склоняется; Существительное на согласную получает обычное окончание своей группы | mSurn has no «ых» and gives «Черных» the consonant ending; l– leaves the patronymic «Петро» |
| fio-surname-a | `"Глинка Михаил Иванович"` | `"Глинка Михаила Ивано"` | `"Глинки Михаила Ивановича"` | Мужская фамилия на «-а» и «-я» склоняется как существительное; Существительное на согласную получает обычное окончание своей группы | mSurn keeps a surname in «а»; l– leaves the patronymic «Ивано» |
| fio-surname-yo | `"Королёва Наталья Кузьминична"` | `"Королёва Натальи Кузьминичны"` | `"Королёвой Натальи Кузьминичны"` | Окончание фамилии сравнивается с ё как е | fSurn compares «ёва» with «ева» and keeps the surname |
| fio-accusative-name | `"Абрамович Роман Аркадьевич"` | `"Абрамовичу Роману Аркадье"` | `"Абрамовича Романа Аркадьевича"` | Винительный падеж ФИО — винительный; Винительный падеж мужского имени, фамилии и отчества на согласную — как родительный; Существительное на согласную получает обычное окончание своей группы | the Вин button a··o calls oak with ko 3, the dative; nounExclusions2 gives the inanimate «роман» (a novel) |
| fio-instrumental-ch | `"Абрамович Роман Аркадьевич"` | `"Абрамовичом Романом Аркадье"` | `"Абрамовичем Романом Аркадьевичем"` | Мужское имя и фамилия на согласную получают окончания своей группы; Существительное на согласную получает обычное окончание своей группы | ––o gives every consonant the ending «ом»; l– leaves the patronymic «Аркадье» |
| fio-four-words | `"Мамедов Эльчин Гусейн оглы"` | `"!!!Это не ФИО, ФИО это 3 слова"` | `"Мамедов Эльчин Гусейн оглы"` | Пустая ячейка ФИО остаётся пустой, а значение не из трёх слов — как есть | oak writes its error text for a value that is not three words |

### xfail

None.

## decline_noun

decline_noun. VBA, RibbonCallbacks.vba: «Просклонять › Существительные» a–ka (L2841, ko 2) … —·ao (L2864, ko 12), the wrapper ka("l–", cell, ko) (L2669): l– (L1518–1520) maps over Split(cell, " "), then a·. l– as compiled: ko 4 and 10 take nounExclusions2 or root & oa(last3, nounSuffixes, ko) before any other test; else an abbreviation al· (L2634) or a word of nonDecl stays, nounExclusions gives its row, and every other word is root & oa(last3, nounSuffixes, ko), because the consonant branch (Select Case True / InStr) never runs. oa (L2208) gives the key itself when the table lacks it. Docs: docs/vba/analysis.md §3.0, §3 «Существительные».

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `decline_noun` | 16 | 5 | 11 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| noun-genitive-consonant | `"диван"` | `"ди"` | `"дивана"` | Существительное на согласную получает обычное окончание своей группы | l– skips its consonant branch (Select Case True never equals InStr), so the empty cell of the endings table leaves the root only: «ди» |
| noun-genitive-k | `"парк"` | `"п"` | `"парка"` | Существительное на согласную получает обычное окончание своей группы | l– skips its consonant branch (Select Case True never equals InStr), so the empty cell of the endings table leaves the root only: «п» |
| noun-genitive-plural | `"диван"` | `"ди"` | `"диванов"` | Существительное на согласную получает обычное окончание своей группы | l– skips its consonant branch (Select Case True never equals InStr), so the empty cell of the endings table leaves the root only: «ди» |
| noun-accusative-indeclinable | `"авиасалес"` | `"авиасалеса"` | `"авиасалес"` | Несклоняемое слово и аббревиатура не меняются ни в одном падеже | l– declines the accusative by the endings table before it tests nonDecl: «лес» → «леса» |
| noun-capital | `"Павел"` | `"Па"` | `"Павла"` | Слово ищется в таблицах в нижнем регистре, форма сохраняет его заглавные; Существительное на согласную получает обычное окончание своей группы | l– looks «Павел» up as written and misses nounExclusions, then the consonant bug leaves «Па» |
| noun-each-word | `"диван  стол"` | `"ди с"` | `"дивану столу"` | Существительное на согласную получает обычное окончание своей группы; фраза делится по любым пробелам, двойных пробелов в результатах нет | l– skips its consonant branch (Select Case True never equals InStr), so the empty cell of the endings table leaves the root only; ka keeps the empty word of the double space, a· collapses it |
| noun-plural-stul | `"стул"` | `"с"` | `"стулья"` | Существительное на согласную получает обычное окончание своей группы; Ошибки таблиц склонения исправлены | l– leaves the root «с» for the empty cell of «тул»; the plural of стул is irregular |
| noun-plural-chelovek | `"человек"` | `"чело"` | `"люди"` | Существительное на согласную получает обычное окончание своей группы; Ошибки таблиц склонения исправлены | l– leaves the root «чело» for the empty cell of «век»; the plural of человек is люди |
| noun-plural-genitive-chelovek | `"человек"` | `"чело"` | `"людей"` | Существительное на согласную получает обычное окончание своей группы; Ошибки таблиц склонения исправлены | l– leaves the root «чело» for the empty cell of «век»; the plural of человек is люди |
| noun-no-plural | `"мебель"` | `"мебели"` | `"мебель"` | Ошибки таблиц склонения исправлены | nounExclusions2 gives мебель a plural |
| noun-accusative-inanimate | `"диван"` | `"дивана"` | `"диван"` | Винительный падеж неодушевлённого существительного — именительный | l– takes the accusative from nounSuffixes, whose «ван» is animate («Иван») |

### xfail

None.

## irrelevant_words

irrelevant_words. VBA, RibbonCallbacks.vba —k–o (L2887) → findIrr.frm searchButton_Click: the form asks the 12 forms of the main word, filled from l– (L1518–1520, with its consonant bug); the selection is changed in place by udalit_toponimy_s_pryedlogami (L1194) and DeletePhrases (L3452) for GEO_Toponyms and markyerypokupki (lower case). For each word triple, w[g] is a form and w[g-1] is in the list of its case (arrImenit … arrPredl): w[g-2] is a candidate unless a stopword. Sheet «Минус-слова»: Слово, Употреблений, Примеры (each «w prep form» and a comma). The result renders as «word=examples». Docs: docs/vba/analysis.md §9.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `irrelevant_words` | 7 | 2 | 5 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| irr-two-uses | `"чехол для телефона \| чехол на телефон"` | `"чехол=чехол на телефон,"` | `"чехол=чехол для телефона, чехол на телефон"` | Формы главного слова — исправленные формы существительного; Примеры нерелевантного слова — через «, », каждый пример один раз | the form fills Род from l–: «теле», so «для телефона» is not found; the examples end in a comma |
| irr-accusative | `"стекло на телефон"` | `"стекло=стекло на телефон,"` | `"стекло=стекло на телефон"` | Примеры нерелевантного слова — через «, », каждый пример один раз | the examples end in a comma |
| irr-repeat | `"чехол на телефон \| чехол на телефон"` | `"чехол=чехол на телефон,"` | `"чехол=чехол на телефон"` | Примеры нерелевантного слова — через «, », каждый пример один раз | the examples end in a comma |
| irr-plural | `"чехлы для телефонов"` | `""` | `"чехлы=чехлы для телефонов"` | Формы главного слова — исправленные формы существительного | the form fills МН Род from l–: «теле», so «телефонов» is not found |
| irr-lower-case | `"Чехол на Телефон"` | `"чехол=чехол на телефон,"` | `"чехол=чехол на телефон"` | Поиск нерелевантных слов не меняет вход; Примеры нерелевантного слова — через «, », каждый пример один раз | DeletePhrases lower-cases the selection in place before the search; the examples end in a comma |

### xfail

None.
