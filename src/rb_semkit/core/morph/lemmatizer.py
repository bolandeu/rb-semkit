"""The Lemmatizer protocol and the bundled SemtoolsLemmatizer (ADR 0003, ADR 0005).

A wordform goes to the !SEMTools dictionary first; a word not in it goes to pymorphy3; a word pymorphy3 does
not know either gets its last four letters replaced by the add-in's `lemmSuf` table. With the fallback "pymorphy",
every word not in the dictionary takes the best guess of pymorphy3 instead. Lemmas are lower case.
`looks_like_adjective` is the add-in's adjective rule by the lemma ending; the pos matcher uses it too.
"""

from __future__ import annotations

from typing import Protocol

import pymorphy3
from pymorphy3.analyzer import Parse

from .. import datastore
from ..normalize import norm_phrase
from ..text.base import choice

LEMMAS = "morph/lemmas.marisa"
FORMS = "morph/forms.marisa"
MORPH = "morph/morph.json"

FALLBACKS = ("pymorphy",)
# The add-in's verb rule: these endings make a verb whatever the dictionary says; «уют» itself is a noun.
VERB_ENDINGS = ("тся", "ься", "ают", "уют")
NOT_VERBS = frozenset({"уют"})
NEGATION = "не"  # a noun of the dictionary in «не-» whose rest is an adjective there is an adjective («нераскладной»)
UNKNOWN = "unkn"  # the code of a word no rule gives a part of speech: «кляк», «15», «диван,»
# pymorphy3 parts of speech as the dictionary's codes; one with no code there gives UNKNOWN.
PYMORPHY_POS = {
    "NOUN": "n",
    "NUMR": "n",
    "ADJF": "a",
    "ADJS": "a",
    "COMP": "a",
    "VERB": "v",
    "INFN": "v",
    "GRND": "v",
    "PRTF": "p",
    "PRTS": "p",
    "ADVB": "advb",
    "PRED": "advb",
    "NPRO": "prn",
    "PREP": "prep",
    "CONJ": "conj",
    "PRCL": "prt",
}


class Lemmatizer(Protocol):
    """What gives the lemma and the part of speech of a wordform, and the wordforms of a lemma."""

    def lemma(self, word: str) -> str: ...

    def pos(self, word: str) -> str: ...

    def forms(self, lemma: str) -> list[str]: ...


def _from_dictionary(word: str) -> tuple[str, str] | None:
    lemmas = datastore.trie(LEMMAS)
    found = lemmas.get(word) or lemmas.get(norm_phrase(word))  # «ёлки» is in the dictionary as «елки»
    if not found:
        return None
    lemma, pos = found[0].decode().split("\t")
    return lemma, pos


def _analyzer() -> pymorphy3.MorphAnalyzer:
    return datastore.once("pymorphy3", pymorphy3.MorphAnalyzer)


def noun_parse(word: str) -> Parse | None:
    """The first parse of pymorphy3 that makes the word a noun (a guess for a word its dictionary lacks); None
    without one. The declension takes the animacy and the gender from it, and the forms of a hyphenated noun."""
    return next((parse for parse in _analyzer().parse(word) if parse.tag.POS == "NOUN"), None)


def _from_pymorphy(word: str, *, guess: bool = False) -> tuple[str, str] | None:
    """The best parse of pymorphy3: of a word its dictionary knows, or with `guess` of any word.

    Its lemma has ё only where the word has it, as the dictionary («вперед» → «вперед», not «вперёд»).
    """
    analyzer = _analyzer()
    if not guess and not analyzer.word_is_known(word):
        return None
    best = analyzer.parse(word)[0]
    lemma = best.normal_form if "ё" in word else norm_phrase(best.normal_form)
    return lemma, PYMORPHY_POS.get(str(best.tag.POS), "")


def _adjective_rule() -> tuple[frozenset[str], frozenset[str]]:
    morph = datastore.table(MORPH)
    return frozenset(morph["adjective_endings"]), frozenset(morph["nouns_like_adjectives"])


def looks_like_adjective(lemma: str) -> bool:
    """The add-in's adjective rule: the lemma ends like an adjective (`adjSuffixes`) and is not a noun like one."""
    endings, nouns_like_adjectives = datastore.once("adjective_rule", _adjective_rule)
    return lemma[-3:] in endings and lemma not in nouns_like_adjectives


def _from_suffixes(word: str) -> tuple[str, str]:
    """The add-in's fallback: the last four letters by `lemmSuf`; an adjective when the lemma ends like one."""
    suffix = word[-4:]
    lemma = word[: len(word) - len(suffix)] + datastore.table(MORPH)["lemma_suffixes"].get(suffix, suffix)
    return lemma, "a" if looks_like_adjective(lemma) else ""


def _is_negated_adjective(word: str, pos: str) -> bool:
    rest = _from_dictionary(word.removeprefix(NEGATION)) if word.startswith(NEGATION) else None
    return pos == "n" and rest is not None and rest[1] == "a"


def _analyse(word: str, fallback: str | None) -> tuple[str, str]:
    guess = fallback == "pymorphy"  # pymorphy3 then gives every word a parse, and the suffix rule is never reached
    lemma, pos = _from_dictionary(word) or _from_pymorphy(word, guess=guess) or _from_suffixes(word)
    if word.endswith(VERB_ENDINGS) and word not in NOT_VERBS:
        pos = "v"
    elif _is_negated_adjective(word, pos):
        pos = "a"
    return lemma, pos or UNKNOWN


class SemtoolsLemmatizer:
    """The default Lemmatizer: the !SEMTools dictionary, then pymorphy3, then the `lemmSuf` fallback.

    fallback: None as above; "pymorphy" gives every word not in the dictionary the best guess of pymorphy3, also a
    word its own dictionary lacks («тиктокерами» → «тиктокер»).
    Each distinct word is analysed once per instance. POS codes are the dictionary's: n, v, a, p (participle),
    advb, prn, prep, conj, prt; nv as in the dictionary (meaning unknown); "" when no rule gives one.
    """

    def __init__(self, fallback: str | None = None) -> None:
        self._fallback = None if fallback is None else choice("fallback", fallback, FALLBACKS)
        self._analysed: dict[str, tuple[str, str]] = {}

    def _analysis(self, word: str) -> tuple[str, str]:
        key = word.lower()
        found = self._analysed.get(key)
        if found is None:
            found = self._analysed[key] = _analyse(key, self._fallback)
        return found

    def lemma(self, word: str) -> str:
        return self._analysis(word)[0]

    def pos(self, word: str) -> str:
        return self._analysis(word)[1]

    def forms(self, lemma: str) -> list[str]:
        """Every wordform of `lemma` in the dictionary; [] for a lemma it does not hold."""
        return [form.decode() for form in datastore.trie(FORMS).get(norm_phrase(lemma), [])]
