from __future__ import annotations
from typing import TYPE_CHECKING, Any, cast
from functools import partial
from .stacked_widget import Stacked_Widget
from .widget_tournament_info import Widget_Tournament_Info
from .widget_tournament_standings import Widget_Tournament_Standings
from .widget_tournament_cross_table import Widget_Tournament_Cross_Table
from .widget_tournament_standings_categories import Widget_Tournament_Standings_Categories
from .widget_tournament_round import Widget_Tournament_Round
from .widget_tournament_round_team import Widget_Tournament_Round_Team
from .window_tournament_actions import Window_Tournament_Actions
from .gui_functions import close_window
from .db_tournament import DB_TOURNAMENT
from .tournament import Tournament
from .functions_pdf import tournament_standings_to_pdf, tournament_participants_to_pdf, tournament_pairings_to_pdf,\
    tournament_results_to_pdf
from .functions_ftp import upload_latest_results, upload_latest_pairings, upload_participants, \
    upload_latest_standings
if TYPE_CHECKING:
    from .window_main import Window_Main


def get_round_widget(tournament: Tournament, roun: int | None) -> Widget_Tournament_Round:
    participant_dict = tournament.get_uuid_to_participant_dict()
    if roun is not None:
        return Widget_Tournament_Round(tournament.get_results()[roun - 1], participant_dict)
    pairings = tournament.get_pairings()
    assert(pairings is not None)
    return Widget_Tournament_Round(
        pairings, participant_dict, tournament.get_drop_outs(),
        tournament.get_possible_scores(), tournament.is_valid_pairings
    )


def get_round_widget_team(tournament: Tournament, roun: int | None) -> Widget_Tournament_Round_Team:
    participant_dict = tournament.get_uuid_to_participant_dict()
    individual_dicts = tournament.get_uuid_to_individual_dicts()
    if roun is not None:
        roun -= 1
        return Widget_Tournament_Round_Team(
            tournament.get_results()[roun], participant_dict, individual_dicts, tournament.get_results_team()[roun]
        )
    pairings = tournament.get_pairings()
    assert(pairings is not None)
    return Widget_Tournament_Round_Team(
        pairings, participant_dict, individual_dicts, None, tournament.get_drop_outs(),
        tournament.get_possible_scores(), tournament.is_valid_pairings_match, tournament.get_boards()
    )


