from PySide6.QtWidgets import QComboBox, QLineEdit, QCheckBox, QSpinBox, QTableWidgetItem, QPushButton, QLabel, \
    QScrollArea, QMainWindow, QVBoxLayout, QWidget, QHeaderView, QApplication, QSizePolicy, QStyledItemDelegate
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
from .class_size_handler import SIZE_HANDLER
from .class_settings_handler import SETTINGS_HANDLER
from .class_translation_handler import TRANSLATION_HANDLER


class Combo_Box_Editable(QComboBox):
    def __init__(self):
        super().__init__()
        self.setEditable(True)
        self.setLineEdit(Combo_Box_Editable_Line_Edit())
        self.lineEdit().setReadOnly(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_up)
        self.timer.start(20)

    def set_alignment(self, alignment):
        self.lineEdit().setAlignment(alignment)

    def showPopup(self):
        if not self.timer.isActive():
            super().showPopup()

    def hidePopup(self):
        self.timer.start(20)
        super().hidePopup()

    def time_up(self):
        self.timer.stop()


class Combo_Box_Editable_Line_Edit(QLineEdit):
    def mousePressEvent(self, event):
        self.parent().showPopup()

    def mouseDoubleClickEvent(self, event):
        pass


class Align_Delegate(QStyledItemDelegate):
    def __init__(self, parent=None, align=None):
        super().__init__(parent)
        self.align = align

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if self.align is not None:
            option.displayAlignment = self.align


class Function_Worker(QThread):
    finished = Signal()

    def __init__(self, function, parent):
        super().__init__(parent=parent)
        self.function = function

    def run(self):
        self.function()
        self.finished.emit()


class Options_Button(QPushButton):
    def __init__(self, var, size, widget_size, text="", bold=False, translate=False):
        super().__init__(TRANSLATION_HANDLER.tl(text) if translate else text)
        self.obj = var
        self.window = Options_Window(self.obj, translate, parent=self)
        self.window.options_closed.connect(self.get_args_and_args_display_from_window)
        self.clicked.connect(self.window.show)

        set_fixed_size(self, SIZE_HANDLER, size, widget_size)
        set_font(self, SIZE_HANDLER, size, bold)

    def get_args_and_args_display_from_window(self):
        if self.obj.is_valid():
            self.window.close()

    def give_back(self):
        return self.obj


class Options_Window(QMainWindow):
    options_closed = Signal()

    def __init__(self, obj, translate=False, parent=None):
        super().__init__(parent=parent)
        set_window_title(self, "Options")

        self.obj = obj
        self.args_widget_data = None
        self.translate = translate

        self.make_window_from_object()

    def closeEvent(self, event):
        self.options_closed.emit()
        super().closeEvent(event)

    def make_window_from_object(self):
        args, args_display = self.obj.get_args_and_args_display()
        self.args_widget_data = tuple(
            (arg, args_display[arg], get_suitable_widget(value, translate=self.translate))
            for arg, value in args.items()
        )

        parameter_widgets = []
        for _, display, widget in self.args_widget_data:
            connect_widget(widget, self.update_widget_data)
            parameter_widgets.extend([get_label(display, "large", translate=self.translate), widget, QLabel()])

        widget = QWidget()
        layout = QVBoxLayout(widget)
        get_scroll_area_widgets_and_layouts(layout, parameter_widgets[:-1], margins=(20, 20, 40, 20), spacing=10)
        self.setCentralWidget(widget)
        self.setFixedWidth(layout.sizeHint().width())
        self.setFixedHeight(min(layout.sizeHint().height() + 2, int(QApplication.primaryScreen().size().height() * .4)))

    def update_widget_data(self):
        self.obj.update({arg: get_value_from_suitable_widget(widget) for arg, _, widget in self.args_widget_data})
        if self.obj.window_update_necessary:
            self.make_window_from_object()


