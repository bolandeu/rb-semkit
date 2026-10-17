"""Words by part of speech, through a Lemmatizer (the bundled one unless another is given)."""

from __future__ import annotations

from collections.abc import Callable

from ...morph import Lemmatizer
from ...morph.functions import BUNDLED
from ...morph.lemmatizer import looks_like_adjective
from ..base import WordMatcher, choice

CODES = {"noun": "n", "verb": "v", "adverb": "advb"}
# `··o` (line 1439): a word with one of these codes is no adjective, whatever its lemma looks like
NOT_ADJECTIVES = frozenset({"n", "v", "advb", "p", "prep", "conj", "nv"})
KINDS = ("noun", "adj", "verb", "adverb")


class Pos(WordMatcher):
    def __init__(self, kind: str, lemmatizer: Lemmatizer | None) -> None:
        self._lemmatizer = lemmatizer or BUNDLED
        self._test: Callable[[str], bool] = (
            self._is_adjective if choice("kind", kind, KINDS) == "adj" else self._has_code(CODES[kind])
        )

    def _has_code(self, code: str) -> Callable[[str], bool]:
        return lambda word: self._lemmatizer.pos(word.lower()) == code

    def _is_adjective(self, word: str) -> bool:
        """`··o`: the code «a»; else, but for the codes of NOT_ADJECTIVES, a lemma that ends like an adjective.

        The add-in looks the word up as written, so a word with a capital has no code and goes to the lemma rule.
        """
        code = self._lemmatizer.pos(word) if word == word.lower() else ""
        if code == "a":
            return True
        return code not in NOT_ADJECTIVES and looks_like_adjective(self._lemmatizer.lemma(word.lower()))

    def picks(self, words: list[str]) -> list[bool]:
        return [self._test(word) for word in words]


def pos(kind: str, *, lemmatizer: Lemmatizer | None = None) -> Pos:
    """Words of one part of speech: "noun", "adj", "verb" or "adverb" (a participle is none of them).

    A word is looked up as written, with its punctuation («диван,» is not a noun). An adjective is a word coded «a»,
    or a word with no code, a pronoun or a particle whose lemma ends like an adjective («какой»); a word with a
    capital is looked up by that rule only («Быстро» is an adjective, as in the add-in).
    lemmatizer: what gives the part of speech and the lemma of a word; None is the bundled !SEMTools dictionary.

    VBA (RibbonCallbacks.vba):
        find: `—k–a` (line 2266) noun, `–···` (line 2909) adj, `—k—·` (line 2494) verb, `—kkk` (line 1663) adverb.
        remove: `ak··` (line 2642) noun, `—··a` (line 2697) adj, `ao——` (line 1897) verb, `—···` (line 2563) adverb.
        extract: `–ao·` (line 2891) noun, `–—o—` (line 1948) adj, `–·ka` (line 2246) verb, `–—oa` (line 2480) adverb.
        The tests of a word: `··–` (line 2207) noun, `··o` (line 1439) adj, `·ok` (line 1344) verb, `oa–` (line 2154)
        adverb; the verb endings of `·ok` are in the bundled lemmatizer.
    ADR 0005: split on any whitespace; ё = е in the lookup.
    """
    return Pos(kind, lemmatizer)
