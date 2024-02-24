from typing import Sequence, Any, Callable, TypeVar, cast
from PySide6.QtWidgets import QComboBox, QLineEdit, QCheckBox, QSpinBox, QPushButton, QLabel, QScrollArea, \
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QSizePolicy, QTableWidgetItem, QLayout
from PySide6.QtCore import Qt, QObject, QSize
from PySide6.QtGui import QFont, QScreen
from .manager_size import MANAGER_SIZE
from .manager_settings import MANAGER_SETTINGS
from .manager_translation import MANAGER_TRANSLATION
from .gui_classes import Combo_Box_Editable, Align_Delegate, Function_Worker

T = TypeVar('T', bound=QVBoxLayout | QHBoxLayout)
Widget_Size = tuple[float, float] | tuple[float, None] | tuple[None, float] | None


def close_window(window: QMainWindow | None) -> None:
    try:
        if window is None:
            return
        window.close()
    except RuntimeError:
        pass


def add_widgets_to_layout(layout: QLayout, widgets: Sequence[QWidget]) -> None:
    for widget in widgets:
        layout.addWidget(widget)


def add_widgets_in_layout(
        layout: T, layout_inner: QLayout, widgets: Sequence[QWidget]
) -> None:
    add_widgets_to_layout(layout_inner, widgets)
    layout.addLayout(layout_inner)


def get_scroll_area_widgets_and_layouts(
        layout: QLayout, widgets_in_scroll_area: Sequence[QWidget] | None = None,
        margins: tuple[int, int, int, int] = (0, 0, 0, 0), spacing: int = 0,
        layout_inner: QLayout | None = None, horizontal_bar: bool = False
) -> tuple[QScrollArea, QWidget, QLayout]:
    if widgets_in_scroll_area is None:
        widgets_in_scroll_area = []
    scroll_area = QScrollArea()
    if not horizontal_bar:
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_area.setWidgetResizable(True)
    scroll_area.setMinimumWidth(1)
    widget_inner = QWidget()
    if layout_inner is None:
        layout_inner = QVBoxLayout()
        layout_inner.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_inner.setContentsMargins(*margins)
        layout_inner.setSpacing(spacing)
    for widget in widgets_in_scroll_area:
        layout_inner.addWidget(widget)
    widget_inner.setLayout(layout_inner)
    scroll_area.setWidget(widget_inner)
    layout.addWidget(scroll_area)
    return scroll_area, widget_inner, layout_inner


def get_screen(window: QMainWindow) -> QScreen:
    if window.parent() is None:
        return QApplication.primaryScreen()
    parent = cast(QWidget, window.parent())
    window_center = parent.window().geometry().center()
    app = QApplication.instance()
    assert(app is not None)
    screen = cast(QApplication, app).screenAt(window_center)
    if screen is None:
        return get_screen(cast(QMainWindow, parent.window()))
    return screen


def set_window_title(window: QMainWindow, title: str) -> None:
    window.setWindowTitle(MANAGER_TRANSLATION.tl(title))


