"""The words left out of the counts of a text: the words with a digit and a list of the Human's words."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..errors import InvalidArguments
from ..normalize import norm_phrase


@dataclass(frozen=True)
class Skip:
    """Which words a count leaves out, as if the text did not hold them.

    A word is left out when it holds a digit (`no_digits`) or is one of `exclude`: compared as written with case and
    ё folded, not by lemma.
    """

    no_digits: bool = False
    exclude: frozenset[str] = frozenset()

    @classmethod
    def of(cls, no_digits: object, exclude: object) -> Skip:
        """The words to leave out, from the arguments of a function; anything else raises InvalidArguments."""
        if not isinstance(no_digits, bool):
            raise InvalidArguments(f"no_digits={no_digits!r}; allowed: True or False.")
        if (
            isinstance(exclude, str)
            or not isinstance(exclude, Iterable)
            or not all(isinstance(w, str) for w in exclude)
        ):
            raise InvalidArguments(f"exclude={exclude!r}; allowed: a list of words.")
        return cls(no_digits, frozenset(norm_phrase(word) for word in exclude))

    @property
    def active(self) -> bool:
        return self.no_digits or bool(self.exclude)

    def kept(self, words: list[str]) -> list[str]:
        """The words that stay, in order."""
        return [word for word in words if not self._leaves(word)]

    def _leaves(self, word: str) -> bool:
        return (self.no_digits and any(char.isdigit() for char in word)) or norm_phrase(word) in self.exclude
