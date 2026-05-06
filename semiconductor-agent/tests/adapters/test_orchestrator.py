"""TDD: Orchestrator node — command parsing, routing, mid-interview guard."""
from langchain_core.messages import HumanMessage

from semiconductor.adapters.nodes.orchestrator import (
    orchestrator_node,
    route_from_orchestrator,
)
from semiconductor.adapters.state import create_initial_state


def _state_with_msg(text: str, **overrides) -> dict:
    s = dict(create_initial_state())
    s["messages"] = [HumanMessage(content=text)]
    s.update(overrides)
    return s


# ── orchestrator_node ──────────────────────────────────────────────────────────


class TestOrchestratorNode:
    def test_인터뷰_명령어로_면접_모드_전환(self):
        # given: 사용자가 /인터뷰 입력
        state = _state_with_msg("/인터뷰")
        # when
        result = orchestrator_node(state)
        # then
        assert result["mode"] == "interview"

    def test_영문_interview_명령어도_동작(self):
        state = _state_with_msg("/interview")
        result = orchestrator_node(state)
        assert result["mode"] == "interview"

    def test_qa_명령어로_코칭_모드_전환(self):
        # given: idle 상태에서 /qa 입력
        state = _state_with_msg("/qa")
        result = orchestrator_node(state)
        assert result["mode"] == "qa"
        assert result["hint_count"] == 0

    def test_qa_주제_포함시_current_qa_topic_설정(self):
        state = _state_with_msg("/qa ALD와 CVD 차이")
        result = orchestrator_node(state)
        assert result["mode"] == "qa"
        assert result["current_qa_topic"] == "ALD와 CVD 차이"

    def test_코칭_명령어도_qa_모드_전환(self):
        state = _state_with_msg("/코칭 FinFET")
        result = orchestrator_node(state)
        assert result["mode"] == "qa"

    def test_면접_진행중_qa_요청시_경고_반환(self):
        # given: 면접 진행 중(mode=interview, 질문 출제됨)에서 /qa 입력
        state = _state_with_msg(
            "/qa",
            mode="interview",
            current_question_text="FinFET과 GAA의 차이는?",
        )
        # when
        result = orchestrator_node(state)
        # then: 모드 전환 없이 경고 메시지
        assert "mode" not in result
        assert "⚠️" in result["display_output"]

    def test_면접_질문_없을때_qa는_허용됨(self):
        # given: mode=interview이지만 아직 질문이 없는 경우 (면접 방금 시작)
        state = _state_with_msg(
            "/qa",
            mode="interview",
            current_question_text=None,
        )
        result = orchestrator_node(state)
        # 질문이 없으면 가드가 발동하지 않아야 함
        assert result.get("mode") == "qa"

    def test_진단_명령어로_진단_모드_전환(self):
        state = _state_with_msg("/진단")
        result = orchestrator_node(state)
        assert result["mode"] == "diagnostic"

    def test_영문_diagnostic_명령어도_동작(self):
        state = _state_with_msg("/diagnostic")
        result = orchestrator_node(state)
        assert result["mode"] == "diagnostic"

    def test_알수없는_명령어는_빈_딕셔너리_반환(self):
        state = _state_with_msg("FinFET이 뭔가요?")
        result = orchestrator_node(state)
        assert result == {}

    def test_메시지_없으면_빈_딕셔너리_반환(self):
        s = dict(create_initial_state())
        s["messages"] = []
        result = orchestrator_node(s)
        assert result == {}

    def test_대소문자_구분없이_인터뷰_명령어_인식(self):
        state = _state_with_msg("/INTERVIEW")
        result = orchestrator_node(state)
        assert result["mode"] == "interview"


# ── route_from_orchestrator ────────────────────────────────────────────────────


class TestRouteFromOrchestrator:
    def test_interview_모드는_mock_interviewer로_라우팅(self):
        s = dict(create_initial_state())
        s["mode"] = "interview"
        assert route_from_orchestrator(s) == "mock_interviewer"

    def test_qa_모드는_qa_coach로_라우팅(self):
        s = dict(create_initial_state())
        s["mode"] = "qa"
        assert route_from_orchestrator(s) == "qa_coach"

    def test_diagnostic_모드는_diagnostic으로_라우팅(self):
        s = dict(create_initial_state())
        s["mode"] = "diagnostic"
        assert route_from_orchestrator(s) == "diagnostic"

    def test_idle_모드는_END로_라우팅(self):
        from langgraph.graph import END
        s = dict(create_initial_state())
        s["mode"] = "idle"
        assert route_from_orchestrator(s) == END
