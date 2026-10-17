from __future__ import annotations

from importlib import resources
from pathlib import Path

import typer

from .. import output
from ..core.version import cli_name

app = output.group("Install this CLI's agent skill for AI tools.")

_PACKAGE_NAME = __name__.split(".")[0]
_SKILL_NAME = cli_name()  # matches `name:` in the bundled SKILL.md

# Where each AI tool looks for personal (user-level) and project-level skills.
_TOOL_TARGETS = {
    "claude-code": {
        "user": Path.home() / ".claude" / "skills" / _SKILL_NAME,
        "project": Path(".claude") / "skills" / _SKILL_NAME,
    },
    "agents": {
        "user": Path.home() / ".agents" / "skills" / _SKILL_NAME,
        "project": Path(".agents") / "skills" / _SKILL_NAME,
    },
}


def _skill_content() -> str:
    return resources.files(f"{_PACKAGE_NAME}.data").joinpath("SKILL.md").read_text()


@app.command("install")
@output.guard
def install(
    ctx: typer.Context,
    tool: str = typer.Option(
        "claude-code",
        "--tool",
        help=f"Target AI tool: one of {', '.join(_TOOL_TARGETS)}.",
    ),
    project: bool = typer.Option(
        False, "--project", help="Install into the current project instead of the user-level directory."
    ),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = output.DryRunOption,
) -> None:
    """Copy this CLI's bundled SKILL.md into an AI tool's skill directory.

    With --dry-run nothing is written.

    Example: {cli} skill install --tool claude-code
    """
    from ..core.errors import InvalidArguments

    if tool not in _TOOL_TARGETS:
        raise InvalidArguments(f"Unknown --tool '{tool}'. Choose one of: {', '.join(_TOOL_TARGETS)}.")

    scope = "project" if project else "user"
    target_path = _TOOL_TARGETS[tool][scope] / "SKILL.md"
    if not output.is_dry_run(ctx):
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(_skill_content())

    verb = output.done(ctx, "Installed", "Would install")
    output.emit_success(
        ctx,
        {"tool": tool, "scope": scope, "path": str(target_path.resolve()), "dry_run": output.is_dry_run(ctx)},
        render_human=lambda d: output.human.echo(f"{verb} skill for '{d['tool']}' ({d['scope']}) at {d['path']}"),
    )
