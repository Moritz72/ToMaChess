from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import Qt
from .functions_settings import get_settings, save_settings, reset_settings, settings_display, settings_valid
from .functions_gui import get_suitable_widget, get_value_from_suitable_widget, get_button, size_handler, get_label


class Widget_Settings(QWidget):
    def __init__(self, window_main):
        super().__init__()
        self.settings = get_settings()
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
        for i, (key, value) in enumerate(self.settings.items()):
            self.layout.addWidget(get_label(settings_display[key], "large"), i, 1)
            self.layout.addWidget(get_suitable_widget(value, widget_size_factors=(2, 1)), i, 2)
        self.layout.addWidget(
            get_button("large", (10, 5), "Reset", connect_function=self.reset_settings), len(self.settings), 1
        )
        self.layout.addWidget(
            get_button("large", (30, 5), "Save", connect_function=self.save_settings), len(self.settings), 2
        )

    def reset_settings(self):
        reset_settings()
        self.reload_window()

    def save_settings(self):
        for i, key in enumerate(self.settings):
            value = get_value_from_suitable_widget(self.layout.itemAtPosition(i, 2).widget())
            if settings_valid[key](value):
                self.settings[key] = value
        save_settings(self.settings)
        self.reload_window()

    def reload_window(self):
        size_handler.refresh()
        self.window_main.set_stacked_widget("Default")
        self.window_main.stacked_widget.setCurrentIndex(3)
        self.window_main.side_menu.set_button_unclicked(0)
        self.window_main.side_menu.set_button_clicked(3)
