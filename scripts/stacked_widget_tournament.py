from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtCore import pyqtSignal
from .widget_tournament_standings import Widget_Tournament_Standings
from .widget_tournament_cross_table import Widget_Tournament_Cross_Table
from .widget_tournament_round import Widget_Tournament_Round


class Stacked_Widget_Tournament(QStackedWidget):
    make_side_menu = pyqtSignal()

    def __init__(self, window_main, tournament):
        super().__init__()
        self.window_main = window_main
        self.tournament = tournament
        self.round_widgets = []

        self.standings_widget = Widget_Tournament_Standings(self.tournament)
        self.cross_table_widget = Widget_Tournament_Cross_Table(self.tournament)
        self.addWidget(self.standings_widget)
        self.addWidget(self.cross_table_widget)

        self.add_round_widgets()
        self.set_index()

    def add_round_widget(self, roun, current):
        if current:
            results = [((uuid_1, None), (uuid_2, None)) for uuid_1, uuid_2 in self.tournament.get_pairings()]
        else:
            results = self.tournament.get_results()[roun - 1]
        widget = Widget_Tournament_Round(
            results, self.tournament.get_uuid_to_participant_dict(),
            self.tournament.get_possible_scores(), self.tournament.is_valid_pairings
        )
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
        self.tournament.add_results(self.sender().results)
        self.update_rounds()

    def update_rounds(self):
        self.tournament.save("data/tournaments")
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
