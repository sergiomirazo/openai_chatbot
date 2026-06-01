import pytest
import os
from pathlib import Path
from src.storage.secure_storage import SecureStorage, _load_from_file_fallback, _delete_file_fallback, _storage_path


class TestSecureStorage:
    def test_save_and_get_api_key(self, monkeypatch):
        test_key = "sk-test12345abcdefghijklmnopqrstuv"
        from keyring.errors import KeyringError

        def _fail_set(*args, **kwargs):
            raise KeyringError("mock")

        monkeypatch.setattr("keyring.set_password", _fail_set)
        monkeypatch.setattr("keyring.get_password", lambda *a, **kw: None)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        _delete_file_fallback()
        SecureStorage.save_api_key(test_key)
        assert SecureStorage.has_api_key()
        assert SecureStorage.get_api_key() == test_key

        SecureStorage.delete_api_key()
        assert not SecureStorage.has_api_key()

    def test_env_var_priority(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key-test")
        _delete_file_fallback()
        assert SecureStorage.get_api_key() == "sk-env-key-test"
        monkeypatch.delenv("OPENAI_API_KEY")

    def test_empty_key_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            SecureStorage.save_api_key("")

    def test_whitespace_key_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            SecureStorage.save_api_key("   ")

    def test_storage_path_creation(self, monkeypatch):
        monkeypatch.setattr("os.environ", {"APPDATA": str(Path.home())})
        path = _storage_path()
        assert path.exists()
