from pathlib import Path

from .exceptions import ScopeError


def resolve_scope(name: str | None = None) -> tuple[str, Path]:
    """Returns (scope_name, base_path). Auto-detects if name is None."""
    if name == "global" or (name is None and _no_project()):
        return "global", Path.home() / ".claude"
    if name == "project" or name is None:
        p = _find_project_root()
        if p:
            return "project", p / ".claude"
    if name == "local":
        p = _find_project_root()
        if p:
            return "local", p / ".claude"
    raise ScopeError(f"Cannot resolve scope: {name!r}")


def _find_project_root() -> Path | None:
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists() or (current / ".claude").exists():
            return current
        current = current.parent
    return None


def _no_project() -> bool:
    return _find_project_root() is None
