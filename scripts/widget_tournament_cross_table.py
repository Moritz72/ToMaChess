from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget
from PyQt5.QtCore import Qt
from .functions_gui import add_content_to_table, make_headers_bold_horizontal, make_headers_bold_vertical, size_table,\
    clear_table


def get_results_matrix(results, participant_number, id_to_index):
    results_matrix = [['' for _ in range(participant_number)] for _ in range(participant_number)]
    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 is not None and uuid_2 is not None:
                results_matrix[id_to_index[uuid_1]][id_to_index[uuid_2]] += score_1
                results_matrix[id_to_index[uuid_2]][id_to_index[uuid_1]] += score_2
    return results_matrix


class Widget_Tournament_Cross_Table(QWidget):
    def __init__(self, tournament):
        super().__init__()
        self.tournament = tournament

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout.addWidget(self.table, Qt.AlignCenter)

    def fill_in_table(self):
        participants = [entry[0] for entry in self.tournament.get_standings()[2]]
        results = self.tournament.get_results()
        id_to_index = {player.get_uuid(): i for i, player in enumerate(participants)}
        participant_number = len(participants)

        size_table(
            self.table, participant_number, participant_number + 1, 5,
            max_width=3.5 + 5 * participant_number + 17, widths=[17] + participant_number * [5], header_width=3.5
        )
        self.table.setHorizontalHeaderLabels(["Name"] + [str(i) for i in range(1, participant_number + 1)])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header = self.table.horizontalHeader()
        header = self.table.verticalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)

        for i, participant in enumerate(participants):
            add_content_to_table(self.table, participant, i, 0, edit=False)

        results_matrix = get_results_matrix(results, participant_number, id_to_index)
        for i in range(participant_number):
            for j in range(participant_number):
                if i == j:
                    add_content_to_table(
                        self.table, ' ', i, j + 1, edit=False, align=Qt.AlignCenter, color_bg=(128, 128, 128)
                    )
                else:
                    add_content_to_table(
                        self.table, results_matrix[i][j], i, j + 1, edit=False, align=Qt.AlignCenter, bold=True
                    )

    def update_table(self):
        clear_table(self.table)
        self.fill_in_table()
