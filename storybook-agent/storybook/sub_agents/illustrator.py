from google.adk.agents import LoopAgent

from .page_illustrator import page_illustrator_agent

# LoopAgent: 매 이터레이션마다 한 페이지씩 처리, 5페이지 완료 시 종료
illustrator_agent = LoopAgent(
    name="Illustrator",
    description="5페이지 동화의 각 페이지 이미지를 순차적으로 생성합니다.",
    sub_agents=[page_illustrator_agent],
    max_iterations=5,
)
