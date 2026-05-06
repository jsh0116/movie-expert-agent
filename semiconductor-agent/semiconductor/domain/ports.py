"""Domain ports (interfaces) — define contracts for infrastructure layer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from semiconductor.domain.entities import DiagnosticResult, EvaluationResult, Question


class IQuestionRepository(ABC):
    @abstractmethod
    def get_questions(self, company: str, domain: Optional[str] = None) -> list[Question]:
        """Return questions for a company, optionally filtered by domain."""


class ILLMJudge(ABC):
    @abstractmethod
    def evaluate(self, question: Question, user_answer: str) -> EvaluationResult:
        """Evaluate a user answer against the question rubric."""


class ICoachLLM(ABC):
    @abstractmethod
    def get_response(
        self,
        topic: str,
        messages: list,
        hint_count: int,
    ) -> str:
        """Return Socratic coaching response for the given topic and conversation."""


class IDiagnosticLLM(ABC):
    @abstractmethod
    def analyze(self, evaluations: list[EvaluationResult]) -> DiagnosticResult:
        """Analyze interview evaluations and produce domain scores."""
