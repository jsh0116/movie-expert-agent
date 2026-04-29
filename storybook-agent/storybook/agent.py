from google.adk.agents import SequentialAgent

from .sub_agents.illustrator import illustrator_agent
from .sub_agents.story_writer import story_writer_agent

root_agent = SequentialAgent(
    name="StorybookCreator",
    description="테마를 받아 5페이지 분량의 삽화가 포함된 어린이 동화책을 만듭니다.",
    sub_agents=[story_writer_agent, illustrator_agent],
)
