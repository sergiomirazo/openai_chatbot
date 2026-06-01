import keyring
import os
from pathlib import Path

SERVICE_NAME = "openai_chatbot_mirazolabs"
API_KEY_ACCOUNT = "openai_api_key"
ENV_VAR_NAME = "OPENAI_API_KEY"


class SecureStorage:
    @staticmethod
    def save_api_key(api_key: str) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        try:
            keyring.set_password(SERVICE_NAME, API_KEY_ACCOUNT, api_key.strip())
        except keyring.errors.KeyringError:
            _save_to_file_fallback(api_key.strip())

    @staticmethod
    def get_api_key() -> str | None:
        api_key = os.environ.get(ENV_VAR_NAME)
        if api_key:
            return api_key.strip()

        try:
            api_key = keyring.get_password(SERVICE_NAME, API_KEY_ACCOUNT)
            if api_key:
                return api_key.strip()
        except keyring.errors.KeyringError:
            pass

        return _load_from_file_fallback()

    @staticmethod
    def delete_api_key() -> None:
        try:
            keyring.delete_password(SERVICE_NAME, API_KEY_ACCOUNT)
        except keyring.errors.KeyringError:
            pass
        _delete_file_fallback()

    @staticmethod
    def has_api_key() -> bool:
        return SecureStorage.get_api_key() is not None


def _storage_path() -> Path:
    app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
    path = Path(app_data) / ".openai_chatbot"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save_to_file_fallback(api_key: str) -> None:
    import base64
    file_path = _storage_path() / ".cred"
    encoded = base64.b64encode(api_key.encode("utf-8")).decode("utf-8")
    file_path.write_text(encoded, encoding="utf-8")
    if os.name == "posix":
        file_path.chmod(0o600)


def _load_from_file_fallback() -> str | None:
    import base64
    file_path = _storage_path() / ".cred"
    if not file_path.exists():
        return None
    try:
        encoded = file_path.read_text(encoding="utf-8").strip()
        return base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
    except Exception:
        return None


def _delete_file_fallback() -> None:
    file_path = _storage_path() / ".cred"
    if file_path.exists():
        file_path.unlink()
