from pydantic import BaseModel


class StoryPage(BaseModel):
    page_number: int
    text: str
    visual_description: str


class StoryBook(BaseModel):
    theme: str
    title: str
    pages: list[StoryPage]
