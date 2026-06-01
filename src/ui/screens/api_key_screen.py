from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from src.ui.theme import COLORS, FONT_SIZES, BORDER_RADIUS
from src.storage.secure_storage import SecureStorage
from src.api.openai_client import OpenAIClient


def _make_rect_updater(rect_attr):
    def updater(instance, *_):
        rect = getattr(instance, rect_attr, None)
        if rect:
            rect.pos = instance.pos
            rect.size = instance.size
    return updater


def _make_icon_button(text, on_press, size_dp=36, font_size=None):
    btn = Button(
        text=text,
        size_hint=(None, None),
        size=(dp(size_dp), dp(size_dp)),
        background_normal="",
        background_color=COLORS["bg_card"],
        color=COLORS["white"],
        font_size=font_size or FONT_SIZES["sm"],
        bold=False,
    )
    with btn.canvas.before:
        Color(*COLORS["bg_card"])
        btn._btn_rect = RoundedRectangle(
            pos=btn.pos, size=btn.size, radius=[dp(18)]
        )
    btn.bind(pos=_make_rect_updater('_btn_rect'), size=_make_rect_updater('_btn_rect'))
    btn.bind(on_release=on_press)
    return btn


class ApiKeyScreen(BoxLayout):
    def __init__(self, on_key_validated=None, auto_validate=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(24), dp(40)]
        self.spacing = dp(16)
        self.on_key_validated = on_key_validated
        self.auto_validate = auto_validate
        self._key_visible = False

        with self.canvas.before:
            Color(*COLORS["bg_primary"])
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self._build_ui()

        if self.auto_validate and SecureStorage.has_api_key():
            self._set_loading(True)
            Clock.schedule_once(lambda dt: self._submit_key(), 0.5)

    def _update_bg(self, *_):
        if hasattr(self, '_bg'):
            self._bg.pos = self.pos
            self._bg.size = self.size

    def _build_ui(self):
        self.add_widget(BoxLayout(size_hint_y=0.10))

        logo_container = FloatLayout(size_hint_y=0.15)
        logo = Label(
            text="ChatBot AI",
            color=COLORS["cyan_light"],
            font_size=FONT_SIZES["xxl"],
            bold=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(1, 1),
            halign="center",
            valign="middle",
        )
        logo.bind(size=logo.setter('text_size'))
        logo_container.add_widget(logo)
        self.add_widget(logo_container)



        self.add_widget(BoxLayout(size_hint_y=0.04))

        card = BoxLayout(
            orientation="vertical",
            size_hint_y=0.50,
            spacing=dp(12),
            padding=[dp(20), dp(20)],
        )
        with card.canvas.before:
            Color(*COLORS["bg_card"])
            card._card_bg = RoundedRectangle(
                pos=card.pos, size=card.size, radius=[dp(int(BORDER_RADIUS["lg"][:-2]))]
            )
        card.bind(pos=_make_rect_updater('_card_bg'), size=_make_rect_updater('_card_bg'))

        title = Label(
            text="Enter your OpenAI API Key",
            color=COLORS["white"],
            font_size=FONT_SIZES["lg"],
            bold=True,
            size_hint_y=None,
            height=dp(32),
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter('text_size'))
        card.add_widget(title)

        desc = Label(
            text="Your key is stored securely on this device\nand never sent anywhere but to OpenAI.",
            color=COLORS["white_muted"],
            font_size=FONT_SIZES["xs"],
            size_hint_y=None,
            height=dp(40),
            halign="left",
            valign="top",
        )
        desc.bind(size=desc.setter('text_size'))
        card.add_widget(desc)

        input_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(6),
        )

        input_wrapper = BoxLayout(size_hint_x=1)
        with input_wrapper.canvas.before:
            Color(*COLORS["bg_input"])
            input_wrapper._iw_bg = RoundedRectangle(
                pos=input_wrapper.pos, size=input_wrapper.size,
                radius=[dp(int(BORDER_RADIUS["md"][:-2]))],
            )
        input_wrapper.bind(
            pos=_make_rect_updater('_iw_bg'),
            size=_make_rect_updater('_iw_bg'),
        )

        self.key_input = TextInput(
            text=SecureStorage.get_api_key() or "",
            hint_text="Enter your OpenAI API key...",
            hint_text_color=COLORS["white_muted"],
            foreground_color=COLORS["white"],
            background_color=(0, 0, 0, 0),
            font_size=FONT_SIZES["sm"],
            multiline=False,
            password=True,
            password_mask="\u2022",
            cursor_color=COLORS["cyan_accent"],
            selection_color=COLORS["cyan_dark"],
            size_hint=(1, 1),
            padding=[dp(12), dp(14)],
        )
        input_wrapper.add_widget(self.key_input)
        input_row.add_widget(input_wrapper)

        paste_btn = _make_icon_button(
            text="Paste",
            on_press=lambda _: self._paste_clipboard(),
            size_dp=48,
            font_size=FONT_SIZES["xs"],
        )
        paste_btn.bold = True
        input_row.add_widget(paste_btn)

        self.eye_btn = _make_icon_button(
            text="Show",
            on_press=lambda _: self._toggle_key_visibility(),
            size_dp=48,
            font_size=FONT_SIZES["xs"],
        )
        self.eye_btn.bold = True
        input_row.add_widget(self.eye_btn)

        card.add_widget(input_row)

        self.error_label = Label(
            text="",
            color=COLORS["error"],
            font_size=FONT_SIZES["xs"],
            size_hint_y=None,
            height=dp(20),
            halign="left",
            valign="middle",
            opacity=0,
        )
        self.error_label.bind(size=self.error_label.setter('text_size'))
        card.add_widget(self.error_label)

        btn_wrapper = BoxLayout(size_hint_y=None, height=dp(50))
        self.submit_btn = Button(
            text="Connect",
            size_hint=(1, 1),
            background_normal="",
            background_color=COLORS["cyan_accent"],
            color=COLORS["bg_primary"],
            font_size=FONT_SIZES["md"],
            bold=True,
            disabled=False,
        )
        self.submit_btn.bind(on_release=self._submit_key)

        with self.submit_btn.canvas.before:
            Color(*COLORS["cyan_accent"])
            self.submit_btn._sb_rect = RoundedRectangle(
                pos=self.submit_btn.pos, size=self.submit_btn.size,
                radius=[dp(int(BORDER_RADIUS["md"][:-2]))],
            )
        self.submit_btn.bind(
            pos=_make_rect_updater('_sb_rect'),
            size=_make_rect_updater('_sb_rect'),
        )

        btn_wrapper.add_widget(self.submit_btn)
        card.add_widget(btn_wrapper)

        self.add_widget(card)
        self.add_widget(BoxLayout(size_hint_y=1))

        self._build_footer()

    def _paste_clipboard(self):
        try:
            text = Clipboard.paste()
            if text:
                self.key_input.text = text.strip()
        except Exception:
            pass

    def _toggle_key_visibility(self):
        self._key_visible = not self._key_visible
        self.key_input.password = not self._key_visible
        self.eye_btn.text = "Hide" if self._key_visible else "Show"

    def _build_footer(self):
        footer = Label(
            text="Powered by MirazoLabs",
            color=COLORS["white_muted"],
            font_size=FONT_SIZES["xs"],
            size_hint_y=None,
            height=dp(32),
            halign="center",
            valign="middle",
        )
        footer.bind(size=footer.setter('text_size'))
        self.add_widget(footer)

    def _submit_key(self, *_):
        api_key = self.key_input.text.strip()

        if not api_key:
            self._show_error("Please enter an API key.")
            return

        self._set_loading(True)
        self.error_label.opacity = 0

        SecureStorage.save_api_key(api_key)
        OpenAIClient().reset_client()

        if self.on_key_validated:
            self.on_key_validated()

    def _set_loading(self, loading: bool):
        self.submit_btn.disabled = loading
        self.submit_btn.text = "Connecting..." if loading else "Connect"
        self.submit_btn.background_color = COLORS["white_muted"] if loading else COLORS["cyan_accent"]

    def _show_error(self, message: str):
        self.error_label.text = message
        self.error_label.opacity = 1
        anim = Animation(opacity=0, duration=3.0)
        Clock.schedule_once(lambda _: anim.start(self.error_label), 2.0)
