from google.adk.agents import LlmAgent

from ..domain.models import StoryBook
from ..prompt import STORY_WRITER_DESCRIPTION, STORY_WRITER_INSTRUCTION

story_writer_agent = LlmAgent(
    name="StoryWriter",
    description=STORY_WRITER_DESCRIPTION,
    instruction=STORY_WRITER_INSTRUCTION,
    model="gemini-2.0-flash",
    output_schema=StoryBook,
    output_key="story_data",
)
