from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING, Any
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtCore import Signal
if TYPE_CHECKING:
    from .window_main import Window_Main


class Stacked_Widget(QStackedWidget):
    make_side_menu = Signal()

    def __init__(self, window_main: Window_Main):
        super().__init__()
        self.window_main: Window_Main = window_main

    @abstractmethod
    def get_buttons_args(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get_active_button_index(self) -> int:
        pass
