from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from os import mkdir
from os.path import exists
from .side_menu import Side_Menu
from .stacked_widget_default import Stacked_Widget_Default
from .stacked_widget_tournament import Stacked_Widget_Tournament
from .stacked_widget_ms_tournament import Stacked_Widget_MS_Tournament
from .functions_util import get_root_directory

stacked_widgets = {
    "Default": Stacked_Widget_Default,
    "Tournament": Stacked_Widget_Tournament,
    "MS_Tournament": Stacked_Widget_MS_Tournament
}


def make_data_folders():
    root_directory = get_root_directory()
    folder_directories = (
        f"{root_directory}/data",
        f"{root_directory}/data/tournaments",
        f"{root_directory}/data/players",
        f"{root_directory}/data/teams",
        f"{root_directory}/data/ms_tournaments"
    )
    for directory in folder_directories:
        if not exists(directory):
            mkdir(directory)


class Window_Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ToMaChess")
        self.setGeometry(300, 100, 900, 900)
        self.setStyleSheet("QMainWindow::separator {width: 1px; border: none;}")

        make_data_folders()
        self.side_menu = None
        self.stacked_widget = None
        self.set_stacked_widget("Default")

    def set_stacked_widget(self, string, args=dict()):
        if self.side_menu is not None:
            self.removeDockWidget(self.side_menu)
        self.stacked_widget = stacked_widgets[string](self, **args)
        self.setCentralWidget(self.stacked_widget)
        self.side_menu = Side_Menu(self.stacked_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.side_menu)
