"""`doctor`: the checks of readiness (Python, CLI version, project, config, credentials, external programs).

The report is printed whether or not a check fails; a failed check makes the exit non-zero (Unhealthy), so a script
can rely on the exit code.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import typer

from .. import output
from ..core import deps, services
from ..core.errors import CliTooOld, ConfigInvalid, Unhealthy
from ..core.models import ProjectConfig
from ..core.version import DEV_VERSION, cli_name, installed_version, module_exists

_PACKAGE_NAME = __name__.split(".")[0]


def _auth_checks(provider: str) -> list[dict]:
    # credentials/ is dropped at generation time when include_auth=false;
    # detecting it at runtime keeps this file free of template logic.
    if not module_exists(f"{_PACKAGE_NAME}.credentials.manager"):
        return []
    credentials = importlib.import_module(f"{_PACKAGE_NAME}.credentials.manager")

    backend = credentials.store_backend()
    checks: list[dict] = [
        {
            "name": "credential_store",
            "ok": backend is not None,
            "detail": backend or "no usable OS keychain backend; credentials must come from environment variables",
        }
    ]
    available = credentials.get_credential(provider) is not None
    checks.append(
        {
            "name": "credential",
            "ok": available,
            "detail": f"provider '{provider}'"
            + ("" if available else f" — run '{cli_name()} auth login --provider {provider}'"),
        }
    )
    return checks


def _config_checks(root: Path) -> tuple[ProjectConfig | None, list[dict]]:
    """The checks of the project's config: it loads, and the installed CLI is new enough for it."""
    try:
        config = services.load_config(root)
    except ConfigInvalid as exc:
        return None, [{"name": "config", "ok": False, "detail": exc.message}]
    try:
        services.check_cli_compat(config)
    except CliTooOld as exc:
        return config, [{"name": "config", "ok": True}, {"name": "cli_compat", "ok": False, "detail": exc.message}]
    compat = {"name": "cli_compat", "ok": True, "detail": f"project requires >= {config.cli.min_version}"}
    return config, [{"name": "config", "ok": True}, compat]


@output.guard
def doctor(
    ctx: typer.Context,
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    verbose: bool = output.VerboseOption,
) -> None:
    """Run diagnostic checks and report readiness.

    The report is printed whether or not a check fails; `healthy` says whether every check passed.
    Exits 0 when healthy, 1 (UNHEALTHY) when any check failed.

    Example: {cli} doctor --json
    """
    checks: list[dict] = [{"name": "python", "ok": True}]
    checks.append({"name": "cli_version", "ok": True, "detail": installed_version() or DEV_VERSION})

    start = Path(ctx.obj.get("project") or Path.cwd())
    output.vecho(ctx, f"Searching for a project root starting at: {start}")
    root = services.find_project_root(start)
    checks.append({"name": "project", "ok": root is not None, "detail": str(root) if root else None})

    config, config_checks = _config_checks(root) if root is not None else (None, [])
    checks.extend(config_checks)
    checks.extend(_auth_checks(config.provider.name if config else "default"))
    checks.extend(deps.doctor_checks())  # [[tool.rb.external]] in pyproject.toml
    if module_exists(f"{_PACKAGE_NAME}.core.db"):  # include_db=false drops it at generation time
        checks.extend(importlib.import_module(f"{_PACKAGE_NAME}.core.db").doctor_checks())

    failed = [check["name"] for check in checks if not check["ok"]]
    output.emit_report(
        ctx,
        {"healthy": not failed, "checks": checks},
        lambda data: output.human.render_doctor(data["checks"]),
        Unhealthy(failed) if failed else None,
    )
