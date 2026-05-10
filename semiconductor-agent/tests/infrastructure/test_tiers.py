"""TDD: LLM tier 시스템."""
import pytest

from semiconductor.infrastructure.llm.tiers import (
    DEFAULT_TIER,
    TIERS,
    model_for_role,
    resolve_tier,
)


class TestTiers:
    def test_3개_tier_정의(self):
        assert set(TIERS.keys()) == {"premium", "standard", "budget"}

    def test_각_tier에_4개_역할_모두_정의(self):
        for tier, mapping in TIERS.items():
            assert set(mapping.keys()) == {"judge", "critic", "coach", "diagnostic"}, tier

    def test_premium은_gpt_4o와_claude_sonnet_조합(self):
        assert TIERS["premium"]["judge"] == "openai:gpt-4o"
        assert TIERS["premium"]["critic"] == "anthropic:claude-sonnet-4-6"

    def test_premium_diagnostic은_mini로_비용_절감(self):
        # diagnostic은 analytical → mini 충분. premium에서도 mini 사용.
        assert TIERS["premium"]["diagnostic"] == "openai:gpt-4o-mini"

    def test_standard는_mini_haiku_조합(self):
        assert TIERS["standard"]["judge"] == "openai:gpt-4o-mini"
        assert TIERS["standard"]["critic"].startswith("anthropic:claude-haiku")

    def test_budget은_단일_모델_통일(self):
        # 한 모델로 통일 → caching 효율 + latency 일정
        models = set(TIERS["budget"].values())
        assert len(models) == 1


class TestResolveTier:
    def test_올바른_tier는_그대로_반환(self):
        assert resolve_tier("standard") == "standard"

    def test_None은_default로_fallback(self):
        assert resolve_tier(None) == DEFAULT_TIER

    def test_알수없는_tier도_default로_fallback(self):
        # 잘못된 tier 입력 시 안전한 기본값
        assert resolve_tier("ultra_premium") == DEFAULT_TIER


class TestModelForRole:
    def test_premium_judge_조회(self):
        assert model_for_role("premium", "judge") == "openai:gpt-4o"

    def test_알수없는_역할은_거부(self):
        with pytest.raises(ValueError):
            model_for_role("premium", "unknown_role")

    def test_None_tier는_default_적용(self):
        assert model_for_role(None, "judge") == TIERS[DEFAULT_TIER]["judge"]
