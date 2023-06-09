from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from .widget_tournament_round import Widget_Tournament_Round
from .functions_gui import get_scroll_area_widgets_and_layouts


class Widget_Tournament_Round_Team(QWidget):
    confirmed_results = pyqtSignal()
    confirmed_pairings = pyqtSignal()

    def __init__(
            self, results, uuid_to_participant_dict, possible_scores, is_valid_pairings, boards, results_individual,
            uuid_to_individual_dict
    ):
        super().__init__()
        self.confirmed_results_counter, self.confirmed_pairings_counter = 0, 0
        self.round_widgets = []

        for ((uuid_1, _), (uuid_2, _)), result_individual in zip(results, results_individual):
            round_widget = Widget_Tournament_Round(
                result_individual, uuid_to_individual_dict, possible_scores,
                lambda x, team_uuids=(uuid_1, uuid_2): is_valid_pairings(team_uuids, x),
                headers=(
                    "" if uuid_1 is None else str(uuid_to_participant_dict[uuid_1]),
                    "" if uuid_2 is None else str(uuid_to_participant_dict[uuid_2])
                )
            )
            round_widget.confirmed_results.connect(self.confirm_result)
            round_widget.confirmed_pairings.connect(self.confirm_pairing)
            self.round_widgets.append(round_widget)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        _, widget_inner, _ = get_scroll_area_widgets_and_layouts(self.layout, self.round_widgets)
        widget_inner.setFixedHeight(sum(round_widget.maximumHeight() for round_widget in self.round_widgets))

    def confirm_result(self):
        self.confirmed_results_counter += 1
        if self.confirmed_results_counter == len(self.round_widgets):
            self.confirmed_results.emit()

    def confirm_pairing(self):
        self.confirmed_pairings_counter += 1
        if self.confirmed_pairings_counter == len(self.round_widgets):
            self.confirmed_pairings.emit()

    def get_pairings(self):
        return [round_widget.get_pairings() for round_widget in self.round_widgets]

    def get_results(self):
        return [round_widget.get_results() for round_widget in self.round_widgets]
