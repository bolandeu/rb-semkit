"""`skill install`: copy the bundled skills into the skill folder of an AI tool (user or project level); `skill list`.

An agent then finds the guide of this CLI without `--ai`; --dry-run writes nothing.
"""

from __future__ import annotations

from pathlib import Path

import typer

from .. import output
from ..core import skills

app = output.group("Install this CLI's agent skill for AI tools.")


# Where each AI tool looks for personal (user-level) and project-level skills.
_TOOL_TARGETS = {
    "claude-code": {
        "user": Path.home() / ".claude" / "skills",
        "project": Path(".claude") / "skills",
    },
    "agents": {
        "user": Path.home() / ".agents" / "skills",
        "project": Path(".agents") / "skills",
    },
}


def _chosen(wanted: str | None) -> list[skills.Skill]:
    """Every bundled skill, or the one `--skill` names (by its name or its short name)."""
    from ..core.errors import InvalidArguments

    bundled = skills.bundled()
    if wanted is None:
        return bundled
    found = [s for s in bundled if wanted in (s.name, s.short_name)]
    if not found:
        raise InvalidArguments(f"Unknown --skill '{wanted}'. Bundled skills: {', '.join(s.name for s in bundled)}.")
    return found


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
    skill: str = typer.Option(
        None, "--skill", help="Install only this bundled skill (see `skill list`); by default all."
    ),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
    dry_run: bool = output.DryRunOption,
) -> None:
    """Copy this CLI's bundled skills into an AI tool's skill directory.

    The conventions skill and every extra skill the package ships, each into its own directory.

    With --dry-run nothing is written.

    Example: {cli} skill install --tool claude-code
    """
    from ..core.errors import InvalidArguments

    if tool not in _TOOL_TARGETS:
        raise InvalidArguments(f"Unknown --tool '{tool}'. Choose one of: {', '.join(_TOOL_TARGETS)}.")

    chosen = _chosen(skill)
    scope = "project" if project else "user"
    paths = []
    for item in chosen:
        target_path = _TOOL_TARGETS[tool][scope] / item.name / "SKILL.md"
        if not output.is_dry_run(ctx):
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(item.text)
        paths.append(str(target_path.resolve()))

    data: dict[str, object] = {"tool": tool, "scope": scope, "path": paths[0], "dry_run": output.is_dry_run(ctx)}
    if len(paths) > 1:
        data["paths"] = paths
    verb = output.done(ctx, "Installed", "Would install")
    output.emit_success(
        ctx,
        data,
        render_human=lambda d: output.human.echo(
            f"{verb} skill for '{d['tool']}' ({d['scope']}) at " + "\n  ".join(d.get("paths", [d["path"]]))
        ),
    )


@app.command("list")
@output.guard
def list_skills(
    ctx: typer.Context,
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """List the agent skills this CLI bundles: name and description.

    Example: {cli} skill list
    """
    found = [{"name": s.name, "description": s.description} for s in skills.bundled()]
    output.emit_success(
        ctx,
        {"skills": found},
        render_human=lambda d: output.human.echo("\n".join(f"{s['name']}: {s['description']}" for s in d["skills"])),
    )
