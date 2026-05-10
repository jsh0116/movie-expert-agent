"""Graph 조립 통합 검증 — compile 정상, edge 토폴로지, evaluate→critic 직렬 연결."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage

from semiconductor.adapters.graph import create_app
from semiconductor.domain.entities import EvaluationResult


def _make_eval(total: int = 70) -> EvaluationResult:
    a = min(total * 40 // 100, 40)
    d = min(total * 30 // 100, 30)
    t = total - a - d
    t = max(0, min(t, 30))
    return EvaluationResult(
        accuracy_score=a, depth_score=d, terminology_score=t,
        total_score=a + d + t, feedback="ok", strong_points=[], weak_points=[],
        question="Q", model_answer="A",
    )


class TestGraphCompile:
    def test_create_app_returns_compiled_graph_and_initial_state(self):
        app, state = create_app(company="samsung_ds", max_questions=5)
        assert app is not None
        assert state["mode"] == "idle"
        assert state["interview_phase"] == "present"

    def test_graph_has_all_six_nodes(self):
        app, _ = create_app()
        # LangGraph compiled 앱의 노드 목록 확인
        nodes = set(app.get_graph().nodes.keys())
        for expected in (
            "orchestrator", "mock_present", "mock_evaluate",
            "mock_critic", "qa_coach", "diagnostic",
        ):
            assert expected in nodes, f"missing node: {expected}"


class TestInterviewFlow:
    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_인터뷰_명령이_mock_present로_라우팅된다(self, mock_svc):
        # judge/critic은 호출되지 않아야 함 (질문 출제 turn)
        mock_svc.judge.return_value = MagicMock()
        mock_svc.critic.return_value = MagicMock()

        app, state = create_app(max_questions=5)
        state["messages"] = [HumanMessage(content="/인터뷰")]
        result = app.invoke(state)

        assert result["mode"] == "interview"
        assert result["interview_phase"] == "evaluate"  # 출제 후 evaluate 대기
        assert result["current_question_text"] is not None
        assert "📝" in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_답변_turn은_evaluate_critic_2_pass_체이닝(self, mock_svc):
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval(total=60)
        mock_svc.judge.return_value = mock_judge

        mock_critic = MagicMock()
        mock_critic.critique.return_value = _make_eval(total=70)  # 점수 상향
        mock_svc.critic.return_value = mock_critic

        app, state = create_app(max_questions=5)
        # 직전 turn에서 질문이 출제된 상태 시뮬레이션
        state["mode"] = "interview"
        state["interview_phase"] = "evaluate"
        state["current_question_text"] = "FinFET이란?"
        state["current_question_domain"] = "소자"
        state["current_question_key_points"] = ["게이트", "채널"]
        state["messages"] = [HumanMessage(content="3D 트랜지스터")]

        result = app.invoke(state)

        # judge AND critic 모두 호출됐어야 함
        mock_judge.evaluate.assert_called_once()
        mock_critic.critique.assert_called_once()

        # critic 결과(70점)가 최종에 반영
        assert result["evaluations"][-1]["total_score"] == 70
        # 다음 turn 준비 — phase는 present로 복귀
        assert result["interview_phase"] == "present"
