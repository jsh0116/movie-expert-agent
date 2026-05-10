"""Claude-based 인성면접 STAR 평가 — 한국어 자연스러움 활용."""
from __future__ import annotations

import os

from langchain.chat_models import init_chat_model
from pydantic import BaseModel

from semiconductor.domain.entities import BehavioralEvaluation, BehavioralQuestion
from semiconductor.domain.ports import IBehavioralCoach
from semiconductor.infrastructure.llm.tiers import model_for_role


class _BehavioralSchema(BaseModel):
    situation_score: int
    task_score: int
    action_score: int
    result_score: int
    culture_fit: int
    feedback: str
    strong_points: list[str]
    weak_points: list[str]
    improved_answer: str  # 답변 개선 예시 (3~5문장)


_COMPANY_VALUES = {
    "samsung_ds": "삼성 인재상 (도전·창의·정도·인간미·협력)",
    "sk_hynix": "SK 핵심가치 VWBE (Voluntary, Willingly, Brain, Engagement)",
}

_SYSTEM = """당신은 {company_label}의 인성면접 평가관입니다.
지원자 답변을 STAR 기법(Situation/Task/Action/Result)으로 평가합니다.

평가 기준 (총 100점):
- situation_score (0-20): Situation 명확도 (배경 설정)
- task_score (0-20):      Task 명확도 (본인 역할·목표)
- action_score (0-30):    Action 구체성 (본인이 한 행동, 가장 중요)
- result_score (0-20):    Result 정량화·임팩트
- culture_fit (0-10):     {culture_values} 부합도

추가 출력:
- feedback: 2~3문장 종합
- strong_points: 잘된 부분 1~3개
- weak_points: 보완 필요 1~3개
- improved_answer: STAR 기법으로 다시 쓴 모범답변 예시 (3~5문장)

질문이 평가하려는 역량: {competency}
질문: {question}"""


def _resolve_behavioral_model() -> str:
    explicit = os.getenv("LLM_MODEL_BEHAVIORAL")
    if explicit:
        return explicit if ":" in explicit else f"openai:{explicit}"
    # 인성면접은 한국어 자연스러움 + 평가 일관성 필요 → coach tier model
    tier = os.getenv("LLM_TIER", "premium")
    return model_for_role(tier, "coach")


class ClaudeBehavioralCoach(IBehavioralCoach):
    def __init__(self) -> None:
        model = _resolve_behavioral_model()
        kwargs: dict = {"temperature": 0.2}
        base_url = os.getenv("AI_BASE_URL")
        if base_url and model.startswith("openai:"):
            kwargs["base_url"] = base_url
        self._llm = init_chat_model(model, **kwargs).with_structured_output(_BehavioralSchema)

    def evaluate_behavioral(
        self,
        question: BehavioralQuestion,
        user_answer: str,
    ) -> BehavioralEvaluation:
        system = _SYSTEM.format(
            company_label="삼성전자 DS부문" if question.company == "samsung_ds" else "SK하이닉스",
            culture_values=_COMPANY_VALUES.get(question.company, "회사 인재상"),
            competency=question.competency,
            question=question.question,
        )
        result: _BehavioralSchema = self._llm.invoke([
            {"role": "system", "content": system},
            {"role": "user", "content": user_answer},
        ])
        total = (
            result.situation_score + result.task_score + result.action_score
            + result.result_score + result.culture_fit
        )
        return BehavioralEvaluation(
            situation_score=result.situation_score,
            task_score=result.task_score,
            action_score=result.action_score,
            result_score=result.result_score,
            culture_fit=result.culture_fit,
            total_score=total,
            feedback=result.feedback,
            strong_points=result.strong_points,
            weak_points=result.weak_points,
            improved_answer=result.improved_answer,
        )
