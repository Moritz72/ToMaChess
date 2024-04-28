from typing import Any, Callable, Sequence
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QTableWidget, QWidget
from .gui_functions import Widget_Size, get_button, get_button_threaded, get_combo_box, get_label, set_font
from .gui_options import get_value_from_suitable_widget
from ...common.manager_size import MANAGER_SIZE
from ...common.manager_translation import MANAGER_TRANSLATION
from ...collection.collection import Collection
from ...ms_tournament.ms_tournament import MS_Tournament
from ...player.player import Player
from ...team.team import Team
from ...tournament.tournaments.tournament import Tournament


def set_up_table(
        table: QTableWidget, rows: int, columns: int, header_horizontal: Sequence[str] | None = None,
        header_vertical: Sequence[str] | None = None, translate: bool = False
) -> None:
    font_size = MANAGER_SIZE.font_sizes["medium"]

    table.setRowCount(rows)
    table.setColumnCount(columns)
    set_font(table, "medium")

    horizontal_header, vertical_header = table.horizontalHeader(), table.verticalHeader()
    horizontal_header.setStyleSheet("QHeaderView {font-size: " + str(font_size) + "pt; font-weight: bold;}")
    vertical_header.setStyleSheet("QHeaderView {font-size: " + str(font_size) + "pt; font-weight: bold;}")
    set_font(horizontal_header, "medium")
    set_font(vertical_header, "medium")

    if header_horizontal is not None:
        if translate:
            header_horizontal = MANAGER_TRANSLATION.tl_list(header_horizontal, short=True)
        table.setHorizontalHeaderLabels(header_horizontal)
    if header_vertical is not None:
        if translate:
            header_vertical = MANAGER_TRANSLATION.tl_list(header_vertical, short=True)
        table.setVerticalHeaderLabels(header_vertical)


def size_headers(
        table: QTableWidget, width: float | None, height: float | None,
        stretches_h: list[int] | None = None, stretches_v: list[int] | None = None
) -> None:
    size_factor = MANAGER_SIZE.widget_size_factor
    stretches_h, stretches_v = stretches_h or [], stretches_v or []
    header_h, header_v = table.horizontalHeader(), table.verticalHeader()
    header_h.setMinimumSectionSize(0)
    header_v.setMinimumSectionSize(0)
    if width is not None:
        header_v.setFixedWidth(int(width * size_factor))
    if height is not None:
        header_h.setFixedHeight(int(height * size_factor))
    for column in range(table.columnCount()):
        resize_mode = QHeaderView.ResizeMode.Stretch if column in stretches_h else QHeaderView.ResizeMode.Fixed
        header_h.setSectionResizeMode(column, resize_mode)
    for row in range(table.rowCount()):
        resize_mode = QHeaderView.ResizeMode.Stretch if row in stretches_v else QHeaderView.ResizeMode.Fixed
        header_v.setSectionResizeMode(row, resize_mode)


def size_table(
        table: QTableWidget, rows: int | None = None, columns: int | None = None,
        row_height: float | None = None, column_width: float | None = None,
        max_width: float | None = None, max_height: float | None = None,
        widths: Sequence[float | None] | None = None, heights: Sequence[float | None] | None = None,
        header_width: float | None = None, header_height: float | None = None,
        stretches_h: list[int] | None = None, stretches_v: list[int] | None = None
) -> None:
    widths = widths or []
    heights = heights or []
    size_factor = MANAGER_SIZE.widget_size_factor

    if rows is not None:
        table.setRowCount(rows)
    if columns is not None:
        table.setColumnCount(columns)
    if header_width is None:
        header_width = column_width
    if header_height is None:
        header_height = row_height
    size_headers(table, header_width, header_height, stretches_h, stretches_v)
    if row_height is not None:
        for row in range(table.rowCount()):
            table.setRowHeight(row, int(row_height * size_factor))
    if column_width is not None:
        for column in range(table.columnCount()):
            table.setColumnWidth(column, int(column_width * size_factor))
    for row, height in enumerate(heights):
        if height is not None:
            table.setRowHeight(row, int(height * size_factor))
    for column, width in enumerate(widths):
        if width is not None:
            table.setColumnWidth(column, int(width * size_factor))
    if max_width is not None:
        table.setMaximumWidth(int(max_width * size_factor) + 2)
    else:
        width_sum = sum(table.columnWidth(column) for column in range(table.columnCount()))
        table.setMaximumWidth(table.verticalHeader().width() + width_sum + 2)
    if max_height is not None:
        table.setMaximumHeight(int(max_height * size_factor) + 2)
    else:
        height_sum = sum(table.rowHeight(row) for row in range(table.rowCount()))
        table.setMaximumHeight(table.horizontalHeader().height() + height_sum + 2)


def add_content_to_table(
        table: QTableWidget, content: Any, row: int, column: int, size: str | None = "medium",
        edit: bool = True, align: Qt.AlignmentFlag | None = None, bold: bool = False, translate: bool = False
) -> None:
    content = content or ""
    if translate:
        if not isinstance(content, str | tuple):
            content = str(content)
        content = MANAGER_TRANSLATION.tl(content)
    item = QTableWidgetItem(str(content))
    set_font(item, size, bold)
    if not edit:
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    if align is not None:
        item.setTextAlignment(align)
    table.setItem(row, column, item)


def add_label_to_table(
        table: QTableWidget, row: int, column: int, size: str | None = "medium", widget_size: Widget_Size = None,
        text: str | Sequence[str] = "", bold: bool = False, align: Qt.AlignmentFlag | None = None,
        translate: bool = False, object_name: str | None = None
) -> None:
    label = get_label(text, size, widget_size, bold, align, translate, object_name)
    table.setCellWidget(row, column, label)


