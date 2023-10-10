from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from .widget_tournament_parameters import Widget_Tournament_Parameters
from .functions_gui import set_window_title, set_window_size, get_button


class Window_Tournament_Edit_Parameters(QMainWindow):
    saved_changes = Signal()

    def __init__(self, tournament, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, "Edit Parameters")

        self.tournament = tournament

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.setCentralWidget(self.widget)

        self.widget_tournament_parameters = Widget_Tournament_Parameters(self.tournament)
        save_button = get_button("large", (10, 5), "Save", connect_function=self.save_changes, translate=True)
        self.layout.addWidget(self.widget_tournament_parameters)
        self.layout.addWidget(save_button)
        set_window_size(self, self.sizeHint())

    def save_changes(self):
        valid_parameters = self.widget_tournament_parameters.apply_parameters()
        if valid_parameters:
            self.saved_changes.emit()
            self.close()
