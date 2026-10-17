"""The matchers against their VBA handlers: each row is (phrase, matcher, verb, expected), traced by hand.

The expected values come from the handler entries of docs/vba/matchers.md (algorithm and worked examples) with the
ADR 0005 deviations applied: ё = е, stopwords in any case, split on any whitespace, no double spaces, markers as the
list spells them joined by ', '. A row id names the handler; «fix» marks a row where the code differed from the VBA.
"""

from __future__ import annotations

import pandas as pd
import pytest

import rb_semkit as sk


def case(phrase: str | list[str], matcher: sk.Matcher, verb: str, expected: object, handler: str):
    return pytest.param(phrase, matcher, verb, expected, id=handler)


GEO = sk.markers("geo")
GEO_PREPS = sk.markers("geo", with_prepositions=True)
CITIES = sk.phrases(["Нижний Новгород", "Москва"])

CASES = [
    # chars
    case("диван IKEA", sk.chars("latin"), "find", True, "—·k—"),
    case("Диван IKEA Ektorp 3-местный", sk.chars("latin"), "extract", "IKEA Ektorp", "–ako"),
    case("Wi-Fi роутер", sk.chars("latin"), "extract", "WiFi", "–ako fix"),
    case("Диван IKEA Ektorp", sk.chars("latin"), "remove", "Диван", "ak·—"),
    case("IKEA Эктроп", sk.chars("cyrillic"), "find", True, "—·k–"),
    case("IKEA Є", sk.chars("cyrillic"), "find", False, "—·k– fix"),
    case("Диван IKEA", sk.chars("cyrillic"), "remove", "IKEA", "ak–·"),
    case("IKEA Є", sk.chars("cyrillic"), "remove", "IKEA Є", "ak–· fix"),
    case("Диван-кровать IKEA 3-местный", sk.chars("cyrillic"), "extract", "Диванкровать местный", "–—–a fix"),
    case("диван 2 места", sk.chars("digits"), "find", True, "—·ka"),
    case("120x200", sk.chars("digits"), "remove", "x", "aokk"),
    case("тел 8 (999) 123-45", sk.chars("digits"), "extract", "8 999 12345", "–·ko fix"),
    case("120x200", sk.chars("digits"), "extract", "120200", "–·ko fix"),
    case("диван", sk.chars("letters_digits"), "find", True, "—kko"),
    case("!!! ---", sk.chars("letters_digits"), "find", False, "—kko"),
    case("中文", sk.chars("letters_digits"), "find", False, "—kko fix"),
    case("Диван-кровать, 2 шт.!", sk.chars("letters_digits"), "extract", "Диван кровать 2 шт", "aok—"),
    case("Диван-кровать, 2 шт.!", sk.chars("punctuation"), "remove", "Диван кровать 2 шт", "aok— fix"),
    case("«ИКЕА»", sk.chars("punctuation"), "remove", "ИКЕА", "aok—"),
    case("диван 中文", sk.chars("punctuation"), "remove", "диван", "aok— fix"),
    case("купить Диван", sk.chars("upper"), "find", True, "—·ok"),
    case("диван", sk.chars("upper"), "find", False, "—·ok"),
    case("Ўзбекистон", sk.chars("upper"), "find", True, "—·ok fix"),
    case("ціна дивана", sk.chars("ua"), "find", True, "—·k·"),
    case("купить диван", sk.chars("ua"), "find", False, "—·k·"),
    case("купить кровати", sk.chars("ua"), "find", False, "—·k· fix"),
    case("ґанок", sk.chars("ua"), "find", True, "—·k· fix"),
    case("їжак, ґанок!", sk.chars("ua"), "extract", "ї ґ", "—·k·"),
    # spaces
    case("  купить   диван ", sk.spaces("extra"), "remove", "купить диван", "–aal"),
    case("  купить  диван ", sk.spaces("left"), "remove", "купить  диван ", "—ako"),
    case("  диван  ", sk.spaces("right"), "remove", "  диван", "a–o—"),
    case(" купить  диван ", sk.spaces("both"), "remove", "купить  диван", "a–k—"),
    # positions
    case("1. диван", sk.positions(2), "remove", "диван", "ak——"),
    case("диван", sk.positions(10), "remove", "", "ak——"),
    case("диван.", sk.positions(1, last=True), "remove", "диван", "ak·k"),
    case("диван-кровать", sk.positions(5), "extract", "диван", "–—·–"),
    case("диван-кровать", sk.positions(6, last=True), "extract", "ровать", "–ak·"),
    # around
    case("купить диван синий", sk.around("диван"), "remove", "диван синий", "––·—"),
    case("купить диван синий", sk.around("диван", after=True), "remove", "купить диван", "––—o"),
    case("москва диван москва кресло", sk.around("москва", include=True, last=True), "remove", "кресло", "–—kk"),
    case("стол и кресло и шкаф", sk.around("и", include=True), "extract", "стол и", "–—–o"),
    case("стол и кресло и шкаф", sk.around("и", after=True, last=True), "extract", "шкаф", "–—–k"),
    case("диван", sk.around("стол"), "remove", "диван", "––·a"),
    case("диван", sk.around("стол"), "extract", "", "–—–o"),
    case("  купить  диван  в  москве ", sk.around("в", after=True, include=True), "remove", "купить ди", "––—– fix"),
    case("Товар: диван: синий", sk.around(":", include=True), "remove", "диван: синий", "––·a fix"),
    case("купить Диван синий", sk.around("диван"), "remove", "Диван синий", "––·—"),
    case("a/b/c", sk.around("/", include=True, last=True), "remove", "c", "–—kk fix"),
    case("a/b/B", sk.around("b", last=True), "remove", "b/B", "––·· fix"),
    case("диван - синий - большой", sk.around(" - ", after=True, include=True), "remove", "диван", "––—–"),
    case("a/b/c", sk.around("/", after=True, last=True, include=True), "remove", "a/b", "––—a fix"),
    case("диван, кресло, стол", sk.around(",", include=True), "extract", "диван,", "–—–o fix"),
    case("Купить купить", sk.around("купить", include=True), "extract", "Купить купить", "–—–o fix"),
    case("диван, кресло", sk.around(","), "extract", "диван", "–—–– fix"),
    case("a/b/c", sk.around("/", after=True, last=True, include=True), "extract", "/c", "–—o· fix"),
    case("a/b/c", sk.around("/", after=True, last=True), "extract", "c", "–—–k fix"),
    case("ёлка Елка", sk.around("елка", include=True), "extract", "ёлка", "–—–o"),
    # regex
    case("купить диван", sk.regex("^купить"), "find", True, "—koa"),
    case("Купить диван", sk.regex("^купить"), "find", False, "—koa"),
    case("диван 2 места 3", sk.regex(r"\d+"), "remove", "диван места", "aoka fix"),
    case("диван 120x200", sk.regex(r"\d+"), "extract", "120", "–a—–"),
    case("диван 120x200", sk.regex(r"\d+", all_matches=True), "extract", "120 200", "–a——"),
    case("купить диван в москве", sk.regex(r"\bв\b"), "remove", "купить диван москве", "aoka"),
    case("диван 120x200", sk.regex(r"\d+", invert=True), "remove", "120200", "aok· fix"),
    case("диван 120x200", sk.regex(r"\d+", invert=True), "extract", "диван x", "aok· fix"),
    case("диван 120", sk.regex(r"\d+", invert=True), "find", True, "aok· fix"),
    case("120", sk.regex(r"\d+", invert=True), "find", False, "aok·"),
    # words
    case("Купить Диван", sk.words("диван"), "find", True, "–––o"),
    case("диван-кровать", sk.words("диван"), "find", False, "–––o"),
    case("диван в москве", sk.words(["диван", "москва"], mode="all"), "find", False, "–––k"),
    case("Диван диван-кровать диван", sk.words("диван"), "remove", "диван-кровать", "ao—a"),
    case("Купить диван купить", sk.words(["купить"], where="start"), "remove", "диван купить", "dFWCustom"),
    case("диван купить", sk.words(["купить"], where="end"), "remove", "диван", "dLWCustom"),
    case("Купить Диван и диван", sk.words("диван"), "extract", "Диван диван", "–·oo"),
    # word_content
    case("купить диванчик", sk.word_content("starts", "диван"), "find", True, "—ka—"),
    case("красный диван", sk.word_content("ends", "ный"), "find", True, "—kao"),
    case("красный, синий", sk.word_content("ends", "ный"), "find", False, "—kao fix"),
    case("«диван» кресло", sk.word_content("starts", "див"), "extract", "", "–·–a fix"),
    case("купить диван и диванчик", sk.word_content("starts", "див"), "remove", "купить и", "aoaa"),
    case("диван диванчик кресло", sk.word_content("contains", "диван"), "remove", "кресло", "aoak"),
    case("диван IKEA 3d Ektorp", sk.word_content("only_latin"), "remove", "диван 3d", "a·—–"),
    case("Wi-Fi роутер", sk.word_content("only_latin"), "extract", "Wi-Fi", "——·– fix"),
    case("диван IKEA 3d Ektorp", sk.word_content("has_latin"), "remove", "диван", "a·a–"),
    case("диван 2 120x200 1,5", sk.word_content("only_digits"), "remove", "диван 120x200", "a·—— fix"),
    case("диван 2 1,5 120x200", sk.word_content("only_digits"), "extract", "2 1,5", "——·— fix"),
    case("диван 2 120x200 3d", sk.word_content("has_digits"), "remove", "диван", "a·a—"),
    case("диван 2 120x200 3d", sk.word_content("mixed"), "extract", "120x200 3d", "a·o–"),
    case("第1", sk.word_content("mixed"), "find", False, "a·o– fix"),
    # word_case
    case("диван IKEA", sk.word_case("lower"), "find", True, "aakL"),
    case("Диван IKEA", sk.word_case("lower"), "find", False, "aakL"),
    case("3d", sk.word_case("lower"), "find", True, "aakL"),
    case("купить Диван", sk.word_case("Capital"), "find", True, "aakP"),
    case("iPhone", sk.word_case("Capital"), "find", False, "aakP"),
    case("Из-за Москвы", sk.word_case("Capital"), "extract", "Москвы", "aakP fix"),
    case("диван IKEA", sk.word_case("CAPS"), "find", True, "aakC"),
    case("2024", sk.word_case("CAPS"), "find", False, "aakC"),
    case("В Москве", sk.word_case("CAPS"), "extract", "В", "aakC fix"),
    # word_position
    case("купить диван в москве", sk.word_position(first=1), "remove", "диван в москве", "ak—k"),
    case("купить диван в москве", sk.word_position(first=3), "remove", "москве", "ak—–"),
    case("купить диван", sk.word_position(first=2), "remove", "", "ak—a"),
    case("купить диван в москве", sk.word_position(last=1), "remove", "купить диван в", "aka—"),
    case("купить диван в москве", sk.word_position(first=2), "extract", "купить диван", "–—·—"),
    case("диван", sk.word_position(first=2), "extract", "диван", "–—·—"),
    case("купить диван в москве", sk.word_position(last=2), "extract", "в москве", "–ak—"),
    case("купить диван в москве", sk.word_position(nth=3), "extract", "в", "–—o–"),
    case("купить диван", sk.word_position(nth=3), "extract", "", "–a–k"),
    case("купить диван недорого москва", sk.word_position(to_middle=True), "extract", "купить диван", "–·—k"),
    case("a b c d e", sk.word_position(to_middle=True), "extract", "a b", "–·—k fix"),
    case("диван-кровать недорого", sk.word_position(to_middle=True), "extract", "диван-кровать", "–·—k"),
    case("купить диван недорого", sk.word_position(at_most=12), "extract", "купить диван", "–·—o fix"),
    case("купить диван", sk.word_position(at_most=3), "extract", "купить", "–·—o fix"),
    case("купить диван недорого", sk.word_position(at_most=12), "remove", "недорого", "–·—o fix"),
    # pos
    case("купить красный диван", sk.pos("noun"), "find", True, "—k–a"),
    case("купить красный диван быстро", sk.pos("noun"), "remove", "купить красный быстро", "ak··"),
    case("купить диван, кресло", sk.pos("noun"), "extract", "кресло", "–ao· fix"),
    case("купить красный диван быстро", sk.pos("adj"), "extract", "красный", "–—o—"),
    case("какой диван купить", sk.pos("adj"), "extract", "какой", "··o fix"),
    case("Быстро купить", sk.pos("adj"), "find", True, "··o fix"),
    case("купить красный диван быстро", sk.pos("verb"), "extract", "купить", "–·ka"),
    case("купить красный диван быстро", sk.pos("adverb"), "extract", "быстро", "–—oa"),
    # repeats
    case("диван Диван", sk.repeats(), "find", True, "—k—–"),
    case("диван диваны", sk.repeats(), "find", False, "—k—–"),
    case("диван, диван", sk.repeats(), "find", False, "—k—– fix"),
    case("Диван купить диван, ДИВАН", sk.repeats(), "remove", "Диван купить диван,", "aala fix"),
    case("Купить диван купить диван недорого", sk.repeats(), "remove", "Купить диван недорого", "aala"),
    case("iphone 13 iphone 13", sk.repeats(scope="en"), "remove", "iphone 13 13", "aal1"),
    case("iphone13 iphone13", sk.repeats(scope="en"), "remove", "iphone13", "aal1 fix"),
    case("диван 2 диван 2", sk.repeats(scope="ru"), "remove", "диван 2 2", "aall"),
    case("wi-fi-роутер wi-fi-роутер", sk.repeats(scope="ru"), "remove", "wi-fi-роутер", "aall fix"),
    case("диван диван Диван кресло диван", sk.repeats(scope="adjacent"), "remove", "диван кресло диван", "remrepW"),
    case("диван 2 места 2 шт", sk.repeats(scope="numbers"), "remove", "диван 2 места шт", "aal·"),
    case("1,5 м 1,5", sk.repeats(scope="numbers"), "remove", "1,5 м", "aal· fix"),
    case("диван диваны диванов", sk.repeats("wordforms"), "remove", "диван", "aook"),
    case("купить диван купила", sk.repeats("wordforms"), "remove", "купить диван", "aook"),
    # stopwords
    case("диван для дачи и сада", sk.stopwords(), "remove", "диван дачи сада", "a·–·"),
    case("Диван В Москве", sk.stopwords(), "remove", "Диван Москве", "a·–·"),
    case("кресло и, стол", sk.stopwords(), "remove", "кресло и, стол", "a·–· fix"),
    # phrases
    case("доставка в нижний новгород", CITIES, "find", True, "—k—k"),
    case("нижний тагил", CITIES, "find", False, "—k—k"),
    case("в москва,", CITIES, "find", False, "—k—k fix"),
    case("Купить диван в Москве", sk.phrases(["купить", "в москве"]), "remove", "диван", "aok–"),
    case("Диван Москва", sk.phrases(["москве"]), "remove", "Диван Москва", "aok–"),
    case("Москва, диван москва", sk.phrases(["москва"]), "remove", "Москва, диван", "aok– fix"),
    case("Купить Угловой ДИВАН", sk.phrases(["угловой диван"]), "extract", "угловой диван", "–a–a fix"),
    case("доставка в нижний новгород", CITIES, "extract", "Нижний Новгород", "–a–a"),
    # VBA: купить диван, диван, угловой диван, диван
    case(
        "купить диван угловой диван",
        sk.phrases(["диван", "угловой диван", "купить диван"]),
        "extract",
        "купить диван, угловой диван",
        "–a–a fix",
    ),
    # cells
    case(["Купить диван", "кресло"], sk.cells("contains", items=["диван"]), "find", [True, False], "—kk—"),
    case(
        ["купить диван", "купитьдиван", "диван купить"],
        sk.cells("starts", items=["купить"]),
        "find",
        [True, True, False],
        "—ko·",
    ),
    case(["диван москва", "диван москвы"], sk.cells("ends", items=["москва"]), "find", [True, False], "—koo"),
    case(
        ["для дома диван", "диван для дома", "для, дома"],
        sk.cells("starts", prepositions=True),
        "find",
        [True, False, False],
        "findFFWprps fix",
    ),
    case(["диван для", "диван для,"], sk.cells("ends", prepositions=True), "find", [True, False], "findFLWprps fix"),
    case(["купить диван", "Купить диван"], sk.cells("regex", pattern="^купить"), "find", [True, False], "—koa"),
    case(["Диван", "диван", "кресло"], sk.cells("unique"), "find", [False, False, True], "—k—a fix"),
    case(["Диван", "диван", "кресло"], sk.cells("repeated"), "find", [True, True, False], "—k–— fix"),
    case(["ёлка", "елка"], sk.cells("repeated"), "find", [True, True], "—k–— fix"),
    case(["Диван", "диван", "кресло", "диван"], sk.cells("first"), "find", [True, False, True, False], "—k–k fix"),
    case(["Диван", "диван", "кресло", "диван"], sk.cells("last"), "find", [False, False, True, True], "—k–– fix"),
    case(["", " "], sk.cells("empty"), "find", [True, False], "—kk– fix"),
    case(["Диван", "диван", "кресло"], sk.cells("unique"), "extract", ["", "", "кресло"], "–·k— fix"),
    case(["Диван", "диван", "кресло"], sk.cells("repeated"), "extract", ["Диван", "диван", ""], "–aoa fix"),
    case(["Диван", "диван", "кресло"], sk.cells("repeated"), "remove", ["", "", "кресло"], "ak·a fix"),
    case(["Диван", "диван", "кресло"], sk.cells("unique"), "remove", ["Диван", "диван", ""], "ao—– fix"),
    case(["диванчик", "стол"], sk.cells("contains", items=["диван"]), "remove", ["", "стол"], "akok fix"),
    case(["диван 2", "диван"], sk.cells("regex", pattern=r"\d"), "remove", ["", "диван"], "akk· fix"),
    case(["диван", "", "стол"], sk.cells("empty"), "remove", ["диван", "стол"], "remBlankCellsUp"),
    # markers
    case("купить диван в москве недорого", GEO, "find", True, "—k——"),
    case("в москве, недорого", GEO, "find", False, "—k—— fix"),
    case("купить диван в москве недорого", GEO, "extract", "Москве", "–a·a"),
    # VBA: Нижний Новгород, Новгород
    case("доставка в нижний новгород", GEO, "extract", "Нижний Новгород", "–a·a fix"),
    # VBA: Хересе де Ла Фронтере, Ла Фронтере
    case("отели в хересе де ла фронтере", GEO, "extract", "Хересе де Ла Фронтере", "–a·a fix"),
    # VBA: где, как
    case("Где Купить диван как сделать", sk.markers("questions"), "extract", "где, как сделать", "–a—o fix"),
    case("купить диван в москве недорого", GEO, "remove", "купить диван в недорого", "a·–a"),
    case("доставка в нижний новгород", GEO, "remove", "доставка в", "a·–a"),
    case("купить диван в москве недорого", GEO_PREPS, "remove", "купить диван недорого", "a·—a"),
    case("диван москва", GEO_PREPS, "remove", "диван москва", "a·—a"),
    case("доставка в нижний новгород", GEO_PREPS, "remove", "доставка", "a·—a"),
    case("отели в хересе де ла фронтере", GEO_PREPS, "remove", "отели", "a·—a fix"),
    case("диван in москве", GEO_PREPS, "remove", "диван in москве", "a·—a fix"),
    case("купить диван в москве недорого", GEO_PREPS, "extract", "в Москве", "–·kk"),
    case("диван москва", GEO_PREPS, "extract", "", "–·kk fix"),
    case("доставка в нижний новгород", GEO_PREPS, "extract", "в Нижний Новгород", "–·kk"),
    case("отели в хересе де ла фронтере", GEO_PREPS, "extract", "в Хересе де Ла Фронтере", "–·kk"),
    case("диван москва", GEO_PREPS, "find", False, "a·—a fix"),
    case(
        "офис на таганской у таганской",
        sk.markers("mosmetro", with_prepositions=True),
        "remove",
        "офис у таганской",
        "a·—a fix",
    ),
]


@pytest.mark.parametrize(("phrase", "matcher", "verb", "expected"), CASES)
def test_the_matcher_gives_what_the_vba_handler_gives(
    phrase: str | list[str], matcher: sk.Matcher, verb: str, expected: object
) -> None:
    cells = phrase if isinstance(phrase, list) else [phrase]

    result = getattr(sk, verb)(pd.Series(cells), matcher).tolist()

    assert result == (expected if isinstance(phrase, list) else [expected])
