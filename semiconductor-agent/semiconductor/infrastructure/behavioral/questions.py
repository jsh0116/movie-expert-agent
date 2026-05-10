"""인성면접 질문 풀 (Phase 2A)."""
from __future__ import annotations

import random

from semiconductor.domain.entities import BehavioralQuestion

_QUESTIONS: list[BehavioralQuestion] = [
    BehavioralQuestion(
        company="samsung_ds",
        question="팀 프로젝트에서 팀원과 의견 충돌이 있었던 사례와 본인이 어떻게 해결했는지 STAR 기법으로 답변해주세요.",
        competency="갈등극복",
    ),
    BehavioralQuestion(
        company="samsung_ds",
        question="기존 방식이 비효율적이라고 판단해 새로운 방식을 시도한 경험과 그 결과를 답해주세요.",
        competency="도전",
    ),
    BehavioralQuestion(
        company="samsung_ds",
        question="본인이 주도적으로 팀을 이끌었던 경험을 구체적으로 답해주세요.",
        competency="리더십",
    ),
    BehavioralQuestion(
        company="sk_hynix",
        question="복잡한 문제를 분석·해결한 경험과 사용한 접근법을 답해주세요.",
        competency="문제해결",
    ),
    BehavioralQuestion(
        company="sk_hynix",
        question="다양한 배경의 팀원들과 협업해 성과를 낸 경험을 답해주세요.",
        competency="협력",
    ),
    BehavioralQuestion(
        company="sk_hynix",
        question="실패 경험과 그로부터 배운 점, 이후 어떻게 적용했는지 답해주세요.",
        competency="도전",
    ),
]


def get_questions(company: str | None = None) -> list[BehavioralQuestion]:
    if company is None:
        return list(_QUESTIONS)
    return [q for q in _QUESTIONS if q.company == company]


def pick_question(company: str | None, asked_count: int) -> BehavioralQuestion | None:
    pool = get_questions(company)
    if not pool:
        return None
    return pool[asked_count % len(pool)]
