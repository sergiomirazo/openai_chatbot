import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.config import Config

Config.set("kivy", "window_title", "ChatBot AI")
Config.set("kivy", "exit_on_escape", "1")
Config.set("kivy", "default_font", ["Roboto", "data/fonts/Roboto-Regular.ttf"])
Config.set("input", "mouse", "mouse,multitouch_on_demand")
Config.set("graphics", "minimum_width", "360")
Config.set("graphics", "minimum_height", "640")
Config.write()

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.metrics import dp

from src.ui.theme import COLORS
from src.ui.screens.api_key_screen import ApiKeyScreen
from src.ui.screens.chat_screen import ChatScreen
from src.storage.secure_storage import SecureStorage


class ApiKeyScreenWrapper(Screen):
    def __init__(self, auto_validate=False, **kwargs):
        super().__init__(name="api_key", **kwargs)
        self.api_key_screen = ApiKeyScreen(
            on_key_validated=self._on_validated,
            auto_validate=auto_validate,
        )
        self.add_widget(self.api_key_screen)

    def _on_validated(self):
        self.manager.current = "chat"


class ChatScreenWrapper(Screen):
    def __init__(self, **kwargs):
        super().__init__(name="chat", **kwargs)
        self.chat_screen = ChatScreen()
        self.add_widget(self.chat_screen)


class ChatBotAIApp(App):
    def build(self):
        self.title = "ChatBot AI"
        self.icon = ""

        Window.clearcolor = COLORS["bg_primary"]
        Window.minimum_width = dp(360)
        Window.minimum_height = dp(640)

        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        auto_validate = SecureStorage.has_api_key()
        sm.add_widget(ApiKeyScreenWrapper(auto_validate=auto_validate))
        sm.add_widget(ChatScreenWrapper())
        sm.current = "api_key"

        return sm


if __name__ == "__main__":
    ChatBotAIApp().run()
