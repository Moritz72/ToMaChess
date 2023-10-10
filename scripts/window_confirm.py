from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from .functions_gui import get_label, get_button, add_widgets_in_layout, set_window_title, set_window_size


class Window_Confirm(QMainWindow):
    confirmed = Signal()

    def __init__(self, title, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, title)

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.setCentralWidget(self.widget)

        self.layout.addWidget(get_label("Are you sure?", "large", translate=True))
        yes_button = get_button("large", (10, 4), "Yes", connect_function=self.emit_yes, translate=True)
        no_button = get_button("large", (10, 4), "No", connect_function=self.close, translate=True)
        add_widgets_in_layout(self.layout, QHBoxLayout(), (yes_button, no_button))
        set_window_size(self, self.sizeHint())

    def emit_yes(self):
        self.confirmed.emit()
        self.close()
