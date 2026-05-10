"""자소서 첨삭 유스케이스."""
from __future__ import annotations

from semiconductor.domain.entities import EssayEvaluation, EssayPrompt
from semiconductor.domain.ports import IEssayCoach


class CoachEssayUseCase:
    def __init__(self, essay_coach: IEssayCoach) -> None:
        self._coach = essay_coach

    def execute(self, prompt: EssayPrompt, user_essay: str) -> EssayEvaluation:
        try:
            return self._coach.evaluate_essay(prompt, user_essay)
        except Exception:
            # graceful degradation
            return EssayEvaluation(
                fit_score=0, structure_score=0, specificity_score=0, writing_score=0,
                total_score=0,
                feedback="자소서 평가 중 오류가 발생했습니다. 다시 시도해주세요.",
                strong_points=[],
                weak_points=["평가를 다시 시도해주세요."],
                revised_excerpt="",
                culture_alignment="",
            )
