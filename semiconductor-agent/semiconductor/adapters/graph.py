"""LangGraph assembly — wires all adapter nodes into a compiled StateGraph."""
from __future__ import annotations

from typing import Optional

from langgraph.graph import END, StateGraph

from semiconductor.adapters.nodes.diagnostic import diagnostic_node
from semiconductor.adapters.nodes.mock_interviewer import (
    mock_critic_node,
    mock_evaluate_node,
    mock_present_node,
)
from semiconductor.adapters.nodes.orchestrator import orchestrator_node, route_from_orchestrator
from semiconductor.adapters.nodes.qa_coach import qa_coach_node
from semiconductor.adapters.state import InterviewState, create_initial_state


def create_app(
    company: str = "samsung_ds",
    domain: Optional[str] = None,
    max_questions: int = 5,
):
    """Build and compile the interview StateGraph.

    Topology:
        START → orchestrator
                  ├──▶ mock_present  ──▶ END                 (질문 출제 turn)
                  ├──▶ mock_evaluate ──▶ mock_critic ──▶ END (답변 평가 turn, 2-pass)
                  ├──▶ qa_coach      ──▶ END
                  ├──▶ diagnostic    ──▶ END
                  └──▶ END (idle)

    Returns:
        (app, state) — compiled LangGraph app and an initialized state dict.
    """
    builder = StateGraph(InterviewState)

    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("mock_present", mock_present_node)
    builder.add_node("mock_evaluate", mock_evaluate_node)
    builder.add_node("mock_critic", mock_critic_node)
    builder.add_node("qa_coach", qa_coach_node)
    builder.add_node("diagnostic", diagnostic_node)

    builder.set_entry_point("orchestrator")

    builder.add_conditional_edges(
        "orchestrator",
        route_from_orchestrator,
        {
            "mock_present": "mock_present",
            "mock_evaluate": "mock_evaluate",
            "qa_coach": "qa_coach",
            "diagnostic": "diagnostic",
            END: END,
        },
    )

    # 평가 turn은 evaluate → critic 직렬 연결 (turn 내 2-pass)
    builder.add_edge("mock_evaluate", "mock_critic")
    builder.add_edge("mock_critic", END)
    builder.add_edge("mock_present", END)
    builder.add_edge("qa_coach", END)
    builder.add_edge("diagnostic", END)

    app = builder.compile()
    state = create_initial_state(company=company, domain=domain, max_questions=max_questions)

    return app, state
