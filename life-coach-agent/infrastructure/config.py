import os
from pathlib import Path

from dotenv import load_dotenv
from agents import RunConfig
from agents.models.openai_provider import OpenAIProvider

# 프로젝트 루트 .env → 로컬 .env 순으로 로드 (로컬이 우선)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_LOCAL_DIR = Path(__file__).resolve().parent.parent


def load_run_config() -> RunConfig:
    """환경 변수를 읽어 RunConfig를 생성한다."""
    load_dotenv(_PROJECT_ROOT / ".env")
    load_dotenv(_LOCAL_DIR / ".env", override=True)

    base_url = os.getenv("AI_BASE_URL")
    if base_url:
        return RunConfig(
            model_provider=OpenAIProvider(
                base_url=base_url,
                use_responses=False,
            ),
            tracing_disabled=True,
        )
    return RunConfig()
