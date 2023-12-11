from typing import Sequence, Any, Callable
from PySide6.QtWidgets import QWidget, QHeaderView, QTableWidgetItem, QTableWidget
from PySide6.QtCore import Qt
from .manager_size import MANAGER_SIZE
from .manager_translation import MANAGER_TRANSLATION
from .collection import Collection
from .player import Player
from .team import Team
from .tournament import Tournament
from .ms_tournament import MS_Tournament
from .gui_functions import Widget_Size, set_font, get_button, get_combo_box
from .gui_options import get_value_from_suitable_widget


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


def size_table(
        table: QTableWidget, rows: int, row_height: float,
        max_width: float | None = None, widths: Sequence[float | None] | Sequence[float] | None = None,
        header_width: float | None = None
) -> None:
    size_factor = MANAGER_SIZE.widget_size_factor

    horizontal_header, vertical_header = table.horizontalHeader(), table.verticalHeader()
    horizontal_header.setMinimumSectionSize(0)
    horizontal_header.setFixedHeight(int(row_height * size_factor))
    vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
    vertical_header.setDefaultSectionSize(int(row_height * size_factor))

    table.setRowCount(rows)
    if max_width is not None:
        table.setMaximumWidth(2 + int(max_width * size_factor))
    table.setMaximumHeight(2 + int(row_height * size_factor) * (rows + 1))
    if header_width is not None:
        vertical_header.setFixedWidth(int(header_width * size_factor))
    if widths is None:
        return
    for column, width in enumerate(widths):
        if width is not None:
            table.setColumnWidth(column, int(width * size_factor))


def add_content_to_table(
        table: QTableWidget, content: Any, row: int, column: int,
        edit: bool = True, align: Qt.AlignmentFlag | None = None, bold: bool = False, translate: bool = False
) -> None:
    if content is None:
        content = ""
    item = QTableWidgetItem(MANAGER_TRANSLATION.tl(str(content)) if translate else str(content))
    set_font(item, "medium", bold)
    if not edit:
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    if align is not None:
        item.setTextAlignment(align)
    table.setItem(row, column, item)


def add_button_to_table(
        table: QTableWidget, row: int, column: int, size: str | None, widget_size: Widget_Size,
        text: str | Sequence[str] = "", connect: Callable[[], None] | list[Callable[[], None]] | None = None,
        bold: bool = False, checkable: bool = False, enabled: bool = True, translate: bool = False
) -> None:
    button = get_button(size, widget_size, text, connect, bold, checkable, enabled, translate)
    table.setCellWidget(row, column, button)


def add_combobox_to_table(
        table: QTableWidget, choices: Sequence[Any], row: int, column: int, size: str | None, widget_size: Widget_Size,
        current_index: int | None = None, current: Any = None, bold: bool = False,
        align: Qt.AlignmentFlag | None = None, down_arrow: bool = True, translate: bool = False
) -> None:
    combobox = get_combo_box(choices, size, widget_size, current_index, current, bold, align, down_arrow, translate)
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
