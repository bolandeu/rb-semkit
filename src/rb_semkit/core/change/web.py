"""Changes of URLs and texts for the web: UTM tags removed or extracted, hashes."""

from __future__ import annotations

import hashlib
import re
from urllib.parse import unquote_plus

import pandas as pd

from ..text.base import choice
from .common import changed

__all__ = ["extract_utm", "hash_text", "remove_utm"]

UTM_PREFIX = "utm_"
TAGS = ("source", "medium", "campaign", "term", "content")
ALGORITHMS = ("md5", "sha256")
QUERY, PARAMETER, FRAGMENT = "?", "&", "#"


def _without_utm(url: str) -> str:
    head, hash_mark, fragment = url.partition(FRAGMENT)
    path, question_mark, query = head.partition(QUERY)
    if not question_mark:
        return url
    kept = [item for item in query.split(PARAMETER) if item and not item.lower().startswith(UTM_PREFIX)]
    return path + (QUERY + PARAMETER.join(kept) if kept else "") + hash_mark + fragment


def remove_utm(
    data: pd.Series | pd.DataFrame, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The URL without its UTM tags, the parameters whose name starts with «utm_» in any case:
    «https://site.ru/?UTM_Source=ya&utm_medium=cpc&id=5#top» → «https://site.ru/?id=5#top». The rest of the query
    stays after one «?» and between single «&»; with no parameter left, the «?» goes too."""
    return changed(data, _without_utm, "remove_utm", column, inplace)


def extract_utm(
    data: pd.Series | pd.DataFrame, tag: str, *, column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The value of the UTM tag `tag` (source, medium, campaign, term, content) of the URL, URL-decoded:
    «?utm_source=%D0%AF%D0%BD%D0%B4%D0%B5%D0%BA%D1%81» → «Яндекс», «+» as a space. The name counts in any case; the
    first tag of that name wins; no such tag gives an empty string."""
    choice("tag", tag, TAGS)
    pattern = re.compile(rf"(?:^|[?&#]){UTM_PREFIX}{tag}=([^&#]*)", re.IGNORECASE)

    def value(url: str) -> str:
        found = pattern.search(url)
        return unquote_plus(found[1]) if found else ""

    return changed(data, value, "extract_utm", column, inplace)


def hash_text(
    data: pd.Series | pd.DataFrame, *, algorithm: str = "md5", column: str | None = None, inplace: bool = False
) -> pd.Series | pd.DataFrame:
    """The hash of the text as lower-case hex, of its UTF-8 bytes: algorithm "md5" or "sha256". An empty text has a
    hash too (md5 «d41d8cd98f00b204e9800998ecf8427e»)."""
    choice("algorithm", algorithm, ALGORITHMS)
    return changed(
        data,
        lambda text: hashlib.new(algorithm, text.encode("utf-8"), usedforsecurity=False).hexdigest(),
        "hash_text",
        column,
        inplace,
    )
