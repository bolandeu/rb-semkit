"""`doctor`: the checks of readiness (Python, CLI version, project, config, credentials, external programs).

The report is printed whether or not a check fails; a failed check makes the exit non-zero (Unhealthy), so a script
can rely on the exit code.
"""

from __future__ import annotations

import typer

from .. import output
from ..core import deps
from ..core.errors import Unhealthy
from ..core.version import DEV_VERSION, installed_version, optional_module

_PACKAGE_NAME = __name__.split(".")[0]


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

    provider = "default"
    if project := optional_module(f"{_PACKAGE_NAME}.commands.project"):  # include_project=false drops it
        project_checks, config = project.doctor_checks(ctx)
        checks.extend(project_checks)
        provider = config.provider.name if config else provider

    if credentials := optional_module(f"{_PACKAGE_NAME}.credentials.health"):  # include_auth=false drops it
        checks.extend(credentials.doctor_checks(provider))
    checks.extend(deps.doctor_checks())  # [[tool.rb.external]] in pyproject.toml
    if db := optional_module(f"{_PACKAGE_NAME}.core.db"):  # include_db=false drops it at generation time
        checks.extend(db.doctor_checks())

    failed = [check["name"] for check in checks if not check["ok"]]
    output.emit_report(
        ctx,
        {"healthy": not failed, "checks": checks},
        lambda data: output.human.render_doctor(data["checks"]),
        Unhealthy(failed) if failed else None,
    )
