from PyQt5.QtWidgets import QWidget, QDockWidget, QSizePolicy, QVBoxLayout
from .functions_gui import get_button, get_scroll_area_widgets_and_layouts


def get_dummy_button():
    dummy_button = get_button("large", (None, None), text="-------------------------")
    dummy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    dummy_button.setMinimumWidth(0)
    dummy_button.setFixedHeight(0)
    return dummy_button


class Side_Menu(QDockWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setTitleBarWidget(QWidget())
        self.stacked_widget = stacked_widget
        self.stacked_widget.make_side_menu.connect(self.make_side_menu)
        self.buttons = []
        self.make_side_menu()

    def fill_buttons(self):
        for args in self.stacked_widget.get_buttons_args():
            button = get_button("large", (None, 2.5), **args, translate=True)
            button.setObjectName("side_menu_button")
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.setMinimumWidth(0)
            button.setStyleSheet("QPushButton {text-align: left; padding-left: 10px;}")
            button.clicked.connect(self.set_button_clicked_states)
            self.buttons.append(button)

    def make_side_menu(self):
        self.buttons = []
        self.fill_buttons()
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        get_scroll_area_widgets_and_layouts(layout, [get_dummy_button()] + self.buttons)
        widget.setLayout(layout)
        self.setWidget(widget)
        self.set_button_clicked(self.stacked_widget.get_active_button_index())

    def set_button_clicked(self, index):
        self.buttons[index].setChecked(True)

    def set_button_unclicked(self, index):
        self.buttons[index].setChecked(False)

    def set_button_clicked_states(self):
        if not self.sender().isChecked():
            self.sender().setChecked(True)
            return
        for button in self.buttons:
            if button is not self.sender():
                button.setChecked(False)
