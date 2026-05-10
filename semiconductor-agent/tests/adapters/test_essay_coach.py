"""TDD: Essay coach (자소서 첨삭) adapter."""
from unittest.mock import MagicMock, patch

from langchain_core.messages import HumanMessage

from semiconductor.adapters.nodes.essay_coach import essay_evaluate_node, essay_present_node
from semiconductor.adapters.nodes.orchestrator import orchestrator_node, route_from_orchestrator
from semiconductor.adapters.state import create_initial_state
from semiconductor.domain.entities import EssayEvaluation


def _make_essay_eval(total: int = 80) -> EssayEvaluation:
    fit = min(total * 30 // 100, 30)
    struct = min(total * 25 // 100, 25)
    spec = min(total * 25 // 100, 25)
    write = total - fit - struct - spec
    write = max(0, min(write, 20))
    return EssayEvaluation(
        fit_score=fit, structure_score=struct, specificity_score=spec, writing_score=write,
        total_score=fit + struct + spec + write,
        feedback="좋은 자소서", strong_points=["구체적"], weak_points=["서론"],
        revised_excerpt="첨삭 예시...",
        culture_alignment="삼성 인재상 도전 일치",
    )


# ── Orchestrator 명령어 파싱 ──────────────────────────────────────


class TestEssayOrchestratorCommand:
    def test_자소서_명령_없는_인자는_present_phase로_가이드(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="/자소서")]
        result = orchestrator_node(s)
        assert result["mode"] == "essay"
        assert result["essay_phase"] == "present"
        assert result["essay_company"] is None

    def test_자소서_명령_company_item_파싱(self):
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="/자소서 samsung_ds 지원동기")]
        result = orchestrator_node(s)
        assert result["mode"] == "essay"
        assert result["essay_company"] == "samsung_ds"
        assert result["essay_item"] == "지원동기"

    def test_essay_mode_present_phase는_essay_present로_라우팅(self):
        s = dict(create_initial_state())
        s["mode"] = "essay"
        s["essay_phase"] = "present"
        assert route_from_orchestrator(s) == "essay_present"

    def test_essay_mode_evaluate_phase는_essay_evaluate로_라우팅(self):
        s = dict(create_initial_state())
        s["mode"] = "essay"
        s["essay_phase"] = "evaluate"
        assert route_from_orchestrator(s) == "essay_evaluate"


# ── essay_present_node ────────────────────────────────────────────


class TestEssayPresentNode:
    def test_company_item_둘다_있으면_prompt_표시_phase_evaluate로(self):
        s = dict(create_initial_state())
        s["essay_company"] = "samsung_ds"
        s["essay_item"] = "지원동기"
        result = essay_present_node(s)
        assert result["essay_phase"] == "evaluate"
        assert "지원동기" in result["display_output"]
        assert "1500자" in result["display_output"]

    def test_인자_없으면_사용_가이드_표시_idle_복귀(self):
        s = dict(create_initial_state())
        s["essay_company"] = None
        s["essay_item"] = None
        result = essay_present_node(s)
        assert result["mode"] == "idle"
        assert "/자소서" in result["display_output"]
        assert "samsung_ds" in result["display_output"]  # 회사 안내

    def test_지원하지_않는_항목은_거부_idle_복귀(self):
        s = dict(create_initial_state())
        s["essay_company"] = "samsung_ds"
        s["essay_item"] = "이상한항목"
        result = essay_present_node(s)
        assert result["mode"] == "idle"
        assert "❌" in result["display_output"]


# ── essay_evaluate_node ───────────────────────────────────────────


class TestEssayEvaluateNode:
    @patch("semiconductor.adapters.nodes.essay_coach.ClaudeEssayCoach")
    def test_사용자_자소서를_평가하고_출력에_점수_표시(self, mock_coach_cls):
        mock_coach = MagicMock()
        mock_coach.evaluate_essay.return_value = _make_essay_eval(total=85)
        mock_coach_cls.return_value = mock_coach

        s = dict(create_initial_state())
        s["essay_company"] = "samsung_ds"
        s["essay_item"] = "지원동기"
        s["messages"] = [HumanMessage(content="저는 삼성DS에 지원합니다...")]

        result = essay_evaluate_node(s)

        assert "85/100점" in result["display_output"]
        assert "[우수]" in result["display_output"]
        assert "✍️  첨삭 예시" in result["display_output"]
        # 평가 후 idle 복귀
        assert result["mode"] == "idle"
        assert result["essay_company"] is None
        # 누적 평가 저장
        assert len(result["essays_evaluated"]) == 1
        assert result["essays_evaluated"][0]["company"] == "samsung_ds"

    @patch("semiconductor.adapters.nodes.essay_coach.ClaudeEssayCoach")
    def test_빈_자소서는_거부(self, mock_coach_cls):
        s = dict(create_initial_state())
        s["essay_company"] = "samsung_ds"
        s["essay_item"] = "지원동기"
        s["messages"] = [HumanMessage(content="   ")]

        result = essay_evaluate_node(s)

        assert "비어있습니다" in result["display_output"]
        mock_coach_cls.assert_not_called()  # LLM 호출 없음

    def test_컨텍스트_손실시_가이드_복귀(self):
        # essay_company / essay_item 둘 다 None — 잘못된 진입
        s = dict(create_initial_state())
        s["messages"] = [HumanMessage(content="자소서 내용")]
        result = essay_evaluate_node(s)
        assert result["mode"] == "idle"
        assert "다시 시작" in result["display_output"]
