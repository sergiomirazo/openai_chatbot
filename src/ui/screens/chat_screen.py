from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
import threading

from src.ui.theme import COLORS, FONT_SIZES, SPACING, BORDER_RADIUS
from src.ui.widgets.sidebar import Sidebar
from src.ui.widgets.chat_bubble import ChatBubble
from src.ui.widgets.model_selector import ModelSelectorPopup
from src.models.chat import Conversation, ChatMessage, MessageRole
from src.storage.chat_history import ChatHistoryStorage
from src.api.openai_client import OpenAIClient, AVAILABLE_MODELS


class ChatScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLORS["bg_primary"])
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.api_client = OpenAIClient()
        self.storage = ChatHistoryStorage()
        self.conversations = self.storage.load_all() or []
        self.current_conversation = None
        self.is_loading = False
        self.sidebar_visible = True
        self._selected_model = "gpt-4.1-nano"

        self._build_layout()

        if self.conversations:
            self._switch_conversation(self.conversations[0].id)
        else:
            self._new_conversation()

    def _update_bg(self, *_):
        if hasattr(self, '_bg'):
            self._bg.pos = self.pos
            self._bg.size = self.size

    def _build_layout(self):
        self.main_layout = BoxLayout(orientation="horizontal")
        self.add_widget(self.main_layout)

        self.sidebar = Sidebar(
            on_new_chat=self._new_conversation,
            on_select_chat=self._switch_conversation,
            on_delete_chat=self._delete_conversation,
        )
        self.main_layout.add_widget(self.sidebar)

        self.chat_area = BoxLayout(orientation="vertical")
        self.main_layout.add_widget(self.chat_area)

        self._build_top_bar()
        self._build_messages_area()
        self._build_input_area()
        self._build_footer()

        Window.bind(on_resize=self._on_window_resize)
        self._on_window_resize()

    def _on_window_resize(self, *_):
        width, height = Window.size
        is_narrow = width < dp(600)

        if hasattr(self, 'sidebar'):
            if is_narrow:
                self.sidebar_visible = False
                self.sidebar.size_hint_x = 0
                if hasattr(self, 'hamburger_btn'):
                    self.hamburger_btn.opacity = 1
            else:
                self.sidebar_visible = True
                self.sidebar.size_hint_x = 0.28
                if hasattr(self, 'hamburger_btn'):
                    self.hamburger_btn.opacity = 0

        self.sidebar.size_hint_x = 0.28 if self.sidebar_visible else 0

    def _toggle_sidebar(self, *_):
        self.sidebar_visible = not self.sidebar_visible
        target = 0.28 if self.sidebar_visible else 0
        anim = Animation(size_hint_x=target, duration=0.25)
        anim.start(self.sidebar)

    def _build_top_bar(self):
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            padding=[dp(12), dp(6)],
            spacing=dp(8),
        )
        with top_bar.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLORS["bg_primary"])
            top_bar._tb_bg = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=self._update_tb_bg, size=self._update_tb_bg)

        self.hamburger_btn = Button(
            text="\u2630",
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            background_normal="",
            background_color=COLORS["bg_card"],
            color=COLORS["white"],
            font_size=FONT_SIZES["lg"],
            opacity=0,
        )
        with self.hamburger_btn.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*COLORS["bg_card"])
            self.hamburger_btn._hb_rect = RoundedRectangle(
                pos=self.hamburger_btn.pos, size=self.hamburger_btn.size, radius=[dp(18)]
            )
        self.hamburger_btn.bind(
            pos=self._update_hb_rect, size=self._update_hb_rect,
            on_release=self._toggle_sidebar,
        )
        top_bar.add_widget(self.hamburger_btn)

        title = Label(
            text="ChatBot AI",
            color=COLORS["cyan_light"],
            font_size=FONT_SIZES["lg"],
            bold=True,
            size_hint_x=1,
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter('text_size'))
        top_bar.add_widget(title)

        self.model_btn = Button(
            text=self._model_short_name(self._selected_model),
            size_hint=(None, None),
            size=(dp(56), dp(36)),
            background_normal="",
            background_color=COLORS["bg_card"],
            color=COLORS["cyan_light"],
            font_size=FONT_SIZES["xs"],
            bold=True,
        )
        with self.model_btn.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*COLORS["bg_card"])
            self.model_btn._mb_rect = RoundedRectangle(
                pos=self.model_btn.pos, size=self.model_btn.size, radius=[dp(18)]
            )
        self.model_btn.bind(
            pos=self._update_mb_rect, size=self._update_mb_rect,
            on_release=self._show_model_selector,
        )
        top_bar.add_widget(self.model_btn)

        self.chat_area.add_widget(top_bar)

    @staticmethod
    def _model_short_name(model: str) -> str:
        name = (
            model
            .replace("gpt-", "")
            .replace("-nano", "N")
            .replace("-mini", "M")
        )
        name = name.replace("nano", "N").replace("mini", "M")
        return name.upper()

    @staticmethod
    def _update_hb_rect(instance, *_):
        if hasattr(instance, '_hb_rect'):
            instance._hb_rect.pos = instance.pos
            instance._hb_rect.size = instance.size

    @staticmethod
    def _update_mb_rect(instance, *_):
        if hasattr(instance, '_mb_rect'):
            instance._mb_rect.pos = instance.pos
            instance._mb_rect.size = instance.size

    @staticmethod
    def _update_tb_bg(instance, *_):
        if hasattr(instance, '_tb_bg'):
            instance._tb_bg.pos = instance.pos
            instance._tb_bg.size = instance.size

    def _build_messages_area(self):
        self.messages_scroll = ScrollView(
            size_hint=(1, 1),
            scroll_type=["bars", "content"],
            bar_width=dp(4),
            bar_color=COLORS["cyan_dark"],
            bar_inactive_color=COLORS["bg_card"],
        )
        self.messages_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
            padding=[dp(8), dp(8)],
        )
        self.messages_list.bind(minimum_height=self.messages_list.setter('height'))
        self.messages_scroll.add_widget(self.messages_list)
        self.chat_area.add_widget(self.messages_scroll)

    def _build_input_area(self):
        input_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(72),
            padding=[dp(8), dp(8), dp(8), dp(12)],
        )

        with input_container.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLORS["bg_primary"])
            input_container._ic_bg = Rectangle(
                pos=input_container.pos, size=input_container.size,
            )
        input_container.bind(pos=self._update_ic_bg, size=self._update_ic_bg)

        input_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48),
        )

        input_wrapper = BoxLayout(size_hint_x=1)
        with input_wrapper.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*COLORS["bg_input"])
            input_wrapper._iw_bg = RoundedRectangle(
                pos=input_wrapper.pos, size=input_wrapper.size,
                radius=[dp(int(BORDER_RADIUS["md"][:-2]))],
            )
        input_wrapper.bind(pos=self._update_iw_bg, size=self._update_iw_bg)

        self.prompt_input = TextInput(
            hint_text="Type a message...",
            hint_text_color=COLORS["white_muted"],
            foreground_color=COLORS["white"],
            background_color=(0, 0, 0, 0),
            font_size=FONT_SIZES["sm"],
            multiline=False,
            cursor_color=COLORS["cyan_accent"],
            selection_color=COLORS["cyan_dark"],
            size_hint=(1, 1),
            padding=[dp(16), dp(14)],
        )
        self.prompt_input.bind(on_text_validate=self._send_prompt)
        input_wrapper.add_widget(self.prompt_input)
        input_row.add_widget(input_wrapper)

        self.send_btn = Button(
            text="\u2191",
            size_hint=(None, None),
            size=(dp(44), dp(44)),
            background_normal="",
            background_color=COLORS["cyan_accent"],
            color=COLORS["bg_primary"],
            font_size=FONT_SIZES["lg"],
            bold=True,
        )
        with self.send_btn.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*COLORS["cyan_accent"])
            self.send_btn._sb_rect = RoundedRectangle(
                pos=self.send_btn.pos, size=self.send_btn.size,
                radius=[dp(int(BORDER_RADIUS["pill"][:-2]))],
            )
        self.send_btn.bind(
            pos=self._update_sb_rect, size=self._update_sb_rect,
            on_release=self._send_prompt,
        )
        input_row.add_widget(self.send_btn)

        input_container.add_widget(input_row)
        self.chat_area.add_widget(input_container)

    @staticmethod
    def _update_ic_bg(instance, *_):
        if hasattr(instance, '_ic_bg'):
            instance._ic_bg.pos = instance.pos
            instance._ic_bg.size = instance.size

    @staticmethod
    def _update_iw_bg(instance, *_):
        if hasattr(instance, '_iw_bg'):
            instance._iw_bg.pos = instance.pos
            instance._iw_bg.size = instance.size

    @staticmethod
    def _update_sb_rect(instance, *_):
        if hasattr(instance, '_sb_rect'):
            instance._sb_rect.pos = instance.pos
            instance._sb_rect.size = instance.size

    def _build_footer(self):
        footer = Label(
            text="Powered by MirazoLabs",
            color=COLORS["white_muted"],
            font_size=FONT_SIZES["xs"],
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
        )
        footer.bind(size=footer.setter('text_size'))
        self.chat_area.add_widget(footer)

    def _show_model_selector(self, *_):
        popup = ModelSelectorPopup(
            current_model=self._selected_model,
            callback=self._on_model_selected,
        )
        popup.open()

    def _on_model_selected(self, model: str):
        self._selected_model = model
        self.model_btn.text = self._model_short_name(model)
        if self.current_conversation:
            self.current_conversation.model = model
            self.storage.save_conversation(self.current_conversation)

    def _new_conversation(self, *_):
        conv = Conversation(model=self._selected_model)
        self.conversations.insert(0, conv)
        self.storage.save_all(self.conversations)
        self._switch_conversation(conv.id)

    def _switch_conversation(self, conversation_id: str):
        for conv in self.conversations:
            if conv.id == conversation_id:
                self.current_conversation = conv
                self._selected_model = conv.model
                self.model_btn.text = self._model_short_name(conv.model)
                break
        self._render_messages()
        self.sidebar.refresh_list(self.conversations, active_id=conversation_id)

        if not self.sidebar_visible:
            self._toggle_sidebar()

    def _delete_conversation(self, conversation_id: str):
        self.conversations = self.storage.delete_conversation(conversation_id)
        if self.current_conversation and self.current_conversation.id == conversation_id:
            if self.conversations:
                self._switch_conversation(self.conversations[0].id)
            else:
                self._new_conversation()
        else:
            self.sidebar.refresh_list(self.conversations,
                                      active_id=self.current_conversation.id if self.current_conversation else "")

    def _render_messages(self):
        self.messages_list.clear_widgets()
        if not self.current_conversation:
            return
        for msg in self.current_conversation.messages:
            bubble = ChatBubble(message=msg.content, is_user=(msg.role == MessageRole.USER))
            self.messages_list.add_widget(bubble)

        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def _scroll_to_bottom(self, *_):
        if hasattr(self, 'messages_scroll'):
            self.messages_scroll.scroll_y = 0

    def _send_prompt(self, *_):
        if self.is_loading:
            return

        text = self.prompt_input.text.strip()
        if not text:
            return

        self.prompt_input.text = ""
        self.is_loading = True
        self._set_send_enabled(False)

        if not self.current_conversation:
            self._new_conversation()

        user_msg = ChatMessage(role=MessageRole.USER, content=text)
        self.current_conversation.add_message(user_msg)
        self._render_messages()

        self._show_typing_indicator()

        thread = threading.Thread(target=self._fetch_response, daemon=True)
        thread.start()

    def _fetch_response(self):
        try:
            messages = self.current_conversation.to_api_messages()
            response = self.api_client.send_message(
                messages=messages,
                model=self._selected_model,
            )
            assistant_msg = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response.content,
            )
            self.current_conversation.add_message(assistant_msg)
            self.conversations = self.storage.save_conversation(self.current_conversation)
            Clock.schedule_once(lambda dt: self._on_response_received(), 0)

        except ValueError as e:
            error_msg = str(e)
            Clock.schedule_once(lambda dt, msg=error_msg: self._on_error(msg), 0)
        except Exception as e:
            error_msg = str(e)
            Clock.schedule_once(lambda dt, msg=error_msg: self._on_error(f"Error: {msg}"), 0)

    def _on_response_received(self):
        self._remove_typing_indicator()
        self._render_messages()
        self.sidebar.refresh_list(self.conversations,
                                  active_id=self.current_conversation.id if self.current_conversation else "")
        self._set_send_enabled(True)
        self.is_loading = False

    def _on_error(self, message: str):
        self._remove_typing_indicator()
        error_msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=f"Error: {message}",
        )
        if self.current_conversation:
            self.current_conversation.add_message(error_msg)
            self.conversations = self.storage.save_conversation(self.current_conversation)
        self._render_messages()
        self._set_send_enabled(True)
        self.is_loading = False

    def _show_typing_indicator(self):
        self.typing_bubble = ChatBubble(
            message="\u2022 \u2022 \u2022",
            is_user=False,
        )
        self.messages_list.add_widget(self.typing_bubble)
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)

    def _remove_typing_indicator(self):
        if hasattr(self, 'typing_bubble') and self.typing_bubble:
            if self.typing_bubble in self.messages_list.children:
                self.messages_list.remove_widget(self.typing_bubble)
            self.typing_bubble = None

    def _set_send_enabled(self, enabled: bool):
        self.send_btn.disabled = not enabled
        self.send_btn.background_color = COLORS["cyan_accent"] if enabled else COLORS["white_muted"]
