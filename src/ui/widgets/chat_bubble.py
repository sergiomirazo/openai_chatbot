from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from src.ui.theme import COLORS, FONT_SIZES, BORDER_RADIUS


class ChatBubble(BoxLayout):
    def __init__(self, message="", is_user=False, **kwargs):
        self._msg = message
        self._user = is_user
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [dp(8), dp(4)]
        self._build_content()

    def _spacer(self, fraction):
        return BoxLayout(size_hint_x=fraction, size_hint_y=1)

    def _build_content(self):
        label = Label(
            text=self._msg,
            color=COLORS["white"],
            font_size=FONT_SIZES["sm"],
            halign="left",
            valign="middle",
            text_size=(dp(260), None),
            size_hint_x=1,
            padding=[dp(12), dp(10)],
        )

        bubble_bg = COLORS["user_bubble"] if self._user else COLORS["bot_bubble"]

        with label.canvas.before:
            Color(*bubble_bg)
            self._bubble_rect = RoundedRectangle(
                pos=label.pos,
                size=label.size,
                radius=[dp(int(BORDER_RADIUS["md"][:-2]))],
            )
        label.bind(pos=self._update_rect, size=self._update_rect)
        label.bind(texture_size=self._on_texture_size)

        bubble_container = BoxLayout(
            size_hint_x=0.8,
            size_hint_y=None,
            height=dp(44),
        )
        bubble_container.add_widget(label)

        if self._user:
            self.add_widget(self._spacer(0.2))
            self.add_widget(bubble_container)
        else:
            self.add_widget(bubble_container)
            self.add_widget(self._spacer(0.2))

    def _update_rect(self, instance, *_):
        if hasattr(self, '_bubble_rect'):
            self._bubble_rect.pos = instance.pos
            self._bubble_rect.size = instance.size

    def _on_texture_size(self, instance, texture_size):
        w = texture_size[0] + dp(24)
        h = texture_size[1] + dp(20)
        instance.size = (w, h)
        instance.parent.height = h + dp(8)
        self.height = h + dp(8)
