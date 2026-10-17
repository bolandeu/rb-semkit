# Conformance of the markers area with the !SEMTools VBA

`scripts/conformance_report.py` writes this file from the case files `tests/conformance/cases/markers/*.tsv`; do not
edit it. The terms and the other areas: [the summary](../conformance.md).

## Summary

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| [markers](#markers) | 44 | 35 | 9 | 0 |
| **All** | **44** | **35** | **9** | **0** |

## markers

markers. VBA, RibbonCallbacks.vba (docs/vba/matchers.md S10, F3, R3, X3). find: —k—— (L2520) geo, —k—6 (L2047) mosmetro, —k—7 (L2048) districts, —k—8 (L2049) MO, —k—9 (L2050) citiesRu, —k—o (L2040) questions, —k—3 (L2044) fun, —k—4 (L2045) DIY, —k—01 (L2052) edu, —k—02 (L2053) game, —k—l (L2042) sale, —k—00 (L2041) rent, —k—2 (L2043) reviews, —k—0 (L2051) color, —k—03 (L2054) material, —k—04 (L2055) origin, —k—5 (L2046) cars, —k—05 (L2056) names, RbnFind (L3172) several lists; each with –la (L645–646). remove: a·–a (L2204) geo, a·a6 (L2030) and the other a·a* buttons, RbnDelete (L3173) several lists; each with DeletePhrases (L3452–3470), lower-cases the cell; geo with prepositions a·—a (L2967) with udalit_toponimy_s_pryedlogami (L1194–1197), its one-item quirk fixed. extract: –a·a (L2823) geo, ——aa4 (L2014) and the other ——aa* buttons, –a—o (L2409) questions (its later steps, which cut word repeats and sale phrases and lower-case the result, are not taken), RbnExtract (L3174) several lists; each with la— (L647–648): the found items as the list spells them, joined by a backslash; geo with prepositions –·kk (L2674) with k—–– (L1198–1199). la— and k—–– take the first item in list order («как», not «как сделать»), and la— also finds an item anywhere in the phrase, so a word inside a found item gives its own marker («Новгород»). The rows ref-markers_geo-* are the workbook sheet markers_geo. User lists have no handler: derived from —k—k (L2218), aok– (L2733) and –a–a (L1736). Prepositions on other lists and find with prepositions have no handler: derived from udalit_toponimy_s_pryedlogami; vba is the derived value.

| Function | Cases | As the VBA | Deviations | xfail |
|---|---|---|---|---|
| `markers.extract` | 28 | 21 | 7 | 0 |
| `markers.find` | 6 | 6 | 0 | 0 |
| `markers.remove` | 10 | 8 | 2 | 0 |

### Deviations

| Case | Input | VBA | semkit | Rule | Why |
|---|---|---|---|---|---|
| markers-extract-geo-inner | `"доставка в нижний новгород"` | `"Нижний Новгород\Новгород"` | `"Нижний Новгород"` | маркеры — в написании списка, через «, »; Извлечение маркеров берёт самое длинное совпадение | la— finds «Нижний Новгород» and gives «новгород», a key too, its own slot, joined by a backslash |
| markers-extract-geo-inner-long | `"отели в хересе де ла фронтере"` | `"Хересе де Ла Фронтере\Ла Фронтере"` | `"Хересе де Ла Фронтере"` | маркеры — в написании списка, через «, »; Извлечение маркеров берёт самое длинное совпадение | la— gives «ла», a key too, its own slot «Ла Фронтере», joined by a backslash |
| markers-extract-questions | `"Где Купить диван как сделать"` | `"где\как"` | `"где, как сделать"` | маркеры — в написании списка, через «, »; Извлечение маркеров берёт самое длинное совпадение | la— takes «как», first in the list order, and joins by a backslash; –a—o then lower-cases the cell |
| markers-extract-geo-prepositions | `"купить диван в москве недорого"` | `"\\в Москве\\\"` | `"в Москве"` | маркеры — в написании списка, через «, » | k—–– keeps one slot per word, the empty ones too, joined by a backslash |
| markers-extract-geo-prepositions-none | `"диван москва"` | `"\\"` | `""` | маркеры — в написании списка, через «, » | k—–– keeps one slot per word, the empty ones too, joined by a backslash |
| markers-extract-geo-prepositions-phrase | `"доставка в нижний новгород"` | `"\в Нижний Новгород\\\"` | `"в Нижний Новгород"` | маркеры — в написании списка, через «, » | k—–– keeps one slot per word, the empty ones too, joined by a backslash |
| markers-extract-geo-prepositions-long | `"отели в хересе де ла фронтере"` | `"\в Хересе де Ла Фронтере\\\\\"` | `"в Хересе де Ла Фронтере"` | маркеры — в написании списка, через «, » | k—–– keeps one slot per word, the empty ones too, joined by a backslash |
| markers-remove-geo-case | `"Диван Москва"` | `"диван"` | `"Диван"` | Удаление по списку фраз и маркеров сохраняет регистр | DeletePhrases lower-cases the whole cell |
| markers-remove-geo-prepositions-one-item | `"отели в хересе де ла фронтере"` | `"отели де ла фронтере"` | `"отели"` | Удаление топонимов с предлогами убирает топоним целиком | udalit_toponimy_s_pryedlogami cuts only the preposition and the next word when that word keys one list item |

### xfail

None.
