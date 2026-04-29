from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from ..infrastructure.imagen_client import generate_image
from ..prompt import PAGE_ILLUSTRATOR_DESCRIPTION, PAGE_ILLUSTRATOR_INSTRUCTION


async def illustrate_current_page(tool_context: ToolContext) -> dict:
    """state에서 현재 페이지를 읽어 이미지를 생성하고 Artifact로 저장합니다."""
    state = tool_context.state
    story_data = state.get("story_data")
    if not story_data:
        return {"error": "story_data not found in state"}

    page_index = state.get("current_page_index", 0)
    pages = story_data["pages"]

    if page_index >= len(pages):
        return {"status": "all pages illustrated"}

    page = pages[page_index]
    page_number = page["page_number"]
    visual_description = page["visual_description"]

    image_bytes = generate_image(
        f"Children's book illustration, soft watercolor style: {visual_description}"
    )

    artifact = types.Part(
        inline_data=types.Blob(mime_type="image/jpeg", data=image_bytes)
    )
    filename = f"page_{page_number}_image.jpeg"
    await tool_context.save_artifact(filename, artifact)

    state["current_page_index"] = page_index + 1

    return {
        "page_number": page_number,
        "text": page["text"],
        "visual_description": visual_description,
        "artifact": filename,
        "status": "illustrated",
    }


page_illustrator_agent = Agent(
    name="PageIllustrator",
    description=PAGE_ILLUSTRATOR_DESCRIPTION,
    instruction=PAGE_ILLUSTRATOR_INSTRUCTION,
    model="gemini-2.0-flash",
    tools=[illustrate_current_page],
)
