from PyQt5.QtWidgets import QComboBox, QLineEdit, QCheckBox, QSpinBox, QTableWidgetItem, QPushButton, QLabel, \
    QScrollArea, QMainWindow, QVBoxLayout, QWidget, QHeaderView, QApplication, QSizePolicy, QStyledItemDelegate
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from .class_size_handler import size_handler
from .class_settings_handler import settings_handler


class Function_Worker(QThread):
    finished = pyqtSignal()

    def __init__(self, function, parent):
        super().__init__(parent=parent)
        self.function = function

    def run(self):
        self.function()
        self.finished.emit()


class Options_Button(QPushButton):
    def __init__(self, var, size, widget_size, text="", bold=False):
        super().__init__(text)
        self.obj = var
        self.window = Options_Window(self.obj)
        self.window.options_closed.connect(self.get_args_and_args_display_from_window)
        self.clicked.connect(self.window.show)

        set_fixed_size(self, size_handler, size, widget_size)
        set_font(self, size_handler, size, bold)

    def get_args_and_args_display_from_window(self):
        if self.obj.is_valid():
            self.window.close()

    def give_back(self):
        return self.obj


class Options_Window(QMainWindow):
    options_closed = pyqtSignal()

    def __init__(self, obj):
        super().__init__()
        self.setWindowTitle("Options")

        self.obj = obj
        self.args_widget_data = None

        self.make_window_from_object()

    def closeEvent(self, event):
        self.options_closed.emit()
        super().closeEvent(event)

    def make_window_from_object(self):
        args, args_display = self.obj.get_args_and_args_display()
        self.args_widget_data = tuple(
            (arg, args_display[arg], get_suitable_widget(value)) for arg, value in args.items()
        )

        parameter_widgets = []
        for _, display, widget in self.args_widget_data:
            connect_widget(widget, lambda _: self.update_widget_data(self.get_new_args()))
            parameter_widgets.extend([get_label(display, "large"), widget, QLabel()])

        widget = QWidget()
        layout = QVBoxLayout()
        get_scroll_area_widgets_and_layouts(layout, parameter_widgets[:-1], margins=(20, 20, 40, 20), spacing=10)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setFixedWidth(layout.sizeHint().width())
        self.setFixedHeight(min(layout.sizeHint().height() + 2, int(QApplication.primaryScreen().size().height() * .4)))

    def get_new_args(self):
        return {arg: get_value_from_suitable_widget(widget) for arg, _, widget in self.args_widget_data}

    def update_widget_data(self, args):
        self.obj.update(args)
        self.make_window_from_object()


def add_widgets_to_layout(layout, widgets):
    for widget in widgets:
        layout.addWidget(widget)


def add_widgets_in_layout(layout, layout_inner, widgets):
    add_widgets_to_layout(layout_inner, widgets)
    layout.addLayout(layout_inner)


def clear_layout(layout, s=0):
    for i in range(len(layout) - 1, s - 1, -1):
        if layout.itemAt(i) is not None:
            if layout.itemAt(i).scroll_area():
                layout.itemAt(i).scroll_area().setParent(None)
            else:
                clear_layout(layout.itemAt(i))
            layout.removeItem(layout.itemAt(i))


def get_scroll_area_widgets_and_layouts(layout, widgets_in_scroll_area, margins=(0, 0, 0, 0), spacing=0):
    scroll_area = QScrollArea()
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll_area.setWidgetResizable(True)
    scroll_area.setMinimumWidth(1)
    widget_inner = QWidget()
    layout_inner = QVBoxLayout()
    layout_inner.setAlignment(Qt.AlignTop)
    layout_inner.setContentsMargins(*margins)
    layout_inner.setSpacing(spacing)
    for widget in widgets_in_scroll_area:
        layout_inner.addWidget(widget)
    widget_inner.setLayout(layout_inner)
    scroll_area.setWidget(widget_inner)
    layout.addWidget(scroll_area)
    return scroll_area, widget_inner, layout_inner


