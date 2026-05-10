"""Phase 1 — 다음 질문 출제."""
from __future__ import annotations

from semiconductor.adapters.state import InterviewState
from semiconductor.application.use_cases.next_question import GetNextQuestionUseCase
from semiconductor.infrastructure.question_bank import InMemoryQuestionRepository


def mock_present_node(state: InterviewState) -> dict:
    """Fetch next question from pool and display it. Phase: present → evaluate."""
    repo = InMemoryQuestionRepository()
    next_q_uc = GetNextQuestionUseCase(repo)

    q = next_q_uc.execute(
        company=state["company"],
        domain=state.get("domain"),
        asked_count=state["asked_count"],
        max_questions=state["max_questions"],
    )
    if q is None:
        return {
            "mode": "idle",
            "interview_phase": "present",
            "display_output": (
                f"✅ 면접 완료! 총 {state['asked_count']}문제를 풀었습니다.\n"
                "  /진단 명령어로 이해도 진단을 받아보세요."
            ),
        }

    num = state["asked_count"] + 1
    output = (
        f"📝 [{q.domain}] 문제 {num}/{state['max_questions']}\n\n"
        f"{q.question}\n\n"
        "답변을 입력하세요:"
    )
    return {
        "interview_phase": "evaluate",
        "current_question_text": q.question,
        "current_question_domain": q.domain,
        "current_question_key_points": list(q.key_points),
        "display_output": output,
    }
