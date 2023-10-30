from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLineEdit
from PySide6.QtCore import Qt
from .class_settings_handler import SETTINGS_DISPLAY, SETTINGS_HANDLER
from .class_ftp_connection import FTP_CONNECTION
from .functions_util import get_version
from .functions_gui import get_suitable_widget, get_value_from_suitable_widget, get_button, get_label,\
    get_button_threaded, get_scroll_area_widgets_and_layouts
from .functions_rating_lists import update_list_by_name


def get_update_lists_widget(parent):
    button_fide = get_button_threaded(
        parent, "large", (9, 3), "FIDE", "Updating...",
        connect_function=lambda: update_list_by_name("FIDE"), translate=True
    )
    button_dsb = get_button_threaded(
        parent, "large", (9, 3), "DSB", "Updating...",
        connect_function=lambda: update_list_by_name("DSB"), translate=True
    )
    button_uscf = get_button_threaded(
        parent, "large", (9, 3), "USCF", "Updating...",
        connect_function=lambda: update_list_by_name("USCF"), translate=True
    )
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(button_fide)
    layout.addWidget(button_dsb)
    layout.addWidget(button_uscf)
    return widget


class Widget_Settings(QWidget):
    def __init__(self, window_main):
        super().__init__()
        self.window_main = window_main
        self.server_widget = None
        self.ready = False
        self.layout = QVBoxLayout(self)
        self.set_header()

        layout = QGridLayout()
        layout.setHorizontalSpacing(50)
        layout.setVerticalSpacing(20)
        layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(3, 1)

        _, _, self.layout_inner = get_scroll_area_widgets_and_layouts(
            self.layout, layout_inner=layout, horizontal_bar=True
        )
        self.fill_in_layout()
        FTP_CONNECTION.refresh_threaded(self.window_main, self.refresh_server_widget)

    def set_header(self):
        version = get_version()
        if version is None:
            text = "ToMaChess"
        else:
            text = f"ToMaChess {version}"
        header = get_label(text, "extra_large", bold=True)
        header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(header)

    def fill_in_layout(self):
        settings = SETTINGS_HANDLER.settings
        for i, (key, value) in enumerate(settings.items()):
            self.layout_inner.addWidget(get_label(SETTINGS_DISPLAY[key], "large", translate=True), i, 1)
            widget = get_suitable_widget(value, widget_size_factors=(2, 1))
            if key == "server_password":
                widget.setEchoMode(QLineEdit.EchoMode.Password)
            elif key == "server_address":
                self.server_widget = widget
            self.layout_inner.addWidget(widget, i, 2)
        self.layout_inner.addWidget(get_label("Update Lists", "large", translate=True), len(settings), 1)
        self.layout_inner.addWidget(get_update_lists_widget(self.window_main), len(settings), 2)
        reset_button = get_button("large", (15, 5), "Reset", connect_function=self.reset_settings, translate=True)
        save_button = get_button("large", (30, 5), "Save", connect_function=self.save_settings, translate=True)
        self.layout_inner.addWidget(reset_button, len(settings) + 1, 1)
        self.layout_inner.addWidget(save_button, len(settings) + 1, 2)

    def reset_settings(self):
        if not self.ready:
            return
        SETTINGS_HANDLER.reset()
        self.window_main.reload()

    def save_settings(self):
        if not self.ready:
            return
        for i, key in enumerate(SETTINGS_HANDLER.settings):
            SETTINGS_HANDLER.set(key, get_value_from_suitable_widget(self.layout_inner.itemAtPosition(i, 2).widget()))
        SETTINGS_HANDLER.save()
        self.window_main.reload()

    def refresh_server_widget(self):
        if FTP_CONNECTION.check_connection():
            self.server_widget.setObjectName("positive")
        else:
            self.server_widget.setObjectName("negative")
        self.server_widget.style().unpolish(self.server_widget)
        self.server_widget.style().polish(self.server_widget)
        self.ready = True
