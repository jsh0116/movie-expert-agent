"""LangChain-based implementation of all LLM ports."""
from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from semiconductor.domain.entities import (
    DiagnosticResult,
    EvaluationResult,
    Question,
)
from semiconductor.domain.ports import ICoachLLM, IDiagnosticLLM, ILLMJudge

load_dotenv()

_MODEL = "gpt-4o-mini"


def _make_llm() -> ChatOpenAI:
    base_url = os.getenv("AI_BASE_URL")
    kwargs: dict = {"model": _MODEL, "temperature": 0.3}
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)


# ── Pydantic schemas for structured output ────────────────────────

class _EvalSchema(BaseModel):
    accuracy_score: int
    depth_score: int
    terminology_score: int
    feedback: str
    strong_points: list[str]
    weak_points: list[str]


class _DiagSchema(BaseModel):
    domain_scores: dict[str, int]
    weak_topics: list[str]
    strong_topics: list[str]
    recommended_next: str


# ── ILLMJudge ─────────────────────────────────────────────────────

_JUDGE_SYSTEM = """당신은 삼성전자DS/SK하이닉스 반도체 기술면접 평가관입니다.
지원자의 답변을 다음 루브릭으로 평가하세요.

평가 기준:
- accuracy_score (0–40): 정확성 — 핵심 개념이 올바르게 기술되었는가
- depth_score (0–30): 깊이 — 원리·메커니즘까지 설명했는가
- terminology_score (0–30): 전문 용어 — 반도체 공학 용어를 정확하게 사용했는가
- feedback: 2–3문장 구체적 피드백 (한국어)
- strong_points: 잘 답변한 부분 (1–3개)
- weak_points: 보완 필요한 부분 (1–3개)

참고 기준(key_points): {key_points}"""


class OpenAILLMJudge(ILLMJudge):
    def __init__(self) -> None:
        self._llm = _make_llm().with_structured_output(_EvalSchema)

    def evaluate(self, question: Question, user_answer: str) -> EvaluationResult:
        result: _EvalSchema = self._llm.invoke(
            [
                {"role": "system", "content": _JUDGE_SYSTEM.format(
                    key_points=", ".join(question.key_points)
                )},
                {"role": "user", "content": f"질문: {question.question}\n\n답변: {user_answer}"},
            ]
        )
        total = result.accuracy_score + result.depth_score + result.terminology_score
        return EvaluationResult(
            accuracy_score=result.accuracy_score,
            depth_score=result.depth_score,
            terminology_score=result.terminology_score,
            total_score=total,
            feedback=result.feedback,
            strong_points=result.strong_points,
            weak_points=result.weak_points,
            question=question.question,
        )


# ── ICoachLLM ─────────────────────────────────────────────────────

_COACH_RULES = {
    0: "선행 지식을 파악하세요. '어디까지 알고 있어요?' 같은 탐색 질문으로 시작하세요. 절대 직접 답하지 마세요.",
    1: "힌트 1회차: 핵심 키워드나 유추(analogy)를 하나만 제시하세요. 직접 답은 주지 마세요.",
    2: "힌트 2회차: 관련 물리 원리나 수식 힌트를 줄 수 있습니다. 아직 직접 답은 주지 마세요.",
    3: "힌트 3회차 초과: 이제 명확하게 설명하세요 (3–5문장). 설명 후 이해 확인 질문을 1개 추가하세요.",
}

_COACH_SYSTEM = """당신은 반도체 공학 전문 학습 코치입니다. 소크라테스 방식으로 가르칩니다.

현재 학습 주제: {topic}
현재 힌트 횟수: {hint_count}/3

규칙:
{rules}

한국어로 답변하세요."""


class OpenAICoachLLM(ICoachLLM):
    def __init__(self) -> None:
        self._llm = _make_llm()

    def get_response(self, topic: str, messages: list[BaseMessage], hint_count: int) -> str:
        rule_key = min(hint_count, 3)
        system = _COACH_SYSTEM.format(
            topic=topic, hint_count=hint_count, rules=_COACH_RULES[rule_key]
        )
        llm_messages: list = [{"role": "system", "content": system}]
        for m in messages[-10:]:
            if isinstance(m, HumanMessage):
                llm_messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                llm_messages.append({"role": "assistant", "content": m.content})
        response = self._llm.invoke(llm_messages)
        return response.content


# ── IDiagnosticLLM ────────────────────────────────────────────────

_DIAGNOSTIC_SYSTEM = """당신은 반도체 기술면접 이해도 진단 전문가입니다.
아래 면접 평가 결과를 분석하여 도메인별 이해도 점수와 학습 추천을 제공하세요.

평가 결과:
{evaluations_json}

반도체 4대 도메인: 소자, 공정, 회로, 트렌드
평가된 도메인만 점수를 매기고, 없는 도메인은 0으로 설정하세요."""


class OpenAIDiagnosticLLM(IDiagnosticLLM):
    def __init__(self) -> None:
        self._llm = _make_llm().with_structured_output(_DiagSchema)

    def analyze(self, evaluations: list[EvaluationResult]) -> DiagnosticResult:
        evals_json = json.dumps(
            [
                {
                    "question": e.question,
                    "total_score": e.total_score,
                    "strong_points": e.strong_points,
                    "weak_points": e.weak_points,
                }
                for e in evaluations
            ],
            ensure_ascii=False,
            indent=2,
        )
        result: _DiagSchema = self._llm.invoke(
            [{"role": "system", "content": _DIAGNOSTIC_SYSTEM.format(evaluations_json=evals_json)}]
        )
        return DiagnosticResult(
            domain_scores=result.domain_scores,
            weak_topics=result.weak_topics,
            strong_topics=result.strong_topics,
            recommended_next=result.recommended_next,
        )


# ── Composite service for convenience ────────────────────────────

class LangChainLLMService:
    """Factory that creates all LLM port implementations."""

    @staticmethod
    def judge() -> ILLMJudge:
        return OpenAILLMJudge()

    @staticmethod
    def coach() -> ICoachLLM:
        return OpenAICoachLLM()

    @staticmethod
    def diagnostic() -> IDiagnosticLLM:
        return OpenAIDiagnosticLLM()
