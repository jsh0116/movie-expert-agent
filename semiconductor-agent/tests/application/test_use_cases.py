"""TDD: Application use case tests — mock ports, test business logic."""
from unittest.mock import MagicMock

import pytest

from semiconductor.domain.entities import DiagnosticResult, EvaluationResult, Question
from semiconductor.domain.ports import ICoachLLM, IDiagnosticLLM, ILLMJudge, IQuestionRepository
from semiconductor.application.use_cases.evaluate_answer import EvaluateAnswerUseCase
from semiconductor.application.use_cases.next_question import GetNextQuestionUseCase
from semiconductor.application.use_cases.coach_concept import CoachConceptUseCase
from semiconductor.application.use_cases.diagnose_session import DiagnoseSessionUseCase


def _make_eval(total: int = 70, question: str = "test q") -> EvaluationResult:
    a = min(total * 40 // 100, 40)
    d = min(total * 30 // 100, 30)
    t = total - a - d
    t = max(0, min(t, 30))
    return EvaluationResult(
        accuracy_score=a, depth_score=d, terminology_score=t,
        total_score=a + d + t, feedback="ok",
        strong_points=[], weak_points=[], question=question,
    )


class TestEvaluateAnswerUseCase:
    def test_delegates_to_llm_judge(self):
        mock_judge: ILLMJudge = MagicMock()
        expected = _make_eval(75, "Q1")
        mock_judge.evaluate.return_value = expected

        q = Question(domain="소자", question="Q1", key_points=["k1"])
        use_case = EvaluateAnswerUseCase(llm_judge=mock_judge)
        result = use_case.execute(question=q, user_answer="some answer")

        mock_judge.evaluate.assert_called_once_with(question=q, user_answer="some answer")
        assert result == expected

    def test_returns_fallback_on_llm_error(self):
        mock_judge: ILLMJudge = MagicMock()
        mock_judge.evaluate.side_effect = Exception("LLM timeout")

        q = Question(domain="소자", question="Q1", key_points=[])
        use_case = EvaluateAnswerUseCase(llm_judge=mock_judge)
        result = use_case.execute(question=q, user_answer="answer")

        assert result.total_score == 0
        assert result.question == "Q1"
        assert "오류" in result.feedback

    def test_model_answer_is_empty_on_fallback(self):
        # LLM 실패 시 fallback EvaluationResult는 model_answer 빈 값
        mock_judge: ILLMJudge = MagicMock()
        mock_judge.evaluate.side_effect = Exception("LLM timeout")
        q = Question(domain="소자", question="Q1", key_points=[])
        result = EvaluateAnswerUseCase(llm_judge=mock_judge).execute(question=q, user_answer="x")
        assert result.model_answer == ""

    def test_propagates_model_answer_from_judge(self):
        # judge가 반환한 model_answer가 그대로 전달되어야 함
        mock_judge: ILLMJudge = MagicMock()
        expected = EvaluationResult(
            accuracy_score=30, depth_score=20, terminology_score=20,
            total_score=70, feedback="x", strong_points=[], weak_points=[],
            question="Q1", model_answer="FinFET은 3D 트랜지스터로 게이트가 채널을 3면에서 둘러싸...",
        )
        mock_judge.evaluate.return_value = expected
        q = Question(domain="소자", question="Q1", key_points=[])
        result = EvaluateAnswerUseCase(llm_judge=mock_judge).execute(question=q, user_answer="x")
        assert result.model_answer.startswith("FinFET은 3D")


class TestGetNextQuestionUseCase:
    def test_returns_first_question_on_empty_history(self):
        mock_repo: IQuestionRepository = MagicMock()
        q1 = Question(domain="소자", question="Q1", key_points=[])
        q2 = Question(domain="소자", question="Q2", key_points=[])
        mock_repo.get_questions.return_value = [q1, q2]

        use_case = GetNextQuestionUseCase(question_repo=mock_repo)
        result = use_case.execute(company="samsung_ds", domain="소자", asked_count=0, max_questions=3)

        assert result is not None
        assert result.domain == "소자"

    def test_returns_none_when_max_reached(self):
        mock_repo: IQuestionRepository = MagicMock()
        mock_repo.get_questions.return_value = [
            Question(domain="소자", question=f"Q{i}", key_points=[]) for i in range(5)
        ]
        use_case = GetNextQuestionUseCase(question_repo=mock_repo)
        result = use_case.execute(company="samsung_ds", domain="소자", asked_count=4, max_questions=4)
        assert result is None

    def test_returns_none_when_pool_exhausted(self):
        mock_repo: IQuestionRepository = MagicMock()
        mock_repo.get_questions.return_value = []
        use_case = GetNextQuestionUseCase(question_repo=mock_repo)
        result = use_case.execute(company="samsung_ds", domain="소자", asked_count=0, max_questions=3)
        assert result is None


class TestCoachConceptUseCase:
    def test_returns_response_and_increments_hint_count(self):
        mock_coach: ICoachLLM = MagicMock()
        mock_coach.get_response.return_value = "ALD는 원자층 증착입니다..."

        use_case = CoachConceptUseCase(coach_llm=mock_coach)
        response, new_hint_count = use_case.execute(
            topic="ALD", messages=[], hint_count=1
        )

        assert response == "ALD는 원자층 증착입니다..."
        assert new_hint_count == 2

    def test_hint_count_caps_at_4(self):
        mock_coach: ICoachLLM = MagicMock()
        mock_coach.get_response.return_value = "설명입니다"
        use_case = CoachConceptUseCase(coach_llm=mock_coach)
        _, new_count = use_case.execute(topic="x", messages=[], hint_count=4)
        assert new_count == 4  # should not exceed 4

    def test_hint_count_0_means_probe(self):
        mock_coach: ICoachLLM = MagicMock()
        mock_coach.get_response.return_value = "어디까지 알고 있나요?"
        use_case = CoachConceptUseCase(coach_llm=mock_coach)
        response, hint_count = use_case.execute(topic="CVD", messages=[], hint_count=0)
        mock_coach.get_response.assert_called_once()
        call_kwargs = mock_coach.get_response.call_args[1]
        assert call_kwargs["hint_count"] == 0


class TestDiagnoseSessionUseCase:
    def test_empty_evaluations_raises(self):
        mock_llm: IDiagnosticLLM = MagicMock()
        use_case = DiagnoseSessionUseCase(diagnostic_llm=mock_llm)

        with pytest.raises(ValueError, match="평가 데이터"):
            use_case.execute(evaluations=[])

    def test_delegates_to_llm_and_fills_missing_domains(self):
        mock_llm: IDiagnosticLLM = MagicMock()
        mock_llm.analyze.return_value = DiagnosticResult(
            domain_scores={"소자": 80},  # only one domain
            weak_topics=["ALD"],
            strong_topics=["DRAM"],
            recommended_next="ALD 복습",
        )
        evals = [_make_eval(80, "Q1")]
        use_case = DiagnoseSessionUseCase(diagnostic_llm=mock_llm)
        result = use_case.execute(evaluations=evals)

        # Missing domains should be filled with 0
        assert set(result.domain_scores.keys()) == {"소자", "공정", "회로", "트렌드"}
        assert result.domain_scores.get("공정", -1) == 0
