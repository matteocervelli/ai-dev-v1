from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ElementType(str, Enum):
    SKILL = "skill"
    COMMAND = "command"
    AGENT = "agent"


@dataclass
class WriteResult:
    path: Path
    element_type: ElementType
    scope: str

    def __post_init__(self):
        if not isinstance(self.path, Path):
            self.path = Path(self.path)

    def __str__(self):
        return f"{self.element_type.value} written → {self.path}"
