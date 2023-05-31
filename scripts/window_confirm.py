from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from .functions_gui import get_label, get_button, add_widgets_in_layout


class Window_Confirm(QMainWindow):
    confirmed = pyqtSignal()

    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.widget.setLayout(self.layout)

        self.layout.addWidget(get_label("Are you sure?", "large"))
        yes_button = get_button("large", (10, 4), "Yes", connect_function=self.confirmed.emit)
        no_button = get_button("large", (10, 4), "No", connect_function=self.close)
        add_widgets_in_layout(self.layout, QHBoxLayout(), (yes_button, no_button))
