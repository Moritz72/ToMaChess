from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtWidgets import QApplication, QDockWidget, QMainWindow
from ..common.gui_styles import set_stylesheet
from ..common.gui_functions import set_window_title
from ..dock_widgets.side_menu import Side_Menu
from ..stacked_widgets.stacked_widget import Stacked_Widget
from ..stacked_widgets.stacked_widget_menu import Stacked_Widget_Menu
from ..stacked_widgets.stacked_widget_tournament import Stacked_Widget_Tournament
from ..stacked_widgets.stacked_widget_ms_tournament import Stacked_Widget_MS_Tournament
from ...common.manager_size import MANAGER_SIZE
from ...common.manager_settings import MANAGER_SETTINGS
from ...common.manager_translation import MANAGER_TRANSLATION

STACKED_WIDGETS = {
    "Default": Stacked_Widget_Menu,
    "Tournament": Stacked_Widget_Tournament,
    "MS_Tournament": Stacked_Widget_MS_Tournament
}


class Window_Main(QMainWindow):
    def __init__(self) -> None:
        MANAGER_SETTINGS.load()
        MANAGER_SIZE.refresh()
        super().__init__()
        self.stacked_widget: Stacked_Widget = Stacked_Widget_Menu(self)
        self.side_menu: Side_Menu = Side_Menu(self.stacked_widget)
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
        self.stacked_widget = STACKED_WIDGETS[string](self, **args)
        self.setCentralWidget(self.stacked_widget)
        self.side_menu.set_stacked_widget(self.stacked_widget)
        self.set_side_menu()
        if index is not None:
            self.stacked_widget.setCurrentIndex(index)
            self.side_menu.make_side_menu()

    def set_side_menu(self) -> None:
        dock_widgets = self.side_menu.get_widgets()
        dock_widget_heights = [2 * dock_widget.sizeHint().height() for dock_widget in dock_widgets]
        for dock_widget in self.findChildren(QDockWidget):
            self.removeDockWidget(dock_widget)
        for dock_widget in dock_widgets[::-1]:
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_widget)
        for i in range(len(dock_widgets) - 1):
            self.splitDockWidget(dock_widgets[i], dock_widgets[i + 1], Qt.Orientation.Vertical)
        self.resizeDocks(dock_widgets, len(dock_widgets) * [self.side_menu.get_width()], Qt.Orientation.Horizontal)
        self.resizeDocks(dock_widgets, dock_widget_heights, Qt.Orientation.Vertical)

    def reload(self) -> None:
        MANAGER_SIZE.refresh()
        MANAGER_TRANSLATION.refresh()
        set_stylesheet(f"{MANAGER_SETTINGS['style'][0]}.qss")
        self.set_stacked_widget("Default", index=self.stacked_widget.currentIndex())

    def close_windows(self) -> None:
        for window in QApplication.topLevelWidgets():
            if window is not self:
                try:
                    window.close()
                except RuntimeError:
                    pass

    def closeEvent(self, event: QCloseEvent) -> None:
        self.close_windows()
        super().closeEvent(event)
