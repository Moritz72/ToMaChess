from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget
from ..common.gui_functions import add_widgets_in_layout, get_button, get_label, set_window_size, set_window_title


class Window_Confirm(QMainWindow):
    confirmed = Signal()

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, title)

        self.widget = QWidget()
        self.layout_main: QVBoxLayout = QVBoxLayout(self.widget)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.widget)

        self.layout_main.addWidget(get_label("Are you sure?", "large", translate=True))
        yes_button = get_button("large", (10, 4), "Yes", connect=self.emit_yes, translate=True)
        no_button = get_button("large", (10, 4), "No", connect=self.close, translate=True)
        add_widgets_in_layout(self.layout_main, QHBoxLayout(), [yes_button, no_button])
        set_window_size(self, self.sizeHint())

    def emit_yes(self) -> None:
        self.confirmed.emit()
        self.close()
