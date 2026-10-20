"""The project: where it is (the folder with `.rb_semkit/`), its config file, its own folders of word lists and
workflows, and the config's load, save and check against the installed CLI version.

`check_project_compat` is the version gate of `output.guard` (all commands but `output.UNGATED`): the project at or
above a folder must not need a newer CLI than the installed one.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w
from packaging.version import Version

from .errors import CliTooOld, ConfigInvalid, ProjectNotInitialized
from .models import ProjectConfig
from .version import installed_version

# Derived at import time from this package's own name, so this module never
# needs template substitution: it just works under whatever package_name
# the project was generated with.
_PACKAGE_NAME = __name__.split(".")[0]
PROJECT_DIR_NAME = f".{_PACKAGE_NAME}"
CONFIG_FILE_NAME = "config.toml"
LISTS_DIR_NAME = "lists"
WORKFLOWS_DIR_NAME = "workflows"
OLD_WORKFLOWS_DIR_NAME = "scenarios"  # the former name of the folder, still read


def find_project_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / PROJECT_DIR_NAME).is_dir():
            return candidate
    return None


def require_project_root(start: Path) -> Path:
    root = find_project_root(start)
    if root is None:
        raise ProjectNotInitialized(str(start))
    return root


def config_path(project_root: Path) -> Path:
    return project_root / PROJECT_DIR_NAME / CONFIG_FILE_NAME


def project_lists_dir(project_root: Path) -> Path:
    """The folder of the project's own word lists (`semkit lists add` puts them here)."""
    return project_root / PROJECT_DIR_NAME / LISTS_DIR_NAME


def project_workflows_dir(project_root: Path) -> Path:
    """The folder of the project's own workflows (`semkit run NAME`)."""
    return project_root / PROJECT_DIR_NAME / WORKFLOWS_DIR_NAME


def project_old_workflows_dir(project_root: Path) -> Path:
    """The former folder of the project's workflows, still read so that saved files keep running."""
    return project_root / PROJECT_DIR_NAME / OLD_WORKFLOWS_DIR_NAME


def check_cli_compat(config: ProjectConfig) -> None:
    """Raise CliTooOld if this installed CLI is older than the project's `cli.min_version`.

    A project outlives any single CLI release; this is how it refuses to be
    driven by a CLI that predates a config field or command it relies on.
    Skipped for an uninstalled (bare source) run, which has no version, and
    for a build without a `v*` tag in reach (uv-dynamic-versioning's
    `0.0.0` fallback) — a dev checkout, not a release older than anything.
    """
    installed = installed_version()
    if installed is None or Version(installed).release == (0, 0, 0):
        return
    if Version(installed) < Version(config.cli.min_version):
        raise CliTooOld(installed, config.cli.min_version)


def check_project_compat(start: Path) -> None:
    """Raise CliTooOld when the project at or above `start` needs a newer CLI; outside a project there is no check."""
    root = find_project_root(start)
    if root is not None:
        check_cli_compat(load_config(root))


def load_config(project_root: Path) -> ProjectConfig:
    """Load and validate the project config; a file that is not a config raises ConfigInvalid.

    The CLI version the config needs is checked once per command line, by `output.guard` (check_project_compat).
    """
    path = config_path(project_root)
    try:
        return ProjectConfig.model_validate(tomllib.loads(path.read_text()))
    except (OSError, ValueError) as exc:  # TOMLDecodeError and ValidationError are ValueError
        raise ConfigInvalid(str(path), str(exc)) from exc


def save_config(project_root: Path, config: ProjectConfig) -> None:
    path = config_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tomli_w.dumps(config.model_dump()))


def init_project(project_root: Path, name: str, *, dry_run: bool = False) -> ProjectConfig:
    """The config of a new project; written to `project_root` unless `dry_run`."""
    config = ProjectConfig(name=name)
    if not dry_run:
        save_config(project_root, config)
    return config
