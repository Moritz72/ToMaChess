from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING, Any
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtCore import Signal
if TYPE_CHECKING:
    from .window_main import Window_Main

Buttons_Args = list[dict[str, Any]]


class Stacked_Widget(QStackedWidget):
    make_side_menu = Signal()

    def __init__(self, window_main: Window_Main):
        super().__init__()
        self.window_main: Window_Main = window_main

    def get_active_button_index(self, i: int) -> int:
        assert (i == 0)
        return self.currentIndex()

    @abstractmethod
    def get_buttons_args_list(self) -> list[Buttons_Args]:
        pass
