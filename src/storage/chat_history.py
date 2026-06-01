import json
import os
from pathlib import Path
from threading import Lock
from src.models.chat import Conversation


class ChatHistoryStorage:
    _instance = None
    _lock = Lock()

    def __new__(cls) -> "ChatHistoryStorage":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def _storage_path() -> Path:
        app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
        path = Path(app_data) / ".openai_chatbot"
        path.mkdir(parents=True, exist_ok=True)
        return path / "conversations.json"

    def load_all(self) -> list[Conversation]:
        file_path = self._storage_path()
        if not file_path.exists():
            return []
        try:
            with self._lock:
                data = json.loads(file_path.read_text(encoding="utf-8"))
            return [Conversation.from_dict(c) for c in data.get("conversations", [])]
        except (json.JSONDecodeError, KeyError, OSError):
            return []

    def save_all(self, conversations: list[Conversation]) -> None:
        file_path = self._storage_path()
        data = {"conversations": [c.to_dict() for c in conversations]}
        with self._lock:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            if os.name == "posix":
                file_path.chmod(0o600)

    def save_conversation(self, conversation: Conversation) -> list[Conversation]:
        conversations = self.load_all()
        found = False
        for i, conv in enumerate(conversations):
            if conv.id == conversation.id:
                conversations[i] = conversation
                found = True
                break
        if not found:
            conversations.insert(0, conversation)
        self.save_all(conversations)
        return conversations

    def delete_conversation(self, conversation_id: str) -> list[Conversation]:
        conversations = self.load_all()
        conversations = [c for c in conversations if c.id != conversation_id]
        self.save_all(conversations)
        return conversations

    def clear_all(self) -> None:
        file_path = self._storage_path()
        if file_path.exists():
            file_path.unlink()
