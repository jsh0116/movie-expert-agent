from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from ..infrastructure.imagen_client import generate_image


async def illustrate_page(tool_context: ToolContext, page_index: int) -> dict:
    """지정한 인덱스의 페이지 이미지를 생성하고 Artifact로 저장합니다."""
    state = tool_context.state
    story_data = state.get("story_data")
    if not story_data:
        return {"error": "story_data not found in state"}

    pages = story_data["pages"]
    if page_index >= len(pages):
        return {"error": f"page_index {page_index} out of range"}

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

    return {
        "page_number": page_number,
        "text": page["text"],
        "visual_description": visual_description,
        "artifact": filename,
        "status": "illustrated",
    }


def _make_callback(page_num: int):
    def callback(_callback_context: CallbackContext, _llm_request: LlmRequest):
        print(f"🎨 이미지 {page_num}/5 생성 중...")
        return None

    return callback


def _create_page_illustrator(page_index: int) -> Agent:
    page_num = page_index + 1
    return Agent(
        name=f"PageIllustrator{page_num}",
        description=f"페이지 {page_num}의 삽화를 생성합니다.",
        instruction=(
            f"illustrate_page 도구를 page_index={page_index}로 호출하여 "
            f"페이지 {page_num}의 이미지를 생성하세요. 도구를 한 번만 호출하세요."
        ),
        model="gemini-2.0-flash",
        tools=[illustrate_page],
        before_model_callback=_make_callback(page_num),
    )


page_illustrator_agents = [_create_page_illustrator(i) for i in range(5)]
