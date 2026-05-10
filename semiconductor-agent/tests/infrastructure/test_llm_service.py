"""TDD: LLM service — multi-provider routing (OpenAI / Anthropic / Google) via init_chat_model."""
from __future__ import annotations

import importlib
from unittest.mock import MagicMock, patch

import pytest

from semiconductor.infrastructure.llm import llm_service


@pytest.fixture
def mock_init_chat_model():
    """init_chat_model을 가로채서 어떤 model_spec / kwargs로 호출됐는지 검사."""
    with patch.object(llm_service, "init_chat_model") as mock_fn:
        instance = MagicMock()
        instance.with_structured_output.return_value = MagicMock()
        instance.bind_tools.return_value = instance
        mock_fn.return_value = instance
        yield mock_fn


# ── Provider routing — 작업별 다른 provider 사용 ──────────────────────


class TestProviderRouting:
    def test_judge는_OpenAI_gpt_4o를_사용한다(self, mock_init_chat_model):
        # structured output 안정성이 핵심 → OpenAI 유지
        llm_service.OpenAILLMJudge()
        spec = mock_init_chat_model.call_args.args[0]
        assert spec == "openai:gpt-4o"

    def test_diagnostic은_OpenAI_gpt_4o를_사용한다(self, mock_init_chat_model):
        llm_service.OpenAIDiagnosticLLM()
        spec = mock_init_chat_model.call_args.args[0]
        assert spec == "openai:gpt-4o"

    def test_critic은_Anthropic_Claude_Sonnet을_사용한다(self, mock_init_chat_model):
        # 비판적 사고·검증 = Claude 강점
        llm_service.OpenAIEvaluationCritic()
        spec = mock_init_chat_model.call_args.args[0]
        assert spec == "anthropic:claude-sonnet-4-6"

    def test_coach는_Anthropic_Claude_Sonnet을_사용한다(self, mock_init_chat_model):
        # 한국어 자연스러움 + tool calling = Claude
        llm_service.OpenAICoachLLM()
        spec = mock_init_chat_model.call_args.args[0]
        assert spec == "anthropic:claude-sonnet-4-6"


class TestTemperatures:
    def test_judge_critic_diagnostic은_temperature_0_결정론적(self, mock_init_chat_model):
        for cls in (llm_service.OpenAILLMJudge, llm_service.OpenAIEvaluationCritic, llm_service.OpenAIDiagnosticLLM):
            mock_init_chat_model.reset_mock()
            cls()
            assert mock_init_chat_model.call_args.kwargs["temperature"] == 0.0

    def test_coach는_temperature_0_5_다양성_허용(self, mock_init_chat_model):
        llm_service.OpenAICoachLLM()
        assert mock_init_chat_model.call_args.kwargs["temperature"] == 0.5


# ── Env var override ────────────────────────────────────────────────


class TestEnvVarOverride:
    def test_LLM_MODEL_JUDGE_env_var로_provider_변경_가능(self, monkeypatch):
        # provider 자체를 바꿀 수 있어야 함 (Anthropic으로 옮기려면)
        monkeypatch.setenv("LLM_MODEL_JUDGE", "anthropic:claude-opus-4-7")
        importlib.reload(llm_service)
        assert llm_service._MODEL_JUDGE == "anthropic:claude-opus-4-7"

    def test_provider_prefix_없으면_openai로_자동_보완(self, monkeypatch):
        # 기존 env (그냥 'gpt-5') 유저 호환 — colon 없으면 'openai:' prefix 붙임
        monkeypatch.setenv("LLM_MODEL_JUDGE", "gpt-5")
        importlib.reload(llm_service)
        assert llm_service._MODEL_JUDGE == "openai:gpt-5"

    def test_env_var_없으면_provider별_기본값_사용(self, monkeypatch):
        for var in ("LLM_MODEL_JUDGE", "LLM_MODEL_COACH", "LLM_MODEL_DIAGNOSTIC", "LLM_MODEL_CRITIC"):
            monkeypatch.delenv(var, raising=False)
        importlib.reload(llm_service)
        assert llm_service._MODEL_JUDGE == "openai:gpt-4o"
        assert llm_service._MODEL_DIAGNOSTIC == "openai:gpt-4o"
        assert llm_service._MODEL_CRITIC == "anthropic:claude-sonnet-4-6"
        assert llm_service._MODEL_COACH == "anthropic:claude-sonnet-4-6"


# ── AI_BASE_URL: OpenAI provider일 때만 적용 ────────────────────────


class TestAIBaseURLScoping:
    def test_OpenAI_judge에_AI_BASE_URL_전달(self, mock_init_chat_model, monkeypatch):
        monkeypatch.setenv("AI_BASE_URL", "https://custom.example.com/v1")
        llm_service.OpenAILLMJudge()
        assert mock_init_chat_model.call_args.kwargs.get("base_url") == "https://custom.example.com/v1"

    def test_Anthropic_critic에는_AI_BASE_URL_전달_안함(self, mock_init_chat_model, monkeypatch):
        # AI_BASE_URL은 OpenAI-호환 endpoint 변수. Anthropic provider엔 무관.
        monkeypatch.setenv("AI_BASE_URL", "https://custom.example.com/v1")
        llm_service.OpenAIEvaluationCritic()
        assert "base_url" not in mock_init_chat_model.call_args.kwargs

    def test_AI_BASE_URL_없으면_OpenAI에도_base_url_미전달(self, mock_init_chat_model, monkeypatch):
        monkeypatch.delenv("AI_BASE_URL", raising=False)
        llm_service.OpenAILLMJudge()
        assert "base_url" not in mock_init_chat_model.call_args.kwargs


# ── 프롬프트 콘텐츠 (provider 무관) ─────────────────────────────────


class TestPromptContent:
    def test_judge_프롬프트가_LaTeX_사용을_지시한다(self):
        assert "LaTeX" in llm_service._JUDGE_SYSTEM
        assert "$" in llm_service._JUDGE_SYSTEM

    def test_judge_프롬프트에_4도메인_specialty_persona가_정의된다(self):
        for domain in ("소자", "공정", "회로", "트렌드"):
            assert domain in llm_service._SPECIALIST_PERSONAS

    def test_unknown_도메인은_default_persona로_fallback(self):
        persona = llm_service._persona_for("알수없음")
        assert "평가관" in persona
