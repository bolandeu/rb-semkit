"""Tests of the CLI as a whole: the distribution name, root and group help, the output layer's errors and exit codes,
and the built-in commands.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import pytest
import typer
import yaml
from typer.testing import CliRunner

from rb_semkit import output
from rb_semkit._distribution import DIST_NAME
from rb_semkit.cli import app
from rb_semkit.core import errors, services, skills
from rb_semkit.core.errors import InvalidArguments

runner = CliRunner()


def invoke(*args: str, **kwargs):
    return runner.invoke(app, list(args), **kwargs)


def plain(text: str) -> str:
    """The text without ANSI colour codes: CI forces Rich colours the Mac does not."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def invoke_json(*args: str, **kwargs) -> tuple[int, dict]:
    """Run a command with --json and parse stdout — the contract agents rely on."""
    result = invoke(*args, "--json", **kwargs)
    assert result.stdout.strip(), f"no stdout for {args!r}; stderr: {result.stderr}"
    return result.exit_code, json.loads(result.stdout)


def init(tmp_path: Path, name: str = "demo") -> None:
    assert invoke("--project", str(tmp_path), "init", "--name", name).exit_code == 0


# --- names ----------------------------------------------------------------------


def test_distribution_name_is_declared_once() -> None:
    """Only _distribution.py assigns DIST_NAME; a merge that re-declares it elsewhere would silently win."""
    src = Path(__file__).resolve().parents[1] / "src" / "rb_semkit"
    declaring = sorted(
        str(path.relative_to(src))
        for path in src.rglob("*.py")
        if re.search(r"^DIST_NAME\s*[:=]", path.read_text(), re.M)
    )
    assert declaring == ["_distribution.py"]


def test_version_falls_back_to_legacy_distribution_name(monkeypatch: pytest.MonkeyPatch) -> None:
    from rb_semkit.core import version

    installed = version.installed_version()
    monkeypatch.setattr(version, "DIST_NAME", "no-such-distribution-xyz")
    monkeypatch.setattr(version, "DIST_NAME_LEGACY", DIST_NAME)  # an install made under the old name
    assert version.installed_version() == installed
    monkeypatch.setattr(version, "DIST_NAME_LEGACY", None)
    assert version.installed_version() is None


def test_distribution_name_matches_pyproject() -> None:
    """_distribution.DIST_NAME is how importlib.metadata finds this package; it must equal [project] name."""
    pyproject = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
    assert pyproject["project"]["name"] == DIST_NAME


def test_install_section_matches_copier_answers() -> None:
    """[tool.rb.install] is rendered from the copier answers: users split on commas, mac as a bool.

    extras is not a copier answer: a hand-added one only has to be a list of strings.
    """
    root = Path(__file__).resolve().parents[1]
    install = tomllib.loads((root / "pyproject.toml").read_text())["tool"]["rb"]["install"]
    answers = yaml.safe_load((root / ".copier-answers.yml").read_text())
    users = [name.strip() for name in answers["install_homeserver_users"].split(",") if name.strip()]
    assert install["homeserver"] == users
    assert install["mac"] is answers["install_mac"]
    extras = install.get("extras", [])
    assert isinstance(extras, list) and all(isinstance(extra, str) for extra in extras)


# --- help-on-no-args -------------------------------------------------------


def test_bare_invocation_shows_help_and_exits_zero() -> None:
    result = invoke()
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_bare_group_shows_help_and_exits_zero() -> None:
    result = invoke("auth")
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Missing command" not in result.output


def test_init_help_names_the_project_folder_by_the_package() -> None:
    result = invoke("init", "--help")
    assert result.exit_code == 0
    assert ".rb_semkit/config.toml" in result.output


# --- doctor ------------------------------------------------------------------


def test_doctor_json(tmp_path: Path) -> None:
    code, payload = invoke_json("--project", str(tmp_path), "doctor")
    assert code == 1  # unhealthy: the report is still the output
    names = [check["name"] for check in payload["checks"]]
    assert names[:2] == ["python", "cli_version"]
    assert payload["healthy"] is all(check["ok"] for check in payload["checks"])


def test_doctor_prints_one_line_per_check_for_a_human(tmp_path: Path) -> None:
    result = invoke("--project", str(tmp_path), "doctor")
    assert result.exit_code == 1  # unhealthy: no project here
    assert plain(result.stdout).splitlines()[0] == "✓ python"


