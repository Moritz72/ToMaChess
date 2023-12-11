from typing import Any
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QCloseEvent
from .manager_size import MANAGER_SIZE
from .manager_settings import MANAGER_SETTINGS
from .manager_translation import MANAGER_TRANSLATION
from .side_menu import Side_Menu
from .stacked_widget import Stacked_Widget
from .stacked_widget_menu import Stacked_Widget_Menu
from .stacked_widget_tournament import Stacked_Widget_Tournament
from .stacked_widget_ms_tournament import Stacked_Widget_MS_Tournament
from .gui_styles import set_stylesheet
from .gui_functions import set_window_title

STACKED_WIDGETS = {
    "Default": Stacked_Widget_Menu,
    "Tournament": Stacked_Widget_Tournament,
    "MS_Tournament": Stacked_Widget_MS_Tournament
}


class Window_Main(QMainWindow):
    def __init__(self) -> None:
        MANAGER_SETTINGS.load()
        super().__init__()
        self.side_menu: Side_Menu | None = None
        self.stacked_widget: Stacked_Widget | None = None
        self.reload()
        set_window_title(self, "ToMaChess")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F11:
            if self.windowState() == Qt.WindowState.WindowFullScreen:
                self.showNormal()
            else:
                self.showFullScreen()
        super().keyPressEvent(event)

    def set_stacked_widget(self, string: str, args: dict[str, Any] | None = None, index: int | None = None) -> None:
        self.close_windows()
        args = args or dict()
        if self.side_menu is not None:
            self.removeDockWidget(self.side_menu)
        self.stacked_widget = STACKED_WIDGETS[string](self, **args)
        if self.stacked_widget is None:
            return

        self.setCentralWidget(self.stacked_widget)
        self.side_menu = Side_Menu(self.stacked_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.side_menu)
        if index is not None:
            self.stacked_widget.setCurrentIndex(index)
            self.side_menu.make_side_menu()

    def reload(self) -> None:
        MANAGER_SIZE.refresh()
        MANAGER_TRANSLATION.refresh()
        set_stylesheet(f"{MANAGER_SETTINGS['style'][0]}.qss")
        index = 0 if self.stacked_widget is None else self.stacked_widget.currentIndex()
        self.set_stacked_widget("Default", index=index)

    def close_windows(self) -> None:
        for window in QApplication.topLevelWidgets():
            if window is not self:
                window.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.close_windows()
        super().closeEvent(event)
