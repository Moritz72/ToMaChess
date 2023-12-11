from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from .tournament import Tournament
from .widget_tournament_parameters import Widget_Tournament_Parameters
from .gui_functions import set_window_title, set_window_size, get_button


class Window_Tournament_Edit_Parameters(QMainWindow):
    saved_changes = Signal()

    def __init__(self, tournament: Tournament, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, "Edit Parameters")

        self.tournament: Tournament = tournament

        self.widget: QWidget = QWidget()
        self.layout_main: QVBoxLayout = QVBoxLayout(self.widget)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.widget)

        self.widget_tournament_parameters = Widget_Tournament_Parameters(self.tournament)
        save_button = get_button("large", (10, 5), "Save", connect=self.save_changes, translate=True)
        self.layout_main.addWidget(self.widget_tournament_parameters)
        self.layout_main.addWidget(save_button)
        set_window_size(self, self.sizeHint())

    def save_changes(self) -> None:
        valid_parameters = self.widget_tournament_parameters.apply_parameters()
        if valid_parameters:
            self.saved_changes.emit()
            self.close()
