"""The repo's own tooling scripts: the parts of their logic that decide what the gate demands."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = _load("release")


def test_release_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    # Independent of this project's own [tool.cli-generator]: defaults, then configured values.
    monkeypatch.setattr(release, "_tool", lambda name: {})
    assert release.gate_extras() == []

    config = {"gate_extras": ["browser"]}
    monkeypatch.setattr(release, "_tool", lambda name: config if name == "cli-generator" else {})
    assert release.gate_extras() == ["browser"]


def test_release_only_checks() -> None:
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPTS / "release.py"), "patch"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 2
    assert "--check" in result.stderr


def test_external_programs_found_by_literal_name() -> None:
    source = """
import shutil, subprocess
from .core import deps
exe = deps.require_cli("serp", "0.3.0")
shutil.which("ffmpeg")
subprocess.run(["npx", "-y", "lighthouse"], check=True)
subprocess.check_output(("git", "rev-parse", "HEAD"))
subprocess.run([exe, "search"])  # built at runtime: covered by require_cli above
"""
    assert release.external_programs(source) == {"serp", "ffmpeg", "npx", "git"}


def test_external_registry_must_match_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "mod.py").write_text('import shutil\nshutil.which("ffmpeg")\n')
    monkeypatch.setattr(release, "ROOT", tmp_path)

    monkeypatch.setattr(release, "_tool", lambda name: {})
    with pytest.raises(release.StepFailed, match=re.escape("`ffmpeg` is run in src/mod.py but not declared")):
        release.check_external_deps()

    registry: dict[str, list[dict[str, object]]] = {
        "external": [{"name": "ffmpeg", "why": "video"}, {"name": "node", "why": "unused"}]
    }
    monkeypatch.setattr(release, "_tool", lambda name: registry if name == "rb" else {})
    with pytest.raises(release.StepFailed, match=re.escape("`node` is declared but nothing in src/ runs it")):
        release.check_external_deps()

    registry["external"][1]["detect"] = False  # run through an injected runner: declared on trust
    assert release.check_external_deps() == "2 declared, all used (1 with detect = false)"

    registry["external"][1]["why"] = ""
    with pytest.raises(release.StepFailed, match="needs `name` and `why`"):
        release.check_external_deps()


OLD_TESTS = """
LIMIT = 3


def helper():
    return 1


def test_a():
    assert helper() == 1


def test_b():
    assert True


class TestGroup:
    def test_c(self):
        assert LIMIT
"""

NEW_TESTS = """
LIMIT = 4


def test_b():
    assert True


def test_a():
    assert helper() == 2


class TestGroup:
    def test_c(self):
        assert LIMIT


def test_new():
    assert True
"""


def test_existing_tests_that_changed() -> None:
    """Changed or removed tests are listed; moved, untouched and new ones aren't."""
    assert release.changed_existing_tests("tests/t.py", OLD_TESTS, NEW_TESTS) == [
        "tests/t.py: module-level code changed",
        "tests/t.py::helper removed",
        "tests/t.py::test_a changed",
    ]
    assert release.changed_existing_tests("tests/t.py", OLD_TESTS, None) == ["tests/t.py removed"]
    assert release.changed_existing_tests("tests/t.py", OLD_TESTS, OLD_TESTS) == []
    assert release.changed_existing_tests("tests/t.py", "def broken(:\n", NEW_TESTS) == ["tests/t.py changed"]


def test_existing_tests_step_reports_against_the_last_tag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)  # noqa: S603, S607

    (tmp_path / "tests" / "snapshots").mkdir(parents=True)
    (tmp_path / "tests" / "test_x.py").write_text(OLD_TESTS)
    (tmp_path / "tests" / "snapshots" / "help.txt").write_text("old\n")
    git("init", "-q", "-b", "main")
    git("add", "-A")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "i")
    git("-c", "user.name=t", "-c", "user.email=t@t", "tag", "-a", "v0.1.0", "-m", "v0.1.0")
    monkeypatch.setattr(release, "ROOT", tmp_path)
    assert release.check_existing_tests() == "none changed since v0.1.0"

    (tmp_path / "tests" / "test_x.py").write_text(NEW_TESTS)
    (tmp_path / "tests" / "snapshots" / "help.txt").write_text("new\n")
    (tmp_path / "tests" / "test_added.py").write_text("def test_z():\n    pass\n")
    detail = release.check_existing_tests()
    assert detail.startswith("4 changed since v0.1.0")
    assert "tests/test_x.py::test_a changed" in detail
    assert "tests/snapshots/help.txt changed" in detail
    assert "test_added" not in detail


