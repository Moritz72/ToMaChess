from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from .class_size_handler import size_handler
from .side_menu import Side_Menu
from .stacked_widget_default import Stacked_Widget_Default
from .stacked_widget_tournament import Stacked_Widget_Tournament
from .stacked_widget_ms_tournament import Stacked_Widget_MS_Tournament

stacked_widgets = {
    "Default": Stacked_Widget_Default,
    "Tournament": Stacked_Widget_Tournament,
    "MS_Tournament": Stacked_Widget_MS_Tournament
}


class Window_Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ToMaChess")
        self.setGeometry(300, 100, 900, 900)
        self.setStyleSheet("QMainWindow::separator {width: 1px; border: none;}")

        self.side_menu = None
        self.stacked_widget = None
        self.set_stacked_widget("Default")

    def set_stacked_widget(self, string, args=None):
        args = args or dict()
        if self.side_menu is not None:
            self.removeDockWidget(self.side_menu)
        self.stacked_widget = stacked_widgets[string](self, **args)
        self.setCentralWidget(self.stacked_widget)
        self.side_menu = Side_Menu(self.stacked_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.side_menu)

    def reload(self, i):
        size_handler.refresh()
        self.set_stacked_widget("Default")
        self.stacked_widget.setCurrentIndex(i)
        self.side_menu.set_button_unclicked(0)
        self.side_menu.set_button_clicked(i)
