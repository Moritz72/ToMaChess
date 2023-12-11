from typing import Sequence, Callable, cast
from copy import deepcopy
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QComboBox, QTableWidget
from PySide6.QtCore import Qt, Signal, QTimer
from .pairing import Pairing
from .result import Result
from .tournament import Participant
from .gui_table import add_content_to_table, add_button_to_table, add_combobox_to_table, clear_table,\
    set_up_table, size_table, add_blank_to_table

U = (str | None) | Sequence[str | None]


class Widget_Tournament_Round(QWidget):
    confirmed_pairings = Signal()
    confirmed_results = Signal()

    def __init__(
            self, data: list[Pairing] | list[Result], uuid_to_participant_dict: dict[str, Participant],
            drop_outs: list[str] | None = None, possible_scores: list[tuple[str, str]] | None = None,
            is_valid_pairings: Callable[[Sequence[Pairing]], bool] | None = None, headers: tuple[str, str] = ("", "")
    ) -> None:
        super().__init__()
        self.data: list[Pairing] | list[Result] = data
        self.uuid_to_participant_dict: dict[str, Participant] = uuid_to_participant_dict
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

    def get_name(self, uuid: str | None) -> str:
        if uuid is None:
            return "bye"
        return self.uuid_to_participant_dict[uuid].get_name()

    def get_first_not_selected_index(self, uuids: Sequence[str | None]) -> int:
        return next((index for index, uuid in enumerate(uuids) if uuid not in self.initially_selected_uuids), 0)

    def add_selected_uuid(self, uuid: str | None) -> None:
        if uuid is not None:
            self.initially_selected_uuids.add(uuid)

    def add_row_name(self, row: int, column: int, uuid_s: U) -> None:
        if isinstance(uuid_s, str) or uuid_s is None:
            add_content_to_table(
                self.table, self.get_name(uuid_s), row, column,
                edit=False, align=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            self.add_selected_uuid(uuid_s)
        else:
            current_index = self.get_first_not_selected_index(uuid_s)
            add_combobox_to_table(
                self.table, ["bye" if uuid is None else self.uuid_to_participant_dict[uuid] for uuid in uuid_s],
                row, column, "medium", None, current_index=current_index, translate=True
            )
            self.add_selected_uuid(uuid_s[current_index])

    def add_row_result(self, row: int, column: int, scores: tuple[str, str] | list[tuple[str, str]]) -> None:
        if isinstance(scores, list):
            add_combobox_to_table(
                self.table, [" : "] + [" : ".join(score) for score in scores], row, column, "medium", None,
                down_arrow=False, bold=True, align=Qt.AlignmentFlag.AlignCenter
            )
        else:
            add_content_to_table(
                self.table, f"{scores[0]} : {scores[1]}", row, column,
                edit=False, align=Qt.AlignmentFlag.AlignCenter, bold=True
            )

    def add_row(self, row: int, uuid_s_1: U, uuid_s_2: U, scores: tuple[str, str] | list[tuple[str, str]]) -> None:
        add_content_to_table(self.table, row + 1, row, 0, edit=False, bold=True, align=Qt.AlignmentFlag.AlignCenter)
        self.add_row_name(row, 1, uuid_s_1)
        self.add_row_result(row, 2, scores)
        self.add_row_name(row, 3, uuid_s_2)

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
        size_table(self.table, self.get_rows(), 3.5, max_width=55, widths=[3.5, None, 5, None])

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header_horizontal.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header_vertical.setVisible(False)

        if self.drop_outs is None or self.possible_scores is None or self.is_valid_pairings is None:
            for i, ((uuid_1, score_1), (uuid_2, score_2)) in enumerate(self.get_results()):
                self.add_row(i, uuid_1, uuid_2, (score_1, score_2))
            return

        pairings = self.get_pairings()
        for i, (uuid_1, uuid_2) in enumerate(pairings):
            scores: tuple[str, str] | list[tuple[str, str]]
            if uuid_1 is None and uuid_2 is None:
                scores = ('-', '-')
            elif uuid_1 is None:
                scores = ('-', '+')
            elif uuid_2 is None:
                scores = ('+', '-')
            else:
                scores = self.possible_scores
            self.add_row(i, uuid_1, uuid_2, scores)
        self.add_last_row(all(pairing.is_fixed() for pairing in pairings))

    def fix_pairing_entry(self, pairings: Sequence[Pairing], row: int, column: int) -> None:
        widget = self.table.cellWidget(row, column)
        if not isinstance(widget, QComboBox):
            return
        if widget.currentData() == "bye":
            pairings[row].fix(column == 3, None)
        else:
            pairings[row].fix(column == 3, cast(Participant, widget.currentData()).get_uuid())

    def get_fixed_pairings(self, pairings: list[Pairing]) -> list[Pairing]:
        fixed_pairings = deepcopy(pairings)
        for row in range(len(fixed_pairings)):
            self.fix_pairing_entry(fixed_pairings, row, 1)
            self.fix_pairing_entry(fixed_pairings, row, 3)
        return fixed_pairings

    def get_result_entry(self, row: int, column: int) -> tuple[str, str]:
        item = self.table.item(row, column)
        widget = self.table.cellWidget(row, column)
        if isinstance(widget, QComboBox):
            return cast(tuple[str, str], tuple(widget.currentText().split(" : ")))
        return cast(tuple[str, str], tuple(item.text().split(" : ")))

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
            Result((cast(str | None, uuid_1), score_1), (cast(str | None, uuid_2), score_2))
            for (uuid_1, uuid_2), (score_1, score_2) in zip(self.get_pairings(), results)
        ]
        self.drop_outs = self.possible_scores = self.is_valid_pairings = None
        self.update_table()
        QTimer.singleShot(0, self.confirmed_results.emit)

    def update_table(self) -> None:
        clear_table(self.table)
        self.fill_in_table()
