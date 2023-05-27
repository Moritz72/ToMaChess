from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtCore import pyqtSignal
from .widget_players import Widget_Players
from .widget_tournaments import Widget_Tournaments
from .widget_teams import Widget_Teams
from .widget_ms_tournaments import Widget_MS_Tournaments
from .widget_collections import Widget_Collections
from .widget_settings import Widget_Settings


class Stacked_Widget_Default(QStackedWidget):
    make_side_menu = pyqtSignal()

    def __init__(self, window_main):
        super().__init__()
        self.window_main = window_main
        self.widget_tournament = Widget_Tournaments()
        self.widget_tournament.selected_tournament.connect(self.open_tournament)
        self.widget_ms_tournament = Widget_MS_Tournaments()
        self.widget_ms_tournament.selected_tournament.connect(self.open_ms_tournament)

        self.addWidget(self.widget_tournament)
        self.addWidget(Widget_Players())
        self.addWidget(Widget_Teams())
        self.addWidget(self.widget_ms_tournament)
        self.addWidget(Widget_Collections(window_main))
        self.addWidget(Widget_Settings(window_main))

    def get_buttons_args(self):
        return (
            {"text": "Tournaments", "connect_function": lambda _: self.setCurrentIndex(0), "checkable": True},
            {"text": "Players", "connect_function": lambda _: self.setCurrentIndex(1), "checkable": True},
            {"text": "Teams", "connect_function": lambda _: self.setCurrentIndex(2), "checkable": True},
            {"text": "MS Tournaments", "connect_function": lambda _: self.setCurrentIndex(3), "checkable": True},
            {"text": "Collections", "connect_function": lambda _: self.setCurrentIndex(4), "checkable": True},
            {"text": "Settings", "connect_function": lambda _: self.setCurrentIndex(5), "checkable": True}
        )

    def get_active_button_index(self):
        return self.currentIndex()

    def open_tournament(self):
        tournament = self.widget_tournament.get_current_tournament_loaded()
        self.window_main.set_stacked_widget("Tournament", {"tournament": tournament})

    def open_ms_tournament(self):
        tournament = self.widget_ms_tournament.get_current_tournament_loaded()
        self.window_main.set_stacked_widget(
            "MS_Tournament", {"ms_tournament": tournament, "stage": tournament.get_stage()}
        )
