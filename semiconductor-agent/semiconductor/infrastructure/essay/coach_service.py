"""Claude-based 자소서 첨삭 — 한국어 작문 자연스러움이 핵심이라 Anthropic 사용."""
from __future__ import annotations

import os

from langchain.chat_models import init_chat_model
from pydantic import BaseModel

from semiconductor.domain.entities import EssayEvaluation, EssayPrompt
from semiconductor.domain.ports import IEssayCoach
from semiconductor.infrastructure.llm.safety import INJECTION_GUARD, wrap_user_input
from semiconductor.infrastructure.llm.tiers import model_for_role
from semiconductor.infrastructure.observability.usage_log import log_llm_call


class _EssaySchema(BaseModel):
    fit_score: int
    structure_score: int
    specificity_score: int
    writing_score: int
    feedback: str
    strong_points: list[str]
    weak_points: list[str]
    revised_excerpt: str  # 약점 부분 1~2문장 첨삭 예시
    culture_alignment: str  # "삼성 인재상 X와 일치" 같은 한 줄


_COMPANY_PERSONA = {
    "samsung_ds": (
        "당신은 삼성전자 DS부문 인사팀의 자소서 평가 전문가입니다. "
        "삼성 인재상(도전, 창의, 정도, 인간미, 협력)과 부합하는지를 중점 평가합니다."
    ),
    "sk_hynix": (
        "당신은 SK하이닉스 인사팀의 자소서 평가 전문가입니다. "
        "SK 핵심가치 VWBE(Voluntary, Willingly, Brain, Engagement)와 부합하는지를 중점 평가합니다."
    ),
}

_SYSTEM = """{persona}

지원자의 자소서를 다음 4축으로 평가하세요. 한국어로 작성하세요.

평가 항목:
- fit_score (0–30): 회사 인재상 부합도 (가장 중요)
- structure_score (0–25): 구조 (서론-본론-결론, STAR 기법, 논리 흐름)
- specificity_score (0–25): 구체성 (수치, 사례, 본인 액션, 결과)
- writing_score (0–20): 한국어 작문 (자연스러움, 어휘 다양성, 문장력)

추가 출력:
- feedback: 2~3문장 종합 피드백
- strong_points: 잘된 부분 1~3개
- weak_points: 보완 필요 1~3개
- revised_excerpt: 약점 부분 중 1~2문장을 골라 첨삭 예시 제시
- culture_alignment: "{company} 인재상 X와 일치/불일치" 한 줄

자소서 항목: {item}
항목 의도: {item_description}
글자 수 제한: {word_limit}자"""


def _resolve_essay_model() -> str:
    explicit = os.getenv("LLM_MODEL_ESSAY")
    if explicit:
        return explicit if ":" in explicit else f"openai:{explicit}"
    # 자소서는 한국어 작문 비중 큼 → coach tier model 재사용 (premium=Claude Sonnet)
    tier = os.getenv("LLM_TIER", "premium")
    return model_for_role(tier, "coach")


class ClaudeEssayCoach(IEssayCoach):
    def __init__(self) -> None:
        model = _resolve_essay_model()
        kwargs: dict = {"temperature": 0.3}
        base_url = os.getenv("AI_BASE_URL")
        if base_url and model.startswith("openai:"):
            kwargs["base_url"] = base_url
        self._llm = init_chat_model(model, **kwargs).with_structured_output(_EssaySchema)
        self._model_spec = model

    def evaluate_essay(self, prompt: EssayPrompt, user_essay: str) -> EssayEvaluation:
        persona = _COMPANY_PERSONA.get(prompt.company, "당신은 자소서 평가 전문가입니다.")
        system = _SYSTEM.format(
            persona=persona,
            company=prompt.company,
            item=prompt.item,
            item_description=prompt.description,
            word_limit=prompt.word_limit,
        ) + INJECTION_GUARD
        result: _EssaySchema = self._llm.invoke([
            {"role": "system", "content": system},
            {"role": "user", "content": wrap_user_input(user_essay, tag="user_essay")},
        ])
        log_llm_call(result, node="essay", model=self._model_spec)
        total = (
            result.fit_score + result.structure_score
            + result.specificity_score + result.writing_score
        )
        return EssayEvaluation(
            fit_score=result.fit_score,
            structure_score=result.structure_score,
            specificity_score=result.specificity_score,
            writing_score=result.writing_score,
            total_score=total,
            feedback=result.feedback,
            strong_points=result.strong_points,
            weak_points=result.weak_points,
            revised_excerpt=result.revised_excerpt,
            culture_alignment=result.culture_alignment,
        )
