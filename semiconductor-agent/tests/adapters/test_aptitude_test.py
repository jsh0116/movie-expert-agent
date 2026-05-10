"""TDD: Aptitude test (GSAT/SKCT) adapter — LLM 미사용, 정적 채점."""
from langchain_core.messages import HumanMessage

from semiconductor.adapters.nodes.aptitude_test import (
    _parse_user_choice,
    aptitude_evaluate_node,
    aptitude_present_node,
)
from semiconductor.adapters.nodes.orchestrator import orchestrator_node, route_from_orchestrator
from semiconductor.adapters.state import create_initial_state


# ── Choice parser ────────────────────────────────────────────────


class TestParseUserChoice:
    def test_숫자_파싱(self):
        assert _parse_user_choice("1") == 0
        assert _parse_user_choice("4") == 3

    def test_원형숫자_파싱(self):
        assert _parse_user_choice("①") == 0
        assert _parse_user_choice("③") == 2

    def test_숫자_뒤에_텍스트_있어도_첫글자만(self):
        assert _parse_user_choice("2번이요") == 1
        assert _parse_user_choice("3. 어쩌고") == 2

    def test_숫자_아니면_invalid(self):
        assert _parse_user_choice("answer") == -1
        assert _parse_user_choice("") == -1
        assert _parse_user_choice("9") == -1  # _NUMBER_MAP에 없음


# ── Orchestrator command ──────────────────────────────────────────


class TestAptitudeOrchestratorCommand:
    def test_적성_명령_GSAT_파싱(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="/적성 GSAT")]
        result = orchestrator_node(s)
        assert result["mode"] == "aptitude"
        assert result["aptitude_test_type"] == "GSAT"
        assert result["aptitude_phase"] == "present"

    def test_적성_명령_SKCT_파싱(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="/적성 SKCT")]
        result = orchestrator_node(s)
        assert result["aptitude_test_type"] == "SKCT"

    def test_적성_명령_인자_없으면_GSAT_기본(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="/적성")]
        result = orchestrator_node(s)
        assert result["aptitude_test_type"] == "GSAT"

    def test_잘못된_test_type_GSAT으로_fallback(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="/적성 ABC")]
        result = orchestrator_node(s)
        assert result["aptitude_test_type"] == "GSAT"

    def test_aptitude_routing_present(self):
        s = dict(create_initial_state())
        s["mode"] = "aptitude"
        s["aptitude_phase"] = "present"
        assert route_from_orchestrator(s) == "aptitude_present"

    def test_aptitude_routing_evaluate(self):
        s = dict(create_initial_state())
        s["mode"] = "aptitude"
        s["aptitude_phase"] = "evaluate"
        assert route_from_orchestrator(s) == "aptitude_evaluate"


# ── present node ─────────────────────────────────────────────────


class TestAptitudePresentNode:
    def test_GSAT_문제_출제_phase_evaluate로(self):
        s = dict(create_initial_state())
        s["aptitude_test_type"] = "GSAT"
        s["aptitude_asked_count"] = 0
        result = aptitude_present_node(s)
        assert result["aptitude_phase"] == "evaluate"
        assert result["aptitude_current"] is not None
        assert result["aptitude_current"]["test_type"] == "GSAT"
        assert "GSAT" in result["display_output"]
        assert "1." in result["display_output"]  # 선택지

    def test_SKCT_문제_출제(self):
        s = dict(create_initial_state())
        s["aptitude_test_type"] = "SKCT"
        result = aptitude_present_node(s)
        assert result["aptitude_current"]["test_type"] == "SKCT"


# ── evaluate node ────────────────────────────────────────────────


class TestAptitudeEvaluateNode:
    def _state_with_current(self, correct_index: int = 1):
        s = dict(create_initial_state())
        s["aptitude_test_type"] = "GSAT"
        s["aptitude_current"] = {
            "test_type": "GSAT",
            "domain": "수리",
            "question": "1+1=?",
            "choices": ["1", "2", "3", "4"],
            "correct_index": correct_index,
            "explanation": "1+1=2",
        }
        return s

    def test_정답_입력시_정답_표시(self):
        s = self._state_with_current(correct_index=1)
        s["messages"] = [HumanMessage(content="2")]
        result = aptitude_evaluate_node(s)
        assert "✅ 정답" in result["display_output"]
        assert result["aptitude_results"][0]["is_correct"] is True

    def test_오답_입력시_오답_표시_및_정답_안내(self):
        s = self._state_with_current(correct_index=1)
        s["messages"] = [HumanMessage(content="3")]
        result = aptitude_evaluate_node(s)
        assert "❌ 오답" in result["display_output"]
        assert result["aptitude_results"][0]["is_correct"] is False
        assert result["aptitude_results"][0]["user_choice"] == 2

    def test_잘못된_입력은_phase_유지_재입력_요청(self):
        s = self._state_with_current(correct_index=1)
        s["messages"] = [HumanMessage(content="abc")]
        result = aptitude_evaluate_node(s)
        # 잘못된 입력 → 누적 결과 변경 없음, phase 유지
        assert "유효한 답이 아닙니다" in result["display_output"]
        assert "aptitude_results" not in result

    def test_평가_후_idle_복귀_누적_정확도_표시(self):
        s = self._state_with_current(correct_index=1)
        s["messages"] = [HumanMessage(content="2")]
        result = aptitude_evaluate_node(s)
        assert result["mode"] == "idle"
        assert result["aptitude_phase"] == "present"
        assert result["aptitude_current"] is None
        assert result["aptitude_asked_count"] == 1
        assert "📊 진행 1문제" in result["display_output"]

    def test_컨텍스트_손실_가이드(self):
        s = dict(create_initial_state())
        s["aptitude_current"] = None
        s["messages"] = [HumanMessage(content="2")]
        result = aptitude_evaluate_node(s)
        assert result["mode"] == "idle"
        assert "다시 시작" in result["display_output"]
