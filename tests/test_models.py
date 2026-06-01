import pytest
from datetime import datetime
from src.models.chat import ChatMessage, Conversation, MessageRole


class TestChatMessage:
    def test_create_user_message(self):
        msg = ChatMessage(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)

    def test_to_api_dict(self):
        msg = ChatMessage(role=MessageRole.USER, content="Hello")
        d = msg.to_api_dict()
        assert d == {"role": "user", "content": "Hello"}

    def test_to_dict_and_from_dict(self):
        msg = ChatMessage(role=MessageRole.ASSISTANT, content="Hi there")
        data = msg.to_dict()
        restored = ChatMessage.from_dict(data)
        assert restored.role == msg.role
        assert restored.content == msg.content
        assert restored.id == msg.id

    def test_system_message(self):
        msg = ChatMessage(role=MessageRole.SYSTEM, content="You are helpful")
        assert msg.to_api_dict()["role"] == "system"


class TestConversation:
    def test_create_conversation(self):
        conv = Conversation(title="Test Chat")
        assert conv.title == "Test Chat"
        assert len(conv.messages) == 0

    def test_add_message_updates_title(self):
        conv = Conversation()
        conv.add_message(ChatMessage(role=MessageRole.USER, content="What is Python?"))
        assert "What is Python?" in conv.title

    def test_to_api_messages(self):
        conv = Conversation()
        conv.add_message(ChatMessage(role=MessageRole.SYSTEM, content="Be helpful"))
        conv.add_message(ChatMessage(role=MessageRole.USER, content="Hi"))
        api_msgs = conv.to_api_messages()
        assert len(api_msgs) == 2
        assert api_msgs[0]["role"] == "system"
        assert api_msgs[1]["role"] == "user"

    def test_to_dict_and_from_dict(self):
        conv = Conversation(model="gpt-4.1")
        conv.add_message(ChatMessage(role=MessageRole.USER, content="Hello"))
        conv.add_message(ChatMessage(role=MessageRole.ASSISTANT, content="Hi!"))
        data = conv.to_dict()
        restored = Conversation.from_dict(data)
        assert restored.title == conv.title
        assert restored.model == "gpt-4.1"
        assert len(restored.messages) == 2
        assert restored.messages[0].content == "Hello"
        assert restored.messages[1].content == "Hi!"