def close_window(window):
    try:
        if window is None:
            return
        window.close()
    except RuntimeError:
        pass


def add_widgets_to_layout(layout, widgets):
    for widget in widgets:
        layout.addWidget(widget)


def add_widgets_in_layout(layout, layout_inner, widgets):
    add_widgets_to_layout(layout_inner, widgets)
    layout.addLayout(layout_inner)


def get_scroll_area_widgets_and_layouts(
        layout, widgets_in_scroll_area=[], margins=(0, 0, 0, 0), spacing=0, layout_inner=None, horizontal_bar=False
):
    scroll_area = QScrollArea()
    if not horizontal_bar:
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll_area.setWidgetResizable(True)
    scroll_area.setMinimumWidth(1)
    widget_inner = QWidget()
    if layout_inner is None:
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


def get_screen(window):
    if window.parent() is None:
        return QApplication.primaryScreen()
    window_center = window.parent().window().geometry().center()
    screen = QApplication.instance().screenAt(window_center)
    if screen is None:
        return window.parent().window()
    return screen


def set_window_title(window, title):
    window.setWindowTitle(TRANSLATION_HANDLER.tl(title))


def set_window_size_absolute(window, size):
    screen_geometry = get_screen(window).availableGeometry()
    window_center = window.parent().window().geometry().center()
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


def set_window_size(window, size, factor_x=None, factor_y=None):
    screen_geometry = get_screen(window).availableGeometry()
    if factor_x is not None:
        size.setWidth(int(factor_x * screen_geometry.width()))
    if factor_y is not None:
        size.setHeight(int(factor_y * screen_geometry.height()))
    set_window_size_absolute(window, size)


def set_up_table(table, rows, columns, header_horizontal=None, header_vertical=None, translate=False):
    font_size = SIZE_HANDLER.font_sizes["medium"]

    table.setRowCount(rows)
    table.setColumnCount(columns)
    set_font(table, SIZE_HANDLER, "medium")

    horizontal_header, vertical_header = table.horizontalHeader(), table.verticalHeader()
    horizontal_header.setStyleSheet("QHeaderView {font-size: " + str(font_size) + "pt; font-weight: bold;}")
    vertical_header.setStyleSheet("QHeaderView {font-size: " + str(font_size) + "pt; font-weight: bold;}")
    set_font(horizontal_header, SIZE_HANDLER, "medium")
    set_font(vertical_header, SIZE_HANDLER, "medium")

    if header_horizontal is not None:
        if translate:
            header_horizontal = TRANSLATION_HANDLER.tl_list(header_horizontal, short=True)
        table.setHorizontalHeaderLabels(header_horizontal)
    if header_vertical is not None:
        if translate:
            header_vertical = TRANSLATION_HANDLER.tl_list(header_vertical, short=True)
        table.setVerticalHeaderLabels(header_vertical)


def size_table(table, rows, row_height, max_width=None, widths=[], header_width=None):
    size_factor = SIZE_HANDLER.widget_size_factor

    horizontal_header, vertical_header = table.horizontalHeader(), table.verticalHeader()
    horizontal_header.setMinimumSectionSize(0)
    horizontal_header.setFixedHeight(int(row_height * size_factor))
    vertical_header.setSectionResizeMode(QHeaderView.Fixed)
    vertical_header.setDefaultSectionSize(int(row_height * size_factor))

    table.setRowCount(rows)
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
    size_factor = size_handler.widget_size_factor
    if widget_size[0] is not None:
        widget.setFixedWidth(int(widget_size[0] * size_factor))
    if widget_size[1] is not None:
        widget.setFixedHeight(int(widget_size[1] * size_factor))


def get_font(font_size=None, bold=False):
    font = QFont(SETTINGS_HANDLER.settings["font"][0])
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


def get_label(text, size, bold=False, translate=False):
    if translate:
        text = TRANSLATION_HANDLER.tl(text)
    label = QLabel(text)
    set_font(label, SIZE_HANDLER, size, bold)
    return label


