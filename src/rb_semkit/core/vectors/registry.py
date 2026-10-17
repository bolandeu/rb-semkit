"""The encoders semkit knows, by short name, and the settings of the steps by meaning: the package settings file
`data/vectors/models.toml` (`bundled()`).

`model(name)` takes a short name (e5-small, bge-m3, potion) or `hf:<id>` of any model of the Hugging Face hub; an
unknown name is refused with the names it takes. `threshold(model, given)` is the similarity a step by meaning uses.
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

Runtime = Literal["onnx", "static"]
Pooling = Literal["mean", "cls"]


@dataclass(frozen=True)
class Model:
    """An encoder as `models pull` fetches it and a step opens it.

    files: the path of each file in the repo and its sha256; an empty checksum is not pinned (a hub model).
    revision: None for a hub model until it is pulled (the hub's latest revision); its runtime is known only then.
    threshold: None for a hub model: a step needs --threshold.
    """

    name: str
    repo: str
    revision: str | None
    runtime: Runtime
    pooling: Pooling
    prefix: str
    max_tokens: int
    threshold: float | None
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
class Registry:
    default: str
    models: Mapping[str, Model]
    index: IndexSettings
    batch: int
    max_tokens: int  # of a hub model


@functools.cache
def bundled() -> Registry:
    """The package settings file, read once."""
    values = tomllib.loads((datastore.DATA_DIR / SETTINGS).read_text(encoding="utf-8"))
    models = {name: Model(name=name, **entry) for name, entry in values["models"].items()}
    encoder = values["encoder"]
    return Registry(values["default"], models, IndexSettings(**values["index"]), **encoder)


def default_name() -> str:
    return bundled().default


def model(name: str) -> Model:
    """The encoder of `name`: a short name of the registry, or hf:<id> of a model of the hub."""
    known = bundled().models
    if name in known:
        return known[name]
    repo = name.removeprefix(HUB)
    if name.startswith(HUB) and repo.count("/") == 1 and all(repo.split("/")):
        return Model(name, repo, None, "onnx", "mean", "", bundled().max_tokens, None)
    raise InvalidArguments(f"model={name!r}: no such encoder; allowed: {', '.join([*known, HUB_FORM])}.")


def threshold(model: Model, given: float | None) -> float:
    """`given`, or the default threshold of the model; a similarity from 0 to 1."""
    if given is None:
        if model.threshold is None:
            raise InvalidArguments(
                f"threshold: not given, and {model.name} has no default threshold; allowed: a number from 0 to 1."
            )
        return model.threshold
    if not 0 <= given <= 1:
        raise InvalidArguments(f"threshold={given!r}; allowed: a number from 0 to 1.")
    return given
