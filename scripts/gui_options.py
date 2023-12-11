from typing import Any
from PySide6.QtWidgets import QPushButton, QMainWindow, QWidget, QLineEdit, QCheckBox, QSpinBox, QComboBox, \
    QApplication, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent
from .manager_translation import MANAGER_TRANSLATION
from .parameter import Parameter
from .gui_functions import Widget_Size, set_fixed_size, set_font, set_window_title, connect_widget, get_label, \
    get_scroll_area_widgets_and_layouts, get_lineedit, get_check_box, get_spin_box, get_combo_box


class Options_Button(QPushButton):
    def __init__(
            self, var: Parameter, size: str | None, widget_size: Widget_Size, text: str = "",
            bold: bool = False, translate: bool = False
    ) -> None:
        super().__init__(MANAGER_TRANSLATION.tl(text) if translate else text)
        self.obj: Parameter = var
        self.options_window: Options_Window = Options_Window(self.obj, translate, parent=self)
        self.options_window.options_closed.connect(self.get_args_and_args_display_from_window)
        self.clicked.connect(self.options_window.show)

        set_fixed_size(self, widget_size)
        set_font(self, size, bold)

    def get_args_and_args_display_from_window(self) -> None:
        if self.obj.is_valid():
            self.options_window.close()

    def give_back(self) -> Parameter:
        return self.obj


class Options_Window(QMainWindow):
    options_closed = Signal()

    def __init__(self, obj: Parameter, translate: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        set_window_title(self, "Options")

        self.obj: Parameter = obj
        self.widgets: list[QWidget] = []
        self.translate: bool = translate

        self.make_window_from_object()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.options_closed.emit()
        super().closeEvent(event)

    def make_window_from_object(self) -> None:
        arg_list, arg_display_list = self.obj.get_arg_list(), self.obj.get_arg_display_list()
        self.widgets = [get_suitable_widget(value, translate=self.translate) for value in arg_list]

        parameter_widgets: list[QWidget] = []
        for display, widg in zip(arg_display_list, self.widgets):
            connect_widget(widg, self.update_widget_data)
            parameter_widgets.extend([get_label(display, "large", translate=self.translate), widg, QLabel()])

        widget = QWidget()
        layout = QVBoxLayout(widget)
        get_scroll_area_widgets_and_layouts(layout, parameter_widgets[:-1], margins=(20, 20, 40, 20), spacing=10)
        self.setCentralWidget(widget)
        self.setFixedWidth(layout.sizeHint().width())
        self.setFixedHeight(min(layout.sizeHint().height() + 2, int(QApplication.primaryScreen().size().height() * .4)))

    def update_widget_data(self) -> None:
        self.obj.update([get_value_from_suitable_widget(widget) for widget in self.widgets])
        if self.obj.window_update_necessary:
            self.make_window_from_object()


def get_suitable_widget(
        var: Any, size: str | None = "medium", widget_size_factors: tuple[int, int] = (1, 1), translate: bool = False
) -> QWidget:
    size_x, size_y = widget_size_factors
    match var:
        case str():
            return get_lineedit(size, (15 * size_x, 3 * size_y), text=var)
        case bool():
            return get_check_box(var, (3 * size_x, 3 * size_y))
        case int():
            return get_spin_box(var, size, (5 * size_x, 3 * size_y), align=Qt.AlignmentFlag.AlignCenter)
        case list():
            return get_combo_box(var, size, (15 * size_x, 3 * size_y), translate=translate)
        case _:
            return Options_Button(var, size, (15 * size_x, 3 * size_y), text="Options", translate=translate)


def get_value_from_suitable_widget(widget: QWidget) -> Any:
    match widget:
        case QLineEdit():
            return widget.text()
        case QCheckBox():
            return widget.isChecked()
        case QSpinBox():
            return widget.value()
        case QComboBox():
            return sorted((widget.itemData(i) for i in range(widget.count())), key=lambda x: x != widget.currentData())
        case Options_Button():
            return widget.give_back()
        case QPushButton():
            return ""
    return NotImplemented
