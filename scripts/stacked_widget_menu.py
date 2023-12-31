from __future__ import annotations
from typing import TYPE_CHECKING
from functools import partial
from .stacked_widget import Buttons_Args, Stacked_Widget
from .widget_menu_players import Widget_Menu_Players
from .widget_menu_tournaments import Widget_Menu_Tournaments
from .widget_menu_teams import Widget_Menu_Teams
from .widget_menu_ms_tournament import Widget_Menu_MS_Tournament
from .widget_menu_collections import Widget_Menu_Collections
from .widget_settings import Widget_Settings
if TYPE_CHECKING:
    from .window_main import Window_Main


class Stacked_Widget_Menu(Stacked_Widget):
    def __init__(self, window_main: Window_Main):
        super().__init__(window_main)
        self.widget_tournament: Widget_Menu_Tournaments = Widget_Menu_Tournaments()
        self.widget_tournament.selected_tournament.connect(self.open_tournament)
        self.widget_ms_tournament: Widget_Menu_MS_Tournament = Widget_Menu_MS_Tournament()
        self.widget_ms_tournament.selected_tournament.connect(self.open_ms_tournament)

        self.addWidget(self.widget_tournament)
        self.addWidget(Widget_Menu_Players())
        self.addWidget(Widget_Menu_Teams())
        self.addWidget(self.widget_ms_tournament)
        self.addWidget(Widget_Menu_Collections(window_main))
        self.addWidget(Widget_Settings(window_main))

    def get_buttons_args_list(self) -> list[Buttons_Args]:
        return [[
            {"text": "Tournaments", "connect": partial(self.setCurrentIndex, 0), "checkable": True},
            {"text": "Players", "connect": partial(self.setCurrentIndex, 1), "checkable": True},
            {"text": "Teams", "connect": partial(self.setCurrentIndex, 2), "checkable": True},
            {"text": "MS Tournaments", "connect": partial(self.setCurrentIndex, 3), "checkable": True},
            {"text": "Collections", "connect": partial(self.setCurrentIndex, 4), "checkable": True},
            {"text": "Settings", "connect": partial(self.setCurrentIndex, 5), "checkable": True}
        ]]

    def open_tournament(self) -> None:
        tournament = self.widget_tournament.get_current_tournament_loaded()
        self.window_main.set_stacked_widget("Tournament", {"tournament": tournament})

    def open_ms_tournament(self) -> None:
        ms_tournament = self.widget_ms_tournament.get_current_tournament_loaded()
        self.window_main.set_stacked_widget(
            "MS_Tournament", {"ms_tournament": ms_tournament, "stage": ms_tournament.get_stage()}
        )
