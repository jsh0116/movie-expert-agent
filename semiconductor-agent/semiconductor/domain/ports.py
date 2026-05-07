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


class ILLMCritic(ABC):
    """Self-critique layer — LLM이 본인의 평가를 다시 검증·수정한다.

    교수 1명의 즉답보다 깊은 분석을 위해 평가→재검증 2회 추론으로 정확도를 높인다.
    """

    @abstractmethod
    def critique(
        self,
        question: Question,
        user_answer: str,
        initial_evaluation: EvaluationResult,
    ) -> EvaluationResult:
        """Review an initial evaluation and return a revised one if needed."""
