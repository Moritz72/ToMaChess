from PyQt5.QtWidgets import QComboBox, QLineEdit, QCheckBox, QSpinBox, QTableWidgetItem, QPushButton, QLabel, \
    QScrollArea, QMainWindow, QVBoxLayout, QWidget, QHeaderView, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from .class_size_handler import Size_Handler

size_handler = Size_Handler()


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
            parameter_widgets = parameter_widgets + [get_label(display, "large"), widget, QLabel()]
        widget = QWidget()
        layout = QVBoxLayout()
        get_scroll_area_widgets_and_layouts(
            layout, parameter_widgets[:-1], margins=(20, 20, 40, 20), spacing=10
        )

        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setFixedWidth(layout.sizeHint().width())
        self.setFixedHeight(min(layout.sizeHint().height(), int(QApplication.primaryScreen().size().height() * .4)))

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
                layout.removeItem(layout.itemAt(i))
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
    table.setFont(get_font(font_size))

    horizontal_header = table.horizontalHeader()
    horizontal_header.setMinimumSectionSize(0)
    horizontal_header.setFixedHeight(int(row_height * size_factor))
    vertical_header = table.verticalHeader()
    vertical_header.setSectionResizeMode(QHeaderView.Fixed)
    vertical_header.setDefaultSectionSize(int(row_height * size_factor))

    if max_width is not None:
        table.setMaximumWidth(2 + int(max_width * size_factor))
    table.setMaximumHeight(2 + int(row_height * size_factor) * (rows + 1))
    if header_width is not None:
        vertical_header.setFixedWidth(int(header_width * size_factor))
    for column, width in enumerate(widths):
        if width is not None:
            table.setColumnWidth(column, int(width * size_factor))
    return table


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
    font = QFont()
    if font_size is not None:
        font.setPointSize(font_size)
    font.setBold(bold)
    return font


def set_font(widget, size_handler, size, bold=False):
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


def get_check_box(boolean, widget_size):
    check_box = QCheckBox()
    check_box.setChecked(boolean)
    if widget_size is not None:
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
    set_fixed_size(spin_box, size_handler, size, widget_size)
    set_font(spin_box, size_handler, size, bold)
    spin_box.setValue(value)
    if align:
        spin_box.setAlignment(align)
    return spin_box


def get_combo_box(choices, size, widget_size, current=None, bold=False, item_limit=None):
    combo_box = QComboBox()
    if item_limit is not None:
        combo_box.setStyleSheet("combobox-popup: 0;")
        combo_box.setMaxVisibleItems(item_limit)
    set_fixed_size(combo_box, size_handler, size, widget_size)
    set_font(combo_box, size_handler, size, bold)
    for i, choice in enumerate(choices):
        if isinstance(choice, str):
            combo_box.addItem(choice)
        elif isinstance(choice, type(None)):
            combo_box.addItem("", choice)
        else:
            combo_box.addItem(str(choice), choice)
    if current is not None and current in choices:
        combo_box.setCurrentIndex(choices.index(current))
    return combo_box


def add_content_to_table(table, content, row, column, edit=True, align=None, bold=False, color_bg=None):
    if content is None:
        content = ""
    item = QTableWidgetItem(str(content))
    set_font(item, size_handler, None, bold)
    if not edit:
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    if align is not None:
        item.setTextAlignment(align)
    if color_bg is not None:
        item.setBackground(QColor(*color_bg))
    table.setItem(row, column, item)


def add_button_to_table(table, row, column, size, widget_size, text, connect_function=None, bold=False):
    button = get_button(size, widget_size, text, connect_function, bold)
    table.setCellWidget(row, column, button)


def add_combobox_to_table(table, choices, row, column, size, widget_size, current=None, bold=False, item_limit=None):
    combobox = get_combo_box(choices, size, widget_size, current, bold, item_limit)
    table.setCellWidget(row, column, combobox)


def make_headers_bold_horizontal(table):
    table.horizontalHeader().setFont(get_font(None, True))


def make_headers_bold_vertical(table):
    table.verticalHeader().setFont(get_font(None, True))


def clear_table(table):
    table.clearContents()
    table.setRowCount(0)


def get_suitable_widget(var, size="medium", widget_size_factors=(1, 1)):
    if isinstance(var, str):
        return get_lineedit(size, (15*widget_size_factors[0], 3*widget_size_factors[1]), text=var)
    if isinstance(var, bool):
        return get_check_box(var, (3*widget_size_factors[0], 3*widget_size_factors[1]))
    if isinstance(var, int):
        return get_spin_box(var, size, (5*widget_size_factors[0], 3*widget_size_factors[1]), align=Qt.AlignCenter)
    if isinstance(var, list):
        return get_combo_box(var, size, (15*widget_size_factors[0], 3*widget_size_factors[1]))
    return Options_Button(var, size, (15*widget_size_factors[0], 3*widget_size_factors[1]), text="Options")


def get_value_from_suitable_widget(widget):
    if isinstance(widget, QLineEdit):
        return widget.text()
    if isinstance(widget, QCheckBox):
        return widget.isChecked()
    if isinstance(widget, QSpinBox):
        return widget.value()
    if isinstance(widget, QComboBox):
        return sorted([widget.itemText(i) for i in range(widget.count())], key=lambda x: x != widget.currentText())
    return widget.give_back()


def connect_widget(widget, function):
    if isinstance(widget, QLineEdit):
        widget.textChanged.connect(function)
    if isinstance(widget, QCheckBox):
        widget.stateChanged.connect(function)
    if isinstance(widget, QSpinBox):
        widget.valueChanged.connect(function)
    if isinstance(widget, QComboBox):
        widget.currentIndexChanged.connect(function)
