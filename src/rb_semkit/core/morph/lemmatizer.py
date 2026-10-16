"""The Lemmatizer protocol and the bundled SemtoolsLemmatizer (ADR 0003, ADR 0005).

A wordform goes to the !SEMTools dictionary first; a word not in it goes to pymorphy3; a word pymorphy3 does
not know either gets its last four letters replaced by the add-in's `lemmSuf` table. Lemmas are lower case.
"""

from __future__ import annotations

from typing import Protocol

import pymorphy3

from .. import datastore

LEMMAS = "morph/lemmas.marisa"
FORMS = "morph/forms.marisa"
MORPH = "morph/morph.json"

# The add-in's verb rule: these endings make a verb whatever the dictionary says; «уют» itself is a noun.
VERB_ENDINGS = ("тся", "ься", "ают", "уют")
NOT_VERBS = frozenset({"уют"})
# pymorphy3 parts of speech as the dictionary's codes; one with no code there gives "".
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


def _ye(word: str) -> str:
    return word.replace("ё", "е")


def _from_dictionary(word: str) -> tuple[str, str] | None:
    lemmas = datastore.trie(LEMMAS)
    found = lemmas.get(word) or lemmas.get(_ye(word))
    if not found:
        return None
    lemma, pos = found[0].decode().split("\t")
    return lemma, pos


def _from_pymorphy(word: str) -> tuple[str, str] | None:
    analyzer = datastore.once("pymorphy3", pymorphy3.MorphAnalyzer)
    if not analyzer.word_is_known(word):
        return None
    best = analyzer.parse(word)[0]
    return best.normal_form, PYMORPHY_POS.get(str(best.tag.POS), "")


def _adjective_rule() -> tuple[frozenset[str], frozenset[str]]:
    morph = datastore.table(MORPH)
    return frozenset(morph["adjective_endings"]), frozenset(morph["nouns_like_adjectives"])


def _from_suffixes(word: str) -> tuple[str, str]:
    """The add-in's fallback: the last four letters by `lemmSuf`; an adjective when the lemma ends like one."""
    suffix = word[-4:]
    lemma = word[: len(word) - len(suffix)] + datastore.table(MORPH)["lemma_suffixes"].get(suffix, suffix)
    endings, nouns_like_adjectives = datastore.once("adjective_rule", _adjective_rule)
    is_adjective = lemma[-3:] in endings and lemma not in nouns_like_adjectives
    return lemma, "a" if is_adjective else ""


def _analyse(word: str) -> tuple[str, str]:
    lemma, pos = _from_dictionary(word) or _from_pymorphy(word) or _from_suffixes(word)
    if word.endswith(VERB_ENDINGS) and word not in NOT_VERBS:
        pos = "v"
    return lemma, pos


class SemtoolsLemmatizer:
    """The default Lemmatizer: the !SEMTools dictionary, then pymorphy3, then the `lemmSuf` fallback.

    Each distinct word is analysed once per instance. POS codes are the dictionary's: n, v, a, p (participle),
    advb, prn, prep, conj, prt; nv as in the dictionary (meaning unknown); "" when no rule gives one.
    """

    def __init__(self) -> None:
        self._analysed: dict[str, tuple[str, str]] = {}

    def _analysis(self, word: str) -> tuple[str, str]:
        key = word.lower()
        found = self._analysed.get(key)
        if found is None:
            found = self._analysed[key] = _analyse(key)
        return found

    def lemma(self, word: str) -> str:
        return self._analysis(word)[0]

    def pos(self, word: str) -> str:
        return self._analysis(word)[1]

    def forms(self, lemma: str) -> list[str]:
        """Every wordform of `lemma` in the dictionary; [] for a lemma it does not hold."""
        return [form.decode() for form in datastore.trie(FORMS).get(_ye(lemma.lower()), [])]
