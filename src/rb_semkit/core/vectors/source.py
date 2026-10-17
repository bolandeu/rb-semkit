"""Where `models pull` gets the files of a model (`SOURCE`): the Hugging Face hub for an encoder, an address for word
data.

A source resolves a model (a hub model gets the hub's latest revision, its runtime, pooling and files) and downloads
its files into a folder; whatever it raises stops the pull.
"""

from __future__ import annotations

import dataclasses
import json
import shutil
import urllib.request
from pathlib import Path
from typing import Protocol

from ..errors import InvalidArguments
from . import registry
from .registry import ENCODERS, Model, Pooling

ONNX_FILES = ("onnx/model.onnx", "model.onnx")
STATIC_FILES = ("config.json", "model.safetensors", "tokenizer.json")
POOLING_FILE = "1_Pooling/config.json"  # the sentence-transformers pooling of a model
STATIC_LIBRARY = "model2vec"


class Source(Protocol):
    def resolve(self, model: Model) -> Model: ...

    def download(self, model: Model, into: Path) -> None: ...


class HubSource:
    """The Hugging Face hub; a pinned model is fetched at its revision, a hub model at the latest one."""

    def resolve(self, model: Model) -> Model:
        if model.revision is not None:
            return model
        from huggingface_hub import HfApi

        info = HfApi().model_info(model.repo)
        names = {sibling.rfilename for sibling in info.siblings or []}
        found = next((name for name in ONNX_FILES if name in names), None)
        beside = f"{found.rpartition('/')[0]}/tokenizer.json" if found else None
        tokenizer = next((name for name in (beside, "tokenizer.json") if name in names), None)
        if found is not None and tokenizer is not None:
            pooling = self._pooling(model.repo, info.sha) if POOLING_FILE in names else model.pooling
            files = dict.fromkeys([found, tokenizer], "")
            return dataclasses.replace(model, revision=info.sha, runtime="onnx", pooling=pooling, files=files)
        if info.library_name == STATIC_LIBRARY and set(STATIC_FILES) <= names:
            return dataclasses.replace(
                model, revision=info.sha, runtime="static", files=dict.fromkeys(STATIC_FILES, "")
            )
        raise InvalidArguments(
            f"model={model.name!r}: the repo has no ONNX export ({' or '.join(ONNX_FILES)}, with tokenizer.json) and is"
            " no model2vec model;"
            " allowed: a model with one of them."
        )

    def download(self, model: Model, into: Path) -> None:
        from huggingface_hub import hf_hub_download

        for path in model.files:
            hf_hub_download(model.repo, path, revision=model.revision, local_dir=into)
        shutil.rmtree(into / ".cache", ignore_errors=True)  # the hub's notes on the download

    @staticmethod
    def _pooling(repo: str, revision: str | None) -> Pooling:
        from huggingface_hub import HfFileSystem

        config = json.loads(HfFileSystem().read_text(f"{repo}/{POOLING_FILE}", revision=revision))
        return "cls" if config.get("pooling_mode_cls_token") else "mean"


class UrlSource:
    """Word data: each file is at `<repo>/<path>`; the address is pinned by the checksum of the file."""

    def resolve(self, model: Model) -> Model:
        return model

    def download(self, model: Model, into: Path) -> None:
        for path in model.files:
            (into / path).parent.mkdir(parents=True, exist_ok=True)
            with (
                urllib.request.urlopen(f"{model.repo}/{path}", timeout=registry.bundled().words.timeout) as response,  # noqa: S310
                (into / path).open("wb") as file,
            ):
                shutil.copyfileobj(response, file)


class RoutedSource:
    """An encoder from the hub, word data from its address."""

    hub, url = HubSource(), UrlSource()

    def resolve(self, model: Model) -> Model:
        return self._of(model).resolve(model)

    def download(self, model: Model, into: Path) -> None:
        self._of(model).download(model, into)

    def _of(self, model: Model) -> Source:
        return self.hub if model.runtime in ENCODERS else self.url


SOURCE: Source = RoutedSource()
