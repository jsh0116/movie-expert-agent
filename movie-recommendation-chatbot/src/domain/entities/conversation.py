from dataclasses import dataclass, field


@dataclass
class ConversationMemory:
    """대화 기록을 관리하는 엔티티.

    messages 리스트에 user/assistant 메시지를 축적하여
    에이전트가 이전 대화 컨텍스트를 활용할 수 있도록 한다.
    """

    messages: list[dict] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def get_messages(self) -> list[dict]:
        return self.messages
