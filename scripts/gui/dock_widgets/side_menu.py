from typing import Any, cast
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QDockWidget, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from ..stacked_widgets.stacked_widget import Buttons_Args, Stacked_Widget
from ..common.gui_functions import get_button, get_scroll_area_widgets_and_layouts


class Side_Menu_Widget(QDockWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setTitleBarWidget(QWidget())
        self.buttons: list[QPushButton] = []

    def fill_in_buttons(self, buttons_args: Buttons_Args) -> None:
        self.buttons.clear()
        for args in buttons_args:
            defaults: dict[str, Any] = {"widget_size": (None, 3), "translate": True}
            args = defaults | args
            button = get_button("large", **args)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setMinimumWidth(0)
            button.setStyleSheet("QPushButton {text-align: left; padding-left: 10px; padding-right: 10px;}")
            button.clicked.connect(self.set_button_clicked_states)
            self.buttons.append(button)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        get_scroll_area_widgets_and_layouts(layout, self.buttons)
        self.setWidget(widget)

    def set_button_clicked_states(self) -> None:
        sender = cast(QPushButton, self.sender())
        if not sender.isChecked():
            sender.setChecked(True)
            return
        for button in self.buttons:
            if button is not self.sender():
                button.setChecked(False)


class Side_Menu(QObject):
    size_changed = Signal()

    def __init__(self, stacked_widget: Stacked_Widget) -> None:
        super().__init__()
        self.stacked_widget: Stacked_Widget = stacked_widget
        self.widgets: list[Side_Menu_Widget] = []
        self.set_stacked_widget(stacked_widget)

    def get_widgets(self) -> list[Side_Menu_Widget]:
        return self.widgets

    def get_width(self) -> int:
        return max(int(widget.layout().sizeHint().width() * 1.2) for widget in self.widgets)

    def set_stacked_widget(self, stacked_widget: Stacked_Widget) -> None:
        self.widgets.clear()
        self.stacked_widget = stacked_widget
        self.stacked_widget.make_side_menu.connect(self.make_side_menu)
        self.make_side_menu()

    def make_side_menu(self) -> None:
        buttons_args_list = self.stacked_widget.get_buttons_args_list()
        difference = len(buttons_args_list) - len(self.widgets)
        if difference > 0:
            self.widgets.extend([Side_Menu_Widget() for _ in range(difference)])
        elif difference < 0:
            self.widgets = self.widgets[:difference]
        if difference != 0:
            self.size_changed.emit()
        for i, (widget, buttons_args) in enumerate(zip(self.widgets, buttons_args_list)):
            widget.fill_in_buttons(buttons_args)
            widget.buttons[self.stacked_widget.get_active_button_index(i)].setChecked(True)
