from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtCore import pyqtSignal
from .widget_tournament_standings import Widget_Tournament_Standings
from .widget_tournament_cross_table import Widget_Tournament_Cross_Table
from .widget_tournament_round import Widget_Tournament_Round


class Stacked_Widget_MS_Tournament(QStackedWidget):
    make_side_menu = pyqtSignal()

    def __init__(self, window_main, ms_tournament, stage):
        super().__init__()
        self.window_main = window_main
        self.ms_tournament = ms_tournament
        self.stage = stage
        self.tournaments = self.ms_tournament.get_tournaments(self.stage)

        self.standings_widgets = []
        self.cross_table_widgets = []
        self.round_widgets = []
        self.start_widget_indicies = []

        for i, tournament in enumerate(self.tournaments):
            self.add_tournament_widgets(tournament)
            self.add_connect_function(i)
        self.set_index()

    def add_tournament_widgets(self, tournament):
        self.start_widget_indicies.append(self.count())
        self.round_widgets.append([])
        standings_widget = Widget_Tournament_Standings(tournament)
        cross_table_widget = Widget_Tournament_Cross_Table(tournament)
        self.standings_widgets.append(standings_widget)
        self.cross_table_widgets.append(cross_table_widget)
        self.addWidget(standings_widget)
        self.addWidget(cross_table_widget)
        self.add_round_widgets(tournament)

    @staticmethod
    def get_round_widget(tournament, roun, current):
        if current:
            results = [((uuid_1, None), (uuid_2, None)) for uuid_1, uuid_2 in tournament.get_pairings()]
        else:
            results = tournament.get_results()[roun - 1]
        return Widget_Tournament_Round(
            results, tournament.get_uuid_to_participant_dict(),
            tournament.get_possible_scores(), tournament.is_valid_pairings
        )

    def add_round_widget(self, widget, index):
        if index < 0:
            index = index+len(self.start_widget_indicies)
        self.round_widgets[index].append(widget)
        if index < len(self.start_widget_indicies)-1:
            self.insertWidget(self.start_widget_indicies[index+1], widget)
        else:
            self.insertWidget(self.count(), widget)
        for i in range(index+1, len(self.start_widget_indicies)):
            self.start_widget_indicies[i] += 1

    def add_round_widgets(self, tournament):
        rounds = tournament.get_round()
        tournament.load_pairings()
        for i in range(1, rounds):
            self.add_round_widget(self.get_round_widget(tournament, i, False), -1)
        if tournament.get_pairings() is not None:
            self.add_round_widget(self.get_round_widget(tournament, rounds, True), -1)

    def add_connect_function(self, i):
        if len(self.round_widgets) > 0 and self.round_widgets[i][-1].is_current():
            self.round_widgets[i][-1].confirmed_round.connect(lambda index=i: self.load_next_round(index))

    def set_index(self):
        for tournament, index in zip(self.tournaments, self.start_widget_indicies):
            if not tournament.is_done():
                self.setCurrentIndex(index + 1 + tournament.get_round())
                return

    def get_button_args(self):
        text_lists = [
            [tournament.get_name(), "Standings", "Crosstable"] +
            [tournament.get_round_name(i + 1) for i in range(len(round_widgets))] +
            [""]
            for tournament, round_widgets in zip(self.tournaments, self.round_widgets)
        ]
        bolds, enableds, functions = [], [], []
        counter = 0
        for text_list in text_lists:
            for i in range(len(text_list)):
                if i == 0 or i == len(text_list) - 1:
                    bolds.append(True)
                    enableds.append(False)
                    functions.append(None)
                else:
                    bolds.append(False)
                    enableds.append(True)
                    functions.append(lambda _, index=counter: self.setCurrentIndex(index))
                    counter += 1
        texts = [element for text_list in text_lists for element in text_list]
        args_lists = [
            {"text": text, "connect_function": function, "bold": bold, "enabled": enabled, "checkable": True}
            for text, function, bold, enabled in zip(texts, functions, bolds, enableds)
        ]
        if self.stage > 0:
            args_lists.append({
                "text": "Previous Stage", "connect_function": self.move_down_stage, "bold": True,
                "enabled": True, "checkable": True
            })
        if self.stage < self.ms_tournament.get_stage():
            args_lists.append({
                "text": "Next Stage", "connect_function": self.move_up_stage, "bold": True,
                "enabled": True, "checkable": True
            })
        args_lists.append({
            "text": "Back", "connect_function": self.open_default, "bold": True, "enabled": True, "checkable": True
        })
        return args_lists

    def widget_index_to_button_index(self, widget_index):
        button_index = widget_index + 1
        i = 1
        while i < len(self.start_widget_indicies) and self.start_widget_indicies[i] <= widget_index:
            button_index += 2
            i += 1
        return button_index

    def get_active_button_index(self):
        return self.widget_index_to_button_index(self.currentIndex())

    def open_default(self):
        self.window_main.set_stacked_widget("Default")

    def load_next_round(self, i):
        self.tournaments[i].add_results(self.sender().results)
        self.ms_tournament.save_tournament(self.stage, i)
        self.standings_widgets[i].update_table()
        self.cross_table_widgets[i].update_table()

        if self.ms_tournament.current_stage_is_done() and self.stage + 1 < self.ms_tournament.get_stages():
            self.ms_tournament.advance_stage()
            self.ms_tournament.save()
            self.move_up_stage()
        else:
            self.add_new_round(i)
            self.make_side_menu.emit()

    def add_new_round(self, i):
        self.tournaments[i].load_pairings()
        if self.tournaments[i].get_pairings() is None:
            self.setCurrentIndex(self.start_widget_indicies[i])
        else:
            roun = self.tournaments[i].get_round()
            widget = self.get_round_widget(self.tournaments[i], roun, True)
            self.add_round_widget(widget, i)
            self.add_connect_function(i)
            self.setCurrentIndex(self.indexOf(widget))

    def move_up_stage(self):
        self.window_main.set_stacked_widget(
            "MS_Tournament",
            {"ms_tournament": self.ms_tournament, "stage": self.stage + 1}
        )

    def move_down_stage(self):
        self.window_main.set_stacked_widget(
            "MS_Tournament",
            {"ms_tournament": self.ms_tournament, "stage": self.stage - 1}
        )
