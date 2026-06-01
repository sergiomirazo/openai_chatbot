import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.storage.chat_history import ChatHistoryStorage
from src.models.chat import Conversation, ChatMessage, MessageRole


class TestChatHistoryStorage:
    @pytest.fixture
    def storage(self):
        storage = ChatHistoryStorage()
        storage._instance = None
        ChatHistoryStorage._instance = None
        return ChatHistoryStorage()

    @pytest.fixture
    def temp_file(self, tmp_path):
        return tmp_path / "conversations.json"

    def test_load_empty(self, storage, temp_file):
        with patch.object(ChatHistoryStorage, "_storage_path", return_value=temp_file):
            conversations = storage.load_all()
            assert conversations == []

    def test_save_and_load(self, storage, temp_file):
        conv = Conversation(title="Test")
        conv.add_message(ChatMessage(role=MessageRole.USER, content="Hello"))

        with patch.object(ChatHistoryStorage, "_storage_path", return_value=temp_file):
            storage.save_all([conv])
            loaded = storage.load_all()
            assert len(loaded) == 1
            assert loaded[0].title == "Test"
            assert len(loaded[0].messages) == 1
            assert loaded[0].messages[0].content == "Hello"

    def test_save_conversation_new(self, storage, temp_file):
        conv = Conversation(title="New Chat")
        with patch.object(ChatHistoryStorage, "_storage_path", return_value=temp_file):
            storage.save_conversation(conv)
            loaded = storage.load_all()
            assert len(loaded) == 1
            assert loaded[0].id == conv.id

    def test_save_conversation_update(self, storage, temp_file):
        conv = Conversation(title="Original")
        with patch.object(ChatHistoryStorage, "_storage_path", return_value=temp_file):
            storage.save_conversation(conv)
            conv.title = "Updated"
            conv.add_message(ChatMessage(role=MessageRole.USER, content="Hello"))
            storage.save_conversation(conv)
            loaded = storage.load_all()
            assert len(loaded) == 1
            assert loaded[0].title == "Updated"
            assert len(loaded[0].messages) == 1

    def test_delete_conversation(self, storage, temp_file):
        conv1 = Conversation(title="Keep")
        conv2 = Conversation(title="Delete")
        with patch.object(ChatHistoryStorage, "_storage_path", return_value=temp_file):
            storage.save_all([conv1, conv2])
            remaining = storage.delete_conversation(conv2.id)
            assert len(remaining) == 1
            assert remaining[0].title == "Keep"

    def test_clear_all(self, storage, temp_file):
        conv = Conversation()
        with patch.object(ChatHistoryStorage, "_storage_path", return_value=temp_file):
            storage.save_all([conv])
            storage.clear_all()
            assert not temp_file.exists()
