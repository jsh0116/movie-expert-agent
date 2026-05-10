"""LLM tier 시스템 — 사용자 등급별 model mix.

비용/품질 트레이드오프를 등급으로 추상화. env var `LLM_TIER`로 선택.
역할별 env var (`LLM_MODEL_JUDGE` 등) 명시 시 그것이 최종 우선.

Tier 가격 효과 (gpt-4o + sonnet vs mini + haiku, 토큰 동일):
  premium  : gpt-4o + claude-sonnet-4-6 + caching      → 100% 품질, 50% 비용 (cache hit 가정)
  standard : gpt-4o-mini + claude-haiku-4-5            → 80% 품질, 20% 비용
  budget   : gpt-4o-mini × 4 (all 한 모델)             → 70% 품질, 10% 비용
"""
from __future__ import annotations

# 역할별 모델 매핑 — provider:model 형식
TIERS: dict[str, dict[str, str]] = {
    "premium": {
        # 평가 정확도 + 비판 깊이 우선. caching으로 비용 절감.
        "judge":      "openai:gpt-4o",
        "critic":     "anthropic:claude-sonnet-4-6",
        "coach":      "anthropic:claude-sonnet-4-6",
        "diagnostic": "openai:gpt-4o-mini",  # 진단은 mini로 충분 (analytical only)
    },
    "standard": {
        # Free → Pro 진입 사용자. 품질 80%, 비용 1/5.
        "judge":      "openai:gpt-4o-mini",
        "critic":     "anthropic:claude-haiku-4-5-20251001",
        "coach":      "anthropic:claude-haiku-4-5-20251001",
        "diagnostic": "openai:gpt-4o-mini",
    },
    "budget": {
        # Free 무제한 사용자. 한 모델로 통일해 latency 일정 + 캐시 효율.
        "judge":      "openai:gpt-4o-mini",
        "critic":     "openai:gpt-4o-mini",
        "coach":      "openai:gpt-4o-mini",
        "diagnostic": "openai:gpt-4o-mini",
    },
}

DEFAULT_TIER = "premium"
VALID_ROLES = frozenset(("judge", "critic", "coach", "diagnostic"))


def resolve_tier(tier: str | None) -> str:
    """Validate tier name. Falls back to default with warning value."""
    if tier and tier in TIERS:
        return tier
    return DEFAULT_TIER


def model_for_role(tier: str, role: str) -> str:
    """Return provider:model for (tier, role). Raises if role unknown."""
    if role not in VALID_ROLES:
        raise ValueError(f"역할은 {VALID_ROLES} 중 하나여야 합니다. 받은 값: {role!r}")
    return TIERS[resolve_tier(tier)][role]