# --- error handling contract ---------------------------------------------------


def _app_with(command):
    """A throwaway app with the real ctx.obj plumbing, for exercising output.guard."""
    test_app = typer.Typer()

    @test_app.callback()
    def _root(
        ctx: typer.Context,
        json_output: bool = output.JsonOption,
        verbose: bool = output.VerboseOption,
        non_interactive: bool = output.NonInteractiveOption,
    ) -> None:
        ctx.ensure_object(dict)
        ctx.obj["json"] = json_output
        ctx.obj["verbose"] = verbose
        ctx.obj["non_interactive"] = non_interactive

    test_app.command("cmd")(output.guard(command))
    return test_app


def test_error_message_and_action_in_square_brackets_reach_stderr_whole() -> None:
    def fail(ctx: typer.Context) -> None:
        raise errors.CliError("PATH_NOT_FOUND", "[library] path not found", action="use [a-z0-9-]")

    result = runner.invoke(_app_with(fail), ["cmd"])
    assert result.exit_code == 1
    assert "[library] path not found" in plain(result.stderr)
    assert "use [a-z0-9-]" in plain(result.stderr)


def test_verbose_line_in_square_brackets_reaches_stderr_whole() -> None:
    def progress(ctx: typer.Context) -> None:
        output.vecho(ctx, "step [1/3] of [a-z0-9-]")

    result = runner.invoke(_app_with(progress), ["--verbose", "cmd"])
    assert "step [1/3] of [a-z0-9-]" in plain(result.stderr)


@pytest.mark.parametrize(
    ("error", "code", "exit_code"),
    [
        (errors.InvalidArguments("bad"), "INVALID_ARGUMENTS", 2),
        (errors.AuthRequired("demo"), "AUTH_REQUIRED", 3),
        (errors.CredentialsUnhealthy({"demo": "invalid"}), "CREDENTIALS_UNHEALTHY", 3),
        (errors.ProjectNotInitialized("/work"), "PROJECT_NOT_INITIALIZED", 4),
        (errors.ProviderError("demo", "down", status=503), "PROVIDER_ERROR", 5),
        (errors.DatabaseUnavailable("down"), "DATABASE_UNAVAILABLE", 5),
        (errors.CliTooOld("1.0.0", "2.0.0"), "CLI_TOO_OLD", 6),
        (errors.DatabaseTooNew("0009"), "CLI_TOO_OLD", 6),
        (errors.DatabaseNotMigrated(None, "0002"), "DATABASE_NOT_MIGRATED", 1),
        (errors.DependencyTooOld("serp", None, "0.3"), "DEPENDENCY_TOO_OLD", 1),
        (errors.CredentialStoreUnavailable("demo", "locked"), "CREDENTIAL_STORE_UNAVAILABLE", 1),
        (errors.Aborted("Delete everything"), "ABORTED", 1),
    ],
    ids=lambda value: type(value).__name__ if isinstance(value, errors.CliError) else None,
)
def test_each_error_has_the_code_and_exit_code_of_the_standard(
    error: errors.CliError, code: str, exit_code: int
) -> None:
    """The error codes table of the Standard (Errors): the code in the envelope and the exit code."""
    payload = error.to_dict()
    assert (payload["code"], error.exit_code) == (code, exit_code)
    assert payload["message"]


def test_report_with_a_problem_keeps_the_payload() -> None:
    """output.emit_report: data plus ok=false + error, exit code from the problem (auth status uses it)."""

    def report(ctx: typer.Context) -> None:
        render = lambda d: output.human.echo(f"items: {d['items']}")  # noqa: E731
        output.emit_report(ctx, {"items": [1]}, render, InvalidArguments("bad"))

    result = runner.invoke(_app_with(report), ["--json", "cmd"])
    payload = json.loads(result.stdout)
    assert (result.exit_code, payload["ok"], payload["items"], payload["error"]["code"]) == (
        2,
        False,
        [1],
        "INVALID_ARGUMENTS",
    )
    result = runner.invoke(_app_with(report), ["cmd"])
    assert result.exit_code == 2
    assert "items: [1]" in plain(result.stdout)
    assert "bad" in result.stderr


