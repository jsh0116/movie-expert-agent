from google.adk.agents import ParallelAgent

from .page_illustrator import page_illustrator_agents

illustrator_agent = ParallelAgent(
    name="Illustrator",
    description="5페이지 동화의 삽화를 동시에 생성합니다.",
    sub_agents=page_illustrator_agents,
)
