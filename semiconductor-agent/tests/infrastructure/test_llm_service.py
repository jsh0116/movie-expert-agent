"""TDD: LLM service — 작업별 모델 차등화 검증."""
from __future__ import annotations

import importlib
from unittest.mock import MagicMock, patch

import pytest

from semiconductor.infrastructure.llm import llm_service


@pytest.fixture
def mock_chat_openai():
    """ChatOpenAI 생성자를 가로채서 어떤 인자로 호출됐는지 검사."""
    with patch.object(llm_service, "ChatOpenAI") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.with_structured_output.return_value = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_cls


class TestModelDifferentiation:
    def test_critic은_gpt_4o를_사용한다(self, mock_chat_openai):
        llm_service.OpenAIEvaluationCritic()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs["model"] == "gpt-4o"

    def test_critic은_temperature_0으로_결정론적이다(self, mock_chat_openai):
        llm_service.OpenAIEvaluationCritic()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs["temperature"] == 0.0

    def test_judge는_gpt_4o를_사용한다(self, mock_chat_openai):
        llm_service.OpenAILLMJudge()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs["model"] == "gpt-4o"

    def test_judge는_temperature_0으로_결정론적이다(self, mock_chat_openai):
        llm_service.OpenAILLMJudge()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs["temperature"] == 0.0

    def test_diagnostic은_gpt_4o를_사용한다(self, mock_chat_openai):
        llm_service.OpenAIDiagnosticLLM()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs["model"] == "gpt-4o"

    def test_diagnostic도_temperature_0으로_결정론적이다(self, mock_chat_openai):
        llm_service.OpenAIDiagnosticLLM()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs["temperature"] == 0.0

    def test_coach는_가성비_gpt_4o_mini를_사용한다(self, mock_chat_openai):
        llm_service.OpenAICoachLLM()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs["model"] == "gpt-4o-mini"

    def test_coach는_temperature_0_5로_다양성을_허용한다(self, mock_chat_openai):
        llm_service.OpenAICoachLLM()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs["temperature"] == 0.5


class TestEnvVarOverride:
    def test_LLM_MODEL_JUDGE_env_var로_재정의_가능(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL_JUDGE", "gpt-5")
        importlib.reload(llm_service)
        assert llm_service._MODEL_JUDGE == "gpt-5"

    def test_LLM_MODEL_COACH_env_var로_재정의_가능(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL_COACH", "gpt-3.5-turbo")
        importlib.reload(llm_service)
        assert llm_service._MODEL_COACH == "gpt-3.5-turbo"

    def test_env_var_없으면_기본값_사용(self, monkeypatch):
        monkeypatch.delenv("LLM_MODEL_JUDGE", raising=False)
        monkeypatch.delenv("LLM_MODEL_COACH", raising=False)
        monkeypatch.delenv("LLM_MODEL_DIAGNOSTIC", raising=False)
        monkeypatch.delenv("LLM_MODEL_CRITIC", raising=False)
        importlib.reload(llm_service)
        assert llm_service._MODEL_JUDGE == "gpt-4o"
        assert llm_service._MODEL_DIAGNOSTIC == "gpt-4o"
        assert llm_service._MODEL_COACH == "gpt-4o-mini"
        assert llm_service._MODEL_CRITIC == "gpt-4o"

    def test_LLM_MODEL_CRITIC_env_var로_재정의_가능(self, monkeypatch):
        monkeypatch.setenv("LLM_MODEL_CRITIC", "gpt-5")
        importlib.reload(llm_service)
        assert llm_service._MODEL_CRITIC == "gpt-5"


class TestPromptContent:
    def test_judge_프롬프트가_LaTeX_사용을_지시한다(self):
        # 수식이 핵심인 답변(MOSFET Vth 등)에 LaTeX 표기 사용 지시 포함
        assert "LaTeX" in llm_service._JUDGE_SYSTEM
        assert "$" in llm_service._JUDGE_SYSTEM  # 인라인 또는 블록 수식 예시

    def test_judge_프롬프트에_4도메인_specialty_persona가_정의된다(self):
        # 4개 도메인 모두 specialist persona 매핑 존재
        for domain in ("소자", "공정", "회로", "트렌드"):
            assert domain in llm_service._SPECIALIST_PERSONAS

    def test_unknown_도메인은_default_persona로_fallback(self):
        # 도메인이 비표준이면 일반 평가관 페르소나 반환
        persona = llm_service._persona_for("알수없음")
        assert "평가관" in persona


class TestAIBaseURLOverride:
    def test_AI_BASE_URL_설정시_base_url_전달(self, mock_chat_openai, monkeypatch):
        monkeypatch.setenv("AI_BASE_URL", "https://custom.example.com/v1")
        llm_service.OpenAILLMJudge()
        kwargs = mock_chat_openai.call_args.kwargs
        assert kwargs.get("base_url") == "https://custom.example.com/v1"

    def test_AI_BASE_URL_없으면_base_url_미전달(self, mock_chat_openai, monkeypatch):
        monkeypatch.delenv("AI_BASE_URL", raising=False)
        llm_service.OpenAILLMJudge()
        kwargs = mock_chat_openai.call_args.kwargs
        assert "base_url" not in kwargs
