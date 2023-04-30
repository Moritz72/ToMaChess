from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal
from .stacked_widget_tournament import Stacked_Widget_Tournament
from .widget_tournament_round import Widget_Tournament_Round
from .functions_gui import get_scroll_area_widgets_and_layouts


class Stacked_Widget_Tournament_Team(Stacked_Widget_Tournament):
    make_side_menu = pyqtSignal()

    def __init__(self, window_main, tournament):
        self.current_matches_widgets = []
        super().__init__(window_main, tournament)

    def get_round_widget_individual(self, results, is_valid_pairings, headers):
        return Widget_Tournament_Round(
            results, self.tournament.get_uuid_to_individual_dict(),
            self.tournament.get_possible_scores(), is_valid_pairings, headers
        )

    def add_round_widget(self, roun, current):
        if current:
            pairings_uuid = self.tournament.get_pairings()
        else:
            pairings_uuid = [(uuid_1, uuid_2) for (uuid_1, _), (uuid_2, _) in self.tournament.get_results()[roun-1]]
        pairings_team = [
            tuple(
                None if uuid is None else self.tournament.get_uuid_to_participant_dict()[uuid] for uuid in pairing
            ) for pairing in pairings_uuid
        ]
        if current:
            results_all = [[
                tuple(
                    (None if team is None else list(team.get_uuid_to_member_dict()) + [None], None) for team in pairing
                ) for _ in range(self.tournament.get_parameter("boards"))
            ] for pairing in pairings_team]
        else:
            results_all = self.tournament.get_variable("results_individual")[roun-1]

        round_widgets = []
        for uuids, teams, results in zip(pairings_uuid, pairings_team, results_all):
            round_widget = self.get_round_widget_individual(
                results, lambda x, team_uuids=uuids: self.tournament.is_valid_pairings_match(team_uuids, x),
                ("" if teams[0] is None else str(teams[0]), "" if teams[1] is None else str(teams[1]))
            )
            round_widgets.append(round_widget)
            if current:
                self.current_matches_widgets.append(round_widget)
                round_widget.confirmed_round.connect(self.load_next_round)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        _, widget_inner, _ = get_scroll_area_widgets_and_layouts(layout, round_widgets)
        widget_inner.setFixedHeight(sum(round_widget.table.maximumHeight()+20 for round_widget in round_widgets))
        self.round_widgets.append(widget)
        self.addWidget(widget)

    def load_next_round(self):
        if any(widget.is_current() for widget in self.current_matches_widgets):
            return
        self.tournament.add_results([widget.results for widget in self.current_matches_widgets])
        self.current_matches_widgets = []
        self.update_rounds()