def size_table(table, rows, columns, row_height, max_width=None, widths=[], header_width=None):
    font_size = size_handler.font_sizes["medium"]
    size_factor = size_handler.widget_size_factor
    table.setRowCount(rows)
    table.setColumnCount(columns)
    set_font(table, size_handler, "medium")

    horizontal_header, vertical_header = table.horizontalHeader(), table.verticalHeader()
    horizontal_header.setStyleSheet("QHeaderView {font-size: " + str(font_size) + "pt; font-weight: bold;}")
    horizontal_header.setMinimumSectionSize(0)
    horizontal_header.setFixedHeight(int(row_height * size_factor))
    set_font(horizontal_header, size_handler, "medium")
    vertical_header.setStyleSheet("QHeaderView {font-size: " + str(font_size) + "pt; font-weight: bold;}")
    vertical_header.setSectionResizeMode(QHeaderView.Fixed)
    vertical_header.setDefaultSectionSize(int(row_height * size_factor))
    set_font(vertical_header, size_handler, "medium")

    if max_width is not None:
        table.setMaximumWidth(2 + int(max_width * size_factor))
    table.setMaximumHeight(2 + int(row_height * size_factor) * (rows + 1))
    if header_width is not None:
        vertical_header.setFixedWidth(int(header_width * size_factor))
    for column, width in enumerate(widths):
        if width is not None:
            table.setColumnWidth(column, int(width * size_factor))


def set_fixed_size(widget, size_handler, size, widget_size):
    if widget_size is None:
        return
    font_size = size_handler.font_sizes[size]
    size_factor = size_handler.widget_size_factor
    if widget_size[0] is not None:
        widget.setFixedWidth(int(widget_size[0] * size_factor))
    if widget_size[1] is not None:
        widget.setFixedHeight(int(widget_size[1] * size_factor))


def get_font(font_size=None, bold=False):
    font = QFont(settings_handler.settings["font"][0])
    if font_size is not None:
        font.setPointSize(font_size)
    font.setBold(bold)
    return font


def set_font(widget, size_handler, size, bold=False):
    if widget is None:
        return
    if size is None:
        widget.setFont(get_font(None, bold))
    else:
        widget.setFont(get_font(size_handler.font_sizes[size], bold))


def get_label(text, size, bold=False):
    label = QLabel(text)
    set_font(label, size_handler, size, bold)
    return label


def get_lineedit(size, widget_size, text="", connect_function=None, bold=False):
    lineedit = QLineEdit(text)
    lineedit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    set_fixed_size(lineedit, size_handler, size, widget_size)
    set_font(lineedit, size_handler, size, bold)
    if connect_function is not None:
        lineedit.editingFinished.connect(connect_function)
    return lineedit


def get_button(size, widget_size, text="", connect_function=None, bold=False, checkable=False, enabled=True):
    button = QPushButton(text)
    set_fixed_size(button, size_handler, size, widget_size)
    set_font(button, size_handler, size, bold)
    button.setCheckable(checkable)
    button.setEnabled(enabled)
    if connect_function is not None:
        button.clicked.connect(connect_function)
    return button


def get_button_threaded(
        parent, size, widget_size, text="", load_text="", connect_function=None, bold=False, checkable=True,
        enabled=True
):
    button = get_button(size, widget_size, text, None, bold, checkable, enabled)

    def threaded_function():
        button.setEnabled(False)
        button.setChecked(True)
        button.setText(load_text)
        worker = Function_Worker(connect_function, parent)
        worker.finished.connect(on_finish)
        worker.start()

    def on_finish():
        try:
            button.setEnabled(True)
            button.setChecked(False)
            button.setText(text)
        except RuntimeError:
            pass

    button.clicked.connect(threaded_function)
    return button


def get_check_box(boolean, size, widget_size):
    check_box = QCheckBox()
    check_box.setChecked(boolean)
    size_factor = size_handler.widget_size_factor
    check_box.setStyleSheet(
        "QCheckBox::indicator {"
        "width:  " + str(int(size_factor * widget_size[0])) + "px;"
        "height: " + str(int(size_factor * widget_size[1])) + "px;"
        "}"
    )
    return check_box


def get_spin_box(value, size, widget_size, bold=False, align=None):
    spin_box = QSpinBox()
    spin_box.setStyleSheet(
        "QAbstractSpinBox:up-button {width: " + str(1.3 * size_handler.font_sizes[size]) + "px;}"
        "QAbstractSpinBox:down-button {width: " + str(1.3 * size_handler.font_sizes[size]) + "px;}"
        "QAbstractSpinBox::down-arrow {"
        "width: " + str(size_handler.font_sizes[size]) + "px;"
        "height: " + str(size_handler.font_sizes[size]) + "px;"
        "}"
        "QAbstractSpinBox::up-arrow {"
        "width: " + str(size_handler.font_sizes[size]) + "px;"
        "height: " + str(size_handler.font_sizes[size]) + "px;"
        "}"
    )
    set_fixed_size(spin_box, size_handler, size, widget_size)
    set_font(spin_box, size_handler, size, bold)
    spin_box.setValue(value)
    if align:
        spin_box.setAlignment(align)
    return spin_box


