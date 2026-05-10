"""회사별 자소서 항목 prompt 저장소 — 인메모리 (Phase 2A)."""
from __future__ import annotations

from semiconductor.domain.entities import EssayPrompt

ESSAY_PROMPTS: dict[tuple[str, str], EssayPrompt] = {
    ("samsung_ds", "지원동기"): EssayPrompt(
        company="samsung_ds", item="지원동기",
        description=(
            "삼성전자 DS부문에 지원한 이유와 본인의 강점이 어떻게 회사·직무에 부합하는지 작성하세요. "
            "구체적 경험·수치 포함."
        ),
        word_limit=1500,
    ),
    ("samsung_ds", "직무역량"): EssayPrompt(
        company="samsung_ds", item="직무역량",
        description=(
            "지원 직무 수행에 필요한 본인의 핵심 역량과 이를 입증하는 구체적 경험·성과를 작성하세요."
        ),
        word_limit=1500,
    ),
    ("samsung_ds", "성장과정"): EssayPrompt(
        company="samsung_ds", item="성장과정",
        description=(
            "지원자의 성장에 가장 큰 영향을 미친 경험과 그로 인해 형성된 본인의 가치관·강점을 작성하세요."
        ),
        word_limit=1500,
    ),
    ("samsung_ds", "갈등극복"): EssayPrompt(
        company="samsung_ds", item="갈등극복",
        description=(
            "팀 또는 조직에서 갈등을 경험하고 이를 극복한 사례를 STAR 기법으로 작성하세요."
        ),
        word_limit=1500,
    ),
    ("sk_hynix", "지원동기"): EssayPrompt(
        company="sk_hynix", item="지원동기",
        description=(
            "SK하이닉스에 지원한 이유와 본인이 추구하는 가치가 SK 핵심가치(VWBE)와 어떻게 부합하는지."
        ),
        word_limit=1000,
    ),
    ("sk_hynix", "직무역량"): EssayPrompt(
        company="sk_hynix", item="직무역량",
        description=(
            "SK하이닉스 지원 직무에 필요한 역량과 본인의 준비 사항·경험을 작성하세요."
        ),
        word_limit=1000,
    ),
    ("sk_hynix", "성장과정"): EssayPrompt(
        company="sk_hynix", item="성장과정",
        description="본인의 성장에 영향을 준 경험과 그로 인한 변화를 작성하세요.",
        word_limit=1000,
    ),
    ("sk_hynix", "갈등극복"): EssayPrompt(
        company="sk_hynix", item="갈등극복",
        description="팀 갈등 해결 경험을 STAR 기법으로 작성하세요.",
        word_limit=1000,
    ),
}


def get_essay_prompt(company: str, item: str) -> EssayPrompt | None:
    """회사·항목으로 prompt 조회. 없으면 None."""
    return ESSAY_PROMPTS.get((company, item))


def list_companies() -> list[str]:
    return sorted({c for c, _ in ESSAY_PROMPTS.keys()})


def list_items(company: str) -> list[str]:
    return sorted({i for c, i in ESSAY_PROMPTS.keys() if c == company})
