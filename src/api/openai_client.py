from dataclasses import dataclass
from typing import Optional
import openai
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, AuthenticationError, APIConnectionError

from src.storage.secure_storage import SecureStorage

TIMEOUT_SECONDS = 60
MAX_RETRIES = 2

AVAILABLE_MODELS = [
    "gpt-4.1-nano",
    "gpt-4.1-mini",
    "gpt-4.1",
    "gpt-4o-mini",
    "gpt-4o",
    "o4-mini",
    "o3",
]


@dataclass
class ChatResponse:
    content: str
    model: str
    usage: Optional[dict] = None


class OpenAIClient:
    _instance: Optional["OpenAIClient"] = None

    def __new__(cls) -> "OpenAIClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
        return cls._instance

    def _get_client(self) -> OpenAI:
        if self._client is not None:
            return self._client

        api_key = SecureStorage.get_api_key()
        if not api_key:
            raise ValueError("No API key configured. Please enter your OpenAI API key.")

        self._client = OpenAI(
            api_key=api_key,
            timeout=TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES,
        )
        return self._client

    def reset_client(self) -> None:
        self._client = None

    def validate_key(self) -> bool:
        try:
            client = self._get_client()
            client.models.list(limit=1)
            return True
        except (AuthenticationError, ValueError):
            return False
        except (APIError, APITimeoutError, APIConnectionError):
            return False
        except Exception:
            return False

    def send_message(
        self,
        messages: list[dict],
        model: str = "gpt-4.1-nano",
    ) -> ChatResponse:
        if model not in AVAILABLE_MODELS:
            raise ValueError(
                f"Unsupported model '{model}'. Available: {', '.join(AVAILABLE_MODELS)}"
            )

        if not messages:
            raise ValueError("Messages cannot be empty")

        client = self._get_client()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
            )
        except AuthenticationError:
            raise ValueError(
                "Invalid API key. Please check your key and try again."
            )
        except RateLimitError:
            raise ValueError(
                "Rate limit exceeded. Please wait a moment and try again."
            )
        except APITimeoutError:
            raise ValueError(
                "Request timed out. Please check your connection and try again."
            )
        except APIError as e:
            raise ValueError(f"OpenAI API error: {e.message}")

        content = response.choices[0].message.content or ""
        return ChatResponse(
            content=content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
        )

    @staticmethod
    def get_available_models() -> list[str]:
        return list(AVAILABLE_MODELS)
