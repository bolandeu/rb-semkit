"""split_paragraphs: texts into their paragraphs, one row per paragraph.

A paragraph is a block between empty lines, its lines joined by a space; a heading line (a short line without a
sentence end of `text.words`, followed by text) is a paragraph of its own. How short a heading is: the settings file
`data/text/paragraphs.toml`.
"""

from __future__ import annotations

import tomllib

import pandas as pd

from .. import datastore
from ..text.words import SENTENCE_ENDS, text_words

SETTINGS = "text/paragraphs.toml"
COLUMNS = ("url", "number", "paragraph")


def heading_words() -> int:
    """The most words of a heading line, read once."""
    return datastore.once(
        SETTINGS, lambda: tomllib.loads((datastore.DATA_DIR / SETTINGS).read_text(encoding="utf-8"))["heading_words"]
    )


def split_paragraphs(data: pd.Series, *, urls: pd.Series | None = None) -> pd.DataFrame:
    """Texts into their paragraphs: a report of one row per paragraph.

    urls: the url of each text, by the index of `data`; without it the url is empty.

    A paragraph is a block between empty lines; the lines of a block are joined by a space. A heading line (a short
    line without a sentence end: . ! ? …, followed by text) is a paragraph of its own. Spaces at the ends are trimmed;
    an empty text gives no rows. The columns: url, number (from 1 in each text) and paragraph.
    """
    given = pd.Series("", index=data.index) if urls is None else urls.reindex(data.index).fillna("").astype(str)
    rows = [
        (url, number, paragraph)
        for text, url in zip(data.fillna("").astype(str), given, strict=True)
        for number, paragraph in enumerate(_paragraphs(text), 1)
    ]
    return pd.DataFrame(rows, columns=list(COLUMNS)).astype({"url": object, "number": "Int64", "paragraph": object})


def _paragraphs(text: str) -> list[str]:
    """The paragraphs of one text."""
    found: list[str] = []
    block: list[str] = []
    for line in [*text.splitlines(), ""]:
        if line.strip():
            block.append(line.strip())
        elif block:
            found += _block(block)
            block = []
    return found


def _block(lines: list[str]) -> list[str]:
    """The paragraphs of a block of lines: a heading line followed by text is one of its own."""
    found: list[str] = []
    joined: list[str] = []
    for position, line in enumerate(lines):
        if position < len(lines) - 1 and _is_heading(line):
            found += [" ".join(joined), line] if joined else [line]
            joined = []
        else:
            joined.append(line)
    return found + ([" ".join(joined)] if joined else [])


def _is_heading(line: str) -> bool:
    return line[-1] not in SENTENCE_ENDS and len(text_words(line)) <= heading_words()
