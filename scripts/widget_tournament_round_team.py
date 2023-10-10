from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from .widget_tournament_round import Widget_Tournament_Round
from .functions_gui import get_scroll_area_widgets_and_layouts


def get_header(uuid, uuid_to_participant_dict):
    return "" if uuid is None else str(uuid_to_participant_dict[uuid])


def adjust_individual_result_by_drop_outs(team_uuid_1, team_uuid_2, result_individual, drop_outs):
    drop_out_1, drop_out_2 = team_uuid_1 in drop_outs, team_uuid_2 in drop_outs
    return [
        ((None if drop_out_1 else uuid_1, score_1), (None if drop_out_2 else uuid_2, score_2))
        for (uuid_1, score_1), (uuid_2, score_2) in result_individual
    ]


class Widget_Tournament_Round_Team(QWidget):
    confirmed_results = Signal()
    confirmed_pairings = Signal()

    def __init__(
            self, results, uuid_to_participant_dict, drop_outs, possible_scores, is_valid_pairings, boards,
            results_individual, uuid_to_individual_dict
    ):
        super().__init__()
        self.confirmed_results_counter, self.confirmed_pairings_counter = 0, 0
        self.round_widgets = []

        current = any(score_1 is None or score_2 is None for (_, score_1), (_, score_2) in results)
        for ((uuid_1, _), (uuid_2, _)), result_individual in zip(results, results_individual):
            if current:
                result_individual = adjust_individual_result_by_drop_outs(uuid_1, uuid_2, result_individual, drop_outs)
            round_widget = Widget_Tournament_Round(
                result_individual, uuid_to_individual_dict, [], possible_scores,
                lambda x, team_uuids=(uuid_1, uuid_2): is_valid_pairings(team_uuids, x),
                headers=(get_header(uuid_1, uuid_to_participant_dict), get_header(uuid_2, uuid_to_participant_dict))
            )
            round_widget.confirmed_results.connect(self.confirm_result)
            round_widget.confirmed_pairings.connect(self.confirm_pairing)
            self.round_widgets.append(round_widget)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

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
