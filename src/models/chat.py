from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: uuid4().hex)

    def to_api_dict(self) -> dict:
        return {"role": self.role.value, "content": self.content}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatMessage":
        return cls(
            id=data.get("id", uuid4().hex),
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class Conversation:
    id: str = field(default_factory=lambda: uuid4().hex)
    title: str = "New Chat"
    messages: list[ChatMessage] = field(default_factory=list)
    model: str = "gpt-4.1-nano"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_message(self, message: ChatMessage) -> None:
        self.messages.append(message)
        self.updated_at = datetime.now()
        if self.title == "New Chat" and message.role == MessageRole.USER:
            self.title = message.content[:40] + ("..." if len(message.content) > 40 else "")

    def to_api_messages(self) -> list[dict]:
        return [msg.to_api_dict() for msg in self.messages]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "model": self.model,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        return cls(
            id=data.get("id", uuid4().hex),
            title=data.get("title", "New Chat"),
            messages=[ChatMessage.from_dict(m) for m in data.get("messages", [])],
            model=data.get("model", "gpt-4.1-nano"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
