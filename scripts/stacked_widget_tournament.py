from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtCore import pyqtSignal
from .widget_tournament_standings import Widget_Tournament_Standings
from .widget_tournament_cross_table import Widget_Tournament_Cross_Table
from .widget_tournament_round import Widget_Tournament_Round
from .widget_tournament_round_team import Widget_Tournament_Round_Team
from .functions_tournament import update_tournament


def get_round_widget(tournament, roun, current):
    if current:
        results = [((uuid_1, None), (uuid_2, None)) for uuid_1, uuid_2 in tournament.get_pairings()]
    else:
        results = tournament.get_results()[roun - 1]
    return Widget_Tournament_Round(
        results, tournament.get_uuid_to_participant_dict(), tournament.get_possible_scores(),
        tournament.is_valid_pairings
    )


def get_team_members_from_uuid(uuid, uuid_to_participant_dict):
    return None if uuid is None else list(uuid_to_participant_dict[uuid].get_uuid_to_member_dict()) + [None]


def get_round_widget_team(tournament, roun, current):
    uuid_to_participant_dict = tournament.get_uuid_to_participant_dict()
    boards = tournament.get_parameter("boards")
    if current:
        results = [((uuid_1, None), (uuid_2, None)) for uuid_1, uuid_2 in tournament.get_pairings()]
        results_individual = [[
            (
                (get_team_members_from_uuid(uuid_1, uuid_to_participant_dict), None),
                (get_team_members_from_uuid(uuid_2, uuid_to_participant_dict), None)
            ) for _ in range(boards)
        ] for (uuid_1, _), (uuid_2, _) in results]
    else:
        results = tournament.get_results()[roun - 1]
        results_individual = tournament.get_variable("results_individual")[roun - 1]
    return Widget_Tournament_Round_Team(
        results, uuid_to_participant_dict, tournament.get_possible_scores(),
        tournament.is_valid_pairings_match, boards, results_individual,
        tournament.get_uuid_to_individual_dict()
    )


class Stacked_Widget_Tournament(QStackedWidget):
    make_side_menu = pyqtSignal()

    def __init__(self, window_main, tournament):
        super().__init__()
        self.window_main = window_main
        self.tournament = tournament
        if self.tournament.is_team_tournament():
            self.get_round_widget = get_round_widget_team
        else:
            self.get_round_widget = get_round_widget
        self.round_widgets = []

        self.standings_widget = Widget_Tournament_Standings(self.tournament)
        self.cross_table_widget = Widget_Tournament_Cross_Table(self.tournament)
        self.addWidget(self.standings_widget)
        self.addWidget(self.cross_table_widget)

        self.add_round_widgets()
        self.set_index()

    def add_round_widget(self, roun, current):
        widget = self.get_round_widget(self.tournament, roun, current)
        self.round_widgets.append(widget)
        self.addWidget(widget)
        if current:
            widget.confirmed_round.connect(self.load_next_round)

    def add_round_widgets(self):
        rounds = self.tournament.get_round()
        self.tournament.load_pairings()
        for i in range(1, rounds):
            self.add_round_widget(i, False)
        if self.tournament.get_pairings() is not None:
            self.add_round_widget(rounds, True)

    def set_index(self):
        if self.tournament.is_done():
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(self.count() - 1)

    def get_button_args(self):
        texts = ["Standings", "Crosstable"] + \
                [self.tournament.get_round_name(i + 1) for i in range(len(self.round_widgets))] + \
                ["Back"]
        functions = [lambda _, index=i: self.setCurrentIndex(index) for i in range(len(self.round_widgets) + 2)] + \
                    [self.open_default]
        return (
            {"text": text, "connect_function": function, "checkable": True} for text, function in zip(texts, functions)
        )

    def get_active_button_index(self):
        return self.currentIndex()

    def open_default(self):
        self.window_main.set_stacked_widget("Default")

    def load_next_round(self):
        self.tournament.add_results(self.sender().get_results())
        self.update_rounds()

    def update_rounds(self):
        update_tournament("", self.tournament)
        self.standings_widget.update_table()
        self.cross_table_widget.update_table()
        self.add_new_round()
        self.make_side_menu.emit()

    def add_new_round(self):
        self.tournament.load_pairings()
        if self.tournament.get_pairings() is None:
            self.setCurrentIndex(0)
        else:
            roun = self.tournament.get_round()
            self.add_round_widget(roun, True)
            self.setCurrentIndex(self.count() - 1)
