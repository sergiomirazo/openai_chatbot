from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ObjectProperty
from src.ui.theme import COLORS, FONT_SIZES
from src.api.openai_client import AVAILABLE_MODELS


def _rect_updater(rect_attr):
    def updater(instance, *_):
        rect = getattr(instance, rect_attr, None)
        if rect:
            rect.pos = instance.pos
            rect.size = instance.size
    return updater


class ModelSelectorPopup(ModalView):
    model_buttons = ObjectProperty(None)
    on_model_selected = ObjectProperty(None)

    def __init__(self, current_model="gpt-4.1-nano", callback=None, **kwargs):
        super().__init__(**kwargs)
        self.current_model = current_model
        self.callback = callback
        self.size_hint = (0.88, None)
        self.height = dp(340)
        self.auto_dismiss = True
        self.background = ""
        self.background_color = (0, 0, 0, 0)

        self._build_ui()

    def _build_ui(self):
        container = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(16), dp(20), dp(16), dp(16)],
        )

        with container.canvas.before:
            Color(*COLORS["bg_secondary"])
            container._bg = RoundedRectangle(
                pos=container.pos, size=container.size, radius=[dp(16)]
            )
        container.bind(
            pos=_rect_updater('_bg'),
            size=_rect_updater('_bg'),
        )

        title = Label(
            text="Select Model",
            color=COLORS["white"],
            font_size=FONT_SIZES["lg"],
            bold=True,
            size_hint_y=None,
            height=dp(36),
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter('text_size'))
        container.add_widget(title)

        for model in AVAILABLE_MODELS:
            row = BoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(44),
            )
            model_label = Label(
                text=model,
                color=COLORS["white_dim"],
                font_size=FONT_SIZES["sm"],
                size_hint_x=0.65,
                halign="left",
                valign="middle",
            )
            model_label.bind(size=model_label.setter('text_size'))

            is_selected = model == self.current_model
            btn = Button(
                text="Selected" if is_selected else "  Choose  ",
                size_hint_x=0.35,
                size_hint_y=None,
                height=dp(36),
                background_normal="",
                background_color=COLORS["cyan_accent"] if is_selected else COLORS["bg_card"],
                color=COLORS["bg_primary"] if is_selected else COLORS["white"],
                font_size=FONT_SIZES["xs"],
                bold=True,
            )
            btn.model_choice = model
            btn.bind(on_release=self._on_select)

            with btn.canvas.before:
                Color(*btn.background_color)
                btn._br = RoundedRectangle(
                    pos=btn.pos, size=btn.size, radius=[dp(18)]
                )
            btn.bind(pos=_rect_updater('_br'), size=_rect_updater('_br'))

            row.add_widget(model_label)
            row.add_widget(btn)
            container.add_widget(row)

        self.add_widget(container)

    def _on_select(self, instance):
        if self.callback:
            self.callback(instance.model_choice)
        self.dismiss()