def get_combo_box(choices, size, widget_size, current=None, bold=False, down_arrow=True):
    combo_box = QComboBox()
    combo_box.setItemDelegate(QStyledItemDelegate(combo_box))
    if down_arrow:
        combo_box.setStyleSheet(
            "QComboBox::drop-down {width: " + str(1.3 * size_handler.font_sizes[size]) + "px;}"
            "QComboBox::down-arrow {"
            "width: " + str(size_handler.font_sizes[size]) + "px;"
            "height: " + str(size_handler.font_sizes[size]) + "px;"
            "}"
        )
    else:
        combo_box.setStyleSheet("QComboBox::drop-down {width: 0px;} QComboBox::down-arrow {width: 0px;}")
    set_fixed_size(combo_box, size_handler, size, widget_size)
    set_font(combo_box, size_handler, size, bold)
    for i, choice in enumerate(choices):
        match choice:
            case str():
                combo_box.addItem(choice)
            case None:
                combo_box.addItem("", choice)
            case _:
                combo_box.addItem(str(choice), choice)
    if current is not None and current in choices:
        combo_box.setCurrentIndex(choices.index(current))
    return combo_box


def add_content_to_table(table, content, row, column, edit=True, align=None, bold=False):
    if content is None:
        content = ""
    item = QTableWidgetItem(str(content))
    set_font(item, size_handler, "medium", bold)
    if not edit:
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    if align is not None:
        item.setTextAlignment(align)
    table.setItem(row, column, item)


def add_button_to_table(table, row, column, size, widget_size, text, connect_function=None, bold=False):
    button = get_button(size, widget_size, text, connect_function, bold)
    table.setCellWidget(row, column, button)


def add_combobox_to_table(
        table, choices, row, column, size, widget_size, current=None, bold=False, down_arrow=True
):
    combobox = get_combo_box(choices, size, widget_size, current, bold, down_arrow)
    table.setCellWidget(row, column, combobox)


def add_blank_to_table(table, row, column):
    blank_widget = QWidget()
    blank_widget.setObjectName("blank_widget")
    table.setCellWidget(row, column, blank_widget)


def clear_table(table):
    table.clearContents()
    table.setRowCount(0)


def get_suitable_widget(var, size="medium", widget_size_factors=(1, 1)):
    match var:
        case str():
            return get_lineedit(size, (15 * widget_size_factors[0], 3 * widget_size_factors[1]), text=var)
        case bool():
            return get_check_box(var, size, (3 * widget_size_factors[0], 3 * widget_size_factors[1]))
        case int():
            return get_spin_box(
                var, size, (5 * widget_size_factors[0], 3 * widget_size_factors[1]), align=Qt.AlignCenter
            )
        case list():
            return get_combo_box(var, size, (15 * widget_size_factors[0], 3 * widget_size_factors[1]))
        case _:
            return Options_Button(var, size, (15 * widget_size_factors[0], 3 * widget_size_factors[1]), text="Options")


def get_value_from_suitable_widget(widget):
    match widget:
        case QLineEdit():
            return widget.text()
        case QCheckBox():
            return widget.isChecked()
        case QSpinBox():
            return widget.value()
        case QComboBox():
            return sorted((widget.itemText(i) for i in range(widget.count())), key=lambda x: x != widget.currentText())
        case Options_Button():
            return widget.give_back()


def get_table_value(table, row, column):
    if table.cellWidget(row, column) is not None:
        return get_value_from_suitable_widget(table.cellWidget(row, column))
    if table.item(row, column) is None:
        return ""
    return table.item(row, column).text()


def connect_widget(widget, function):
    match widget:
        case QLineEdit():
            widget.textChanged.connect(function)
        case QCheckBox():
            widget.stateChanged.connect(function)
        case QSpinBox():
            widget.valueChanged.connect(function)
        case QComboBox():
            widget.currentIndexChanged.connect(function)
