from __future__ import annotations
from typing import TYPE_CHECKING, Any
from functools import partial
from .stacked_widget import Stacked_Widget
from .stacked_widget_tournament import Stacked_Widget_Tournament
from .db_ms_tournament import DB_MS_TOURNAMENT
from .ms_tournament import MS_Tournament
from .functions_ftp import make_index_file_ms_tournament
if TYPE_CHECKING:
    from .window_main import Window_Main


class Stacked_Widget_MS_Tournament(Stacked_Widget):
    def __init__(self, window_main: Window_Main, ms_tournament: MS_Tournament, stage: int) -> None:
        super().__init__(window_main)
        self.ms_tournament: MS_Tournament = ms_tournament
        self.stage: int = stage
        self.is_current: bool = (self.stage == self.ms_tournament.get_stage())
        self.tournament_widgets: list[Stacked_Widget_Tournament] = []

        make_index_file_ms_tournament(self.ms_tournament)
        self.add_tournament_widgets()

    def add_tournament_widgets(self) -> None:
        for tournament in self.ms_tournament.get_stage_tournaments(self.stage):
            if not tournament.is_valid():
                continue
            tournament_widget = Stacked_Widget_Tournament(self.window_main, tournament, self.ms_tournament.get_name())
            tournament_widget.make_side_menu.connect(self.check_for_changes)
            self.addWidget(tournament_widget)
            self.tournament_widgets.append(tournament_widget)

    def get_buttons_args(self) -> list[dict[str, Any]]:
        buttons_args = []
        cut_out = 1 + 2 * (not self.is_current)
        cut_out_change_index = 2 * self.is_current
        tournaments_buttons_args = [
            tournament_widget.get_buttons_args()[:-cut_out] for tournament_widget in self.tournament_widgets
        ]

        for i, tournament_buttons_args in enumerate(tournaments_buttons_args):
            for args in tournament_buttons_args[:len(tournament_buttons_args) - cut_out_change_index]:
                args["connect"] = [args["connect"], partial(self.setCurrentIndex, i)]

        for tournament_widget, tournament_buttons_args in zip(self.tournament_widgets, tournaments_buttons_args):
            buttons_args.append({"text": tournament_widget.tournament.get_name(), "bold": True, "enabled": False})
            buttons_args.extend(tournament_buttons_args)
            buttons_args.append({"enabled": False})

        if self.stage > 0:
            buttons_args.append({"text": "Previous Stage", "connect": self.move_down_stage, "bold": True})
        if not self.is_current:
            buttons_args.append({"text": "Next Stage", "connect": self.move_up_stage, "bold": True})
        buttons_args.append({"text": "Back", "connect": self.open_default, "bold": True})

        return buttons_args

    def get_active_button_index(self) -> int:
        offset = sum(tournament_widget.count() for tournament_widget in self.tournament_widgets[:self.currentIndex()])
        offset += 1 + (2 + 2 * self.is_current) * self.currentIndex()
        return offset + self.tournament_widgets[self.currentIndex()].get_active_button_index()

    def open_default(self) -> None:
        DB_MS_TOURNAMENT.update_list("", [self.ms_tournament])
        self.window_main.set_stacked_widget("Default")

    def check_for_changes(self) -> None:
        DB_MS_TOURNAMENT.update_list("", [self.ms_tournament])
        if self.ms_tournament.current_stage_is_done() and self.stage + 1 < self.ms_tournament.get_stages():
            self.ms_tournament.advance_stage()
            DB_MS_TOURNAMENT.update_list("", [self.ms_tournament])
            self.move_up_stage()
        self.make_side_menu.emit()

    def move_up_stage(self) -> None:
        if self.ms_tournament.get_stage() > self.stage:
            DB_MS_TOURNAMENT.update_list("", [self.ms_tournament])
            self.window_main.set_stacked_widget(
                "MS_Tournament", {"ms_tournament": self.ms_tournament, "stage": self.stage + 1}
            )

    def move_down_stage(self) -> None:
        DB_MS_TOURNAMENT.update_list("", [self.ms_tournament])
        self.window_main.set_stacked_widget(
            "MS_Tournament", {"ms_tournament": self.ms_tournament, "stage": self.stage - 1}
        )
