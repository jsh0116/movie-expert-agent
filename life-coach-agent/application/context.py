from dataclasses import dataclass

from application.use_cases import CoachChatUseCase


@dataclass
class AppContext:
    coach_chat: CoachChatUseCase
