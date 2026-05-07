"""TDD: Mock interviewer node — 모범답안 표시 + eval_dict 직렬화 검증."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage

from semiconductor.adapters.nodes.mock_interviewer import mock_interviewer_node
from semiconductor.adapters.state import create_initial_state
from semiconductor.domain.entities import EvaluationResult


def _phase2_state(question: str = "FinFET 설명하세요") -> dict:
    s = dict(create_initial_state())
    s["company"] = "samsung_ds"
    s["max_questions"] = 5
    s["asked_count"] = 0
    s["mode"] = "interview"
    s["current_question_text"] = question
    s["current_question_domain"] = "소자"
    s["current_question_key_points"] = ["게이트", "채널"]
    s["messages"] = [HumanMessage(content="3D 구조의 트랜지스터")]
    return s


def _make_eval(model_answer: str = "") -> EvaluationResult:
    return EvaluationResult(
        accuracy_score=30, depth_score=20, terminology_score=20,
        total_score=70, feedback="좋은 답변", strong_points=["정의"],
        weak_points=["깊이"], question="FinFET 설명하세요",
        model_answer=model_answer,
    )


class TestMockInterviewerModelAnswer:
    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_평가_결과에_모범답안이_있으면_출력에_포함된다(self, mock_svc):
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval(
            model_answer="FinFET은 3D 구조의 트랜지스터로, 게이트가 채널을 3면에서 둘러싸 단채널 효과를 억제합니다."
        )
        mock_svc.judge.return_value = mock_judge

        result = mock_interviewer_node(_phase2_state())

        assert "📚 모범답안" in result["display_output"]
        assert "FinFET은 3D" in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_모범답안이_빈_문자열이면_섹션이_생략된다(self, mock_svc):
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval(model_answer="")
        mock_svc.judge.return_value = mock_judge

        result = mock_interviewer_node(_phase2_state())

        assert "📚 모범답안" not in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_eval_dict에_model_answer가_직렬화된다(self, mock_svc):
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval(model_answer="모범답안 텍스트")
        mock_svc.judge.return_value = mock_judge

        result = mock_interviewer_node(_phase2_state())

        evals = result["evaluations"]
        assert len(evals) == 1
        assert evals[0]["model_answer"] == "모범답안 텍스트"
