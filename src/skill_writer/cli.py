from pathlib import Path

import typer
from dotenv import load_dotenv

from .exceptions import SkillWriterError
from .writer import SkillWriter

load_dotenv()
app = typer.Typer(help="Generate Claude Code skills, commands, and agents.")

scope_opt = typer.Option(
    None, "--scope", "-s", help="global | project | local (auto-detect if omitted)"
)


@app.command("scope")
def show_scope(scope: str = scope_opt):
    """Show the active scope and its path."""
    sw = SkillWriter(scope=scope)
    typer.echo(f"scope : {sw.scope_name}")
    typer.echo(f"path  : {sw.scope_path}")


@app.command("list")
def list_elements(scope: str = scope_opt):
    """List all skills, commands, and agents in the active scope."""
    sw = SkillWriter(scope=scope)
    for kind, paths in sw.list().items():
        if paths:
            typer.echo(f"\n{kind}s ({len(paths)}):")
            for p in paths:
                typer.echo(f"  {p.stem}")


skill_app = typer.Typer()
app.add_typer(skill_app, name="skill")


@skill_app.command("create")
def skill_create(
    name: str,
    description: str = typer.Option(..., "--description", "-d"),
    content: str = typer.Option("", "--content", "-c"),
    generate: bool = typer.Option(
        False, "--generate", "-g", help="Generate content with Claude AI"
    ),
    scope: str = scope_opt,
    overwrite: bool = typer.Option(False, "--overwrite"),
):
    """Create a Claude Code skill."""
    try:
        sw = SkillWriter(scope=scope)
        result = sw.skill(
            name, description, content=content, generate=generate, overwrite=overwrite
        )
        typer.echo(f"✓ {result}")
    except SkillWriterError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


command_app = typer.Typer()
app.add_typer(command_app, name="command")


@command_app.command("create")
def command_create(
    name: str,
    description: str = typer.Option(..., "--description", "-d"),
    content: str = typer.Option("", "--content", "-c"),
    generate: bool = typer.Option(False, "--generate", "-g"),
    scope: str = scope_opt,
    overwrite: bool = typer.Option(False, "--overwrite"),
):
    """Create a Claude Code slash command."""
    try:
        sw = SkillWriter(scope=scope)
        result = sw.command(
            name, description, content=content, generate=generate, overwrite=overwrite
        )
        typer.echo(f"✓ {result}")
    except SkillWriterError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


agent_app = typer.Typer()
app.add_typer(agent_app, name="agent")


@agent_app.command("create")
def agent_create(
    name: str,
    description: str = typer.Option(..., "--description", "-d"),
    content: str = typer.Option("", "--content", "-c"),
    generate: bool = typer.Option(False, "--generate", "-g"),
    scope: str = scope_opt,
    overwrite: bool = typer.Option(False, "--overwrite"),
):
    """Create a Claude Code sub-agent."""
    try:
        sw = SkillWriter(scope=scope)
        result = sw.agent(
            name, description, content=content, generate=generate, overwrite=overwrite
        )
        typer.echo(f"✓ {result}")
    except SkillWriterError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
