"""Aptitude test (GSAT/SKCT) nodes — 객관식 출제·채점, LLM 미사용.

Phase 패턴:
  aptitude_present  → 다음 문제 출제 (선택지 표시) → phase: present → evaluate
  aptitude_evaluate → 사용자 입력 (1~4) → 정답 비교 + 해설 → 다음 문제로
"""
from __future__ import annotations

from langchain_core.messages import HumanMessage

from semiconductor.adapters.state import InterviewState
from semiconductor.domain.entities import AptitudeQuestion
from semiconductor.infrastructure.aptitude.questions import pick_question


_NUMBER_MAP = {
    "1": 0, "2": 1, "3": 2, "4": 3, "5": 4,
    "①": 0, "②": 1, "③": 2, "④": 3, "⑤": 4,
}


def _parse_user_choice(text: str) -> int:
    """첫 글자만 잡아 0-based index로 변환. 잘못된 입력은 -1."""
    if not text:
        return -1
    head = text.strip()[:1]
    return _NUMBER_MAP.get(head, -1)


def _serialize(q: AptitudeQuestion) -> dict:
    return {
        "test_type": q.test_type,
        "domain": q.domain,
        "question": q.question,
        "choices": list(q.choices),
        "correct_index": q.correct_index,
        "explanation": q.explanation,
    }


def aptitude_present_node(state: InterviewState) -> dict:
    test_type = state.get("aptitude_test_type") or "GSAT"
    asked = state.get("aptitude_asked_count", 0)

    q = pick_question(test_type, asked)
    if q is None:
        return {
            "mode": "idle",
            "aptitude_phase": "present",
            "display_output": f"❌ {test_type} 문제 풀이 비어있습니다.",
        }

    choice_lines = "\n".join(f"  {i + 1}. {c}" for i, c in enumerate(q.choices))
    output = (
        f"🧠 [{test_type} — {q.domain}] 문제 {asked + 1}\n\n"
        f"{q.question}\n\n"
        f"{choice_lines}\n\n"
        "정답 번호(1~4)를 입력하세요:"
    )
    return {
        "aptitude_phase": "evaluate",
        "aptitude_current": _serialize(q),
        "display_output": output,
    }


def aptitude_evaluate_node(state: InterviewState) -> dict:
    current = state.get("aptitude_current")
    if not current:
        return {
            "mode": "idle",
            "aptitude_phase": "present",
            "display_output": "❌ 적성검사 컨텍스트 손실. /적성 으로 다시 시작하세요.",
        }

    human_msgs = [m for m in state.get("messages", []) if isinstance(m, HumanMessage)]
    user_text = human_msgs[-1].content if human_msgs else ""
    user_choice = _parse_user_choice(user_text)

    if user_choice < 0 or user_choice >= len(current["choices"]):
        # 잘못된 입력 — 다시 입력 받음 (phase 유지)
        return {
            "display_output": (
                f"❌ '{user_text.strip()[:20]}'은(는) 유효한 답이 아닙니다. "
                f"숫자 1~{len(current['choices'])} 중 하나를 입력하세요."
            ),
        }

    is_correct = user_choice == current["correct_index"]
    icon = "✅ 정답" if is_correct else "❌ 오답"
    correct_label = current["choices"][current["correct_index"]]
    user_label = current["choices"][user_choice]

    lines = [
        f"{icon}",
        f"  당신의 답: {user_choice + 1}. {user_label}",
        f"  정답:     {current['correct_index'] + 1}. {correct_label}",
        "",
        f"💡 풀이:\n{current['explanation']}",
    ]

    new_results = state.get("aptitude_results", []) + [{
        "test_type": current["test_type"],
        "domain": current["domain"],
        "question": current["question"],
        "user_choice": user_choice,
        "correct_index": current["correct_index"],
        "is_correct": is_correct,
    }]
    new_count = state.get("aptitude_asked_count", 0) + 1

    # 다음 문제 안내
    next_q = pick_question(current["test_type"], new_count)
    if next_q is not None:
        # 누적 정확도 표시
        correct_count = sum(1 for r in new_results if r["is_correct"])
        lines.append(f"\n📊 진행 {new_count}문제 — 정답률 {correct_count}/{new_count}")
        lines.append("\n다음 문제는 /적성 명령으로 계속 진행하세요.")
    else:
        lines.append("\n🎉 모든 문제를 풀었습니다!")

    return {
        "aptitude_results": new_results,
        "aptitude_asked_count": new_count,
        "aptitude_current": None,
        "aptitude_phase": "present",
        "mode": "idle",
        "display_output": "\n".join(lines),
    }