def test_unexpected_exception_still_yields_json_envelope() -> None:
    def boom(ctx: typer.Context) -> None:
        raise RuntimeError("kaboom")

    result = runner.invoke(_app_with(boom), ["--json", "cmd"])
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "UNEXPECTED"
    assert "kaboom" in payload["error"]["message"]
    assert "Traceback" not in result.stdout


def test_unexpected_exception_prints_traceback_only_with_verbose() -> None:
    def boom(ctx: typer.Context) -> None:
        raise RuntimeError("kaboom")

    quiet = runner.invoke(_app_with(boom), ["cmd"])
    assert quiet.exit_code == 1
    assert "Traceback" not in quiet.stderr
    assert "kaboom" in quiet.stderr  # human error goes to stderr, not stdout
    assert quiet.stdout == ""

    loud = runner.invoke(_app_with(boom), ["--verbose", "cmd"])
    assert "Traceback" in loud.stderr or "RuntimeError" in loud.stderr


@pytest.mark.parametrize(
    "args",
    [
        ("doctor", "--json", "--no-such-option"),
        ("--json", "--no-such-option"),
        ("--json", "auth", "status", "--provider"),
    ],
)
def test_usage_error_under_json_is_the_error_envelope(args: tuple[str, ...]) -> None:
    """An unknown option or a missing value (Click's usage errors) under --json: the envelope on stdout, exit 2."""
    result = invoke(*args)
    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert (payload["ok"], payload["error"]["code"]) == (False, "INVALID_ARGUMENTS")
    assert payload["error"]["message"]


def test_usage_error_without_json_stays_on_stderr() -> None:
    result = invoke("doctor", "--no-such-option")
    assert result.exit_code == 2
    assert result.stdout == ""
    assert "--no-such-option" in plain(result.stderr)


def test_require_confirmation_blocks_non_interactive_without_confirm() -> None:
    def destroy(ctx: typer.Context, confirm: bool = output.ConfirmOption) -> None:
        output.require_confirmation(ctx, "Delete everything", confirm=confirm)
        print("destroyed")

    blocked = runner.invoke(_app_with(destroy), ["--json", "--non-interactive", "cmd"])
    assert blocked.exit_code == 2
    assert json.loads(blocked.stdout)["error"]["code"] == "INVALID_ARGUMENTS"

    # --confirm bypasses the prompt/non-interactive check entirely.
    allowed = runner.invoke(_app_with(destroy), ["--non-interactive", "cmd", "--confirm"])
    assert allowed.exit_code == 0
    assert "destroyed" in allowed.stdout


def test_declined_confirmation_is_a_structured_abort() -> None:
    def destroy(ctx: typer.Context) -> None:
        output.require_confirmation(ctx, "Delete everything", confirm=False)
        raise AssertionError("must not get here")

    result = runner.invoke(_app_with(destroy), ["--json", "cmd"], input="n\n")
    assert result.exit_code == 1
    # The prompt itself precedes the envelope on stdout; the envelope is the last line.
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["error"]["code"] == "ABORTED"


# --- skill ---------------------------------------------------------------------


def test_skill_install_writes_to_project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    code, payload = invoke_json("skill", "install", "--tool", "claude-code", "--project")
    assert code == 0
    installed = tmp_path / ".claude" / "skills" / "semkit" / "SKILL.md"
    assert installed.is_file()
    assert "name: semkit" in installed.read_text()
    assert payload["path"] == str(installed)


