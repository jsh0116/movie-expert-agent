from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest

from ..domain.models import StoryBook
from ..prompt import STORY_WRITER_DESCRIPTION, STORY_WRITER_INSTRUCTION


def _story_writing_callback(_callback_context: CallbackContext, _llm_request: LlmRequest):
    print("📖 스토리 작성 중...")
    return None


story_writer_agent = LlmAgent(
    name="StoryWriter",
    description=STORY_WRITER_DESCRIPTION,
    instruction=STORY_WRITER_INSTRUCTION,
    model="gemini-2.0-flash",
    output_schema=StoryBook,
    output_key="story_data",
    before_model_callback=_story_writing_callback,
)