def get_lineedit(size, widget_size, text="", connect_function=None, bold=False):
    lineedit = QLineEdit(text)
    lineedit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    set_fixed_size(lineedit, SIZE_HANDLER, size, widget_size)
    set_font(lineedit, SIZE_HANDLER, size, bold)
    if connect_function is not None:
        lineedit.editingFinished.connect(connect_function)
    return lineedit


def get_button(
        size, widget_size, text="", connect_function=None, bold=False, checkable=False, enabled=True, translate=False
):
    if translate:
        text = TRANSLATION_HANDLER.tl(text)
    button = QPushButton(text)
    set_fixed_size(button, SIZE_HANDLER, size, widget_size)
    set_font(button, SIZE_HANDLER, size, bold)
    button.setCheckable(checkable)
    button.setEnabled(enabled)
    if connect_function is not None:
        button.clicked[bool].connect(connect_function)
    return button


def get_button_threaded(
        parent, size, widget_size, text="", load_text="", connect_function=None, bold=False, checkable=True,
        enabled=True, translate=False
):
    if translate:
        text = TRANSLATION_HANDLER.tl(text)
        load_text = TRANSLATION_HANDLER.tl(load_text)
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
    size_factor = SIZE_HANDLER.widget_size_factor
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
        "QAbstractSpinBox:up-button {width: " + str(1.3 * SIZE_HANDLER.font_sizes[size]) + "px;}"
        "QAbstractSpinBox:down-button {width: " + str(1.3 * SIZE_HANDLER.font_sizes[size]) + "px;}"
        "QAbstractSpinBox::down-arrow {"
        "width: " + str(SIZE_HANDLER.font_sizes[size]) + "px;"
        "height: " + str(SIZE_HANDLER.font_sizes[size]) + "px;"
        "}"
        "QAbstractSpinBox::up-arrow {"
        "width: " + str(SIZE_HANDLER.font_sizes[size]) + "px;"
        "height: " + str(SIZE_HANDLER.font_sizes[size]) + "px;"
        "}"
    )
    set_fixed_size(spin_box, SIZE_HANDLER, size, widget_size)
    set_font(spin_box, SIZE_HANDLER, size, bold)
    spin_box.setValue(value)
    if align:
        spin_box.setAlignment(align)
    return spin_box


def get_combo_box(choices, size, widget_size, current=None, bold=False, align=None, down_arrow=True, translate=False):
    if align is None:
        combo_box = QComboBox()
    else:
        combo_box = Combo_Box_Editable()
        combo_box.set_alignment(align)
        set_font(combo_box.lineEdit(), SIZE_HANDLER, size, bold)
    combo_box.setItemDelegate(Align_Delegate(combo_box, align))
    if down_arrow:
        combo_box.setStyleSheet(
            "QComboBox::drop-down {width: " + str(1.3 * SIZE_HANDLER.font_sizes[size]) + "px;}"
            "QComboBox::down-arrow {"
            "width: " + str(SIZE_HANDLER.font_sizes[size]) + "px;"
            "height: " + str(SIZE_HANDLER.font_sizes[size]) + "px;"
            "}"
        )
    else:
        combo_box.setStyleSheet(
            "QComboBox {padding-left: 0px; padding-right: 0px;}"
            "QComboBox::drop-down {width: 0px;} QComboBox::down-arrow {width: 0px;}"
        )
    set_fixed_size(combo_box, SIZE_HANDLER, size, widget_size)
    set_font(combo_box, SIZE_HANDLER, size, bold)
    for i, choice in enumerate(choices):
        match choice:
            case str():
                combo_box.addItem(TRANSLATION_HANDLER.tl(choice) if translate else choice, choice)
            case None:
                combo_box.addItem("", choice)
            case _:
                combo_box.addItem(TRANSLATION_HANDLER.tl(str(choice)) if translate else str(choice), choice)
    if current is not None and current in choices:
        combo_box.setCurrentIndex(choices.index(current))
    return combo_box


