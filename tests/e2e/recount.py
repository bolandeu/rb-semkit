"""The independent recount of the end-to-end runs: plain Python, pymorphy3 for the lemmas, no rb_semkit code.

Each function states the rule it counts by, as the help of its step states it; the tests compare the result of the
CLI with it row by row.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter
from collections.abc import Iterable
from functools import cache
from itertools import combinations
from pathlib import Path

import pymorphy3

FIXTURES = Path(__file__).parent / "fixtures"
DECIMALS = 4
# A word: letters and digits; a hyphen or an apostrophe between two of them, a point or a comma between two digits,
# stay inside it («кресло-кровать», «31.03.2026», «275-30-85»). Any other character is no part of a word.
CHAR = r"[A-Za-zА-Яа-яЁё0-9]"
WORD = re.compile(rf"{CHAR}+(?:(?:['’-]|(?<=[0-9])[.,](?=[0-9])){CHAR}+)*")
SENTENCE_ENDS = ".!?…"
# A point after these words is no sentence end («г. Краснознаменск», «ул. Березовая», «т. е.»): the abbreviations
# the help of coverage and split-text names, written out.
ABBREVIATIONS = frozenset(
    [
        "г",
        "гг",
        "д",
        "е",
        "м",
        "п",
        "т",
        "ул",
        "пер",
        "пр",
        "просп",
        "наб",
        "пл",
        "обл",
        "корп",
        "стр",
        "кв",
        "эт",
        "тел",
        "руб",
        "коп",
        "тыс",
        "млн",
        "млрд",
        "шт",
        "др",
    ]
)
# Words of the sofa core and of the lists whose lemma the bundled dictionary gives otherwise than pymorphy3:
# word -> (the dictionary's lemma, pymorphy3's lemma). The recount takes the first; a test checks the second, so the
# list follows pymorphy3.
DICTIONARY_LEMMAS = {
    "авито": ("авито", "авить"),
    "аскона": ("аскона", "аскон"),
    "атланта": ("атлант", "атланта"),
    "бединге": ("бединг", "бединга"),
    "бельевым": ("бельевой", "бельевая"),
    "большие": ("большой", "больший"),
    "большим": ("большой", "больший"),
    "встроенная": ("встроенный", "встроить"),
    "гостиной": ("гостиный", "гостиная"),
    "деко": ("деко", "декий"),
    "дешево": ("дешевый", "дешево"),
    "дорого": ("дорогой", "дорого"),
    "дорогой": ("дорогой", "дорога"),
    "йошкар": ("йошкар", "йошкара"),
    "марта": ("марта", "март"),
    "мини": ("мини", "минь"),
    "недорого": ("недорогой", "недорого"),
    "оле": ("ола", "оля"),
    "орматек": ("орматек", "орматечь"),
    "петушках": ("петушки", "петушок"),
    "пожилого": ("пожилой", "пожилое"),
    "пуше": ("пуш", "пуша"),
    "раскладывающийся": ("раскладывающийся", "раскладываться"),
    "складные": ("складной", "складный"),
    "см": ("см", "смотреть"),
    "спальным": ("спальный", "спальная"),
    "старого": ("старый", "старое"),
    "столплит": ("столплит", "столплита"),
    "темно": ("темный", "темно"),
    "трансформер": ("трансформер", "трансформера"),
    "трансформеры": ("трансформер", "трансформера"),
    "тучково": ("тучково", "тучковый"),
    "флока": ("флок", "флока"),
}


def rows(name: str) -> list[dict[str, str]]:
    """The rows of a CSV fixture, every cell as written."""
    with (FIXTURES / name).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def lines(name: str) -> list[str]:
    """The items of a list fixture, one per line."""
    return [line.strip() for line in (FIXTURES / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def text(name: str) -> str:
    """A text fixture as the CLI reads it with --whole: without a BOM, line ends as '\\n'."""
    return (FIXTURES / name).read_text(encoding="utf-8-sig")


def key(word: str) -> str:
    """A word or phrase as compared: NFKC, lower case, ё as е, single spaces."""
    return " ".join(unicodedata.normalize("NFKC", word).lower().replace("ё", "е").split())


def words(phrase: str) -> list[str]:
    return WORD.findall(phrase)


@cache
def _morph() -> pymorphy3.MorphAnalyzer:
    return pymorphy3.MorphAnalyzer()


def pymorphy_lemma(word: str) -> str:
    return key(_morph().parse(word)[0].normal_form)


@cache
def lemma(word: str) -> str:
    """The lemma of a word (as `key` folds it): pymorphy3, or the dictionary's where DICTIONARY_LEMMAS says so."""
    folded = key(word)
    return DICTIONARY_LEMMAS[folded][0] if folded in DICTIONARY_LEMMAS else pymorphy_lemma(folded)


