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


def _make_eval(
    model_answer: str = "",
    specialist_commentary: str = "",
    follow_up_question: str = "",
) -> EvaluationResult:
    return EvaluationResult(
        accuracy_score=30, depth_score=20, terminology_score=20,
        total_score=70, feedback="좋은 답변", strong_points=["정의"],
        weak_points=["깊이"], question="FinFET 설명하세요",
        model_answer=model_answer,
        specialist_commentary=specialist_commentary,
        follow_up_question=follow_up_question,
    )


class TestMockInterviewerModelAnswer:
    def _setup_mocks(self, mock_svc, evaluation):
        """judge는 평가 반환, critic은 그대로 통과시킴."""
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = evaluation
        mock_svc.judge.return_value = mock_judge
        mock_critic = MagicMock()
        mock_critic.critique.side_effect = lambda question, user_answer, initial_evaluation: initial_evaluation
        mock_svc.critic.return_value = mock_critic

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_평가_결과에_모범답안이_있으면_출력에_포함된다(self, mock_svc):
        self._setup_mocks(mock_svc, _make_eval(
            model_answer="FinFET은 3D 구조의 트랜지스터로, 게이트가 채널을 3면에서 둘러싸 단채널 효과를 억제합니다."
        ))
        result = mock_interviewer_node(_phase2_state())
        assert "📚 모범답안" in result["display_output"]
        assert "FinFET은 3D" in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_모범답안이_빈_문자열이면_섹션이_생략된다(self, mock_svc):
        self._setup_mocks(mock_svc, _make_eval(model_answer=""))
        result = mock_interviewer_node(_phase2_state())
        assert "📚 모범답안" not in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_eval_dict에_model_answer가_직렬화된다(self, mock_svc):
        self._setup_mocks(mock_svc, _make_eval(model_answer="모범답안 텍스트"))
        result = mock_interviewer_node(_phase2_state())
        evals = result["evaluations"]
        assert len(evals) == 1
        assert evals[0]["model_answer"] == "모범답안 텍스트"

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_critic이_호출된다_self_critique_레이어_검증(self, mock_svc):
        # mock_interviewer 노드는 평가 후 반드시 critic.critique을 호출해야 함
        eval_result = _make_eval(model_answer="x")
        mock_judge = MagicMock()
        mock_judge.evaluate.return_value = eval_result
        mock_svc.judge.return_value = mock_judge
        mock_critic = MagicMock()
        mock_critic.critique.return_value = eval_result
        mock_svc.critic.return_value = mock_critic

        mock_interviewer_node(_phase2_state())

        mock_critic.critique.assert_called_once()

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_도메인_전문가_평가_헤더가_출력에_포함된다(self, mock_svc):
        # 질문 도메인이 "소자"면 출력 헤더에 "[소자 전문가 평가]"가 들어가야 함
        self._setup_mocks(mock_svc, _make_eval(specialist_commentary="x"))
        result = mock_interviewer_node(_phase2_state())
        assert "[소자 전문가 평가]" in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_specialist_commentary가_있으면_전문가_코멘트_섹션_출력(self, mock_svc):
        self._setup_mocks(mock_svc, _make_eval(
            specialist_commentary="소자 전문가 관점에서 게이트 산화막을 더 명확히 설명하면 좋겠습니다."
        ))
        result = mock_interviewer_node(_phase2_state())
        assert "🔬 전문가 코멘트" in result["display_output"]
        assert "게이트 산화막" in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_specialist_commentary_빈값이면_섹션_생략(self, mock_svc):
        self._setup_mocks(mock_svc, _make_eval(specialist_commentary=""))
        result = mock_interviewer_node(_phase2_state())
        assert "🔬 전문가 코멘트" not in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_follow_up_질문이_있으면_심화_질문_섹션_표시(self, mock_svc):
        self._setup_mocks(mock_svc, _make_eval(
            follow_up_question="그럼 FinFET에서 GAA로 넘어간 이유는 무엇인가요?"
        ))
        result = mock_interviewer_node(_phase2_state())
        assert "💡 심화 질문" in result["display_output"]
        assert "GAA로 넘어간 이유" in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_follow_up_빈값이면_심화_질문_섹션_생략(self, mock_svc):
        self._setup_mocks(mock_svc, _make_eval(follow_up_question=""))
        result = mock_interviewer_node(_phase2_state())
        assert "💡 심화 질문" not in result["display_output"]

    @patch("semiconductor.adapters.nodes.mock_interviewer.LangChainLLMService")
    def test_eval_dict에_follow_up_question_직렬화(self, mock_svc):
        self._setup_mocks(mock_svc, _make_eval(follow_up_question="후속질문"))
        result = mock_interviewer_node(_phase2_state())
        assert result["evaluations"][0]["follow_up_question"] == "후속질문"
