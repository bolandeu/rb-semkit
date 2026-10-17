"""Spelling providers: what finds the misspelt words of phrases. CoreSpelling (the default) learns the words from the
phrases themselves; LanguageTool asks a LanguageTool server."""

from __future__ import annotations

import json
import time
import tomllib
from bisect import bisect_right
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields
from itertools import accumulate
from typing import NamedTuple, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .. import datastore
from ..errors import InvalidArguments, ProviderError

__all__ = ["LanguageTool", "LanguageToolSettings", "Misspelling", "SpellingProvider"]

SETTINGS = "corpus/languagetool.toml"


class Misspelling(NamedTuple):
    """A misspelt word of a phrase: where it starts, its length, and its corrections, the most likely first."""

    offset: int
    length: int
    replacements: tuple[str, ...]


class SpellingProvider(Protocol):
    """What finds the misspelt words of phrases: for each phrase, its misspellings ([] when it has none).

    `name` names the provider in its errors. A provider that cannot check every phrase raises: it never returns a
    partial result.
    """

    name: str

    def check(self, phrases: list[str]) -> list[list[Misspelling]]: ...


@dataclass(frozen=True)
class LanguageToolSettings:
    """Where the LanguageTool server is and how to talk to it; `bundled()` reads the package settings file."""

    url: str
    language: str
    rules: str
    timeout: float
    batch_lines: int
    parallel: int
    retries: int
    backoff: float

    @classmethod
    def bundled(cls) -> LanguageToolSettings:
        path = datastore.DATA_DIR / SETTINGS
        values = tomllib.loads(path.read_text(encoding="utf-8"))
        missing = [field.name for field in fields(cls) if field.name not in values]
        if missing:
            raise InvalidArguments(f"{path}: no settings {missing!r}; allowed: a file with every LanguageTool setting.")
        return cls(**{field.name: values[field.name] for field in fields(cls)})


class LanguageTool:
    """A spelling provider that asks a LanguageTool server, `settings` (default: the package settings file).

    The phrases go one per line in batches of `batch_lines`, at most `parallel` requests at once. A request that gets
    a 5xx answer, a timeout or a lost connection is retried after a pause that doubles each time; when the retries run
    out, or the server refuses the request (4xx) or answers what is no check result, the check raises ProviderError.
    """

    name = "languagetool"

    def __init__(self, settings: LanguageToolSettings | None = None) -> None:
        self.settings = settings or LanguageToolSettings.bundled()
        if not self.settings.url.startswith(("http://", "https://")):
            raise InvalidArguments(f"url={self.settings.url!r}; allowed: an http or https URL.")

    def check(self, phrases: list[str]) -> list[list[Misspelling]]:
        size = self.settings.batch_lines
        batches = [phrases[start : start + size] for start in range(0, len(phrases), size)]
        pool = ThreadPoolExecutor(max_workers=self.settings.parallel)
        try:
            return [found for batch in pool.map(self._check_batch, batches) for found in batch]
        finally:
            pool.shutdown(cancel_futures=True)

    def _check_batch(self, phrases: list[str]) -> list[list[Misspelling]]:
        lines = [phrase.replace("\n", " ") for phrase in phrases]
        starts = list(accumulate((len(line) + 1 for line in lines[:-1]), initial=0))
        found: list[list[Misspelling]] = [[] for _ in lines]
        for match in self._post("\n".join(lines)):
            line = bisect_right(starts, match["offset"]) - 1
            replacements = tuple(item["value"] for item in match.get("replacements", ()))
            found[line].append(Misspelling(match["offset"] - starts[line], match["length"], replacements))
        return found

    def _post(self, text: str) -> list[dict]:
        settings = self.settings
        form = {"language": settings.language, "text": text, "enabledRules": settings.rules, "enabledOnly": "true"}
        request = Request(settings.url, data=urlencode(form).encode())  # noqa: S310  # the scheme is checked above
        pause, status, failure = settings.backoff, None, ""
        for attempt in range(settings.retries + 1):
            if attempt:
                time.sleep(pause)
                pause *= 2
            try:
                with urlopen(request, timeout=settings.timeout) as response:  # noqa: S310
                    return self._matches(response.read())
            except HTTPError as error:
                if error.code < 500:
                    raise ProviderError(
                        self.name, f"the server refused the request: HTTP {error.code}", status=error.code
                    ) from None
                failure, status = f"HTTP {error.code}", error.code
            except (TimeoutError, URLError) as error:
                failure = (
                    f"no answer in {settings.timeout:g} s" if isinstance(error, TimeoutError) else str(error.reason)
                )
        raise ProviderError(self.name, f"{failure} after {settings.retries + 1} attempts", status=status)

    def _matches(self, body: bytes) -> list[dict]:
        try:
            return json.loads(body)["matches"]
        except (ValueError, KeyError, TypeError):
            raise ProviderError(self.name, "the answer is no LanguageTool check result") from None