class Stacked_Widget_Tournament(Stacked_Widget):
    def __init__(self, window_main: Window_Main, tournament: Tournament, sub_folder: str = "") -> None:
        super().__init__(window_main)
        self.tournament: Tournament = tournament
        self.sub_folder: str = sub_folder
        self.window_tournament_actions: Window_Tournament_Actions | None = None

        self.widgets_info: list[Widget_Tournament_Info] = []
        self.widgets_info.append(Widget_Tournament_Standings(self.tournament))
        self.widgets_info.append(Widget_Tournament_Cross_Table(self.tournament))
        if self.tournament.get_category_ranges():
            self.widgets_info.append(Widget_Tournament_Standings_Categories(self.tournament))
        for widget_info in self.widgets_info:
            self.addWidget(widget_info)

        self.widgets_round: list[Widget_Tournament_Round | Widget_Tournament_Round_Team] = []
        for roun in range(1, self.tournament.get_round()):
            self.add_round_widget(roun)
        self.tournament.load_pairings()
        if self.tournament.get_pairings() is not None:
            self.add_round_widget()

        if self.tournament.get_pairings() is not None and self.tournament.is_team_tournament():
            tournament_pairings_to_pdf(self.tournament, self.sub_folder)
            upload_latest_pairings(self.tournament, self.sub_folder)

        self.set_index()
        tournament_participants_to_pdf(self.tournament, self.sub_folder)
        upload_participants(self.tournament, self.sub_folder)

    def add_round_widget(self, roun: int | None = None) -> None:
        if self.tournament.is_team_tournament():
            self.widgets_round.append(get_round_widget_team(self.tournament, roun))
        else:
            self.widgets_round.append(get_round_widget(self.tournament, roun))
        self.addWidget(self.widgets_round[-1])
        if roun is None:
            self.widgets_round[-1].confirmed_pairings.connect(self.pairings_confirmed)
            self.widgets_round[-1].confirmed_results.connect(self.load_next_round)

    def set_index(self) -> None:
        if self.tournament.is_done():
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(self.count() - 1)

    def get_buttons_args(self) -> list[dict[str, Any]]:
        texts: list[str | tuple[str, ...]] = ["Standings", "Crosstable"]
        if len(self.widgets_info) == 3:
            texts.append("Categories")
        texts.extend([self.tournament.get_round_name(i + 1) for i in range(len(self.widgets_round))])

        buttons_args: list[dict[str, Any]] = [
            {"text": text, "connect": partial(self.setCurrentIndex, i), "checkable": True}
            for i, text in enumerate(texts)
        ]
        buttons_args.append({"enabled": False})
        buttons_args.append({"text": "Actions", "connect": self.open_actions, "bold": True})
        buttons_args.append({"text": "Back", "connect": self.open_default, "bold": True})
        return buttons_args

    def get_active_button_index(self) -> int:
        return self.currentIndex()

    def open_default(self) -> None:
        if self.sub_folder == "":
            DB_TOURNAMENT.update_list("", [self.tournament])
        self.window_main.set_stacked_widget("Default")

    def open_actions(self) -> None:
        close_window(self.window_tournament_actions)
        self.window_tournament_actions = Window_Tournament_Actions(self.tournament, parent=self)
        self.window_tournament_actions.reload_local_signal.connect(self.reload_local)
        self.window_tournament_actions.undo_signal.connect(self.undo_last_round)
        self.window_tournament_actions.reload_global_signal.connect(self.reload_global)
        self.window_tournament_actions.show()

    def pairings_confirmed(self) -> None:
        if not self.tournament.is_team_tournament():
            sender = cast(Widget_Tournament_Round, self.sender())
            self.tournament.set_pairings(sender.get_pairings())
            tournament_pairings_to_pdf(self.tournament, self.sub_folder)
            upload_latest_pairings(self.tournament, self.sub_folder)

    def load_next_round(self) -> None:
        sender = cast(Widget_Tournament_Round | Widget_Tournament_Round_Team, self.sender())
        self.tournament.add_results(sender.get_results())
        tournament_results_to_pdf(self.tournament, self.sub_folder)
        tournament_standings_to_pdf(self.tournament, self.sub_folder)
        upload_latest_standings(self.tournament, self.sub_folder)
        upload_latest_results(self.tournament, self.sub_folder)
        self.add_new_round()
        self.update_rounds()

    def undo_last_round(self) -> None:
        if self.tournament.get_round() == 1:
            return
        self.removeWidget(self.widgets_round.pop())
        if not self.tournament.is_done():
            self.removeWidget(self.widgets_round.pop())
        self.tournament.remove_results()
        self.add_new_round()
        self.update_rounds()

    def reload_local(self) -> None:
        if self.tournament.get_pairings() is None:
            return
        self.removeWidget(self.widgets_round.pop())
        self.tournament.clear_pairings()
        self.tournament.load_pairings()
        self.add_new_round()
        self.make_side_menu.emit()

    def reload_global(self) -> None:
        if self.tournament.get_pairings() is None:
            self.add_new_round()
        else:
            self.reload_local()
        self.update_rounds()

    def update_rounds(self) -> None:
        if not self.sub_folder:
            DB_TOURNAMENT.update_list("", [self.tournament])
        for widget_info in self.widgets_info:
            widget_info.refresh()
        self.make_side_menu.emit()
        self.update_window_tournament_actions()

    def add_new_round(self) -> None:
        self.tournament.load_pairings()
        if self.tournament.get_pairings() is not None:
            self.add_round_widget()
        self.set_index()
        self.update_window_tournament_actions()

    def update_window_tournament_actions(self) -> None:
        try:
            if self.window_tournament_actions is None:
                return
            self.window_tournament_actions.add_buttons()
        except RuntimeError:
            pass
