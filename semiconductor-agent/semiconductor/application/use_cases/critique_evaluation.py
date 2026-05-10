"""Self-Critique 검증 use case — graph node에서 호출하기 위해 분리."""
from semiconductor.domain.entities import EvaluationResult, Question
from semiconductor.domain.ports import ILLMCritic


class CritiqueEvaluationUseCase:
    """1차 평가(Judge 결과)를 검증·수정하는 2-pass 추론.

    실패 시 원본 평가를 그대로 반환 (graceful degradation).
    """

    def __init__(self, llm_critic: ILLMCritic) -> None:
        self._critic = llm_critic

    def execute(
        self,
        question: Question,
        user_answer: str,
        initial_evaluation: EvaluationResult,
    ) -> EvaluationResult:
        try:
            return self._critic.critique(
                question=question,
                user_answer=user_answer,
                initial_evaluation=initial_evaluation,
            )
        except Exception:
            return initial_evaluation
