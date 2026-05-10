"""TDD: Memory checkpointer + Parallel Send API."""
from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from semiconductor.adapters.graph import create_app, create_app_with_memory
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


class TestMemoryCheckpointer:
    def test_create_app_with_memory_returns_compiled_app(self):
        app, state = create_app_with_memory(max_questions=5)
        assert app is not None
        assert state["mode"] == "idle"

    def test_create_app_accepts_custom_checkpointer(self):
        memory = MemorySaver()
        app, _ = create_app(checkpointer=memory)
        # 컴파일된 앱은 checkpointer를 가짐
        assert app.checkpointer is memory

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_thread_id로_state가_세션간_지속된다(self, mock_svc):
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval()
        mock_svc.judge.return_value = mock_judge
        mock_critic = MagicMock()
        mock_critic.critique.return_value = _make_eval()
        mock_svc.critic.return_value = mock_critic

        app, state = create_app_with_memory(max_questions=5)
        config = {"configurable": {"thread_id": "user_001"}}

        # Turn 1: /인터뷰 → 첫 질문 출제
        state["messages"] = [HumanMessage(content="/인터뷰")]
        result1 = app.invoke(state, config=config)
        assert result1["mode"] == "interview"

        # Turn 2: 같은 thread로 재호출 — 이전 state 자동 복원
        # state 인자 없이 messages만 추가하면 checkpointer가 이전 state 로드
        result2 = app.invoke(
            {"messages": [HumanMessage(content="3D 트랜지스터")]},
            config=config,
        )
        # 같은 thread이므로 면접 모드 유지, asked_count 증가
        assert result2["mode"] == "interview"
        assert result2["asked_count"] >= 1


class TestParallelSendAPI:
    @patch("semiconductor.adapters.nodes.web_enrichment.IndustrySearchService")
    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_트렌드_도메인일때_web_enrichment가_병렬_실행(self, mock_svc, mock_search_cls):
        # given: judge + critic mock + search mock
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval()
        mock_svc.judge.return_value = mock_judge
        mock_critic = MagicMock()
        mock_critic.critique.return_value = _make_eval()
        mock_svc.critic.return_value = mock_critic
        mock_search = MagicMock()
        mock_search.search.return_value = "HBM3E 양산 발표 (2026)"
        mock_search_cls.return_value = mock_search

        app, state = create_app(max_questions=5)
        # 트렌드 도메인 평가 turn 시뮬레이션
        state["mode"] = "interview"
        state["interview_phase"] = "evaluate"
        state["current_question_text"] = "HBM3E와 HBM3 차이는?"
        state["current_question_domain"] = "트렌드"
        state["current_question_key_points"] = ["TSV", "대역폭"]
        state["messages"] = [HumanMessage(content="대역폭이 늘어났다")]

        result = app.invoke(state)

        # 트렌드 도메인이면 search 호출됨 + judge도 호출됨 (병렬)
        mock_search.search.assert_called_once()
        mock_judge.evaluate.assert_called_once()
        # critic은 두 결과를 다 받고 최종 평가
        mock_critic.critique.assert_called_once()
        # 출력에 산업 동향 섹션 포함
        assert "🌐 산업 최신 동향" in result["display_output"]

    @patch("semiconductor.adapters.nodes.web_enrichment.IndustrySearchService")
    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_비_트렌드_도메인은_web_enrichment_호출_안함(self, mock_svc, mock_search_cls):
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = _make_eval()
        mock_svc.judge.return_value = mock_judge
        mock_critic = MagicMock()
        mock_critic.critique.return_value = _make_eval()
        mock_svc.critic.return_value = mock_critic
        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search

        app, state = create_app(max_questions=5)
        state["mode"] = "interview"
        state["interview_phase"] = "evaluate"
        state["current_question_text"] = "FinFET 설명"
        state["current_question_domain"] = "소자"  # 트렌드 아님
        state["current_question_key_points"] = []
        state["messages"] = [HumanMessage(content="3D 트랜지스터")]

        result = app.invoke(state)

        mock_judge.evaluate.assert_called_once()
        mock_search.search.assert_not_called()  # 병렬 검색 안 됨
        assert "🌐 산업 최신 동향" not in result["display_output"]
