from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from .class_size_handler import SIZE_HANDLER
from .class_settings_handler import SETTINGS_HANDLER
from .class_translation_handler import TRANSLATION_HANDLER
from .side_menu import Side_Menu
from .stacked_widget_default import Stacked_Widget_Default
from .stacked_widget_tournament import Stacked_Widget_Tournament
from .stacked_widget_ms_tournament import Stacked_Widget_MS_Tournament
from .functions_styles import set_stylesheet
from .functions_gui import set_window_title

STACKED_WIDGETS = {
    "Default": Stacked_Widget_Default,
    "Tournament": Stacked_Widget_Tournament,
    "MS_Tournament": Stacked_Widget_MS_Tournament
}


class Window_Main(QMainWindow):
    def __init__(self):
        SETTINGS_HANDLER.load()
        super().__init__()
        self.side_menu = None
        self.stacked_widget = None
        self.reload()
        set_window_title(self, "ToMaChess")

    def set_stacked_widget(self, string, args=None, index=None):
        args = args or dict()
        if self.side_menu is not None:
            self.removeDockWidget(self.side_menu)
        self.stacked_widget = STACKED_WIDGETS[string](self, **args)
        self.setCentralWidget(self.stacked_widget)
        self.side_menu = Side_Menu(self.stacked_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.side_menu)
        if index is not None:
            self.stacked_widget.setCurrentIndex(index)
            self.side_menu.make_side_menu()

    def reload(self):
        SIZE_HANDLER.refresh()
        TRANSLATION_HANDLER.refresh()
        set_stylesheet(f"{SETTINGS_HANDLER.settings['style'][0]}.qss")
        index = 0 if self.stacked_widget is None else self.stacked_widget.currentIndex()
        self.set_stacked_widget("Default", index=index)
