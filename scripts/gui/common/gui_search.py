from typing import Callable
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLineEdit, QSizePolicy
from .gui_functions import Widget_Size, set_fixed_size, set_font


class Search_Bar(QLineEdit):
    def __init__(
            self, function: Callable[[], None], size: str, widget_size: Widget_Size = None, interval: int = 300
    ) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        set_fixed_size(self, widget_size)
        set_font(self, size)
        self.textChanged.connect(self.reset_timer)

        self.timer: QTimer = QTimer()
        self.timer.setInterval(interval)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(function)

    def reset_timer(self) -> None:
        self.timer.stop()
        self.timer.start()
