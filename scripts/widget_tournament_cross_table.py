from PySide6.QtWidgets import QVBoxLayout, QTableWidget
from PySide6.QtCore import Qt
from .tournament import Tournament
from .widget_tournament_info import Widget_Tournament_Info
from .gui_classes import Vertical_Text_Delegate
from .gui_table import add_content_to_table, set_up_table, size_table, clear_table, add_blank_to_table


class Widget_Tournament_Cross_Table(Widget_Tournament_Info):
    def __init__(self, tournament: Tournament) -> None:
        super().__init__("Crosstable", tournament)
        self.layout_main: QVBoxLayout = QVBoxLayout(self)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout_main.addWidget(self.table)

    def fill_in_table(self) -> None:
        cross_table = self.tournament.get_cross_table()
        size = 2 * max(1.5, cross_table.get_max_length())
        names_left = cross_table.names_left or []
        names_top = cross_table.names_top or []
        is_left, is_top = bool(names_left), bool(names_top)
        header_h = [str(i) for i in range(1, len(cross_table[0]) + 1)]
        header_v = [str(i) for i in range(1, len(cross_table) + 1)]
        if is_left:
            header_h = [""] + header_h
        if is_top:
            header_v = [""] + header_v
        len_h, len_v = len(header_h), len(header_v)
        widths = is_left * [17.] + (len_h - is_left) * [size]
        heights = is_top * [17.] + (len_v - is_top) * [size]

        set_up_table(self.table, len_v, len_h, header_horizontal=header_h, header_vertical=header_v)
        size_table(self.table, widths=widths, heights=heights, header_width=3.5, header_height=3.5)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        if is_left and is_top:
            add_blank_to_table(self.table, 0, 0)
        if is_top:
            self.table.setItemDelegateForRow(0, Vertical_Text_Delegate(self.table))
        for i, name in enumerate(names_left):
            add_content_to_table(self.table, name, is_top + i, 0, edit=False)
        for i, name in enumerate(names_top):
            add_content_to_table(
                self.table, name, 0, is_left + i,
                edit=False, align=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignVCenter
            )

        for row, entries in enumerate(cross_table):
            for column, entry in enumerate(entries):
                r, c = is_top + row, is_left + column
                if entry is None:
                    add_blank_to_table(self.table, r, c)
                    continue
                add_content_to_table(self.table, entry, r, c, edit=False, align=Qt.AlignmentFlag.AlignCenter, bold=True)

    def refresh(self) -> None:
        clear_table(self.table)
        self.fill_in_table()
