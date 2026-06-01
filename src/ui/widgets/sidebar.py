from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import ObjectProperty, ListProperty
from typing import Callable
from src.ui.theme import COLORS, FONT_SIZES, SPACING, BORDER_RADIUS
from src.models.chat import Conversation


class HistoryItem(Button):
    def __init__(self, conversation: Conversation, is_active=False, **kwargs):
        super().__init__(
            text=conversation.title,
            size_hint_y=None,
            height=dp(44),
            background_normal="",
            background_color=COLORS["cyan_dark"] if is_active else COLORS["bg_primary"],
            color=COLORS["white"] if is_active else COLORS["white_dim"],
            font_size=FONT_SIZES["xs"],
            halign="left",
            valign="middle",
            text_size=(dp(180), None),
            padding=[dp(12), dp(0)],
            **kwargs,
        )
        self.conversation = conversation

        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*self.background_color)
            self._rect = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[dp(int(BORDER_RADIUS["sm"][:-2]))],
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_):
        if hasattr(self, '_rect'):
            self._rect.pos = self.pos
            self._rect.size = self.size

    def set_active(self, active: bool):
        self.background_color = COLORS["cyan_dark"] if active else COLORS["bg_primary"]
        self.color = COLORS["white"] if active else COLORS["white_dim"]
        if hasattr(self, '_rect'):
            with self.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(*self.background_color)
                self._rect = RoundedRectangle(
                    pos=self.pos, size=self.size,
                    radius=[dp(int(BORDER_RADIUS["sm"][:-2]))],
                )


class Sidebar(BoxLayout):
    conversations = ListProperty([])

    def __init__(self, on_new_chat: Callable = None, on_select_chat: Callable = None,
                 on_delete_chat: Callable = None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_x = 0.32
        self.padding = [dp(8), dp(12)]
        self.spacing = dp(6)
        self.on_new_chat = on_new_chat
        self.on_select_chat = on_select_chat
        self.on_delete_chat = on_delete_chat

        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLORS["bg_secondary"])
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self._build_header()
        self._build_list()

    def _update_bg(self, *_):
        if hasattr(self, '_bg_rect'):
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size

    def _build_header(self):
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(6),
        )

        title = Label(
            text="Chats",
            color=COLORS["white"],
            font_size=FONT_SIZES["md"],
            bold=True,
            size_hint_x=0.7,
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter('text_size'))

        new_btn = Button(
            text="+",
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(36),
            background_normal="",
            background_color=COLORS["cyan_accent"],
            color=COLORS["bg_primary"],
            font_size=FONT_SIZES["lg"],
            bold=True,
        )
        new_btn.bind(on_release=lambda _: self._on_new_chat())

        with new_btn.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*COLORS["cyan_accent"])
            new_btn._nb_rect = RoundedRectangle(
                pos=new_btn.pos, size=new_btn.size, radius=[dp(18)]
            )
        new_btn.bind(pos=self._update_nb_rect, size=self._update_nb_rect)

        header.add_widget(title)
        header.add_widget(new_btn)
        self.add_widget(header)

    def _update_nb_rect(self, instance, *_):
        if hasattr(instance, '_nb_rect'):
            instance._nb_rect.pos = instance.pos
            instance._nb_rect.size = instance.size

    def _build_list(self):
        self.list_view = ScrollView(size_hint=(1, 1))
        self.list_content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
            padding=[0, dp(4)],
        )
        self.list_content.bind(minimum_height=self.list_content.setter('height'))
        self.list_view.add_widget(self.list_content)
        self.add_widget(self.list_view)

    def _on_new_chat(self):
        if self.on_new_chat:
            self.on_new_chat()

    def _on_delete(self, conversation):
        if self.on_delete_chat:
            self.on_delete_chat(conversation.id)

    def refresh_list(self, conversations: list[Conversation], active_id: str = ""):
        self.conversations = conversations
        self.list_content.clear_widgets()
        for conv in conversations:
            item = HistoryItem(conv, is_active=(conv.id == active_id))
            item.bind(on_release=lambda _, c=conv: self._select_chat(c))
            self.list_content.add_widget(item)

    def _select_chat(self, conversation: Conversation):
        if self.on_select_chat:
            self.on_select_chat(conversation.id)
