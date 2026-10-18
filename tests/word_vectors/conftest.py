"""The word data tests: a small RuWordNet and a small navec, written here and served as the pulled files.

The thesaurus: диван and софа (and тахта, and a phrase) are one synset; кресло is another; the customs senses are
there for the phrases (a sense is the synset, the name and, when it differs, the lemma). The word vectors have two
numbers a word, of length 1: диван (1, 0), софа and софы (0.8, 0.6), тахта (0.6, 0.8), кресло (0, 1), so the cosine of
диван and софа is 0.8, of диван and тахта 0.6, of диван and кресло 0.
"""

from __future__ import annotations

import dataclasses
import gzip
import hashlib
import io
import sqlite3
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rb_semkit.core.vectors import registry, source

from ..vectors.conftest import LocalSource, models_dir  # noqa: F401  (a fixture the tests use)

SENSES: list[tuple[str, ...]] = [
    ("1-N", "ДИВАН"),
    ("1-N", "СОФА"),
    ("1-N", "ТАХТА"),
    ("1-N", "МЯГКАЯ МЕБЕЛЬ"),
    ("2-N", "КРЕСЛО"),
    ("3-N", "РАСТАМОЖКА"),
    ("3-N", "РАСТАМОЖИВАНИЕ"),
    ("3-N", "РАСТАМАЖИВАТЬ"),
    ("3-N", "ТАМОЖЕННОЕ ОФОРМЛЕНИЕ", "ТАМОЖЕННЫЙ ОФОРМЛЕНИЕ"),
    ("3-N", "ТАМОЖЕННАЯ ОЧИСТКА", "ТАМОЖЕННЫЙ ОЧИСТКА"),
    ("3-N", "ТАМОЖЕННОЕ ОФОРМЛЕНИЕ ТОВАРОВ", "ТАМОЖЕННЫЙ ОФОРМЛЕНИЕ ТОВАР"),
    ("3-N", "ОФОРМИТЬ НА ТАМОЖНЕ", "ОФОРМИТЬ НА ТАМОЖНЯ"),
    ("5-N", "РАСТАМОЖКА"),
    ("5-N", "РАСТАМАЖИВАТЬ"),
    ("6-N", "ТРАНСПОРТНОЕ СРЕДСТВО", "ТРАНСПОРТНЫЙ СРЕДСТВО"),
    ("6-N", "СРЕДСТВО ПЕРЕДВИЖЕНИЯ", "СРЕДСТВО ПЕРЕДВИЖЕНИЕ"),
    ("6-N", "ТРАНСПОРТ"),
    ("7-N", "ДИЗАЙН"),
    ("7-N", "ОФОРМЛЕНИЕ"),
    ("8-N", "ЗИМА ЛЕТО"),
    ("8-N", "ВЕСНА"),
    ("9-N", "ЛЕТО ОСЕНЬ"),
    ("9-N", "ЗАКАТ"),
]
VECTORS = {
    "<unk>": (0.0, 0.0),
    "<pad>": (0.0, 0.0),
    "диван": (1.0, 0.0),
    "софа": (0.8, 0.6),
    "софы": (0.8, 0.6),
    "тахта": (0.6, 0.8),
    "кресло": (0.0, 1.0),
}
THESAURUS_FILE, NAVEC_FILE = "ruwordnet-2021.db", "navec_test.tar"
CORE = ["диван", "софа", "кресло"]


def thesaurus_bytes(directory: Path) -> bytes:
    """A RuWordNet file with the senses `SENSES`."""
    path = directory / "ruwordnet.db"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE sense (id VARCHAR, name VARCHAR, lemma VARCHAR, synset_id VARCHAR)")
        connection.executemany(
            "INSERT INTO sense VALUES (?, ?, ?, ?)",
            [
                (f"{synset}-{number}", name, lemma, synset)
                for number, (synset, name, *lemma) in enumerate(SENSES)
                for lemma in [lemma[0] if lemma else name]
            ],
        )
    connection.close()
    return path.read_bytes()


def navec_bytes() -> bytes:
    """A navec pack with the words `VECTORS`: one part a word, a centroid for each word."""
    words = list(VECTORS)
    vocab = np.array([len(words)], np.uint32).tobytes() + np.zeros(len(words), np.uint32).tobytes()
    vocab += "\n".join(words).encode("utf-8")
    codes = np.array([[VECTORS[word] for word in words]], np.float32)
    quantized = np.array([len(words), 2, 1, len(words)], np.uint32).tobytes()
    quantized += np.arange(len(words), dtype=np.uint8).reshape(-1, 1).tobytes() + codes.tobytes()
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as pack:
        for name, content in (("vocab.bin", gzip.compress(vocab)), ("pq.bin", quantized)):
            member = tarfile.TarInfo(name)
            member.size = len(content)
            pack.addfile(member, io.BytesIO(content))
    return buffer.getvalue()


@pytest.fixture
def words_hub(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> LocalSource:
    """The registry pins the two small files; the source serves them from a folder."""
    (tmp_path / "hub" / "test").mkdir(parents=True)
    files = {"ruwordnet": (THESAURUS_FILE, thesaurus_bytes(tmp_path)), "navec": (NAVEC_FILE, navec_bytes())}
    bundled = registry.bundled()
    models = dict(bundled.models)
    for name, (path, content) in files.items():
        (tmp_path / "hub" / "test" / name).mkdir()
        (tmp_path / "hub" / "test" / name / path).write_bytes(content)
        checksum = {path: hashlib.sha256(content).hexdigest()}
        models[name] = dataclasses.replace(bundled.models[name], repo=f"test/{name}", files=checksum)
    monkeypatch.setattr(registry, "bundled", lambda: dataclasses.replace(bundled, models=models))
    local = LocalSource(tmp_path / "hub")
    monkeypatch.setattr(source, "SOURCE", local)
    return local


@pytest.fixture
def core_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, models_dir: Path) -> Path:  # noqa: F811
    """The core: a phrase a word, with a stopword, a number and a word the data lack."""
    path = tmp_path / "core.csv"
    pd.DataFrame({"phrase": [*CORE, "кресло в москве", "диван 2020"]}).to_csv(path, index=False)
    return path
