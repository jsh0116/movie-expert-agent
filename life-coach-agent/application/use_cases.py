from domain.entities import CoachingSession


class CoachChatUseCase:
    """코칭 대화를 관리하는 유스케이스."""

    def __init__(self, session: CoachingSession):
        self._session = session

    @property
    def session(self) -> CoachingSession:
        return self._session

    def add_user_message(self, content: str) -> list[dict]:
        self._session.add_message("user", content)
        return self._session.to_input_list()

    def save_assistant_response(self, content: str) -> None:
        self._session.add_message("assistant", content)

    def get_history(self) -> list[dict]:
        return self._session.to_input_list()

    def clear(self) -> None:
        self._session.clear()
