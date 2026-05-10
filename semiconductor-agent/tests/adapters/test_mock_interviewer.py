"""TDD: Mock Interviewer 3-node split — present / evaluate / critic."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage

from semiconductor.adapters.nodes.mock_interviewer import (
    _serialize_eval,
    mock_critic_node,
    mock_evaluate_node,
    mock_present_node,
)
from semiconductor.adapters.state import create_initial_state
from semiconductor.domain.entities import EvaluationResult


def _make_eval(
    model_answer: str = "",
    specialist_commentary: str = "",
    follow_up_question: str = "",
    total: int = 70,
) -> EvaluationResult:
    a = min(total * 40 // 100, 40)
    d = min(total * 30 // 100, 30)
    t = total - a - d
    t = max(0, min(t, 30))
    return EvaluationResult(
        accuracy_score=a, depth_score=d, terminology_score=t,
        total_score=a + d + t, feedback="좋은 답변", strong_points=["정의"],
        weak_points=["깊이"], question="FinFET 설명하세요",
        model_answer=model_answer,
        specialist_commentary=specialist_commentary,
        follow_up_question=follow_up_question,
    )


def _phase_present_state(asked_count: int = 0) -> dict:
    s = dict(create_initial_state())
    s["company"] = "samsung_ds"
    s["max_questions"] = 5
    s["asked_count"] = asked_count
    s["mode"] = "interview"
    s["interview_phase"] = "present"
    return s


def _phase_evaluate_state(question: str = "FinFET 설명하세요") -> dict:
    s = dict(create_initial_state())
    s["company"] = "samsung_ds"
    s["max_questions"] = 5
    s["asked_count"] = 0
    s["mode"] = "interview"
    s["interview_phase"] = "evaluate"
    s["current_question_text"] = question
    s["current_question_domain"] = "소자"
    s["current_question_key_points"] = ["게이트", "채널"]
    s["messages"] = [HumanMessage(content="3D 구조의 트랜지스터")]
    return s


# ── mock_present_node ─────────────────────────────────────────────


class TestMockPresentNode:
    def test_질문_출제_후_phase가_evaluate로_전환된다(self):
        result = mock_present_node(_phase_present_state())
        assert result["interview_phase"] == "evaluate"
        assert result["current_question_text"]
        assert "📝" in result["display_output"]

    def test_max_questions_도달시_idle로_전환_평가_안_함(self):
        s = _phase_present_state(asked_count=5)
        s["max_questions"] = 5
        result = mock_present_node(s)
        assert result["mode"] == "idle"
        assert "면접 완료" in result["display_output"]


# ── mock_evaluate_node ────────────────────────────────────────────


class TestMockEvaluateNode:
    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_judge_호출_후_pending_evaluation에_저장(self, mock_svc):
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval(model_answer="X")
        mock_svc.judge.return_value = mock_judge

        result = mock_evaluate_node(_phase_evaluate_state())

        assert result["pending_evaluation"] is not None
        assert result["pending_evaluation"]["question"] == "FinFET 설명하세요"
        assert result["pending_evaluation"]["model_answer"] == "X"

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_evaluate_노드는_critic을_호출하지_않는다(self, mock_svc):
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval()
        mock_svc.judge.return_value = mock_judge
        mock_critic = MagicMock()
        mock_svc.critic.return_value = mock_critic

        mock_evaluate_node(_phase_evaluate_state())

        mock_critic.critique.assert_not_called()


# ── mock_critic_node ──────────────────────────────────────────────


class TestMockCriticNode:
    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_pending_평가를_critic이_검증_후_evaluations에_저장(self, mock_svc):
        initial = _make_eval(total=60)
        revised = _make_eval(total=70)
        mock_critic = MagicMock()
        mock_critic.critique.return_value = revised
        mock_svc.critic.return_value = mock_critic

        s = _phase_evaluate_state()
        s["pending_evaluation"] = _serialize_eval(initial)

        result = mock_critic_node(s)

        mock_critic.critique.assert_called_once()
        assert len(result["evaluations"]) == 1
        assert result["evaluations"][0]["total_score"] == 70  # revised 점수
        assert result["pending_evaluation"] is None  # 사용 후 정리

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_critic_후_phase는_present로_복귀_다음_질문_준비(self, mock_svc):
        mock_critic = MagicMock()
        mock_critic.critique.return_value = _make_eval()
        mock_svc.critic.return_value = mock_critic

        s = _phase_evaluate_state()
        s["pending_evaluation"] = _serialize_eval(_make_eval())

        result = mock_critic_node(s)

        assert result["interview_phase"] == "present"
        assert result["current_question_text"] is None  # 다음 질문 받을 준비

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_도메인_전문가_헤더와_각_섹션_출력에_포함(self, mock_svc):
        mock_critic = MagicMock()
        mock_critic.critique.return_value = _make_eval(
            model_answer="모범답안 텍스트",
            specialist_commentary="소자 전문가 코멘트",
            follow_up_question="GAA 차이는?",
        )
        mock_svc.critic.return_value = mock_critic

        s = _phase_evaluate_state()
        s["pending_evaluation"] = _serialize_eval(_make_eval())

        out = mock_critic_node(s)["display_output"]

        assert "[소자 전문가 평가]" in out
        assert "🔬 전문가 코멘트" in out
        assert "📚 모범답안" in out
        assert "💡 심화 질문" in out

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_max_questions_도달시_idle로_전환(self, mock_svc):
        mock_critic = MagicMock()
        mock_critic.critique.return_value = _make_eval()
        mock_svc.critic.return_value = mock_critic

        s = _phase_evaluate_state()
        s["asked_count"] = 4  # 5번째 답변
        s["max_questions"] = 5
        s["pending_evaluation"] = _serialize_eval(_make_eval())

        result = mock_critic_node(s)

        assert result["mode"] == "idle"
        assert "모든 문제를 완료" in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_critic_실패시_초기_평가가_그대로_저장된다(self, mock_svc):
        mock_critic = MagicMock()
        mock_critic.critique.side_effect = Exception("critic timeout")
        mock_svc.critic.return_value = mock_critic

        initial = _make_eval(total=65)
        s = _phase_evaluate_state()
        s["pending_evaluation"] = _serialize_eval(initial)

        result = mock_critic_node(s)

        # graceful degradation — 원본 평가 보존
        assert result["evaluations"][0]["total_score"] == 65