def test_skill_install_without_extra_skills_writes_only_the_conventions_skill(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    code, payload = invoke_json("skill", "install", "--tool", "claude-code", "--project")
    assert code == 0
    assert set(payload) == {"ok", "tool", "scope", "path", "dry_run"}
    assert [p.parent.name for p in (tmp_path / ".claude" / "skills").glob("*/SKILL.md")] == ["semkit"]


@pytest.fixture
def extra_skills(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A package data dir holding the conventions skill and two extra skills."""
    data = tmp_path / "pkgdata"
    data.mkdir()
    (data / "SKILL.md").write_text("---\nname: semkit\ndescription: Conventions.\n---\n")
    for name, description in {"og-image": "Make og images.", "video": "Make videos."}.items():
        (data / "skills" / name).mkdir(parents=True)
        (data / "skills" / name / "SKILL.md").write_text(f"---\nname: semkit-{name}\ndescription: {description}\n---\n")
    monkeypatch.setattr(skills, "_data", lambda: data)
    return data


def test_skill_install_writes_every_bundled_skill_into_its_own_directory(
    extra_skills: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    code, payload = invoke_json("skill", "install", "--tool", "claude-code", "--project")
    assert code == 0
    names = ("semkit", "semkit-og-image", "semkit-video")
    expected = [work / ".claude" / "skills" / name / "SKILL.md" for name in names]
    assert all(path.is_file() for path in expected)
    assert payload["paths"] == [str(path) for path in expected]
    assert payload["path"] == str(expected[0])


def test_skill_install_one_skill_by_short_or_full_name(
    extra_skills: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    for wanted in ("video", "semkit-video"):
        code, payload = invoke_json("skill", "install", "--project", "--skill", wanted)
        assert code == 0
        assert "paths" not in payload
    assert [p.parent.name for p in (work / ".claude" / "skills").glob("*/SKILL.md")] == ["semkit-video"]


def test_skill_install_unknown_skill_names_the_bundled_ones(
    extra_skills: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    code, payload = invoke_json("skill", "install", "--project", "--skill", "nope")
    assert code == 2
    assert payload["error"]["code"] == "INVALID_ARGUMENTS"
    assert "semkit, semkit-og-image, semkit-video" in payload["error"]["message"]


def test_skill_list_and_describe_show_the_same_skills(extra_skills: Path) -> None:
    expected = [
        {"name": "semkit", "description": "Conventions."},
        {"name": "semkit-og-image", "description": "Make og images."},
        {"name": "semkit-video", "description": "Make videos."},
    ]
    code, payload = invoke_json("skill", "list")
    assert code == 0
    assert payload["skills"] == expected
    human = invoke("skill", "list").stdout
    assert "semkit-video: Make videos." in human
    described = json.loads(invoke("describe", "--json").stdout)
    meta = {item["name"]: item["value"] for item in described["command"]["metadata"]}
    assert meta["x-rb-skills"] == expected


# --- auth status without credentials (every CLI has it) ----------


def test_auth_status_without_credentials_is_empty_and_healthy() -> None:
    for args in (("auth", "status"), ("auth", "status", "--check")):
        code, payload = invoke_json(*args)
        assert code == 0
        assert list(payload) == ["ok", "tool", "version", "checked_at", "credentials"]
        assert payload["credentials"] == []
        assert payload["checked_at"].endswith("Z")
    code, payload = invoke_json("auth", "status", "--provider", "x")
    assert (code, payload["error"]["code"]) == (2, "INVALID_ARGUMENTS")
    assert invoke("auth", "login").exit_code == 2  # no such command without credentials
    assert "stores no credentials" in invoke("auth", "status").stdout


# --- SEMKIT-033: top-level commands ----------------------------------------------


def _config_text(project: Path) -> str:
    return services.config_path(project).read_text()


def test_dry_run_config_set_leaves_the_config_unchanged(tmp_path: Path) -> None:
    init(tmp_path)
    before = _config_text(tmp_path)

    code, payload = invoke_json("--dry-run", "--project", str(tmp_path), "config", "set", "name", "x")

    assert (code, payload["dry_run"], payload["value"]) == (0, True, "x")
    assert _config_text(tmp_path) == before


def test_dry_run_init_creates_nothing(tmp_path: Path) -> None:
    code, payload = invoke_json("--dry-run", "--project", str(tmp_path), "init", "--name", "demo")

    assert (code, payload["dry_run"], payload["project"]) == (0, True, "demo")
    assert list(tmp_path.iterdir()) == []


def test_init_takes_dry_run_after_the_command(tmp_path: Path) -> None:
    code, payload = invoke_json("--project", str(tmp_path), "init", "--dry-run")

    assert (code, payload["dry_run"]) == (0, True)
    assert list(tmp_path.iterdir()) == []


def test_dry_run_skill_install_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    code, payload = invoke_json("--dry-run", "skill", "install", "--project")

    assert (code, payload["dry_run"]) == (0, True)
    assert list(tmp_path.iterdir()) == []


def test_dry_run_lists_add_and_rm_change_no_file(tmp_path: Path) -> None:
    init(tmp_path)
    source = tmp_path / "items.txt"
    source.write_text("один\n", encoding="utf-8")
    kept = services.project_lists_dir(tmp_path) / "kept.txt"
    kept.parent.mkdir(parents=True)
    kept.write_text("два\n", encoding="utf-8")

    added = invoke_json("--dry-run", "--project", str(tmp_path), "lists", "add", "new", str(source))
    removed = invoke_json("--dry-run", "--project", str(tmp_path), "lists", "rm", "kept")

    assert [(code, payload["dry_run"]) for code, payload in (added, removed)] == [(0, True), (0, True)]
    assert sorted(path.name for path in kept.parent.iterdir()) == ["kept.txt"]


def _pin_installed(monkeypatch: pytest.MonkeyPatch, version: str) -> None:
    monkeypatch.setattr(services, "installed_version", lambda: version)


def test_config_set_lowers_min_version_the_project_needs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _pin_installed(monkeypatch, "0.1.5")
    init(tmp_path)
    assert invoke("--project", str(tmp_path), "config", "set", "cli.min_version", "0.2.0").exit_code == 0

    result = invoke("--project", str(tmp_path), "config", "set", "cli.min_version", "0.1.0")

    assert result.exit_code == 0, result.output
    assert services.load_config(tmp_path).cli.min_version == "0.1.0"


def _table(tmp_path: Path) -> Path:
    path = tmp_path / "core.csv"
    path.write_text("phrase\nдиван\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    "args",
    [("status",), ("lists",), ("describe",), ("read", "{table}", "write", "{out}")],
    ids=["status", "lists", "describe", "read-without-lists"],
)
def test_the_version_gate_stops_every_command(
    args: tuple[str, ...], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _pin_installed(monkeypatch, "1.0.0")
    init(tmp_path)
    invoke("--project", str(tmp_path), "config", "set", "cli.min_version", "99.0.0")
    filled = [arg.format(table=_table(tmp_path), out=tmp_path / "out.csv") for arg in args]

    result = invoke("--json", "--project", str(tmp_path), *filled)  # global --json: the pipeline ends with write OUT

    assert (result.exit_code, json.loads(result.stdout)["error"]["code"]) == (6, "CLI_TOO_OLD")
    assert not (tmp_path / "out.csv").exists()


def test_config_set_lists_takes_a_json_list(tmp_path: Path) -> None:
    init(tmp_path)

    code, _ = invoke_json("--project", str(tmp_path), "config", "set", "lists", '["/abs", "~/lists"]')

    assert code == 0
    assert tomllib.loads(_config_text(tmp_path))["lists"] == ["/abs", "~/lists"]


@pytest.mark.parametrize(
    ("key", "value"),
    [("version", "abc"), ("lists", "/abs"), ("lists", "[1, 2]"), ("cli.min_version", "abc"), ("cli", "x")],
)
def test_config_set_refuses_a_bad_value_with_the_accepted_format(key: str, value: str, tmp_path: Path) -> None:
    init(tmp_path)
    before = _config_text(tmp_path)

    code, payload = invoke_json("--project", str(tmp_path), "config", "set", key, value)

    assert (code, payload["error"]["code"]) == (2, "INVALID_ARGUMENTS")
    assert "allowed:" in payload["error"]["message"]
    assert _config_text(tmp_path) == before


def test_init_help_names_the_folder_init_creates(tmp_path: Path) -> None:
    init(tmp_path)

    created = [path.name for path in tmp_path.iterdir()]

    assert created == [services.PROJECT_DIR_NAME]
    assert f"{services.PROJECT_DIR_NAME}/config.toml" in invoke("init", "--help", env={"COLUMNS": "200"}).stdout


def _write_list(folder: Path, name: str, text: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.txt").write_text(text, encoding="utf-8")


def _items(*args: str) -> list[str]:
    code, payload = invoke_json("lists", "show", *args)
    assert code == 0, payload
    return payload["items"]


def test_a_relative_semkit_lists_is_from_the_current_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init(tmp_path)
    here = tmp_path / "sub"
    _write_list(here / "mine", "a", "из текущей\n")
    monkeypatch.chdir(here)
    monkeypatch.setenv("SEMKIT_LISTS", "mine")

    assert _items("a") == ["из текущей"]


def test_semkit_lists_wins_over_the_config_lists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    init(tmp_path)
    _write_list(tmp_path / "from-config", "a", "config\n")
    _write_list(tmp_path / "from-env", "a", "env\n")
    config = services.load_config(tmp_path)
    config.lists = [str(tmp_path / "from-config")]
    services.save_config(tmp_path, config)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SEMKIT_LISTS", str(tmp_path / "from-env"))

    assert _items("a") == ["env"]


def test_lists_add_to_a_folder_outside_the_search_warns(tmp_path: Path) -> None:
    source = tmp_path / "items.txt"
    source.write_text("один\n", encoding="utf-8")
    elsewhere = tmp_path / "elsewhere"

    result = invoke("--project", str(tmp_path), "lists", "add", "a", str(source), "--to", str(elsewhere))

    assert result.exit_code == 0, result.output
    assert (elsewhere / "a.txt").is_file()
    assert "SEMKIT_LISTS" in result.stderr


def test_lists_add_to_a_searched_folder_does_not_warn(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "items.txt"
    source.write_text("один\n", encoding="utf-8")
    monkeypatch.setenv("SEMKIT_LISTS", str(tmp_path / "mine"))

    result = invoke("--project", str(tmp_path), "lists", "add", "a", str(source), "--to", str(tmp_path / "mine"))

    assert (result.exit_code, result.stderr) == (0, "")


def test_lists_show_takes_the_leading_at() -> None:
    assert _items("@minus/free") == _items("minus/free")


def test_lists_show_of_an_unknown_name_exits_2() -> None:
    code, payload = invoke_json("lists", "show", "@no/such-list")

    assert (code, payload["error"]["code"]) == (2, "INVALID_ARGUMENTS")


def test_lists_help_names_only_commands_that_exist() -> None:
    lists_group = typer.main.get_command(app).commands["lists"]  # ty: ignore[unresolved-attribute]
    help_text = invoke("lists", "--help", env={"COLUMNS": "200"}).stdout

    assert set(re.findall(r"`semkit lists (\w+)", help_text)) <= set(lists_group.commands)
    assert "lists list" not in help_text


def test_quiet_keeps_the_items_of_lists_show() -> None:
    result = invoke("--quiet", "lists", "show", "minus/free")

    assert result.stdout.splitlines() == _items("minus/free")


@pytest.mark.parametrize("command", ["status", "doctor"])
def test_quiet_keeps_the_result(command: str, tmp_path: Path) -> None:
    init(tmp_path)

    loud = invoke("--project", str(tmp_path), command)
    quiet = invoke("--quiet", "--project", str(tmp_path), command)

    assert (quiet.exit_code, quiet.stdout) == (0, loud.stdout)


def test_doctor_unhealthy_exits_1_and_keeps_the_report(tmp_path: Path) -> None:
    code, payload = invoke_json("--project", str(tmp_path), "doctor")

    assert (code, payload["ok"], payload["healthy"], payload["error"]["code"]) == (1, False, False, "UNHEALTHY")
    assert [check["name"] for check in payload["checks"] if not check["ok"]] == ["project"]


def test_doctor_healthy_exits_0(tmp_path: Path) -> None:
    init(tmp_path)

    code, payload = invoke_json("--project", str(tmp_path), "doctor")

    assert (code, payload["ok"], payload["healthy"]) == (0, True, True)


def test_run_is_shown() -> None:
    assert not typer.main.get_command(app).commands["run"].hidden  # ty: ignore[unresolved-attribute]


def test_version_json_is_an_envelope() -> None:
    result = invoke("--version", "--json")

    assert result.exit_code == 0
    assert list(json.loads(result.stdout)) == ["ok", "version"]


@pytest.mark.parametrize(
    "args",
    [("status",), ("config", "list"), ("config", "get", "name"), ("lists",), ("lists", "show", "minus/free"),
     ("doctor",), ("init",)],
    ids=lambda args: "-".join(args),
)  # fmt: skip
def test_every_success_envelope_opens_with_ok(args: tuple[str, ...], tmp_path: Path) -> None:
    init(tmp_path, name="проект")

    code, payload = invoke_json("--project", str(tmp_path), *args)
    result = invoke("--project", str(tmp_path), *args, "--json")

    assert (code, next(iter(payload)), payload["ok"]) == (0, "ok", True)
    assert "\\u04" not in result.stdout
