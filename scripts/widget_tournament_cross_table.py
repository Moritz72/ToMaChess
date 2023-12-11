from typing import Sequence, cast
from math import ceil, sqrt
from PySide6.QtWidgets import QVBoxLayout, QTableWidget
from PySide6.QtCore import Qt
from .result import Result
from .tournament import Tournament
from .widget_tournament_info import Widget_Tournament_Info
from .gui_table import add_content_to_table, set_up_table, size_table, clear_table, add_blank_to_table


def get_line_breaked_entry(entry: str) -> str:
    if len(entry) == 0:
        return ""
    interval = ceil(sqrt(len(entry)))
    return '\n'.join([entry[i:i + interval] for i in range(0, len(entry), interval)])


def get_results_matrix(
        results: Sequence[Sequence[Result]], participant_number: int, id_to_index: dict[str, int]
) -> list[list[str]]:
    results_matrix = [["" for _ in range(participant_number)] for _ in range(participant_number)]
    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 is not None and uuid_2 is not None:
                results_matrix[id_to_index[uuid_1]][id_to_index[uuid_2]] += score_1
                results_matrix[id_to_index[uuid_2]][id_to_index[uuid_1]] += score_2
    return [[get_line_breaked_entry(entry) for entry in row] for row in results_matrix]


def get_appropriate_width_for_matrix(results_matrix: Sequence[Sequence[str]]) -> float:
    entry_widths = [entry.index('\n') if '\n' in entry else len(entry) for row in results_matrix for entry in row]
    return 2 * max([1.5] + cast(list[float], entry_widths))


class Widget_Tournament_Cross_Table(Widget_Tournament_Info):
    def __init__(self, tournament: Tournament) -> None:
        super().__init__(tournament)
        self.layout_main: QVBoxLayout = QVBoxLayout(self)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout_main.addWidget(self.table)

    def fill_in_table(self) -> None:
        participants = self.tournament.get_standings().participants
        results = self.tournament.get_results()
        id_to_index = {participant.get_uuid(): i for i, participant in enumerate(participants)}
        participant_number = len(participants)
        results_matrix = get_results_matrix(results, participant_number, id_to_index)
        width = get_appropriate_width_for_matrix(results_matrix)
        header_horizontal = ["Name"] + [str(i) for i in range(1, participant_number + 1)]

        set_up_table(self.table, 0, participant_number + 1, header_horizontal=header_horizontal, translate=True)
        size_table(
            self.table, participant_number, width, header_width=3.5, max_width=3.5 + width * participant_number + 17,
            widths=[17.] + participant_number * [width]
        )

        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        for i, participant in enumerate(participants):
            add_content_to_table(self.table, participant, i, 0, edit=False)

        for i in range(participant_number):
            for j in range(participant_number):
                if i == j:
                    add_blank_to_table(self.table, i, j + 1)
                else:
                    add_content_to_table(
                        self.table, results_matrix[i][j], i, j + 1,
                        edit=False, align=Qt.AlignmentFlag.AlignCenter, bold=True
                    )

    def refresh(self) -> None:
        clear_table(self.table)
        self.fill_in_table()