def add_content_to_table(table, content, row, column, edit=True, align=None, bold=False, translate=False):
    if content is None:
        content = ""
    item = QTableWidgetItem(TRANSLATION_HANDLER.tl(str(content)) if translate else str(content))
    set_font(item, SIZE_HANDLER, "medium", bold)
    if not edit:
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    if align is not None:
        item.setTextAlignment(align)
    table.setItem(row, column, item)


def add_button_to_table(
        table, row, column, size, widget_size, text, connect_function=None, bold=False, checkable=False, enabled=True,
        translate=False
):
    button = get_button(size, widget_size, text, connect_function, bold, checkable, enabled, translate)
    table.setCellWidget(row, column, button)


def add_combobox_to_table(
        table, choices, row, column, size, widget_size,
        current=None, bold=False, align=None, down_arrow=True, translate=False
):
    combobox = get_combo_box(choices, size, widget_size, current, bold, align, down_arrow, translate)
    table.setCellWidget(row, column, combobox)


def add_blank_to_table(table, row, column):
    blank_widget = QWidget()
    blank_widget.setObjectName("blank_widget")
    table.setCellWidget(row, column, blank_widget)


def add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates):
    for i, (content, edit, bold, align, translate) in enumerate(zip(contents, edits, bolds, aligns, translates)):
        add_content_to_table(table, content, row, i, edit=edit, bold=bold, align=align, translate=translate)


def add_collection_to_table(table, row, collection, edit=False):
    if collection is None:
        contents = ("", "")
    else:
        contents = (collection.get_name(), collection.get_object_type())
    edits = (edit, False)
    bolds = (True, False)
    aligns = (None, None)
    translates = (False, True)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def add_player_to_table(table, row, player, edit=False):
    if player is None:
        contents = ("", "", "", "", "", "")
    else:
        contents = (
            player.get_name(), player.get_sex(), player.get_birthday(),
            player.get_country(), player.get_title(), player.get_rating()
        )
    edits = (edit, edit, edit, edit, edit, edit)
    bolds = (True, False, False, False, False, False)
    aligns = (None, Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter, Qt.AlignCenter)
    translates = (False, False, False, False, False, False)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def add_team_to_table(table, row, team, edit=False):
    if team is None:
        contents = ("", "")
    else:
        contents = (team.get_name(), team.get_member_count())
    edits = (edit, False)
    bolds = (True, False)
    aligns = (None, Qt.AlignCenter)
    translates = (False, False)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def add_tournament_to_table(table, row, tournament, edit=False):
    if tournament is None:
        contents = ("", "", "")
    else:
        contents = (tournament.get_name(), tournament.get_mode(), tournament.get_participant_count())
    edits = (edit, False, False)
    bolds = (True, False, False)
    aligns = (None, None, Qt.AlignCenter)
    translates = (False, True, False)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def add_ms_tournament_to_table(table, row, ms_tournament, edit=False):
    if ms_tournament is None:
        contents = ("", "")
    else:
        contents = (ms_tournament.get_name(), ms_tournament.get_participant_count())
    edits = (edit, False)
    bolds = (True, False)
    aligns = (None, Qt.AlignCenter)
    translates = (False, False)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def clear_table(table):
    table.clearContents()
    table.setRowCount(0)


def get_suitable_widget(var, size="medium", widget_size_factors=(1, 1), translate=False):
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
            return get_combo_box(
                var, size, (15 * widget_size_factors[0], 3 * widget_size_factors[1]), translate=translate
            )
        case _:
            return Options_Button(
                var, size, (15 * widget_size_factors[0], 3 * widget_size_factors[1]),
                text="Options", translate=translate
            )


def get_value_from_suitable_widget(widget):
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
