"""TDD: qa_coach ReAct loop — LLM이 tool_calls 발행 시 ToolNode로 라우팅."""
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from semiconductor.adapters.nodes.qa_coach import qa_coach_node, route_after_coach
from semiconductor.adapters.state import create_initial_state


class TestRouteAfterCoach:
    def test_AIMessage에_tool_calls_있으면_coach_tools로(self):
        s = dict(create_initial_state())
        s["messages"] = [
            HumanMessage(content="HBM3E 동향?"),
            AIMessage(content="", tool_calls=[
                {"id": "call_1", "name": "industry_trend_search", "args": {"query": "HBM3E"}}
            ]),
        ]
        assert route_after_coach(s) == "coach_tools"

    def test_AIMessage에_tool_calls_없으면_END(self):
        from langgraph.graph import END
        s = dict(create_initial_state())
        s["messages"] = [
            HumanMessage(content="hello"),
            AIMessage(content="answer"),
        ]
        assert route_after_coach(s) == END

    def test_messages_없으면_END(self):
        from langgraph.graph import END
        s = dict(create_initial_state())
        s["messages"] = []
        assert route_after_coach(s) == END


class TestQaCoachNode:
    def test_topic_없으면_안내_메시지(self):
        s = dict(create_initial_state())
        s["current_qa_topic"] = ""
        result = qa_coach_node(s)
        assert "주제를 알려주세요" in result["display_output"]

    @patch("semiconductor.adapters.nodes.qa_coach.init_chat_model")
    def test_LLM이_tool_calls_없는_응답_반환_시_hint_count_증가(self, mock_init):
        # 일반 응답 → END 경로, hint_count 증가
        ai_msg = AIMessage(content="ALD에 대해 어디까지 아세요?", tool_calls=[])
        bound = MagicMock()
        bound.invoke.return_value = ai_msg
        chat = MagicMock()
        chat.bind_tools.return_value = bound
        mock_init.return_value = chat

        s = dict(create_initial_state())
        s["current_qa_topic"] = "ALD"
        s["hint_count"] = 0
        s["messages"] = [HumanMessage(content="ALD가 뭔가요?")]

        result = qa_coach_node(s)

        assert result["hint_count"] == 1  # 0 → 1
        assert result["display_output"] == "ALD에 대해 어디까지 아세요?"
        assert result["messages"][0] == ai_msg

    @patch("semiconductor.adapters.nodes.qa_coach.init_chat_model")
    def test_LLM이_tool_calls_반환시_hint_count_증가_안함_display도_안함(self, mock_init):
        # tool_calls 응답 → 루프 (아직 최종 답변 아님). hint_count 보존.
        ai_msg = AIMessage(content="", tool_calls=[
            {"id": "call_1", "name": "industry_trend_search", "args": {"query": "HBM"}}
        ])
        bound = MagicMock()
        bound.invoke.return_value = ai_msg
        chat = MagicMock()
        chat.bind_tools.return_value = bound
        mock_init.return_value = chat

        s = dict(create_initial_state())
        s["current_qa_topic"] = "HBM"
        s["hint_count"] = 1
        s["messages"] = [HumanMessage(content="요즘 HBM3E 어떻게 됐어?")]

        result = qa_coach_node(s)

        assert "hint_count" not in result  # 보존
        assert "display_output" not in result  # 아직 출력 안 함
        assert result["messages"][0] == ai_msg

    @patch("semiconductor.adapters.nodes.qa_coach.init_chat_model")
    def test_qa_coach는_Anthropic_Claude_Sonnet_provider_spec으로_호출(self, mock_init):
        # 권장 매핑 확인 — coach는 Claude
        ai_msg = AIMessage(content="x", tool_calls=[])
        bound = MagicMock()
        bound.invoke.return_value = ai_msg
        chat = MagicMock()
        chat.bind_tools.return_value = bound
        mock_init.return_value = chat

        s = dict(create_initial_state())
        s["current_qa_topic"] = "FinFET"
        s["messages"] = [HumanMessage(content="설명해줘")]
        qa_coach_node(s)

        spec = mock_init.call_args.args[0]
        assert spec == "anthropic:claude-sonnet-4-6"
