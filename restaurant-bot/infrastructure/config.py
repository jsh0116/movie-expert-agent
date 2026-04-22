import os
from pathlib import Path

from dotenv import load_dotenv
from agents import RunConfig, set_default_openai_api, set_default_openai_client, set_tracing_disabled
from agents.models.openai_provider import OpenAIProvider
from openai import AsyncOpenAI

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_LOCAL_DIR = Path(__file__).resolve().parent.parent


def load_run_config() -> RunConfig:
    """환경 변수를 읽어 RunConfig를 생성한다.

    AI_BASE_URL이 설정된 경우 (예: LiteLLM 프록시):
    - 전역 기본 OpenAI 클라이언트를 해당 base_url로 설정
    - Chat Completions API를 기본으로 사용 (프록시가 Responses API 미지원)
    - 가드레일 등 내부 Runner.run() 호출에도 동일 설정 적용됨

    AI_BASE_URL이 없으면 기본 OpenAI API를 사용한다.
    """
    load_dotenv(_PROJECT_ROOT / ".env")
    load_dotenv(_LOCAL_DIR / ".env", override=True)

    base_url = os.getenv("AI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")

    if base_url:
        client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        set_default_openai_client(client, use_for_tracing=False)
        set_default_openai_api("chat_completions")
        set_tracing_disabled(True)
        return RunConfig(
            model_provider=OpenAIProvider(
                openai_client=client,
                use_responses=False,
            ),
            tracing_disabled=True,
        )
    return RunConfig()
