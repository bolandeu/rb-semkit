"""The cache of the encoders (ADR 0009): `platformdirs.user_cache_path("semkit")/models`, or the folder of the config key
models.dir (a relative one is from the project). A model is the folder `<cache>/<name>` with its files and the
manifest `semkit-model.json`: the model as it was pulled, with the sha256 of each file.

`pull` downloads into a hidden folder of the cache, checks every checksum and renames the folder into place: a model is
there whole or not at all, and of two pulls at once the first to finish places it. The steps only find a model
(`pulled_model`); they never download one.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

import platformdirs

from ..._distribution import TOOL
from .. import services
from ..errors import CliError, InvalidArguments, ModelNotPulled, PullFailed
from . import extra, registry, source
from .registry import Model

MODELS = "models"
MANIFEST = "semkit-model.json"
CHUNK = 1 << 20


@dataclass(frozen=True)
class Pulled:
    """A model in the cache: as it was pulled, its folder and the bytes of its files; `downloaded` by this pull."""

    model: Model
    folder: Path
    size: int
    downloaded: bool = False


def models_dir(start: Path) -> Path:
    """The cache of the encoders for the project at or above `start`."""
    root = services.find_project_root(start)
    if root is not None and services.config_path(root).is_file():
        configured = services.load_config(root).models.dir
        if configured:
            return root / Path(configured).expanduser()
    return platformdirs.user_cache_path(TOOL) / MODELS


def pulled_model(model: Model, start: Path) -> Pulled:
    """The model in the cache at its pinned revision; ModelNotPulled when it is not there."""
    cache = models_dir(start)
    found = _read(cache / model.folder)
    if found is None or not _current(found, model):
        raise ModelNotPulled(model.name, str(cache))
    return found


def pulled_models(start: Path) -> list[Pulled]:
    """Every model in the cache, by the name of its folder."""
    cache = models_dir(start)
    folders = sorted(cache.iterdir()) if cache.is_dir() else []
    return [found for folder in folders if not folder.name.startswith(".") and (found := _read(folder))]


def catalog(start: Path) -> list[dict]:
    """Each model of the registry, pulled or not, then each hub model pulled: name, repo, revision, pulled, size, path,
    threshold (a model pulled at another revision than the pinned one is not pulled)."""
    extra.require()
    pulled = {found.model.name: found for found in pulled_models(start)}
    known = registry.bundled().models
    entries = []
    for model in [*known.values(), *(found.model for name, found in pulled.items() if name not in known)]:
        found = pulled.get(model.name)
        current = found if found is not None and _current(found, model) else None
        shown = current.model if current is not None else model
        entries.append(
            {
                "name": model.name,
                "repo": shown.repo,
                "revision": shown.revision,
                "pulled": current is not None,
                "size": current.size if current is not None else 0,
                "path": str(current.folder) if current is not None else None,
                "threshold": model.threshold,
            }
        )
    return entries


def pull(name: str, start: Path) -> Pulled:
    """Download the model `name` into the cache, unless it is there at its revision."""
    extra.require()
    model = registry.model(name)
    cache = models_dir(start)
    found = _read(cache / model.folder)
    if found is not None and _current(found, model):
        return found
    cache.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{model.folder}-", dir=cache))
    try:
        resolved = source.SOURCE.resolve(model)
        source.SOURCE.download(resolved, temporary)
        checked = _checked(resolved, temporary)
        (temporary / MANIFEST).write_text(json.dumps(dataclasses.asdict(checked), indent=1), encoding="utf-8")
        return _place(temporary, cache / model.folder, checked)
    except CliError:
        raise
    except Exception as error:  # the hub, the network, the disk: whatever stopped the download
        raise PullFailed(model.name, str(error) or type(error).__name__) from error
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def remove(name: str, start: Path, *, dry_run: bool = False) -> Pulled:
    """Remove the model `name` from the cache; one not pulled is refused with the pulled ones."""
    extra.require()
    model = registry.model(name)
    found = _read(models_dir(start) / model.folder)
    if found is None:
        pulled = ", ".join(entry.model.name for entry in pulled_models(start)) or "none"
        raise InvalidArguments(f"{name} is not pulled; pulled: {pulled}.", action="Name a pulled model.")
    if not dry_run:
        shutil.rmtree(found.folder)
    return found


def _read(folder: Path) -> Pulled | None:
    """The model in `folder` by its manifest; None when the folder holds none."""
    try:
        model = Model(**json.loads((folder / MANIFEST).read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):  # no manifest, not JSON, not a model
        return None
    size = sum(path.stat().st_size for path in folder.rglob("*") if path.is_file() and path.name != MANIFEST)
    return Pulled(model, folder, size)


def _current(found: Pulled, model: Model) -> bool:
    """Whether the pulled copy is the one `model` pins: its revision (any revision of a hub model)."""
    return model.revision is None or found.model.revision == model.revision


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def _checked(model: Model, folder: Path) -> Model:
    """The model with the checksum of each downloaded file; a file that differs from its pinned checksum is refused."""
    found = {path: _sha256(folder / path) for path in model.files}
    for path, pinned in model.files.items():
        if pinned and found[path] != pinned:
            raise PullFailed(model.name, f"{path}: its checksum {found[path]} differs from the pinned {pinned}")
    return dataclasses.replace(model, files=found)


def _place(temporary: Path, folder: Path, model: Model) -> Pulled:
    """Rename the downloaded folder into place; a copy another pull placed first is kept, a stale one replaced."""
    try:
        temporary.rename(folder)
    except OSError:
        found = _read(folder)
        if found is not None and _current(found, model):
            return found
        stale = folder.with_name(f".{folder.name}-{uuid.uuid4().hex}")
        folder.rename(stale)
        temporary.rename(folder)
        shutil.rmtree(stale, ignore_errors=True)
    return dataclasses.replace(_read(folder) or Pulled(model, folder, 0), downloaded=True)
