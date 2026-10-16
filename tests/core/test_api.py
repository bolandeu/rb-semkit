"""The root package: every v1 name maps to its module, loaded on first access."""

from __future__ import annotations

import sys

import pytest

import rb_semkit as sk

CORE_NAMES = (
    "find",
    "remove",
    "extract",
    "pipe",
    "words",
    "Matcher",
    "lemmatize",
    "part_of_speech",
    "wordforms",
    "Lemmatizer",
    "SemtoolsLemmatizer",
    "InvalidArguments",
)


@pytest.mark.parametrize("name", CORE_NAMES)
def test_every_core_name_resolves(name: str) -> None:
    assert getattr(sk, name) is not None
    assert name in dir(sk)


@pytest.mark.parametrize(("name", "module"), [("dupes", "rb_semkit.core.dupes"), ("ngrams", "rb_semkit.core.analysis")])
def test_a_name_of_a_later_block_before_its_module_exists(
    monkeypatch: pytest.MonkeyPatch, name: str, module: str
) -> None:
    monkeypatch.delattr(sk, name, raising=False)  # a module that exists by now was cached on first access
    monkeypatch.setitem(sys.modules, module, None)  # the import system's "no such module"

    with pytest.raises(AttributeError, match=f"rb_semkit.{name}"):
        getattr(sk, name)


@pytest.mark.parametrize(
    "name",
    [
        *("chars", "spaces", "positions", "around", "regex", "word_content", "word_case", "word_position", "pos"),
        *("repeats", "stopwords", "phrases", "cells", "markers", "dupes", "ngrams", "bigrams", "counts"),
    ],
)
def test_every_v1_name_is_listed(name: str) -> None:
    assert name in dir(sk)


def test_an_unknown_name_is_an_attribute_error() -> None:
    with pytest.raises(AttributeError, match="nope"):
        sk.nope  # noqa: B018