CONTRACT_RUN = """
tests/test_contracts.py::test_contract[tools-catalog:describe-json] PASSED [ 25%]
tests/test_contracts.py::test_contract[windmill:search-json] FAILED [ 50%]
tests/test_contracts.py::test_contract[windmill:old-field] SKIPPED (windmill:old-field: provider <0.7) [ 75%]
tests/test_contracts.py::test_contract[astro:pages-view] PASSED [100%]
"""


def test_contract_summary() -> None:
    assert release.contract_summary(CONTRACT_RUN) == "4 cases from 3 consumers: 1 failed, 1 skipped (provider version)"
    assert release.contract_summary("") == "0 cases"
    passed = CONTRACT_RUN.replace("FAILED", "PASSED").replace("SKIPPED (windmill:old-field: provider <0.7)", "PASSED")
    assert release.contract_summary(passed) == "4 cases from 3 consumers"


def test_gate_runs_contracts_as_their_own_step() -> None:
    pytest_step = dict(release.COMMANDS)["pytest"]
    assert "--ignore=tests/test_contracts.py" in pytest_step
    assert release.check_contracts.__name__ == "check_contracts"


def test_antagor_project_config() -> None:
    import tomllib

    root = SCRIPTS.parent
    config = tomllib.loads((root / ".agents" / "antagor" / "antagor.toml").read_text())
    assert config["schema"] == 1
    # The prefix is the Plane project identifier: the product's full name in capitals (`antagor new`).
    assert re.fullmatch(r"[A-Z][A-Z0-9]{1,11}", config["prefix"])
    assert config["worker"] == "claude-code"
    assert config["checks"] == ["python3 scripts/check_command_docstrings.py", "uv run scripts/release.py --check"]
    assert config["review"]["required_types"] == ["feature", "bugfix"]
    expected = {"versioning": "semver", "changelog": "CHANGELOG.md", "deploy_command": "sh scripts/deploy.sh"}
    assert {k: config["publish"].get(k) for k in expected} == expected  # Antagor may add its own keys
    # The Human sets the mode (`antagor mode set`, `antagor new --mode`).
    assert config.get("mode") in (None, "strict", "default", "free", "fast")
    assert (root / ".agents" / "antagor" / ".gitignore").read_text().split() == ["state/", "receipts/"]
    assert "ANTAGOR_VERSION" in (SCRIPTS / "deploy.sh").read_text()


def test_antagor_layout() -> None:
    # The method's layout: AGENTS.md holds pointers only, the rules live in their own files (`antagor layout check` runs in check_template.sh).
    root = SCRIPTS.parent
    for name in ("AGENTS.md", "CLAUDE.md", "CONTEXT.md", "CODING_STANDARDS.md", "docs/adr/README.md"):
        assert (root / name).is_file(), name
    agents = (root / "AGENTS.md").read_text()
    for pointer in ("`CONTEXT.md`", "`docs/adr/`", "`CODING_STANDARDS.md`", "`.agents/antagor/`"):
        assert pointer in agents
    for moved in ("TDD", "--dry-run", "expand/contract"):
        assert moved not in agents, moved
    assert "AGENTS.md" in (root / "CLAUDE.md").read_text()
    context = (root / "CONTEXT.md").read_text()
    assert re.fullmatch(r"# \S.*", context.splitlines()[0])
    assert re.search(r"^\*\*[^*]+\*\*:$", re.sub(r"<!--.*?-->", "", context, flags=re.DOTALL), re.MULTILINE)
    readme = (root / "README.md").read_text()
    assert "antagor publish" in readme
    assert "install_hooks" not in readme
    assert "towncrier" not in readme


def test_docstring_check_reads_the_working_tree_only() -> None:
    import inspect

    check = _load("check_command_docstrings")
    assert list(inspect.signature(check.stale_commands).parameters) == ["paths"]
    assert "index" not in (check.stale_commands.__doc__ or "")
