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
        self.add_connect_function()
        self.set_index()

    def add_round_widget(self, widget):
        self.round_widgets.append(widget)
        self.addWidget(widget)

    def add_round_widgets(self):
        rounds = self.tournament.get_round()
        self.tournament.load_pairings()
        if self.tournament.get_pairings() is None:
            rounds = rounds - 1
        for i in range(rounds):
            self.add_round_widget(Widget_Tournament_Round(self.tournament, i + 1))

    def add_connect_function(self):
        if len(self.round_widgets) > 0 and self.round_widgets[-1].current:
            self.round_widgets[-1].confirmed_round.connect(self.load_next_round)

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
            self.add_round_widget(Widget_Tournament_Round(self.tournament, roun))
            self.add_connect_function()
            self.setCurrentIndex(self.count() - 1)
