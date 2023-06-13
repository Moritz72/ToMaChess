from PyQt5.QtWidgets import QWidget, QGridLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from .class_settings_handler import settings_display, settings_valid, settings_handler
from .functions_gui import get_suitable_widget, get_value_from_suitable_widget, get_button, get_label,\
    get_button_threaded
from .functions_rating_lists import update_list_by_name


def get_update_lists_widget(parent):
    button_fide = get_button_threaded(
        parent, "large", (14, 3), "FIDE", "Updating...",
        connect_function=lambda: update_list_by_name("FIDE"), translate=True
    )
    button_dsb = get_button_threaded(
        parent, "large", (14, 3), "DSB", "Updating...",
        connect_function=lambda: update_list_by_name("DSB"), translate=True
    )
    widget = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(button_fide)
    layout.addWidget(button_dsb)
    widget.setLayout(layout)
    return widget


class Widget_Settings(QWidget):
    def __init__(self, window_main):
        super().__init__()
        self.window_main = window_main

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(50)
        self.layout.setVerticalSpacing(20)
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(3, 1)
        self.setLayout(self.layout)

        self.fill_in_layouts()

    def fill_in_layouts(self):
        settings = settings_handler.settings
        for i, (key, value) in enumerate(settings.items()):
            self.layout.addWidget(get_label(settings_display[key], "large", translate=True), i, 1)
            self.layout.addWidget(get_suitable_widget(value, widget_size_factors=(2, 1)), i, 2)
        self.layout.addWidget(get_label("Update Lists", "large", translate=True), len(settings), 1)
        self.layout.addWidget(get_update_lists_widget(self.window_main), len(settings), 2)
        self.layout.addWidget(
            get_button("large", (15, 5), "Reset", connect_function=self.reset_settings, translate=True),
            len(settings) + 1, 1
        )
        self.layout.addWidget(
            get_button("large", (30, 5), "Save", connect_function=self.save_settings, translate=True),
            len(settings) + 1, 2
        )

    def reset_settings(self):
        settings_handler.reset()
        self.window_main.load_up(5)

    def save_settings(self):
        for i, key in enumerate(settings_handler.settings):
            value = get_value_from_suitable_widget(self.layout.itemAtPosition(i, 2).widget())
            if settings_valid[key](value):
                settings_handler.settings[key] = value
        settings_handler.save()
        self.window_main.load_up(5)
