"""The repo's own tooling scripts: the parts of their logic that decide what the gate demands."""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
from pathlib import Path
from types import ModuleType

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_antagor_project_config() -> None:
    import tomllib

    root = SCRIPTS.parent
    config = tomllib.loads((root / ".agents" / "antagor" / "antagor.toml").read_text())
    assert config["schema"] == 1
    # The prefix is the Plane project identifier: the product's full name in capitals (`antagor new`).
    assert re.fullmatch(r"[A-Z][A-Z0-9]{1,11}", config["prefix"])
    assert config["worker"] == "claude-code"
    tag = yaml.safe_load((root / ".copier-answers.yml").read_text())["_commit"]
    gate = (
        'uvx --from "git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git'
        f'@{tag}#subdirectory=gate" rb-release check'
    )
    assert config["checks"] == ["python3 scripts/check_command_docstrings.py", gate]
    assert config["review"]["required_types"] == ["feature", "bugfix"]
    expected = {"versioning": "semver", "changelog": "CHANGELOG.md", "deploy_command": "sh scripts/deploy.sh"}
    assert {k: config["publish"].get(k) for k in expected} == expected  # Antagor may add its own keys
    # The Human sets the mode (`antagor mode set`, `antagor new --mode`).
    assert config.get("mode") in (None, "strict", "default", "free", "fast")
    ignored = (root / ".agents" / "antagor" / ".gitignore").read_text().split()
    assert {"state/", "receipts/"} <= set(ignored)  # Antagor may add its own lines
    assert "ANTAGOR_VERSION" in (SCRIPTS / "deploy.sh").read_text()


def test_antagor_layout() -> None:
    # The method's layout: AGENTS.md holds pointers only, the rules live in their own files (`antagor layout check` runs in check_template.sh).
    root = SCRIPTS.parent
    for name in ("AGENTS.md", "CLAUDE.md", "CONTEXT.md", "CODING_STANDARDS.md", "docs/adr/README.md"):
        assert (root / name).is_file(), name
    agents = (root / "AGENTS.md").read_text()
    for pointer in ("`CONTEXT.md`", "`docs/adr/`", "`CODING_STANDARDS.md`", "`.agents/antagor/`"):
        assert pointer in agents
    for moved in ("TDD", "hand fix", "--dry-run", "expand/contract"):
        assert moved not in agents, moved
    assert "AGENTS.md" in (root / "CLAUDE.md").read_text()
    context = (root / "CONTEXT.md").read_text()
    assert re.fullmatch(r"# \S.*", context.splitlines()[0])
    assert re.search(r"^\*\*[^*]+\*\*:$", re.sub(r"<!--.*?-->", "", context, flags=re.DOTALL), re.MULTILINE)
    readme = (root / "README.md").read_text()
    assert "install_hooks" not in readme
    assert "towncrier" not in readme


def test_docstring_check_reads_the_working_tree_only() -> None:
    import inspect

    check = _load("check_command_docstrings")
    assert list(inspect.signature(check.stale_commands).parameters) == ["paths"]
    assert "index" not in (check.stale_commands.__doc__ or "")


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(  # noqa: S603
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],  # noqa: S607
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def test_env_files_are_ignored(tmp_path: Path) -> None:
    shutil.copy(SCRIPTS.parent / ".gitignore", tmp_path / ".gitignore")
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "i")
    (tmp_path / ".env").write_text("TOKEN=x\n")
    (tmp_path / ".env.local").write_text("TOKEN=y\n")
    assert _git(tmp_path, "status", "--porcelain", "--untracked-files=all") == ""


GITEA_INDEX = "https://homeserver.tailee01ab.ts.net:3000/api/packages/bolandeu/pypi/simple"


def test_project_declares_the_gitea_index_explicit() -> None:
    import tomllib

    config = tomllib.loads((SCRIPTS.parent / "pyproject.toml").read_text())
    assert {"name": "gitea", "url": GITEA_INDEX, "explicit": True} in config["tool"]["uv"]["index"]
