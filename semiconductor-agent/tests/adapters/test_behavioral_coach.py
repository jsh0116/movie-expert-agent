"""TDD: Behavioral interview (인성면접 STAR) adapter."""
from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage

from semiconductor.adapters.nodes.behavioral_coach import (
    behavioral_evaluate_node,
    behavioral_present_node,
)
from semiconductor.adapters.nodes.orchestrator import orchestrator_node, route_from_orchestrator
from semiconductor.adapters.state import create_initial_state
from semiconductor.domain.entities import BehavioralEvaluation


def _make_eval(total: int = 75) -> BehavioralEvaluation:
    return BehavioralEvaluation(
        situation_score=15, task_score=15, action_score=25,
        result_score=15, culture_fit=5, total_score=75,
        feedback="구체적으로 잘 답변", strong_points=["수치"], weak_points=["서론"],
        improved_answer="모범 답변 STAR...",
    )


class TestBehavioralCommand:
    def test_인성_명령_company_없으면_samsung_ds_기본(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="/인성")]
        result = orchestrator_node(s)
        assert result["mode"] == "behavioral"
        assert result["behavioral_company"] == "samsung_ds"
        assert result["behavioral_phase"] == "present"

    def test_인성_명령_company_지정(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="/인성 sk_hynix")]
        result = orchestrator_node(s)
        assert result["behavioral_company"] == "sk_hynix"

    def test_routing_present_phase(self):
        s = dict(create_initial_state())
        s["mode"] = "behavioral"
        s["behavioral_phase"] = "present"
        assert route_from_orchestrator(s) == "behavioral_present"

    def test_routing_evaluate_phase(self):
        s = dict(create_initial_state())
        s["mode"] = "behavioral"
        s["behavioral_phase"] = "evaluate"
        assert route_from_orchestrator(s) == "behavioral_evaluate"


class TestBehavioralPresentNode:
    def test_질문_출제_phase_evaluate로(self):
        s = dict(create_initial_state())
        s["behavioral_company"] = "samsung_ds"
        result = behavioral_present_node(s)
        assert result["behavioral_phase"] == "evaluate"
        assert result["behavioral_question_text"]
        assert result["behavioral_competency"]
        assert "STAR" in result["display_output"]


class TestBehavioralEvaluateNode:
    @patch("semiconductor.adapters.nodes.behavioral_coach.LangChainLLMService")
    def test_답변_평가_후_idle_복귀(self, mock_svc):
        mock_coach = MagicMock()
        mock_coach.evaluate_behavioral.return_value = _make_eval()
        mock_svc.behavioral.return_value = mock_coach

        s = dict(create_initial_state())
        s["behavioral_company"] = "samsung_ds"
        s["behavioral_question_text"] = "갈등 사례를 답해주세요"
        s["behavioral_competency"] = "갈등극복"
        s["messages"] = [HumanMessage(content="저는 팀에서...")]

        result = behavioral_evaluate_node(s)

        assert "75/100" in result["display_output"]
        assert "Action 25/30" in result["display_output"]
        assert "✍️  STAR 모범답변" in result["display_output"]
        assert result["mode"] == "idle"
        assert result["behavioral_question_text"] is None
        assert len(result["behaviorals_evaluated"]) == 1

    @patch("semiconductor.adapters.nodes.behavioral_coach.LangChainLLMService")
    def test_빈_답변_거부(self, mock_svc):
        s = dict(create_initial_state())
        s["behavioral_company"] = "samsung_ds"
        s["behavioral_question_text"] = "x"
        s["behavioral_competency"] = "리더십"
        s["messages"] = [HumanMessage(content="  ")]
        result = behavioral_evaluate_node(s)
        assert "비어있습니다" in result["display_output"]
        mock_svc.behavioral.assert_not_called()

    def test_컨텍스트_손실_가이드_복귀(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="answer")]
        result = behavioral_evaluate_node(s)
        assert result["mode"] == "idle"
        assert "다시 시작" in result["display_output"]
