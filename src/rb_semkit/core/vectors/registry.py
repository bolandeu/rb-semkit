"""The models semkit knows, by short name, and the settings of the steps by meaning: the package settings file
`data/vectors/models.toml` (`bundled()`).

A model is an encoder (e5-small, bge-m3, potion) or word data (ruwordnet, navec), pulled into the same cache.
`model(name)` takes a short name or `hf:<id>` of any encoder of the Hugging Face hub; an unknown name is refused with
the names it takes. `encoder(name)` is the same for a step by meaning: word data is refused there.
`threshold(model, given)` is the similarity a step by meaning uses; `cluster_threshold(model, given)` the same for the
steps that cluster by meaning.
"""

from __future__ import annotations

import functools
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from .. import datastore
from ..errors import InvalidArguments

SETTINGS = "vectors/models.toml"
HUB = "hf:"
HUB_FORM = "hf:<id>"

Runtime = Literal["onnx", "static", "thesaurus", "word-vectors"]
ENCODERS = ("onnx", "static")  # the runtimes of an encoder; the others are word data
Pooling = Literal["mean", "cls"]


@dataclass(frozen=True)
class Model:
    """A model as `models pull` fetches it and a step opens it.

    repo: the repo of the Hugging Face hub; for word data, the address its files are fetched from, as `<repo>/<path>`.
    files: the path of each file in the repo and its sha256; an empty checksum is not pinned (a hub model).
    revision: None for a hub model until it is pulled (the hub's latest revision); its runtime is known only then.
    pooling, prefix, max_tokens, threshold: of an encoder. The threshold is None for a hub model: a step needs
    --threshold. cluster_threshold: the default of the steps that cluster by meaning; None takes the threshold.
    """

    name: str
    repo: str
    revision: str | None
    runtime: Runtime
    pooling: Pooling = "mean"
    prefix: str = ""
    max_tokens: int = 0
    threshold: float | None = None
    cluster_threshold: float | None = None
    files: Mapping[str, str] = field(default_factory=dict)

    @property
    def folder(self) -> str:
        """The name of its folder in the cache: the short name, `hf--org--repo` for a hub model."""
        return self.name.replace(":", "--").replace("/", "--")


@dataclass(frozen=True)
class IndexSettings:
    exact_limit: int
    neighbours: int
    hnsw_links: int
    hnsw_build: int
    hnsw_search: int


@dataclass(frozen=True)
class WordSettings:
    """The settings of the word data. top: the neighbours of a word a step gives. pool: the neighbours looked up for
    each one it gives, as the rest are forms of a word already taken. block: the words compared at once.
    timeout: the seconds a download waits for the address."""

    top: int
    pool: int
    block: int
    timeout: int


@dataclass(frozen=True)
class Registry:
    default: str
    models: Mapping[str, Model]
    index: IndexSettings
    words: WordSettings
    batch: int
    max_tokens: int  # of a hub model


@functools.cache
def bundled() -> Registry:
    """The package settings file, read once."""
    values = tomllib.loads((datastore.DATA_DIR / SETTINGS).read_text(encoding="utf-8"))
    models = {name: Model(name=name, **entry) for name, entry in values["models"].items()}
    encoder = values["encoder"]
    index, words = IndexSettings(**values["index"]), WordSettings(**values["words"])
    return Registry(values["default"], models, index, words, **encoder)


def default_name() -> str:
    return bundled().default


def model(name: str) -> Model:
    """The model of `name`: a short name of the registry, or hf:<id> of an encoder of the hub."""
    known = bundled().models
    if name in known:
        return known[name]
    repo = name.removeprefix(HUB)
    if name.startswith(HUB) and repo.count("/") == 1 and all(repo.split("/")):
        return Model(name, repo, None, "onnx", "mean", "", bundled().max_tokens, None)
    raise InvalidArguments(f"model={name!r}: no such model; allowed: {', '.join([*known, HUB_FORM])}.")


def encoder(name: str) -> Model:
    """The encoder of `name`; word data is refused with the encoders."""
    found = model(name)
    if found.runtime not in ENCODERS:
        names = [known.name for known in bundled().models.values() if known.runtime in ENCODERS]
        raise InvalidArguments(f"model={name!r}: word data, not an encoder; allowed: {', '.join([*names, HUB_FORM])}.")
    return found


def threshold(model: Model, given: float | None) -> float:
    """`given`, or the default threshold of the model; a similarity from 0 to 1."""
    return _checked(model, given, model.threshold)


def cluster_threshold(model: Model, given: float | None) -> float:
    """`given`, or the default threshold of the model for clusters (its threshold when it has none of its own)."""
    return _checked(model, given, model.threshold if model.cluster_threshold is None else model.cluster_threshold)


def _checked(model: Model, given: float | None, default: float | None) -> float:
    if given is None:
        if default is None:
            raise InvalidArguments(
                f"threshold: not given, and {model.name} has no default threshold; allowed: a number from 0 to 1."
            )
        return default
    if not 0 <= given <= 1:
        raise InvalidArguments(f"threshold={given!r}; allowed: a number from 0 to 1.")
    return given
