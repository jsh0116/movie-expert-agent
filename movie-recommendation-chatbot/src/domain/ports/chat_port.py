from abc import ABC, abstractmethod


class IChatAgent(ABC):
    """챗봇 에이전트 포트. Infrastructure 계층에서 구현한다."""

    @abstractmethod
    async def run(self, messages: list[dict]) -> str:
        """대화 기록을 받아 응답을 생성한다."""
        ...
