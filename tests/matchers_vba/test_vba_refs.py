"""Each matcher names, in its docstring, the VBA handlers it ports, with the lines of RibbonCallbacks.vba.

The docstring has a «VBA» section with one entry per verb the matcher supports. A reference is «`handler` (line N)»
or «(lines N–M)», and docs/vba/matchers.md must give that handler the same lines; a verb with no handler says
«no VBA handler: derived from `handler`».
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import rb_semkit as sk

REFERENCE = (Path(__file__).parents[2] / "docs" / "vba" / "matchers.md").read_text(encoding="utf-8")
CITED = re.compile(r"`([^`]+)`\s+\((?:RibbonCallbacks\.vba\s+)?(lines?\s+\d+(?:–\d+)?)\)")
KNOWN = {(name, " ".join(lines.split())) for name, lines in CITED.findall(REFERENCE)}
VERBS = ("find", "remove", "extract")

# One instance of each matcher: its class tells which verbs it supports.
MATCHERS = {
    "chars": sk.chars("latin"),
    "spaces": sk.spaces("extra"),
    "positions": sk.positions(1),
    "around": sk.around("в"),
    "regex": sk.regex("a"),
    "words": sk.words("диван"),
    "word_content": sk.word_content("has_latin"),
    "word_case": sk.word_case("lower"),
    "word_position": sk.word_position(first=1),
    "pos": sk.pos("noun"),
    "repeats": sk.repeats(),
    "stopwords": sk.stopwords(),
    "phrases": sk.phrases(["диван"]),
    "cells": sk.cells("empty"),
    "markers": sk.markers("geo"),
}


def _supported(matcher: sk.Matcher) -> list[str]:
    return [verb for verb in VERBS if getattr(type(matcher), verb) is not getattr(sk.Matcher, verb)]


def _verb_entries(doc: str) -> dict[str, str]:
    """The entries of the «VBA» section by verb: the text from «verb:» up to the next verb or the section end."""
    section = doc.split("VBA (RibbonCallbacks.vba):", 1)[1].split("ADR 0005", 1)[0]
    parts = re.split(r"^\s*(find|remove|extract)(?: \([^)]*\))?:", section, flags=re.MULTILINE)
    return {verb: " ".join(text.split()) for verb, text in zip(parts[1::2], parts[2::2], strict=True)}


@pytest.mark.parametrize("name", MATCHERS)
def test_the_docstring_names_a_handler_for_each_verb(name: str) -> None:
    doc = getattr(sk, name).__doc__ or ""

    assert "VBA (RibbonCallbacks.vba):" in doc
    assert "ADR 0005:" in doc
    entries = _verb_entries(doc)
    for verb in _supported(MATCHERS[name]):
        assert verb in entries, f"{name}: no VBA entry for {verb}"
        assert CITED.search(entries[verb]) or "no VBA handler: derived from" in entries[verb]


@pytest.mark.parametrize("name", MATCHERS)
def test_every_cited_line_is_the_line_of_the_reference(name: str) -> None:
    doc = getattr(sk, name).__doc__ or ""

    cited = {(handler, " ".join(lines.split())) for handler, lines in CITED.findall(doc)}

    assert cited
    assert cited - KNOWN == set()
