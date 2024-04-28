from copy import deepcopy
from typing import Sequence, Callable, cast
from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtWidgets import QComboBox, QTableWidget, QVBoxLayout, QWidget
from ..common.gui_table import add_blank_to_table, add_button_to_table, add_combobox_to_table, add_content_to_table, \
    clear_table, set_up_table, size_table
from ...tournament.common.pairing import Pairing, Pairing_Item_s
from ...tournament.common.pairing_item import Bye_PA, Pairing_Item, get_item_from_string, get_tentative_results
from ...tournament.common.result import Result


class Widget_Tournament_Round(QWidget):
    confirmed_pairings = Signal()
    confirmed_results = Signal()

    def __init__(
            self, data: list[Pairing] | list[Result], name_dict: dict[str, str],
            drop_outs: list[str] | None = None, possible_scores: list[tuple[str, str]] | None = None,
            is_valid_pairings: Callable[[Sequence[Pairing]], bool] | None = None, headers: tuple[str, str] = ("", "")
    ) -> None:
        super().__init__()
        self.data: list[Pairing] | list[Result] = data
        self.name_dict: dict[str, str] = name_dict
        self.headers: tuple[str, str] = headers
        self.drop_outs: list[str] | None = drop_outs
        self.possible_scores: list[tuple[str, str]] | None = possible_scores
        self.is_valid_pairings: Callable[[Sequence[Pairing]], bool] | None = is_valid_pairings
        self.initially_selected_uuids: set[str] = set()

        self.layout_main: QVBoxLayout = QVBoxLayout(self)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout_main.addWidget(self.table)
        margins = self.layout_main.contentsMargins().top() + self.layout_main.contentsMargins().bottom()
        self.setMaximumHeight(self.table.maximumHeight() + margins)

        if self.is_valid_pairings is not None:
            self.confirm_pairings(initial=True)

    def get_pairings(self) -> list[Pairing]:
        return cast(list[Pairing], self.data)

    def get_results(self) -> list[Result]:
        return cast(list[Result], self.data)

    def get_rows(self) -> int:
        return len(self.data) + int(self.drop_outs is not None)

    def get_first_not_selected_index(self, items: Sequence[Pairing_Item]) -> int:
        return next((index for index, uuid in enumerate(items) if uuid not in self.initially_selected_uuids), 0)

    def add_selected_uuid(self, item: Pairing_Item) -> None:
        if not item.is_bye():
            self.initially_selected_uuids.add(item)

    def add_row_name(self, row: int, column: int, item_s: Pairing_Item_s) -> None:
        if isinstance(item_s, list):
            current_index = self.get_first_not_selected_index(item_s)
            add_combobox_to_table(
                self.table, [self.name_dict[item] for item in item_s], row, column, "medium", None,
                data=item_s, current_index=current_index, translate=True
            )
            self.add_selected_uuid(item_s[current_index])
        else:
            add_content_to_table(
                self.table, self.name_dict[item_s], row, column,
                edit=False, align=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            self.add_selected_uuid(item_s)

    def add_row_result(self, row: int, column: int, score_s: tuple[str, str] | list[tuple[str, str]]) -> None:
        if isinstance(score_s, list):
            add_combobox_to_table(
                self.table, [" : "] + [" : ".join(score) for score in score_s], row, column, "medium", None,
                down_arrow=False, bold=True, align=Qt.AlignmentFlag.AlignCenter
            )
        else:
            result = "" if score_s[0] == 'b' else f"{score_s[0]} : {score_s[1]}"
            add_content_to_table(
                self.table, result, row, column,
                edit=False, align=Qt.AlignmentFlag.AlignCenter, bold=True
            )

    def add_row(
            self, row: int, item_s_1: Pairing_Item_s, item_s_2: Pairing_Item_s,
            score_s: tuple[str, str] | list[tuple[str, str]]
    ) -> None:
        add_content_to_table(
            self.table, str(row + 1), row, 0, edit=False, bold=True, align=Qt.AlignmentFlag.AlignCenter
        )
        self.add_row_name(row, 1, item_s_1)
        self.add_row_result(row, 2, score_s)
        self.add_row_name(row, 3, item_s_2)

    def add_last_row(self, pairings_fixed: bool) -> None:
        row = self.table.rowCount() - 1
        for i in range(3):
            add_blank_to_table(self.table, row, i)
        if pairings_fixed:
            add_button_to_table(
                self.table, row, 3, "medium", None, "Confirm Results",
                connect=self.confirm_results, bold=True, translate=True
            )
        else:
            add_button_to_table(
                self.table, row, 3, "medium", None, "Confirm Pairings",
                connect=self.confirm_pairings, bold=True, translate=True
            )

    def fill_in_table(self) -> None:
        set_up_table(self.table, 0, 4, header_horizontal=["", self.headers[0], "", self.headers[1]])
        size_table(
            self.table, rows=self.get_rows(), row_height=3.5, max_width=55, widths=[3.5, None, 5, None],
            header_width=0, stretches_h=[1, 3]
        )

        if self.drop_outs is None or self.possible_scores is None or self.is_valid_pairings is None:
            for i, ((item_1, score_1), (item_2, score_2)) in enumerate(self.get_results()):
                self.add_row(i, item_1, item_2, (score_1, score_2))
            return

        pairings = self.get_pairings()
        for i, (item_s_1, item_s_2) in enumerate(pairings):
            scores: tuple[str, str] | list[tuple[str, str]]
            if isinstance(item_s_1, list) or isinstance(item_s_2, list):
                scores = self.possible_scores
            else:
                item_1 = Bye_PA() if self.drop_outs is not None and item_s_1 in self.drop_outs else item_s_1
                item_2 = Bye_PA() if self.drop_outs is not None and item_s_2 in self.drop_outs else item_s_2
                scores = get_tentative_results(item_1, item_2) or self.possible_scores
            self.add_row(i, item_s_1, item_s_2, scores)
        self.add_last_row(all(pairing.is_fixed() for pairing in pairings))

    def fix_pairing_entry(self, pairings: Sequence[Pairing], row: int, column: int) -> None:
        widget = self.table.cellWidget(row, column)
        assert(isinstance(widget, QComboBox))
        pairings[row].fix(column == 3, get_item_from_string(cast(str, widget.currentData())))

    def get_fixed_pairings(self, pairings: list[Pairing]) -> list[Pairing]:
        fixed_pairings = deepcopy(pairings)
        for row in range(len(fixed_pairings)):
            self.fix_pairing_entry(fixed_pairings, row, 1)
            self.fix_pairing_entry(fixed_pairings, row, 3)
        return fixed_pairings

    def get_result_entry(self, row: int, column: int) -> tuple[str, str]:
        item = self.table.item(row, column)
        widget = self.table.cellWidget(row, column)
        text = widget.currentText() if isinstance(widget, QComboBox) else item.text()
        return cast(tuple[str, str], tuple(text.split(" : "))) if bool(text) else ('b', '-')

    def confirm_pairings(self, initial: bool = False) -> None:
        assert(self.is_valid_pairings is not None)
        pairings = self.get_pairings() if initial else self.get_fixed_pairings(self.get_pairings())
        if all(pairing.is_fixed() for pairing in pairings) and self.is_valid_pairings(pairings):
            self.data = pairings
            self.update_table()
            QTimer.singleShot(0, self.confirmed_pairings.emit)

    def confirm_results(self) -> None:
        results = [self.get_result_entry(row, 2) for row in range(len(self.data))]
        if any(result == ('', '') for result in results):
            return
        self.data = [
            Result((cast(Pairing_Item, item_1), score_1), (cast(Pairing_Item, item_2), score_2))
            for (item_1, item_2), (score_1, score_2) in zip(self.get_pairings(), results)
        ]
        self.drop_outs = self.possible_scores = self.is_valid_pairings = None
        self.update_table()
        QTimer.singleShot(0, self.confirmed_results.emit)

    def update_table(self) -> None:
        clear_table(self.table)
        self.fill_in_table()