def set_window_size_absolute(window: QMainWindow, size: QSize) -> None:
    screen_geometry = get_screen(window).availableGeometry()
    parent = cast(QWidget, window.parent())
    window_center = parent.window().geometry().center()
    window_left = window_center.x() - size.width() // 2
    window_top = window_center.y() - size.height() // 2
    space_left = window_center.x() - size.width() // 2 - screen_geometry.x()
    space_right = screen_geometry.x() + screen_geometry.width() - (window_center.x() + size.width() // 2)
    space_top = window_center.y() - size.height() // 2 - screen_geometry.y()
    space_bottom = screen_geometry.y() + screen_geometry.height() - (window_center.y() + size.height() // 2)

    if space_left < 0:
        window_left -= space_left
    elif space_right < 0:
        window_left += space_right
    if space_top < 40:
        window_top -= space_top - 40
    elif space_bottom < 0:
        window_top += space_bottom

    window.setGeometry(window_left, window_top, 0, 0)
    window.setFixedSize(size)


def set_window_size(
        window: QMainWindow, size: QSize, factor_x: float | None = None, factor_y: float | None = None
) -> None:
    screen_geometry = get_screen(window).availableGeometry()
    if factor_x is not None:
        size.setWidth(int(factor_x * screen_geometry.width()))
    if factor_y is not None:
        size.setHeight(int(factor_y * screen_geometry.height()))
    set_window_size_absolute(window, size)


def set_fixed_size(widget: QWidget, widget_size: Widget_Size) -> None:
    if widget_size is None:
        return
    size_factor = MANAGER_SIZE.widget_size_factor
    if widget_size[0] is not None:
        widget.setFixedWidth(int(widget_size[0] * size_factor))
    if widget_size[1] is not None:
        widget.setFixedHeight(int(widget_size[1] * size_factor))


def set_max_size(widget: QWidget, widget_size: Widget_Size) -> None:
    if widget_size is None:
        return
    size_factor = MANAGER_SIZE.widget_size_factor
    if widget_size[0] is not None:
        widget.setMaximumWidth(int(widget_size[0] * size_factor))
    if widget_size[1] is not None:
        widget.setMaximumHeight(int(widget_size[1] * size_factor))


def get_font(font_size: int | None = None, bold: bool = False) -> QFont:
    font = QFont(MANAGER_SETTINGS["font"][0])
    if font_size is not None:
        font.setPointSize(font_size)
    font.setBold(bold)
    return font


def set_font(widget: QWidget | QTableWidgetItem, size: str | None, bold: bool = False) -> None:
    if widget is None:
        return
    if size is None:
        widget.setFont(get_font(None, bold))
    else:
        widget.setFont(get_font(MANAGER_SIZE.font_sizes[size], bold))


def set_object_name(widget: QWidget, object_name: str | None) -> None:
    if object_name is not None:
        widget.setObjectName(object_name)


def get_label(
        text: str | Sequence[str], size: str | None, widget_size: Widget_Size = None, bold: bool = False,
        align: Qt.AlignmentFlag | None = None, translate: bool = False, object_name: str | None = None
) -> QLabel:
    if translate:
        text = MANAGER_TRANSLATION.tl(text)
    assert(isinstance(text, str))
    label = QLabel(text)
    set_object_name(label, object_name)
    set_fixed_size(label, widget_size)
    set_font(label, size, bold)
    if align is not None:
        label.setAlignment(align)
    return label


def get_lineedit(
        size: str | None, widget_size: Widget_Size = None, text: str | Sequence[str] = "",
        connect: Callable[[], Any] | None = None, bold: bool = False, read_only: bool = False,
        translate: bool = False, object_name: str | None = None
) -> QLineEdit:
    if translate:
        text = MANAGER_TRANSLATION.tl(text)
    assert(isinstance(text, str))
    lineedit = QLineEdit(text)
    lineedit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    set_object_name(lineedit, object_name)
    set_fixed_size(lineedit, widget_size)
    set_font(lineedit, size, bold)
    if connect is not None:
        lineedit.editingFinished.connect(connect)
    lineedit.setReadOnly(read_only)
    return lineedit


def get_button(
        size: str | None, widget_size: Widget_Size = None, text: str | Sequence[str] = "",
        connect: Callable[[], Any] | list[Callable[[], Any]] | None = None, bold: bool = False, align: str = "center",
        checkable: bool = False, enabled: bool = True, translate: bool = False, object_name: str | None = None
) -> QPushButton:
    if translate:
        text = MANAGER_TRANSLATION.tl(text)
    assert(isinstance(text, str))
    button = QPushButton(text)
    set_object_name(button, object_name)
    set_fixed_size(button, widget_size)
    set_font(button, size, bold)
    button.setCheckable(checkable)
    button.setEnabled(enabled)
    button.setStyleSheet(f"text-align: {align}")
    if isinstance(connect, list):
        for function in connect:
            button.clicked.connect(function)
    elif connect is not None:
        button.clicked.connect(connect)
    return button


def get_button_threaded(
        parent: QObject, size: str | None, widget_size: Widget_Size = None, text: str | Sequence[str] = "",
        load_text: str | Sequence[str] = "", connect: Callable[[], Any] | None = None, bold: bool = False,
        align: str = "center", checkable: bool = True, enabled: bool = True, translate: bool = False,
        object_name: str | None = None
) -> QPushButton:
    assert(connect is not None)
    if translate:
        text = MANAGER_TRANSLATION.tl(text)
        load_text = MANAGER_TRANSLATION.tl(load_text)
    assert(isinstance(text, str) and isinstance(load_text, str))
    button = get_button(
        size, widget_size, text=text, bold=bold, align=align,
        checkable=checkable, enabled=enabled, object_name=object_name
    )

    def threaded_function() -> None:
        button.setEnabled(False)
        button.setChecked(True)
        button.setText(load_text)
        worker = Function_Worker(connect, parent)
        worker.finished.connect(on_finish)
        worker.start()

    def on_finish() -> None:
        try:
            button.setEnabled(True)
            button.setChecked(False)
            button.setText(text)
        except RuntimeError:
            pass

    button.clicked.connect(threaded_function)
    return button


def get_check_box(boolean: bool, widget_size: Widget_Size = None, object_name: str | None = None) -> QCheckBox:
    check_box = QCheckBox()
    check_box.setChecked(boolean)
    set_object_name(check_box, object_name)
    size_factor = MANAGER_SIZE.widget_size_factor
    size_string = ""
    if widget_size is not None and widget_size[0] is not None:
        size_string += "width:  " + str(int(size_factor * widget_size[0])) + "px;"
    if widget_size is not None and widget_size[1] is not None:
        size_string += "height:  " + str(int(size_factor * widget_size[1])) + "px;"
    check_box.setStyleSheet("QCheckBox::indicator {" + size_string + "}")
    return check_box


def get_spin_box(
        value: int, size: str | None, widget_size: Widget_Size = None,
        bold: bool = False, align: Qt.AlignmentFlag | None = None, object_name: str | None = None
) -> QSpinBox:
    spin_box = QSpinBox()
    if size is not None:
        size_button = int(1.4 * MANAGER_SIZE.font_sizes[size])
        size_arrow = int(1.3 * MANAGER_SIZE.font_sizes[size])
        spin_box.setStyleSheet(
            "QSpinBox:up-button {width: " + str(size_button) + "px;}"
            "QSpinBox:down-button {width: " + str(size_button) + "px;}"
            "QSpinBox::down-arrow {width: " + str(size_arrow) + "px; height: " + str(size_arrow) + "px;}"
            "QSpinBox::up-arrow {width: " + str(size_arrow) + "px; height: " + str(size_arrow) + "px;}"
        )
    set_object_name(spin_box, object_name)
    set_fixed_size(spin_box, widget_size)
    set_font(spin_box, size, bold)
    spin_box.setValue(value)
    if align is not None:
        spin_box.setAlignment(align)
    return spin_box


def get_combo_box(
        items: Sequence[Any], size: str | None, widget_size: Widget_Size = None, data: Sequence[Any] | None = None,
        current_index: int | None = None, current: Any = None, bold: bool = False,
        align: Qt.AlignmentFlag | None = None, down_arrow: bool = True, translate: bool = False,
        object_name: str | None = None
) -> QComboBox:
    if align is None:
        combo_box = QComboBox()
    else:
        combo_box = Combo_Box_Editable()
        combo_box.set_alignment(align)
        set_font(combo_box.lineEdit(), size, bold)
    combo_box.setItemDelegate(Align_Delegate(combo_box, align))
    if down_arrow and size is not None:
        size_button = int(2 * MANAGER_SIZE.font_sizes[size])
        size_arrow = int(1.6 * MANAGER_SIZE.font_sizes[size])
        combo_box.setStyleSheet(
            "QComboBox::drop-down {width: " + str(size_button) + "px;}"
            "QComboBox::down-arrow {width: " + str(size_arrow) + "px; height: " + str(size_arrow) + "px;}"
        )
    else:
        combo_box.setStyleSheet(
            "QComboBox {padding-left: 0px; padding-right: 0px;}"
            "QComboBox::drop-down {width: 0px;} QComboBox::down-arrow {width: 0px;}"
        )
    set_object_name(combo_box, object_name)
    set_fixed_size(combo_box, widget_size)
    set_font(combo_box, size, bold)
    combo_box.view().window().setWindowFlags(
        Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
    )
    combo_box.view().window().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    for i, item in enumerate(items):
        match item:
            case str():
                combo_box.addItem(MANAGER_TRANSLATION.tl(item) if translate else item, item)
            case None:
                combo_box.addItem("", item)
            case _:
                combo_box.addItem(MANAGER_TRANSLATION.tl(str(item)) if translate else str(item), item)
    if data is not None:
        for i, item in enumerate(data):
            if item is not None:
                combo_box.setItemData(i, item)
    if current_index is not None:
        combo_box.setCurrentIndex(current_index)
    elif current is not None and current in items:
        combo_box.setCurrentIndex(items.index(current))
    return combo_box


def connect_widget(widget: QWidget, function: Callable[[], None]) -> None:
    match widget:
        case QLineEdit():
            widget.textChanged.connect(function)
        case QCheckBox():
            widget.stateChanged.connect(function)
        case QSpinBox():
            widget.valueChanged.connect(function)
        case QComboBox():
            widget.currentIndexChanged.connect(function)
