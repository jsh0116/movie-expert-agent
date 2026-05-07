"""Mock Interviewer node — presents questions and evaluates answers."""
from __future__ import annotations

from langchain_core.messages import HumanMessage

from semiconductor.adapters.state import InterviewState
from semiconductor.application.use_cases.evaluate_answer import EvaluateAnswerUseCase
from semiconductor.application.use_cases.next_question import GetNextQuestionUseCase
from semiconductor.domain.entities import Question
from semiconductor.infrastructure.llm import LangChainLLMService
from semiconductor.infrastructure.question_bank import InMemoryQuestionRepository


def mock_interviewer_node(state: InterviewState) -> dict:
    repo = InMemoryQuestionRepository()
    next_q_uc = GetNextQuestionUseCase(repo)
    eval_uc = EvaluateAnswerUseCase(
        llm_judge=LangChainLLMService.judge(),
        llm_critic=LangChainLLMService.critic(),  # Self-Critique 검증 활성화
    )

    current_q_text = state.get("current_question_text")

    # ── Phase 1: no pending question → fetch and display the next one ──
    if current_q_text is None:
        q = next_q_uc.execute(
            company=state["company"],
            domain=state.get("domain"),
            asked_count=state["asked_count"],
            max_questions=state["max_questions"],
        )
        if q is None:
            return {
                "mode": "idle",
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
            "current_question_text": q.question,
            "current_question_domain": q.domain,
            "current_question_key_points": list(q.key_points),
            "display_output": output,
        }

    # ── Phase 2: pending question → evaluate the latest human message ──
    human_msgs = [m for m in state.get("messages", []) if isinstance(m, HumanMessage)]
    user_answer = human_msgs[-1].content if human_msgs else ""

    q = Question(
        domain=state["current_question_domain"],
        question=current_q_text,
        key_points=state.get("current_question_key_points") or [],
    )

    result = eval_uc.execute(question=q, user_answer=user_answer)

    eval_dict = {
        "question": result.question,
        "accuracy_score": result.accuracy_score,
        "depth_score": result.depth_score,
        "terminology_score": result.terminology_score,
        "total_score": result.total_score,
        "grade": result.grade,
        "feedback": result.feedback,
        "strong_points": result.strong_points,
        "weak_points": result.weak_points,
        "model_answer": result.model_answer,
        "specialist_commentary": result.specialist_commentary,
        "follow_up_question": result.follow_up_question,
    }

    new_asked = state["asked_count"] + 1
    remaining = state["max_questions"] - new_asked

    domain_label = state.get("current_question_domain") or ""
    header = f"📊 평가 결과 [{result.grade}] {result.total_score}/100점"
    if domain_label:
        header = f"🎓 [{domain_label} 전문가 평가] " + header

    output = (
        f"{header}\n\n"
        f"  정확성 {result.accuracy_score}/40 | 깊이 {result.depth_score}/30 | 전문용어 {result.terminology_score}/30\n\n"
        f"💬 {result.feedback}\n\n"
        f"✅ 잘한 점: {', '.join(result.strong_points) or '없음'}\n"
        f"📌 보완점:  {', '.join(result.weak_points) or '없음'}\n"
    )

    if result.specialist_commentary:
        output += f"\n🔬 전문가 코멘트:\n{result.specialist_commentary}\n"

    if result.model_answer:
        output += f"\n📚 모범답안:\n{result.model_answer}\n"

    if result.follow_up_question:
        output += f"\n💡 심화 질문 (선택): {result.follow_up_question}\n"

    if remaining > 0:
        output += f"\n남은 문제: {remaining}개 | 계속하려면 답변을 입력하세요."
    else:
        output += "\n\n🎉 모든 문제를 완료했습니다! /진단 으로 이해도 진단을 받아보세요."

    return {
        "evaluations": state.get("evaluations", []) + [eval_dict],
        "asked_count": new_asked,
        "current_question_text": None,
        "current_question_domain": None,
        "current_question_key_points": [],
        "display_output": output,
        "mode": "idle" if remaining <= 0 else "interview",
    }
