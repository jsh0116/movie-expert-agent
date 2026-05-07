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
from semiconductor.domain.ports import ICoachLLM, IDiagnosticLLM, ILLMCritic, ILLMJudge

load_dotenv()

# 모델 차등화 — 작업 특성에 맞게 다른 모델 사용 (env var로 오버라이드 가능)
#   - Judge / Diagnostic: 평가 정확도가 신뢰의 핵심 → 강한 모델 (기본 gpt-4o)
#   - Coach: 한 줄짜리 힌트 응답 → 가성비 모델 (기본 gpt-4o-mini)
_MODEL_JUDGE = os.getenv("LLM_MODEL_JUDGE", "gpt-4o")
_MODEL_DIAGNOSTIC = os.getenv("LLM_MODEL_DIAGNOSTIC", "gpt-4o")
_MODEL_COACH = os.getenv("LLM_MODEL_COACH", "gpt-4o-mini")
_MODEL_CRITIC = os.getenv("LLM_MODEL_CRITIC", "gpt-4o")


def _make_llm(model: str, temperature: float = 0.3) -> ChatOpenAI:
    base_url = os.getenv("AI_BASE_URL")
    kwargs: dict = {"model": model, "temperature": temperature}
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
    model_answer: str  # 만점 기준 모범답안 (3~5문장)


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
- model_answer: 만점(100점) 수준의 모범답안 — 3~5문장, 핵심 개념·원리·전문 용어를
  모두 포함하고 한국어로 작성. 면접관이 "이렇게 답했으면 만점"이라고 인정할 수준.

참고 기준(key_points): {key_points}"""


class OpenAILLMJudge(ILLMJudge):
    def __init__(self) -> None:
        # 평가는 결정론적이어야 함 (같은 답변 → 같은 점수)
        self._llm = _make_llm(_MODEL_JUDGE, temperature=0.0).with_structured_output(_EvalSchema)

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
            model_answer=result.model_answer,
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
        # 코칭은 약간의 다양성이 자연스러움 (같은 힌트도 매번 살짝 다르게)
        self._llm = _make_llm(_MODEL_COACH, temperature=0.5)

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
        # 진단도 결정론적이어야 함 (같은 평가 → 같은 진단)
        self._llm = _make_llm(_MODEL_DIAGNOSTIC, temperature=0.0).with_structured_output(_DiagSchema)

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


# ── ILLMCritic — Self-Critique 검증 레이어 ─────────────────────────

_CRITIC_SYSTEM = """당신은 반도체 기술면접 평가 검증관입니다.
다른 평가관이 작성한 1차 평가를 검토하고 정확성을 검증하세요.

검토 관점:
1. 점수가 답변의 실제 깊이와 일치하는가? (과대/과소 평가 식별)
2. feedback이 점수와 일관되는가?
3. 핵심 개념(key_points) 반영도가 정확하게 평가됐는가?
4. strong_points / weak_points가 답변에서 실제로 관찰되는가?
5. model_answer가 만점 수준으로 충분한가?

원칙:
- 1차 평가가 합리적이면 거의 동일한 결과 반환 (점수 ±5점 이내)
- 명백한 과대/과소만 수정. 보수적으로.
- 수정 시 feedback에 "[검증] " 접두어를 붙여 검증 흔적 남김.

질문: {question}
key_points 참고: {key_points}

1차 평가 결과:
- accuracy_score: {accuracy_score}/40
- depth_score: {depth_score}/30
- terminology_score: {terminology_score}/30
- feedback: {feedback}
- strong_points: {strong_points}
- weak_points: {weak_points}
- model_answer: {model_answer}

지원자 답변:
{user_answer}

위 1차 평가를 검토하고 최종 평가를 반환하세요."""


class OpenAIEvaluationCritic(ILLMCritic):
    def __init__(self) -> None:
        # 검증도 결정론적이어야 함
        self._llm = _make_llm(_MODEL_CRITIC, temperature=0.0).with_structured_output(_EvalSchema)

    def critique(
        self,
        question: Question,
        user_answer: str,
        initial_evaluation: EvaluationResult,
    ) -> EvaluationResult:
        prompt = _CRITIC_SYSTEM.format(
            question=question.question,
            key_points=", ".join(question.key_points) or "없음",
            accuracy_score=initial_evaluation.accuracy_score,
            depth_score=initial_evaluation.depth_score,
            terminology_score=initial_evaluation.terminology_score,
            feedback=initial_evaluation.feedback,
            strong_points=", ".join(initial_evaluation.strong_points) or "없음",
            weak_points=", ".join(initial_evaluation.weak_points) or "없음",
            model_answer=initial_evaluation.model_answer or "없음",
            user_answer=user_answer,
        )
        result: _EvalSchema = self._llm.invoke([{"role": "system", "content": prompt}])
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
            model_answer=result.model_answer,
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
    def critic() -> ILLMCritic:
        return OpenAIEvaluationCritic()

    @staticmethod
    def diagnostic() -> IDiagnosticLLM:
        return OpenAIDiagnosticLLM()
