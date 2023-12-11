from typing import cast
from PySide6.QtWidgets import QWidget, QDockWidget, QSizePolicy, QVBoxLayout, QPushButton
from .stacked_widget import Stacked_Widget
from .gui_functions import get_button, get_scroll_area_widgets_and_layouts


class Side_Menu(QDockWidget):
    def __init__(self, stacked_widget: Stacked_Widget):
        super().__init__()
        self.setTitleBarWidget(QWidget())
        self.stacked_widget: Stacked_Widget = stacked_widget
        self.stacked_widget.make_side_menu.connect(self.make_side_menu)
        self.buttons: list[QPushButton] = []
        self.make_side_menu()

    def fill_buttons(self) -> None:
        for args in self.stacked_widget.get_buttons_args():
            button = get_button("large", (None, 2.5), **args, translate=True)
            button.setObjectName("side_menu_button")
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setMinimumWidth(0)
            button.setStyleSheet("QPushButton {text-align: left; padding-left: 10px; padding-right: 10px;}")
            button.clicked.connect(self.set_button_clicked_states)
            self.buttons.append(button)

    def make_side_menu(self) -> None:
        self.buttons = []
        self.fill_buttons()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        get_scroll_area_widgets_and_layouts(layout, self.buttons)
        self.setWidget(widget)
        self.set_button_clicked(self.stacked_widget.get_active_button_index())

    def set_button_clicked(self, index: int) -> None:
        self.buttons[index].setChecked(True)

    def set_button_unclicked(self, index: int) -> None:
        self.buttons[index].setChecked(False)

    def set_button_clicked_states(self) -> None:
        sender = cast(QPushButton, self.sender())
        if not sender.isChecked():
            sender.setChecked(True)
            return
        for button in self.buttons:
            if button is not self.sender():
                button.setChecked(False)