def add_button_to_table(
        table: QTableWidget, row: int, column: int, size: str | None, widget_size: Widget_Size,
        text: str | Sequence[str] = "", connect: Callable[[], None] | list[Callable[[], None]] | None = None,
        bold: bool = False, align: str = "center", checkable: bool = False, enabled: bool = True,
        translate: bool = False, object_name: str | None = None
) -> None:
    button = get_button(size, widget_size, text, connect, bold, align, checkable, enabled, translate, object_name)
    table.setCellWidget(row, column, button)


def add_button_threaded_to_table(
        table: QTableWidget, row: int, column: int, parent: QObject, size: str | None, widget_size: Widget_Size = None,
        text: str | Sequence[str] = "", load_text: str | Sequence[str] = "", connect: Callable[[], Any] | None = None,
        on_finish: Callable[[], Any] | None = None, bold: bool = False, align: str = "center", checkable: bool = True,
        enabled: bool = True, translate: bool = False, object_name: str | None = None
) -> None:
    button_threaded = get_button_threaded(
        parent, size, widget_size, text, load_text, connect, on_finish,
        bold, align, checkable, enabled, translate, object_name
    )
    table.setCellWidget(row, column, button_threaded)


def add_combobox_to_table(
        table: QTableWidget, items: Sequence[Any], row: int, column: int, size: str | None, widget_size: Widget_Size,
        data: Sequence[Any] | None = None, current_index: int | None = None, current: Any = None, bold: bool = False,
        align: Qt.AlignmentFlag | None = None, down_arrow: bool = True,
        translate: bool = False, object_name: str | None = None
) -> None:
    combobox = get_combo_box(
        items, size, widget_size, data, current_index, current, bold, align, down_arrow, translate, object_name
    )
    table.setCellWidget(row, column, combobox)


def add_blank_to_table(table: QTableWidget, row: int, column: int) -> None:
    blank_widget = QWidget()
    blank_widget.setObjectName("blank_widget")
    table.setCellWidget(row, column, blank_widget)


def add_object_data_to_table(
        table: QTableWidget, row: int, contents: Sequence[Any], edits: Sequence[bool], bolds: Sequence[bool],
        aligns: Sequence[Qt.AlignmentFlag | None], translates: Sequence[bool]
) -> None:
    for i, (content, edit, bold, align, translate) in enumerate(zip(contents, edits, bolds, aligns, translates)):
        add_content_to_table(table, content, row, i, edit=edit, bold=bold, align=align, translate=translate)


def add_collection_to_table(table: QTableWidget, row: int, collection: Collection | None, edit: bool = False) -> None:
    contents: tuple[str | None, str | None]
    if collection is None:
        contents = (None, None)
    else:
        contents = (collection.get_name(), collection.get_object_type())
    edits = (edit, False)
    bolds = (True, False)
    aligns = (None, None)
    translates = (False, True)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def add_player_to_table(table: QTableWidget, row: int, player: Player | None, edit: bool = False) -> None:
    contents: tuple[str | None, str | None, int | None, str | None, str | None, int | None]
    if player is None:
        contents = (None, None, None, None, None, None)
    else:
        contents = (
            player.get_name(), player.get_sex(), player.get_birthday(),
            player.get_country(), player.get_title(), player.get_rating()
        )
    edits = (edit, edit, edit, edit, edit, edit)
    bolds = (True, False, False, False, False, False)
    aligns = (
        None, Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter,
        Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter, Qt.AlignmentFlag.AlignCenter
    )
    translates = (False, False, False, False, False, False)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def add_team_to_table(table: QTableWidget, row: int, team: Team | None, edit: bool = False) -> None:
    contents: tuple[str | None, int | None]
    if team is None:
        contents = (None, None)
    else:
        contents = (team.get_name(), team.get_member_count())
    edits = (edit, False)
    bolds = (True, False)
    aligns = (None, Qt.AlignmentFlag.AlignCenter)
    translates = (False, False)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def add_tournament_to_table(table: QTableWidget, row: int, tournament: Tournament | None, edit: bool = False) -> None:
    contents: tuple[str | None, str | None, int | None]
    if tournament is None:
        contents = (None, None, None)
    else:
        contents = (tournament.get_name(), tournament.get_mode(), tournament.get_participant_count())
    edits = (edit, False, False)
    bolds = (True, False, False)
    aligns = (None, None, Qt.AlignmentFlag.AlignCenter)
    translates = (False, True, False)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def add_ms_tournament_to_table(
        table: QTableWidget, row: int, ms_tournament: MS_Tournament | None, edit: bool = False
) -> None:
    contents: tuple[str | None, int | None]
    if ms_tournament is None:
        contents = (None, None)
    else:
        contents = (ms_tournament.get_name(), ms_tournament.get_participant_count())
    edits = (edit, False)
    bolds = (True, False)
    aligns = (None, Qt.AlignmentFlag.AlignCenter)
    translates = (False, False)
    add_object_data_to_table(table, row, contents, edits, bolds, aligns, translates)


def clear_table(table: QTableWidget) -> None:
    table.clearContents()
    table.setRowCount(0)


def get_table_value(table: QTableWidget, row: int, column: int) -> Any:
    cell_widget = table.cellWidget(row, column)
    if cell_widget is not None:
        return get_value_from_suitable_widget(cell_widget)
    if table.item(row, column) is None:
        return ""
    return table.item(row, column).text()