# ngrams: every run of n words of a phrase is one occurrence; count = occurrences, docs = rows holding the gram,
# sum = the weight of the row once per occurrence; sorted by count, biggest first, then by the gram.
def ngrams(table: list[dict[str, str]], column: str, weight: str, n: int) -> list[dict]:
    count: Counter[str] = Counter()
    total: Counter[str] = Counter()
    docs: Counter[str] = Counter()
    for row in table:
        keys = [key(word) for word in words(row[column])]
        grams = [" ".join(keys[start : start + n]) for start in range(len(keys) - n + 1)]
        for gram in grams:
            count[gram] += 1
            total[gram] += int(row[weight])
        docs.update(set(grams))
    ordered = sorted(count, key=lambda gram: (-count[gram], gram))
    return [{"ngram": gram, "count": count[gram], "docs": docs[gram], "sum": total[gram]} for gram in ordered]


def _compared(word: str, by_lemmas: bool) -> str:
    return lemma(word) if by_lemmas else key(word)


# drop-words: a row goes when one of its words (split on whitespace) is a listed word; by lemmas, when the lemmas match.
def kept_by_words(phrases: Iterable[str], listed: list[str], *, by_lemmas: bool) -> list[str]:
    wanted = {_compared(item, by_lemmas) for item in listed}
    return [phrase for phrase in phrases if not {_compared(w, by_lemmas) for w in phrase.split()} & wanted]


# drop-phrases: a row goes when the words of a listed phrase stand in it in a row, as whole words.
def kept_by_phrases(phrases: Iterable[str], listed: list[str], *, by_lemmas: bool) -> list[str]:
    wanted = [[_compared(word, by_lemmas) for word in item.split()] for item in listed]

    def holds(phrase: str) -> bool:
        compared = [_compared(word, by_lemmas) for word in phrase.split()]
        return any(compared[start : start + len(item)] == item for item in wanted for start in range(len(compared)))

    return [phrase for phrase in phrases if not holds(phrase)]


# dupes by lemmas: the key of a phrase is its lemmas in any order; a phrase whose key an earlier phrase has is a
# duplicate; an empty phrase never is.
def lemma_duplicates(phrases: Iterable[str]) -> list[bool]:
    seen: set[tuple[str, ...]] = set()
    marks = []
    for phrase in phrases:
        found = tuple(sorted(lemma(word) for word in phrase.split()))
        marks.append(bool(found) and found in seen)
        seen.add(found)
    return marks


def url_key(url: str) -> str:
    """A URL as two tops compare it: lower case, no scheme, no «www.», no slash at the end."""
    lowered = url.strip().lower()
    return re.sub(r"^[a-z][a-z0-9+.-]*://", "", lowered).removeprefix("www.").rstrip("/")


def tops(serp: list[dict[str, str]], top: int) -> dict[str, frozenset[str]]:
    found: dict[str, set[str]] = {}
    for row in serp:
        urls = found.setdefault(row["phrase"], set())
        if int(row["position"]) <= top and row["url"].strip():
            urls.add(url_key(row["url"]))
    return {phrase: frozenset(urls) for phrase, urls in found.items()}


def shared(first: frozenset[str], second: frozenset[str]) -> int:
    return len(first & second)


def pairs(members: list[str]) -> Iterable[tuple[str, str]]:
    return combinations(members, 2)


def sentences(source: str) -> list[list[str]]:
    """The words of a text in sentences: a point, «!», «?» or «…» between two words ends one, unless the point
    follows an abbreviation; a dash, a comma or a bracket does not."""
    found: list[list[str]] = [[]]
    end = 0
    for match in WORD.finditer(source):
        marks = "".join(source[end : match.start()].split())
        if found[-1] and marks.startswith(".") and key(found[-1][-1]) in ABBREVIATIONS:
            marks = marks[1:]
        if found[-1] and any(mark in SENTENCE_ENDS for mark in marks):
            found.append([])
        found[-1].append(match.group())
        end = match.end()
    return [sentence for sentence in found if sentence]


# coverage exact: the words of a phrase in a row inside one sentence, folded; an occurrence does not overlap the one
# before it; first = the 1-based number of the word where it first starts; density = count x words of the phrase /
# words of the text, 4 decimals.
def coverage(phrases: Iterable[str], source: str) -> list[dict]:
    keyed = [[key(word) for word in sentence] for sentence in sentences(source)]
    total = sum(len(sentence) for sentence in keyed)
    result = []
    for phrase in dict.fromkeys(phrases):
        wanted = [key(word) for word in phrase.split()]
        count, first, offset = 0, None, 0
        for sentence in keyed:
            free = 0
            for start in range(len(sentence)):
                if start >= free and sentence[start : start + len(wanted)] == wanted:
                    count += 1
                    free = start + len(wanted)
                    first = first or offset + start + 1
            offset += len(sentence)
        density = round(count * len(wanted) / total, DECIMALS)
        result.append({"phrase": phrase, "count": count, "docs": int(count > 0), "density": density, "first": first})
    return result


def char_stats(source: str) -> dict[str, int]:
    """chars, chars_no_spaces and words of a text."""
    return {"chars": len(source), "chars_no_spaces": len("".join(source.split())), "words": len(words(source))}
