"""Ready patterns: domains, e-mails, Russian phone numbers and dates, through the three verbs."""

from __future__ import annotations

from typing import NamedTuple

from ..text.base import choice
from ..text.matchers.regex import Regex

__all__ = ["ready_pattern"]


class Ready(NamedTuple):
    pattern: str
    all_matches: bool
    sep: str = " "


READY = {
    "domain": Ready(
        r"(?!-)(?:(?:[a-zA-Z\d][a-zA-Z\d-]{0,61})?[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z\d]{1,63}", all_matches=True
    ),
    "email": Ready(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", all_matches=False),
    "phone": Ready(r"(?:\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}", all_matches=True, sep=", "),
    "date_ddmmyyyy": Ready(r"(?<!\d)[0-3]\d([-./]?)[01]\d\1[12]\d{3}(?!\d)", all_matches=False),
    "date_yyyymmdd": Ready(r"(?<!\d)[12]\d{3}([-./]?)[01]\d\1[0-3]\d(?!\d)", all_matches=False),
}


class ReadyPattern(Regex):
    def __init__(self, kind: str) -> None:
        ready = READY[choice("kind", kind, tuple(READY))]
        super().__init__(ready.pattern, all_matches=ready.all_matches, invert=False)
        self._sep = ready.sep

    def _found(self, phrase: str) -> str:
        matches = [match.group() for match in self._pattern.finditer(phrase)]
        return self._sep.join(matches if self._all else matches[:1])


def ready_pattern(kind: str) -> ReadyPattern:
    """A ready regular expression, found anywhere in a phrase, case-sensitive.

    kind: "domain" (Latin domains with subdomains: «www.example.com»; extract gives all, joined by a space),
    "email" (the first e-mail), "phone" (Russian numbers from +7 or 8: «8 (999) 123-45-67»; all, joined by ", "),
    "date_ddmmyyyy" (the first date as 05.11.2023, 05-11-2023, 05/11/2023 or 05112023) or "date_yyyymmdd" (as
    2023-11-05 … 20231105). A date has the same separator twice, or none, and is never part of a longer number; its
    day and month are not checked (39.19.2999 is found).
    find: the pattern is there. remove: every match is cut out. extract: as above, '' where none.
    """
    return ReadyPattern(kind)
