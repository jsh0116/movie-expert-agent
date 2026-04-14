from dataclasses import dataclass, field
from enum import Enum


class CoachingCategory(Enum):
    MOTIVATION = "motivation"
    HABITS = "habits"
    WELLNESS = "wellness"
    PRODUCTIVITY = "productivity"
    MINDFULNESS = "mindfulness"


@dataclass
class CoachingMessage:
    role: str
    content: str


@dataclass
class CoachingSession:
    messages: list[CoachingMessage] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(CoachingMessage(role=role, content=content))

    def to_input_list(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def clear(self) -> None:
        self.messages.clear()
