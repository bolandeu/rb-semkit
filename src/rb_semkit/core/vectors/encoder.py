"""The encoder: phrases in, their phrase vectors out, float32 rows of length 1, in batches.

`encoder_for(model, start)` opens a model pulled into the cache; it downloads nothing. An ONNX model runs in
onnxruntime (no torch): the tokens of each phrase, with the prefix the model needs («query: » for e5), are pooled by
their mean or by the first token. A static model (model2vec) averages the vectors of its tokens.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

import numpy as np

from . import cache, extra, registry
from .registry import Model


class Encoder(Protocol):
    def encode(self, phrases: Sequence[str]) -> np.ndarray:
        """The vector of each phrase: a float32 array of one row per phrase, each row of length 1."""
        ...


def normalized(vectors: np.ndarray) -> np.ndarray:
    """The rows as float32 of length 1; a row of zeros stays zeros."""
    lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
    return (vectors / np.where(lengths == 0, 1, lengths)).astype(np.float32)


class OnnxEncoder:
    """An ONNX export of a transformer: its tokenizer.json and model.onnx in the folder of the model."""

    def __init__(self, model: Model, folder: Path, batch: int) -> None:
        import onnxruntime
        from tokenizers import Tokenizer

        paths = {Path(path).name: folder / path for path in model.files}
        self.model, self.batch = model, batch
        self.tokenizer = Tokenizer.from_file(str(paths["tokenizer.json"]))
        self.tokenizer.enable_truncation(model.max_tokens)
        self.tokenizer.enable_padding()
        self.session = onnxruntime.InferenceSession(str(paths["model.onnx"]), providers=["CPUExecutionProvider"])
        self.inputs = {given.name for given in self.session.get_inputs()}

    def encode(self, phrases: Sequence[str]) -> np.ndarray:
        # Phrases of close length go in one batch: less padding. The rows come back in the order of the phrases.
        order = np.argsort([len(phrase) for phrase in phrases], kind="stable")
        batches = [order[start : start + self.batch] for start in range(0, len(order), self.batch)]
        if not batches:
            return np.zeros((0, 0), dtype=np.float32)
        vectors = np.vstack([self._batch([phrases[row] for row in rows]) for rows in batches])
        restored = np.empty_like(vectors)
        restored[order] = vectors
        return restored

    def _batch(self, phrases: list[str]) -> np.ndarray:
        encoded = self.tokenizer.encode_batch([self.model.prefix + phrase for phrase in phrases])
        ids = np.array([item.ids for item in encoded], dtype=np.int64)
        mask = np.array([item.attention_mask for item in encoded], dtype=np.int64)
        feed = {"input_ids": ids, "attention_mask": mask, "token_type_ids": np.zeros_like(ids)}
        tokens = np.asarray(
            self.session.run(None, {name: value for name, value in feed.items() if name in self.inputs})[0]
        )
        if self.model.pooling == "cls":
            return normalized(tokens[:, 0])
        return normalized((tokens * mask[..., None]).sum(axis=1) / mask.sum(axis=1, keepdims=True))


class StaticEncoder:
    """A model2vec model: a vector per token, a phrase is their mean."""

    def __init__(self, model: Model, folder: Path, batch: int) -> None:
        from model2vec import StaticModel

        self.model, self.batch = model, batch
        self.static = StaticModel.from_pretrained(folder)

    def encode(self, phrases: Sequence[str]) -> np.ndarray:
        prefixed = [self.model.prefix + phrase for phrase in phrases]
        return normalized(self.static.encode(prefixed, batch_size=self.batch, show_progress_bar=False))


RUNTIMES = {"onnx": OnnxEncoder, "static": StaticEncoder}


def encoder_for(model: Model, start: Path) -> Encoder:
    """The encoder of `model` as pulled into the cache of the project at or above `start`.

    It refuses when the vectors extra is not installed (VectorsNotInstalled) or the model is not in the cache
    (ModelNotPulled, with the command that pulls it).
    """
    extra.require()
    pulled = cache.pulled_model(model, start)
    return RUNTIMES[pulled.model.runtime](pulled.model, pulled.folder, registry.bundled().batch)
