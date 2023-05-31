from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtCore import pyqtSignal
from .stacked_widget_tournament import Stacked_Widget_Tournament
from .functions_ms_tournament import update_ms_tournament


class Stacked_Widget_MS_Tournament(QStackedWidget):
    make_side_menu = pyqtSignal()

    def __init__(self, window_main, ms_tournament, stage):
        super().__init__()
        self.window_main = window_main
        self.ms_tournament = ms_tournament
        self.stage = stage
        self.tournament_widgets = []

        self.add_tournament_widgets()

    def add_tournament_widgets(self):
        for tournament in self.ms_tournament.get_stage_tournaments(self.stage):
            if not tournament.is_valid():
                continue
            tournament_widget = Stacked_Widget_Tournament(self.window_main, tournament, self.ms_tournament.get_name())
            tournament_widget.make_side_menu.connect(self.load_next_round)
            self.addWidget(tournament_widget)
            self.tournament_widgets.append(tournament_widget)

    def get_buttons_args(self):
        buttons_args = []
        tournaments_buttons_args = [
            tournament_widget.get_buttons_args()[:-1] for tournament_widget in self.tournament_widgets
        ]

        for i, tournament_buttons_args in enumerate(tournaments_buttons_args):
            for args in tournament_buttons_args[:-2]:
                temp = args["connect_function"]
                del args["connect_function"]
                args["connect_function"] = lambda _, index=i, func=temp: (func(_), self.setCurrentIndex(index))

        for tournament_widget, tournament_buttons_args in zip(self.tournament_widgets, tournaments_buttons_args):
            buttons_args.append({"text": tournament_widget.tournament.get_name(), "bold": True, "enabled": False})
            buttons_args.extend(tournament_buttons_args)
            buttons_args.append({"enabled": False})

        if self.stage > 0:
            buttons_args.append({"text": "Previous Stage", "connect_function": self.move_down_stage, "bold": True})
        if self.stage < self.ms_tournament.get_stage():
            buttons_args.append({"text": "Next Stage", "connect_function": self.move_up_stage, "bold": True})
        buttons_args.append({"text": "Back", "connect_function": self.open_default, "bold": True})

        return buttons_args

    def get_active_button_index(self):
        offset = sum(tournament_widget.count() for tournament_widget in self.tournament_widgets[:self.currentIndex()])
        offset += 1 + 2 * self.currentIndex()
        return offset + self.tournament_widgets[self.currentIndex()].get_active_button_index()

    def open_default(self):
        self.window_main.set_stacked_widget("Default")

    def load_next_round(self):
        update_ms_tournament("", self.ms_tournament)
        if self.ms_tournament.current_stage_is_done() and self.stage + 1 < self.ms_tournament.get_stages():
            self.ms_tournament.advance_stage()
            update_ms_tournament("", self.ms_tournament)
            self.move_up_stage()
        self.make_side_menu.emit()

    def move_up_stage(self):
        self.window_main.set_stacked_widget(
            "MS_Tournament", {"ms_tournament": self.ms_tournament, "stage": self.stage + 1}
        )

    def move_down_stage(self):
        self.window_main.set_stacked_widget(
            "MS_Tournament", {"ms_tournament": self.ms_tournament, "stage": self.stage - 1}
        )
