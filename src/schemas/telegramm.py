from pydantic import BaseModel

class TelegrammChatBase(BaseModel):
    chat_id: int
    first_name: str | None = None
    username: str | None = None

class Chat(BaseModel):
    id: int
    first_name: str | None = None
    username: str | None = None

class Message(BaseModel):
    chat: Chat
    text: str | None = ""

class TelegramUpdate(BaseModel):
    update_id: int
    message: Message