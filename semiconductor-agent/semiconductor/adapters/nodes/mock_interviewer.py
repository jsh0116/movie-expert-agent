"""Mock Interviewer — split into 3 graph nodes for visibility:
  mock_present_node  → fetch + display next question
  mock_evaluate_node → judge user answer (1차 평가)
  mock_critic_node   → self-critique (2차 검증) + display + advance
"""
from __future__ import annotations

from langchain_core.messages import HumanMessage

from semiconductor.adapters.state import InterviewState
from semiconductor.application.use_cases.critique_evaluation import CritiqueEvaluationUseCase
from semiconductor.application.use_cases.evaluate_answer import EvaluateAnswerUseCase
from semiconductor.application.use_cases.next_question import GetNextQuestionUseCase
from semiconductor.domain.entities import EvaluationResult, Question
from semiconductor.infrastructure.llm import LangChainLLMService
from semiconductor.infrastructure.question_bank import InMemoryQuestionRepository


# ── Node 1: Present next question ─────────────────────────────────

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


# ── Node 2: Evaluate (Judge only) ─────────────────────────────────

def mock_evaluate_node(state: InterviewState) -> dict:
    """1차 평가: 도메인 전문가 페르소나로 judge가 답변 평가."""
    eval_uc = EvaluateAnswerUseCase(llm_judge=LangChainLLMService.judge())  # critic은 다음 노드에서

    human_msgs = [m for m in state.get("messages", []) if isinstance(m, HumanMessage)]
    user_answer = human_msgs[-1].content if human_msgs else ""

    q = Question(
        domain=state["current_question_domain"],
        question=state["current_question_text"],
        key_points=state.get("current_question_key_points") or [],
    )

    result = eval_uc.execute(question=q, user_answer=user_answer)

    return {
        "pending_evaluation": _serialize_eval(result),
    }


# ── Node 3: Critique + Advance ────────────────────────────────────

def mock_critic_node(state: InterviewState) -> dict:
    """2차 검증: critic이 1차 평가 검토. 출력 생성 + 다음 질문으로 진행."""
    pending = state.get("pending_evaluation")
    if pending is None:
        return {"display_output": "❌ 평가 데이터가 없습니다."}

    initial = _deserialize_eval(pending)

    critique_uc = CritiqueEvaluationUseCase(llm_critic=LangChainLLMService.critic())
    q = Question(
        domain=state["current_question_domain"],
        question=state["current_question_text"],
        key_points=state.get("current_question_key_points") or [],
    )
    human_msgs = [m for m in state.get("messages", []) if isinstance(m, HumanMessage)]
    user_answer = human_msgs[-1].content if human_msgs else ""

    final = critique_uc.execute(
        question=q,
        user_answer=user_answer,
        initial_evaluation=initial,
    )

    new_asked = state["asked_count"] + 1
    remaining = state["max_questions"] - new_asked

    domain_label = state.get("current_question_domain") or ""
    header = f"📊 평가 결과 [{final.grade}] {final.total_score}/100점"
    if domain_label:
        header = f"🎓 [{domain_label} 전문가 평가] " + header

    output = (
        f"{header}\n\n"
        f"  정확성 {final.accuracy_score}/40 | 깊이 {final.depth_score}/30 | 전문용어 {final.terminology_score}/30\n\n"
        f"💬 {final.feedback}\n\n"
        f"✅ 잘한 점: {', '.join(final.strong_points) or '없음'}\n"
        f"📌 보완점:  {', '.join(final.weak_points) or '없음'}\n"
    )

    if final.specialist_commentary:
        output += f"\n🔬 전문가 코멘트:\n{final.specialist_commentary}\n"

    if final.model_answer:
        output += f"\n📚 모범답안:\n{final.model_answer}\n"

    if final.follow_up_question:
        output += f"\n💡 심화 질문 (선택): {final.follow_up_question}\n"

    # 트렌드 도메인 병렬 웹 검색 결과가 있으면 출력에 첨부
    enrichment = state.get("web_enrichment")
    if enrichment:
        output += f"\n🌐 산업 최신 동향 (병렬 검색):\n{enrichment[:600]}\n"  # 길면 잘림

    if remaining > 0:
        output += f"\n남은 문제: {remaining}개 | 계속하려면 답변을 입력하세요."
    else:
        output += "\n\n🎉 모든 문제를 완료했습니다! /진단 으로 이해도 진단을 받아보세요."

    return {
        "evaluations": state.get("evaluations", []) + [_serialize_eval(final)],
        "asked_count": new_asked,
        "current_question_text": None,
        "current_question_domain": None,
        "current_question_key_points": [],
        "pending_evaluation": None,
        "web_enrichment": None,  # turn 종료 시 정리
        "interview_phase": "present",
        "display_output": output,
        "mode": "idle" if remaining <= 0 else "interview",
    }


# ── Serialization helpers ─────────────────────────────────────────

def _serialize_eval(e: EvaluationResult) -> dict:
    return {
        "question": e.question,
        "accuracy_score": e.accuracy_score,
        "depth_score": e.depth_score,
        "terminology_score": e.terminology_score,
        "total_score": e.total_score,
        "grade": e.grade,
        "feedback": e.feedback,
        "strong_points": list(e.strong_points),
        "weak_points": list(e.weak_points),
        "model_answer": e.model_answer,
        "specialist_commentary": e.specialist_commentary,
        "follow_up_question": e.follow_up_question,
    }


def _deserialize_eval(d: dict) -> EvaluationResult:
    return EvaluationResult(
        accuracy_score=d["accuracy_score"],
        depth_score=d["depth_score"],
        terminology_score=d["terminology_score"],
        total_score=d["total_score"],
        feedback=d.get("feedback", ""),
        strong_points=d.get("strong_points", []),
        weak_points=d.get("weak_points", []),
        question=d["question"],
        model_answer=d.get("model_answer", ""),
        specialist_commentary=d.get("specialist_commentary", ""),
        follow_up_question=d.get("follow_up_question", ""),
    )
