import os
from pathlib import Path

from dotenv import load_dotenv
from agents import RunConfig, set_default_openai_api, set_default_openai_client, set_tracing_disabled
from agents.models.openai_provider import OpenAIProvider
from openai import AsyncOpenAI

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_LOCAL_DIR = Path(__file__).resolve().parent.parent


def _get_api_key() -> str | None:
    """Streamlit secrets → 환경 변수 순서로 API 키를 조회한다."""
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def load_run_config() -> RunConfig:
    """환경 변수 또는 Streamlit secrets에서 RunConfig를 생성한다."""
    load_dotenv(_PROJECT_ROOT / ".env")
    load_dotenv(_LOCAL_DIR / ".env", override=True)

    base_url = os.getenv("AI_BASE_URL")
    api_key = _get_api_key()

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
