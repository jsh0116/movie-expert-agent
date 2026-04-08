from src.domain.entities.conversation import ConversationMemory
from src.domain.ports.chat_port import IChatAgent


class ChatUseCase:
    """대화 유스케이스.

    ConversationMemory로 messages를 관리하고,
    IChatAgent 포트를 통해 에이전트 응답을 생성한다.
    """

    def __init__(self, agent: IChatAgent, memory: ConversationMemory):
        self._agent = agent
        self._memory = memory

    async def chat(self, user_input: str) -> str:
        # 1. 사용자 메시지 저장
        self._memory.add_user_message(user_input)

        # 2. 전체 대화 기록을 에이전트에 전달하여 응답 생성
        response = await self._agent.run(self._memory.get_messages())

        # 3. 에이전트 응답 저장
        self._memory.add_assistant_message(response)

        return response
