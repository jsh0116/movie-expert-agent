import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from src.domain.entities.conversation import ConversationMemory
from src.adapters.agent.movie_chat_agent import OpenAIChatAgent
from src.application.use_cases.chat_use_case import ChatUseCase


async def main():
    memory = ConversationMemory()
    agent = OpenAIChatAgent()
    chat = ChatUseCase(agent=agent, memory=memory)

    print("영화 추천 챗봇입니다. 종료하려면 'q'를 입력하세요.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() == "q":
            print("종료합니다.")
            break
        response = await chat.chat(user_input)
        print(f"AI: {response}\n")


if __name__ == "__main__":
    asyncio.run(main())
