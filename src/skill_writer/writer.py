import os
import re
from pathlib import Path

from .exceptions import CreationError, InvalidNameError
from .models import ElementType, WriteResult
from .scope import resolve_scope


def _validate_name(name: str) -> None:
    if len(name) > 1 and not re.match(r"^[a-z0-9][a-z0-9\-]*[a-z0-9]$", name):
        raise InvalidNameError(f"Name must be lowercase alphanumeric with hyphens: {name!r}")


def _frontmatter(name: str, description: str) -> str:
    return f"---\nname: {name}\ndescription: {description}\n---\n\n"


def _command_frontmatter(description: str) -> str:
    return f"---\ndescription: {description}\n---\n\n"


class SkillWriter:
    """Generate Claude Code skills, commands, and agents programmatically.

    Usage:
        sw = SkillWriter()                  # auto-detect scope
        sw = SkillWriter(scope="global")    # explicit scope

        result = sw.skill("summarize", description="Summarize any text", content="...")
        result = sw.skill("review",    description="Code review",         generate=True)
    """

    def __init__(self, scope: str | None = None):
        self.scope_name, self.scope_path = resolve_scope(scope)

    def skill(
        self,
        name: str,
        description: str,
        content: str = "",
        generate: bool = False,
        overwrite: bool = False,
    ) -> WriteResult:
        _validate_name(name)
        if generate or not content:
            content = self._generate(name, description, ElementType.SKILL)
        return self._write(ElementType.SKILL, name, description, content, overwrite)

    def command(
        self,
        name: str,
        description: str,
        content: str = "",
        generate: bool = False,
        overwrite: bool = False,
    ) -> WriteResult:
        _validate_name(name)
        if generate or not content:
            content = self._generate(name, description, ElementType.COMMAND)
        return self._write(ElementType.COMMAND, name, description, content, overwrite)

    def agent(
        self,
        name: str,
        description: str,
        content: str = "",
        generate: bool = False,
        overwrite: bool = False,
    ) -> WriteResult:
        _validate_name(name)
        if generate or not content:
            content = self._generate(name, description, ElementType.AGENT)
        return self._write(ElementType.AGENT, name, description, content, overwrite)

    def _write(
        self, element_type: ElementType, name: str, description: str, content: str, overwrite: bool
    ) -> WriteResult:
        subdir = element_type.value + "s"  # skills, commands, agents
        directory = self.scope_path / subdir
        file_path = directory / f"{name}.md"

        if file_path.exists() and not overwrite:
            raise CreationError(f"{file_path} already exists — use overwrite=True")

        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise CreationError(f"Cannot create {directory}: {e}")

        if element_type == ElementType.COMMAND:
            header = _command_frontmatter(description)
            body = f"# /{name}\n\n{content}\n"
        elif element_type == ElementType.AGENT:
            header = _frontmatter(name, description)
            body = content + "\n"
        else:  # SKILL
            header = _frontmatter(name, description)
            body = content + "\n"

        try:
            file_path.write_text(header + body, encoding="utf-8")
        except OSError as e:
            raise CreationError(f"Cannot write {file_path}: {e}")

        return WriteResult(path=file_path, element_type=element_type, scope=self.scope_name)

    def _generate(self, name: str, description: str, element_type: ElementType) -> str:
        try:
            import anthropic
        except ImportError:
            raise CreationError(
                "anthropic package required for generate=True: pip install anthropic"
            )

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise CreationError("ANTHROPIC_API_KEY not set in environment")

        client = anthropic.Anthropic(api_key=api_key)

        type_label = {
            ElementType.SKILL: "skill (reusable instruction set)",
            ElementType.COMMAND: "slash command",
            ElementType.AGENT: "sub-agent",
        }[element_type]

        system = (
            "You write Claude Code configuration files. "
            "Write practical, concise instructions a developer can follow. "
            "No preamble, no markdown fences, no meta-commentary. "
            "Output only the instruction content — no YAML frontmatter."
        )
        user = f"Write a Claude Code {type_label} named '{name}' that: {description}"

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text.strip()

    def list(self) -> dict[str, list[Path]]:
        result = {}
        for et in ElementType:
            d = self.scope_path / (et.value + "s")
            result[et.value] = sorted(d.glob("*.md")) if d.exists() else []
        return result
