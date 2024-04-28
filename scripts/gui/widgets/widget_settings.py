from __future__ import annotations
from typing import TYPE_CHECKING, cast
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLineEdit, QVBoxLayout, QWidget
from ..common.gui_functions import get_button, get_label, get_scroll_area_widgets_and_layouts
from ..common.gui_options import get_suitable_widget, get_value_from_suitable_widget
from ..windows.window_rating_lists import Window_Rating_Lists
from ...common.functions_util import get_version
from ...common.manager_settings import MANAGER_SETTINGS, SETTINGS_DISPLAY
from ...export.ftp.ftp_connection import FTP_CONNECTION
if TYPE_CHECKING:
    from ..windows.window_main import Window_Main


class Widget_Settings(QWidget):
    def __init__(self, window_main: Window_Main) -> None:
        super().__init__()
        self.window_main: Window_Main = window_main
        self.window_lists: Window_Rating_Lists = Window_Rating_Lists(self.window_main, self)
        self.server_widget: QWidget | None = None
        self.ready: bool = False
        self.layout_main: QVBoxLayout = QVBoxLayout(self)
        self.set_header()

        layout_inner = QGridLayout()
        layout_inner.setHorizontalSpacing(50)
        layout_inner.setVerticalSpacing(20)
        layout_inner.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        layout_inner.setColumnStretch(0, 1)
        layout_inner.setColumnStretch(3, 1)

        self.layout_inner = cast(QGridLayout, get_scroll_area_widgets_and_layouts(
            self.layout_main, layout_inner=layout_inner, horizontal_bar=True
        )[2])
        self.fill_in_layout()
        FTP_CONNECTION.refresh_threaded(self.window_main, self.refresh_server_widget)

    def set_header(self) -> None:
        version = get_version()
        if version is None:
            text = "ToMaChess"
        else:
            text = f"ToMaChess {version}"
        header = get_label(text, "extra_large", bold=True, align=Qt.AlignmentFlag.AlignCenter)
        self.layout_main.addWidget(header)

    def fill_in_layout(self) -> None:
        settings = MANAGER_SETTINGS
        for i, (key, value) in enumerate(settings.items()):
            self.layout_inner.addWidget(get_label(SETTINGS_DISPLAY[key], "large", translate=True), i, 1)
            widget = get_suitable_widget(value, widget_size_factors=(2, 1))
            if key == "server_password":
                cast(QLineEdit, widget).setEchoMode(QLineEdit.EchoMode.Password)
            elif key == "server_address":
                self.server_widget = widget
            self.layout_inner.addWidget(widget, i, 2)

        rating_list_button = get_button("large", (None, 4), "Open", connect=self.window_lists.show, translate=True)
        reset_button = get_button("large", (15, 5), "Reset", connect=self.reset_settings, translate=True)
        save_button = get_button("large", (30, 5), "Save", connect=self.save_settings, translate=True)
        self.layout_inner.addWidget(get_label("Rating Lists", "large", translate=True), len(settings), 1)
        self.layout_inner.addWidget(rating_list_button, len(settings), 2)
        self.layout_inner.addWidget(reset_button, len(settings) + 1, 1)
        self.layout_inner.addWidget(save_button, len(settings) + 1, 2)

    def reset_settings(self) -> None:
        if not self.ready:
            return
        MANAGER_SETTINGS.reset()
        self.window_main.reload()

    def save_settings(self) -> None:
        if not self.ready:
            return
        for i, key in enumerate(MANAGER_SETTINGS):
            MANAGER_SETTINGS[key] = get_value_from_suitable_widget(self.layout_inner.itemAtPosition(i, 2).widget())
        MANAGER_SETTINGS.save()
        self.window_main.reload()

    def refresh_server_widget(self) -> None:
        if self.server_widget is None:
            return
        if FTP_CONNECTION.check_connection():
            self.server_widget.setObjectName("positive")
        else:
            self.server_widget.setObjectName("negative")
        self.server_widget.style().unpolish(self.server_widget)
        self.server_widget.style().polish(self.server_widget)
        self.ready = True
