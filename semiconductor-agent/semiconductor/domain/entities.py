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
        model_answer: str = "",
        specialist_commentary: str = "",
        follow_up_question: str = "",
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
        self.model_answer = model_answer
        self.specialist_commentary = specialist_commentary
        self.follow_up_question = follow_up_question

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


# ── 자소서 (Essay Coach) ─────────────────────────────────────────

VALID_ESSAY_COMPANIES = frozenset(("samsung_ds", "sk_hynix"))
VALID_ESSAY_ITEMS = frozenset(("지원동기", "직무역량", "성장과정", "갈등극복"))


@dataclass(frozen=True)
class EssayPrompt:
    company: str       # samsung_ds | sk_hynix
    item: str          # 지원동기 | 직무역량 | 성장과정 | 갈등극복
    description: str   # 회사가 묻는 의도 (system이 사용자에게 보여줌)
    word_limit: int    # 한국어 char 수 제한 (예: 1500)

    def __post_init__(self):
        if self.company not in VALID_ESSAY_COMPANIES:
            raise ValueError(f"회사는 {VALID_ESSAY_COMPANIES} 중 하나여야 합니다.")
        if self.item not in VALID_ESSAY_ITEMS:
            raise ValueError(f"항목은 {VALID_ESSAY_ITEMS} 중 하나여야 합니다.")
        if self.word_limit <= 0:
            raise ValueError(f"word_limit은 양수여야 합니다: {self.word_limit}")


class EssayEvaluation:
    """자소서 첨삭 결과.

    Rubric (총 100점):
      fit_score (0-30):         회사 인재상 부합도
      structure_score (0-25):   구조 (서론-본론-결론, STAR 등)
      specificity_score (0-25): 구체성 (수치, 사례, 액션)
      writing_score (0-20):     한국어 작문 (자연스러움, 어휘)
    """

    def __init__(
        self,
        fit_score: int,
        structure_score: int,
        specificity_score: int,
        writing_score: int,
        total_score: int,
        feedback: str,
        strong_points: list[str],
        weak_points: list[str],
        revised_excerpt: str = "",
        culture_alignment: str = "",
    ) -> None:
        if not (0 <= fit_score <= 30):
            raise ValueError(f"fit_score는 0–30 범위여야 합니다: {fit_score}")
        if not (0 <= structure_score <= 25):
            raise ValueError(f"structure_score는 0–25 범위여야 합니다: {structure_score}")
        if not (0 <= specificity_score <= 25):
            raise ValueError(f"specificity_score는 0–25 범위여야 합니다: {specificity_score}")
        if not (0 <= writing_score <= 20):
            raise ValueError(f"writing_score는 0–20 범위여야 합니다: {writing_score}")
        expected = fit_score + structure_score + specificity_score + writing_score
        if total_score != expected:
            raise ValueError(f"total_score({total_score})가 부분 점수의 합({expected})과 다릅니다.")
        self.fit_score = fit_score
        self.structure_score = structure_score
        self.specificity_score = specificity_score
        self.writing_score = writing_score
        self.total_score = total_score
        self.feedback = feedback
        self.strong_points = list(strong_points)
        self.weak_points = list(weak_points)
        self.revised_excerpt = revised_excerpt
        self.culture_alignment = culture_alignment

    @property
    def grade(self) -> str:
        if self.total_score >= 80:
            return "우수"
        if self.total_score >= 50:
            return "보통"
        return "미흡"
