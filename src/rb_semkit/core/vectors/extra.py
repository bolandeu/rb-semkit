"""The optional extra rb-semkit[vectors]: the modules the encoders, the index and the pull import, and the command
that installs semkit with it."""

from __future__ import annotations

import importlib

from packaging.version import Version

from ..._distribution import DIST_NAME
from ..errors import VectorsNotInstalled
from ..version import installed_version, repository_url

MODULES = ("faiss", "huggingface_hub", "model2vec", "onnxruntime", "tokenizers")
NAME = "vectors"
ANY_TAG = "vX.Y.Z"  # a build that is no release: the Human puts the latest release tag


def require() -> None:
    """Refuse, with the install command, when a module of the extra cannot be imported."""
    for module in MODULES:
        try:
            importlib.import_module(module)
        except ImportError:
            raise VectorsNotInstalled(module, install_command()) from None


def install_command() -> str:
    """`uv tool install` of this release of semkit with the extra."""
    version = installed_version()
    released = version is not None and str(Version(version)) == Version(version).base_version
    tag = f"v{version}" if released else ANY_TAG
    return f'uv tool install --force "{DIST_NAME}[{NAME}] @ git+{repository_url()}.git@{tag}"'
