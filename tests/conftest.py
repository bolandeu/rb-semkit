"""Shared fixtures: a test sees only the word lists it sets up, never the ones of the machine it runs on; the steps by
meaning get a small deterministic encoder in place of the real models, and the steps by words (synonym-candidates,
relate-phrases) a small thesaurus and small word vectors, so no test downloads or loads a real one.

A test marked `real_encoder` gets the models as semkit opens them: the vectors extra, the cache, the model files. Those
tests share one xdist group, so one worker holds the models, and each model is opened once per worker.
"""

from __future__ import annotations

import os
import subprocess
import sys
import zlib
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path

import numpy as np
import pytest

CONTRACT_TESTS = "test_contracts.py"

PLAIN_HELP_ENV = {"NO_COLOR": "1", "TERM": "dumb", "COLUMNS": "100"}
CI_ENV_NAMES = ("FORCE_COLOR", "CI", "GITHUB_ACTIONS", "TTY_COMPATIBLE", "TTY_INTERACTIVE")

# The consoles of rb_semkit read the environment when they are built, at import: set it before the imports below.
os.environ.update(PLAIN_HELP_ENV)
for _name in CI_ENV_NAMES:
    os.environ.pop(_name, None)

from rb_semkit.core.vectors import encoder  # noqa: E402
from rb_semkit.core.vectors.registry import Model  # noqa: E402
from rb_semkit.core.word_vectors import navec, thesaurus  # noqa: E402
from rb_semkit.core.word_vectors.navec import WordVectors  # noqa: E402
from rb_semkit.steps import word_vectors  # noqa: E402

# Typer reads these once, at import, and then forces terminal output — what a CI runner sets.
CI_ENV = {"GITHUB_ACTIONS": "true", "FORCE_COLOR": "1", "PY_COLORS": "1"}

WORD_DIMENSIONS = 64

# The most xdist workers: the real models are ~2.4 GB and a gate may run beside other gates on a 16 GB machine.
MAX_WORKERS = 3
WORKERS_ENV = "PYTEST_XDIST_AUTO_NUM_WORKERS"
REAL_MODELS_GROUP = "real_models"


class WordEncoder:
    """The test encoder: a phrase is the sum of its words, each word a fixed random vector (seeded by the word).

    Phrases of the same words get the same vector, phrases that share words close ones, phrases of other words far
    ones; the same phrase gives the same vector in every run.
    """

    def encode(self, phrases: Sequence[str]) -> np.ndarray:
        vectors = np.zeros((len(phrases), WORD_DIMENSIONS), dtype=np.float32)
        for row, phrase in enumerate(phrases):
            for word in phrase.lower().split():
                vectors[row] += np.random.default_rng(zlib.crc32(word.encode())).standard_normal(WORD_DIMENSIONS)
        lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.where(lengths == 0, 1, lengths)


def _once(name: str, opened: Callable, cache: dict, folder_at: int) -> Callable:
    """`opened` that returns the object it made for the same folder (its argument number `folder_at`) instead of
    opening it again."""

    def cached(*arguments):
        key = (name, arguments[folder_at])
        if key not in cache:
            cache[key] = opened(*arguments)
        return cache[key]

    return cached


@pytest.fixture(scope="session", autouse=True)
def _real_models_opened_once() -> Iterator[None]:
    """The real encoders, the thesaurus and the word vectors are opened once per worker, whichever test asks, by the
    folder they are read from: a model pulled into another folder is another object."""
    opened: dict = {}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(navec, "load", _once("navec", navec.load, opened, 0))
        patch.setattr(thesaurus, "load", _once("thesaurus", thesaurus.load, opened, 0))
        runtimes = {name: _once(name, runtime, opened, 1) for name, runtime in encoder.RUNTIMES.items()}
        patch.setattr(encoder, "RUNTIMES", runtimes)
        yield


@pytest.fixture(autouse=True)
def _no_machine_word_lists(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SEMKIT_LISTS", raising=False)


@pytest.fixture(autouse=True)
def _plain_help_in_any_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Help renders without colour and at one width, whatever the CI of the machine sets."""
    for name, value in PLAIN_HELP_ENV.items():
        monkeypatch.setenv(name, value)
    for name in CI_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def _test_encoder(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.node.get_closest_marker("real_encoder"):
        return

    def opened(model: Model, start: Path) -> WordEncoder:
        return WordEncoder()

    monkeypatch.setattr(encoder, "encoder_for", opened)


@pytest.fixture(autouse=True)
def _test_word_data(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """A thesaurus where диван and чехол are synonyms, and so are растаможка and таможенное оформление, and word vectors where they are close."""
    if request.node.get_closest_marker("real_encoder"):
        return
    words = ["<unk>", "<pad>", "диван", "чехол"]
    codes = np.array([[[0, 0], [0, 0], [1, 0], [0.8, 0.6]]], dtype=np.float32)
    vectors = WordVectors(words, np.arange(len(words), dtype=np.uint8).reshape(-1, 1), codes)
    monkeypatch.setattr(
        thesaurus,
        "open_thesaurus",
        lambda start: thesaurus.Thesaurus(
            [
                ("1", "ДИВАН", "ДИВАН"),
                ("1", "ЧЕХОЛ", "ЧЕХОЛ"),
                ("2", "РАСТАМОЖКА", "РАСТАМОЖКА"),
                ("2", "ТАМОЖЕННОЕ ОФОРМЛЕНИЕ", "ТАМОЖЕННЫЙ ОФОРМЛЕНИЕ"),
            ]
        ),
    )
    monkeypatch.setattr(word_vectors, "open_word_vectors", lambda start: vectors)


@pytest.fixture
def same_in_ci(request: pytest.FixtureRequest) -> Callable[[str], None]:
    """Rerun this file's tests matching `-k` under CI_ENV in a fresh interpreter: the only way to set a value read at import."""
    if request.config.getoption("--snapshot-update"):
        pytest.skip("the snapshots are being written; there is nothing to compare yet")

    def run(selection: str) -> None:
        options = ["-k", selection, "-p", "no:cacheprovider", "--no-cov", "-q"]
        command = [sys.executable, "-m", "pytest", str(request.path), *options]
        env = {**os.environ, **CI_ENV}
        result = subprocess.run(command, env=env, capture_output=True, text=True, check=False)  # noqa: S603
        assert result.returncode == 0, result.stdout[-3000:]

    return run


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """A run of the contract tests alone stays serial: the gate reads their `-vv` lines, and xdist prints them in
    another shape (`[gw0] [ 50%] PASSED tests/...`), so it would count no case."""
    args = [Path(arg.split("::")[0]).name for arg in config.args]
    if args and set(args) == {CONTRACT_TESTS}:
        config.option.numprocesses = 0
        config.option.dist = "no"


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_auto_num_workers(config: pytest.Config) -> int:
    """`-n auto` runs at most MAX_WORKERS workers, and fewer when the environment asks for fewer (Antagor sets the
    variable so that parallel runs share the machine)."""
    asked = os.environ.get(WORKERS_ENV)
    return min(MAX_WORKERS, int(asked)) if asked else MAX_WORKERS


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """The tests that open the real models share one xdist group (`--dist loadgroup`): one worker holds the models."""
    for item in items:
        if item.get_closest_marker("real_encoder"):
            item.add_marker(pytest.mark.xdist_group(REAL_MODELS_GROUP))
