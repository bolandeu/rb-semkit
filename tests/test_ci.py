"""The Gitea Actions workflow, when the project has one (include_ci=true)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".gitea" / "workflows" / "ci.yml"
# adopt_core=true renders no scripts/release.py: the gate is `rb-release check` from rb-cli-core.
ADOPTED_CORE = not (ROOT / "scripts" / "release.py").exists()
GATE = "uv run rb-release check" if ADOPTED_CORE else "uv run scripts/release.py --check"
GATE_STEP = "if [ -f scripts/release.py ]; then uv run scripts/release.py --check; else uv run rb-release check; fi"


def test_no_github_workflow() -> None:
    assert not (ROOT / ".github").exists()


def test_workflow_runs_the_gate_on_the_docker_runner() -> None:
    if not WORKFLOW.exists():
        pytest.skip("include_ci=false: no workflow")
    job = yaml.safe_load(WORKFLOW.read_text())["jobs"]["gate"]
    assert job["runs-on"] == "docker"
    assert "ci-cache:/cache" in job["container"]["volumes"]
    checkout = next(step for step in job["steps"] if str(step.get("uses", "")).startswith("actions/checkout@"))
    assert checkout["with"]["fetch-depth"] == 0
    assert job["steps"][-1]["run"].strip() == GATE_STEP


def _steps() -> list[dict]:
    return yaml.safe_load(WORKFLOW.read_text())["jobs"]["gate"]["steps"]


def test_scanners_are_installed_before_the_gate_at_pinned_versions() -> None:
    if not WORKFLOW.exists():
        pytest.skip("include_ci=false: no workflow")
    steps = _steps()
    gate = next(i for i, step in enumerate(steps) if str(step.get("run", "")).strip() == GATE_STEP)
    scripts = [step["run"] for step in steps[:gate] if "run" in step]
    for tool in ("osv-scanner", "gitleaks"):
        script = next(s for s in scripts if f"/cache/bin/{tool}-" in s)
        urls = re.findall(r"https://github\.com/\S+", script)
        assert urls
        assert all(re.search(r"/download/v\d+\.\d+\.\d+/", url) for url in urls)
        assert "latest" not in script


def test_scanners_are_cached_per_pinned_version() -> None:
    if not WORKFLOW.exists():
        pytest.skip("include_ci=false: no workflow")
    script = next(step["run"] for step in _steps() if "gitleaks" in step.get("run", ""))
    lines = script.splitlines()
    for tool, version in (("osv-scanner", "2.7.0"), ("gitleaks", "8.30.1")):
        cached = f"/cache/bin/{tool}-{version}"
        var = next(line.split("=")[0] for line in lines if line.endswith(f"={cached}"))
        download = next(line for line in lines if line.startswith(f"[ -x ${var} ] ||"))
        assert f"/download/v{version}/" in download
        assert f"ln -sf ${var} /usr/local/bin/{tool}" in lines


def _shell_gate(project: Path) -> str:
    """Run the workflow's gate step in `project` with `uv` replaced by an echo; return what it ran."""
    step = _steps()[-1]["run"]
    bin_dir = project / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text('#!/bin/sh\necho "uv $*"\n')
    uv.chmod(0o755)
    env = {"PATH": f"{bin_dir}:/usr/bin:/bin"}
    return subprocess.run(  # noqa: S603
        ["/bin/sh", "-c", step], cwd=project, env=env, capture_output=True, text=True, check=True
    ).stdout.strip()


def test_gate_step_runs_rb_release_without_the_script(tmp_path: Path) -> None:
    if not WORKFLOW.exists():
        pytest.skip("include_ci=false: no workflow")
    assert _shell_gate(tmp_path) == "uv run rb-release check"


def test_gate_step_runs_the_script_when_present(tmp_path: Path) -> None:
    if not WORKFLOW.exists():
        pytest.skip("include_ci=false: no workflow")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "release.py").write_text("")
    assert _shell_gate(tmp_path) == "uv run scripts/release.py --check"


def test_project_files_name_the_gate_of_their_answer() -> None:
    import tomllib

    checks = tomllib.loads((ROOT / ".agents" / "antagor" / "antagor.toml").read_text())["checks"]
    assert GATE in checks
    assert GATE in (ROOT / "AGENTS.md").read_text()
    # README.md is the project's own (copier skips it on update): not checked here.
    if ADOPTED_CORE:
        for name in (".agents/antagor/antagor.toml", "AGENTS.md", "CODING_STANDARDS.md"):
            assert "scripts/release.py" not in (ROOT / name).read_text(), name
