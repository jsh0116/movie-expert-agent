from semiconductor.domain.entities import EvaluationResult, Question
from semiconductor.domain.ports import ILLMJudge


class EvaluateAnswerUseCase:
    def __init__(self, llm_judge: ILLMJudge) -> None:
        self._judge = llm_judge

    def execute(self, question: Question, user_answer: str) -> EvaluationResult:
        try:
            return self._judge.evaluate(question=question, user_answer=user_answer)
        except Exception:
            return EvaluationResult(
                accuracy_score=0,
                depth_score=0,
                terminology_score=0,
                total_score=0,
                feedback="평가 처리 중 오류가 발생했습니다. 다시 시도해주세요.",
                strong_points=[],
                weak_points=["평가를 다시 시도해주세요."],
                question=question.question,
            )
