"""Domain entities — pure business objects, no infrastructure dependencies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

VALID_DOMAINS = frozenset(("소자", "공정", "회로", "트렌드"))


@dataclass(frozen=True)
class Question:
    domain: str
    question: str
    key_points: list[str]

    def __post_init__(self):
        if self.domain not in VALID_DOMAINS:
            raise ValueError(f"도메인은 {VALID_DOMAINS} 중 하나여야 합니다. 받은 값: {self.domain!r}")
        if not self.question.strip():
            raise ValueError("질문 텍스트는 비어있을 수 없습니다.")


class EvaluationResult:
    """LLM judge output for a single interview answer.

    Scoring rubric:
      accuracy_score:    0–40  (정확성)
      depth_score:       0–30  (깊이)
      terminology_score: 0–30  (전문 용어)
      total_score:       0–100 (= sum of above)
    """

    def __init__(
        self,
        accuracy_score: int,
        depth_score: int,
        terminology_score: int,
        total_score: int,
        feedback: str,
        strong_points: list[str],
        weak_points: list[str],
        question: str,
    ) -> None:
        if not (0 <= accuracy_score <= 40):
            raise ValueError(f"accuracy_score는 0–40 범위여야 합니다. 받은 값: {accuracy_score}")
        if not (0 <= depth_score <= 30):
            raise ValueError(f"depth_score는 0–30 범위여야 합니다. 받은 값: {depth_score}")
        if not (0 <= terminology_score <= 30):
            raise ValueError(f"terminology_score는 0–30 범위여야 합니다. 받은 값: {terminology_score}")
        expected_total = accuracy_score + depth_score + terminology_score
        if total_score != expected_total:
            raise ValueError(
                f"total_score({total_score})가 부분 점수의 합({expected_total})과 다릅니다."
            )
        self.accuracy_score = accuracy_score
        self.depth_score = depth_score
        self.terminology_score = terminology_score
        self.total_score = total_score
        self.feedback = feedback
        self.strong_points = list(strong_points)
        self.weak_points = list(weak_points)
        self.question = question

    @property
    def grade(self) -> str:
        if self.total_score >= 80:
            return "우수"
        if self.total_score >= 50:
            return "보통"
        return "미흡"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EvaluationResult):
            return NotImplemented
        return (
            self.accuracy_score == other.accuracy_score
            and self.depth_score == other.depth_score
            and self.terminology_score == other.terminology_score
            and self.total_score == other.total_score
            and self.question == other.question
        )


@dataclass
class DiagnosticResult:
    domain_scores: dict[str, int]  # {"소자": 75, "공정": 42, ...}
    weak_topics: list[str]
    strong_topics: list[str]
    recommended_next: str

    def __post_init__(self):
        for domain, score in self.domain_scores.items():
            if not (0 <= score <= 100):
                raise ValueError(f"도메인 점수는 0–100 범위여야 합니다. {domain}: {score}")

    @property
    def weakest_domain(self) -> Optional[str]:
        if not self.domain_scores:
            return None
        return min(self.domain_scores, key=lambda d: self.domain_scores[d])
