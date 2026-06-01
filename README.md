# ChatBot AI - OpenAI Chatbot

Chatbot client for OpenAI API with a modern Kivy UI, secure API key storage, and local conversation history.
Version: 2.0 (2026)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Kivy](https://img.shields.io/badge/Kivy-2.3%2B-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API%20v1-cyan)

## Features

- **Secure API key storage** via OS keyring (Windows/macOS/Linux) with encrypted file fallback
- **Modern Kivy UI** — black / dark cyan / white theme, rounded cards, responsive layout
- **API key input screen** — enter and validate your OpenAI key before accessing chat
- **Conversation sidebar** — browse, switch, and delete past conversations stored locally
- **Model selector** — choose from GPT 4.1, GPT 5.4, and GPT 5.5 families
- **Smartphone-first responsive design** — collapsible sidebar on narrow screens


## Supported Models

| Model | Context |
|-------|---------|
| gpt-4.1-nano | Fastest |
| gpt-4.1-mini | Balanced |
| gpt-4.1 | Full power |
| gpt-5.4-nano | Fastest |
| gpt-5.4-mini | Balanced |
| gpt-5.4 | Full power |
| gpt-5.5 | Latest |

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip
- An [OpenAI API key](https://platform.openai.com/api-keys) (starts with `sk-`)

### Setup

```bash
# Clone the repo
git clone <repo-url>
cd openai_chatbot

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

On first launch, enter your OpenAI API key. It will be validated and stored securely.

### Environment Variable (optional)

Set `OPENAI_API_KEY` as an environment variable to skip the API key screen entirely:

```bash
# Windows
set OPENAI_API_KEY=sk-your-key-here

# macOS / Linux
export OPENAI_API_KEY=sk-your-key-here
python main.py
```

## Project Structure

```
openai_chatbot/
├── main.py                    # App entry point
├── requirements.txt           # Python dependencies
├── build_exe.py               # PyInstaller build script for Windows .exe
├── buildozer.spec             # Buildozer config for Android .apk
├── src/
│   ├── api/
│   │   └── openai_client.py   # OpenAI API client (v1.x syntax)
│   ├── models/
│   │   └── chat.py            # ChatMessage, Conversation dataclasses
│   ├── storage/
│   │   ├── secure_storage.py  # API key storage (keyring + file fallback)
│   │   └── chat_history.py    # Local conversation persistence (JSON)
│   └── ui/
│       ├── theme.py           # Colors, fonts, spacing, radii
│       ├── screens/
│       │   ├── api_key_screen.py  # API key entry screen
│       │   └── chat_screen.py     # Main chat dashboard
│       └── widgets/
│           ├── chat_bubble.py     # Message bubble widget
│           ├── model_selector.py  # Model picker popup
│           └── sidebar.py         # Conversation history sidebar
└── tests/
    ├── test_models.py
    ├── test_secure_storage.py
    └── test_chat_history.py
```

## Building for Distribution

### Windows .exe

```bash
python build_exe.py
```

Output: `dist/MirazoChat.exe`

### Android .apk

Requires [Buildozer](https://buildozer.readthedocs.io/) (Linux or WSL):

```bash
buildozer android debug
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Security

- API keys are **never hardcoded** in source code
- Keys are stored via the OS **keyring** (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- If the keyring is unavailable, an **encrypted file fallback** is used with OS-level permissions (`chmod 600` on POSIX)
- API keys are **never logged** or exposed in error messages
- Input validation on both UI and data layers
- HTTP timeouts and retry handling via the OpenAI SDK

## License

See [LICENSE](LICENSE)
