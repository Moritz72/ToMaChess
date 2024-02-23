from __future__ import annotations
from typing import TYPE_CHECKING, cast
from functools import partial
from .stacked_widget import Buttons_Args, Stacked_Widget
from .widget_tournament_info import Widget_Tournament_Info
from .widget_tournament_details import Widget_Tournament_Details
from .widget_tournament_standings import Widget_Tournament_Standings
from .widget_tournament_cross_table import Widget_Tournament_Cross_Table
from .widget_tournament_bracket_tree import Widget_Tournament_Bracket_Tree
from .widget_tournament_standings_categories import Widget_Tournament_Standings_Categories
from .widget_tournament_round import Widget_Tournament_Round
from .widget_tournament_round_team import Widget_Tournament_Round_Team
from .window_tournament_actions import Window_Tournament_Actions
from .gui_functions import close_window
from .db_tournament import DB_TOURNAMENT
from .tournament import Tournament
from .functions_pdf import tournament_standings_to_pdf, tournament_participants_to_pdf, tournament_pairings_to_pdf,\
    tournament_results_to_pdf
from .functions_ftp import get_file_name, upload_latest_results, upload_latest_pairings, upload_participants, \
    upload_latest_standings
if TYPE_CHECKING:
    from .window_main import Window_Main


def get_round_widget(tournament: Tournament, roun: int | None) -> Widget_Tournament_Round:
    name_dict = tournament.get_uuid_to_name_dict() | {"bye": "bye", "": ""}
    if roun is not None:
        return Widget_Tournament_Round(tournament.get_results()[roun - 1], name_dict)
    return Widget_Tournament_Round(
        tournament.get_pairings(), name_dict, tournament.get_drop_outs(),
        tournament.get_possible_scores(), tournament.is_valid_pairings
    )


def get_round_widget_team(tournament: Tournament, roun: int | None) -> Widget_Tournament_Round_Team:
    name_dict = tournament.get_uuid_to_name_dict() | {"bye": "bye", "": ""}
    individual_dicts = tournament.get_uuid_to_individual_dicts()
    if roun is not None:
        return Widget_Tournament_Round_Team(
            tournament.get_results()[roun - 1], name_dict, individual_dicts, tournament.get_results_team()[roun - 1]
        )
    return Widget_Tournament_Round_Team(
        tournament.get_pairings(), name_dict, individual_dicts, None, tournament.get_drop_outs(),
        tournament.get_possible_scores(), tournament.is_valid_pairings_match, tournament.get_boards()
    )


class Stacked_Widget_Tournament(Stacked_Widget):
    def __init__(
            self, window_main: Window_Main, tournament: Tournament, associate: tuple[str, str] | None = None
    ) -> None:
        super().__init__(window_main)
        self.tournament: Tournament = tournament
        self.associate: tuple[str, str] | None = associate
        self.window_tournament_actions: Window_Tournament_Actions | None = None
        self.tournament.load_pairings()

        self.widgets_info: list[Widget_Tournament_Info] = [
            Widget_Tournament_Details(self.tournament), Widget_Tournament_Standings(self.tournament),
        ]
        if self.tournament.has_cross_table():
            self.widgets_info.append(Widget_Tournament_Cross_Table(self.tournament))
        if self.tournament.has_bracket_tree():
            self.widgets_info.append(Widget_Tournament_Bracket_Tree(self.tournament))
        if self.tournament.get_category_ranges():
            self.widgets_info.append(Widget_Tournament_Standings_Categories(self.tournament))
        for widget_info in self.widgets_info:
            self.addWidget(widget_info)

        self.widgets_round: list[Widget_Tournament_Round | Widget_Tournament_Round_Team] = []
        for roun in range(1, self.tournament.get_round()):
            self.add_round_widget(roun)
        if bool(self.tournament.get_pairings()):
            self.add_round_widget()

        self.set_index()
        tournament_participants_to_pdf(self.tournament, self.get_folder())
        upload_participants(self.tournament, self.get_folder())

    def get_folder(self) -> str:
        if self.associate is not None:
            return get_file_name(self.associate[0])
        return ""

    def add_round_widget(self, roun: int | None = None) -> None:
        if self.tournament.is_team_tournament():
            self.widgets_round.append(get_round_widget_team(self.tournament, roun))
        else:
            self.widgets_round.append(get_round_widget(self.tournament, roun))
        self.addWidget(self.widgets_round[-1])
        if roun is None:
            self.widgets_round[-1].confirmed_pairings.connect(self.pairings_confirmed)
            self.widgets_round[-1].confirmed_results.connect(self.load_next_round)
            if self.tournament.is_team_tournament():
                tournament_pairings_to_pdf(self.tournament, self.get_folder())
                upload_latest_pairings(self.tournament, self.get_folder())

    def set_index(self) -> None:
        if self.tournament.is_done():
            self.setCurrentIndex(1)
        else:
            self.setCurrentIndex(self.count() - 1)

    def get_buttons_args_list(self) -> list[Buttons_Args]:
        texts: list[str | tuple[str, ...]] = [widget_info.name for widget_info in self.widgets_info]
        texts.extend([self.tournament.get_round_name(i + 1) for i in range(len(self.widgets_round))])

        buttons_args: Buttons_Args = [
            {"text": text, "connect": partial(self.setCurrentIndex, i), "checkable": True}
            for i, text in enumerate(texts)
        ]
        buttons_args.append({"enabled": False})
        buttons_args.append({"text": "Actions", "connect": self.open_actions, "bold": True})
        buttons_args.append({"text": "Back", "connect": self.open_default, "bold": True})
        return [buttons_args]

    def open_default(self) -> None:
        if self.associate is None:
            DB_TOURNAMENT.update_list("", [self.tournament])
        self.window_main.set_stacked_widget("Default")

    def open_actions(self) -> None:
        close_window(self.window_tournament_actions)
        self.window_tournament_actions = Window_Tournament_Actions(self.tournament, self.associate, self)
        self.window_tournament_actions.reload_local_signal.connect(self.reload_local)
        self.window_tournament_actions.undo_signal.connect(self.undo_last_round)
        self.window_tournament_actions.reload_global_signal.connect(self.reload_global)
        self.window_tournament_actions.show()

    def pairings_confirmed(self) -> None:
        if not self.tournament.is_team_tournament():
            sender = cast(Widget_Tournament_Round, self.sender())
            self.tournament.set_pairings(sender.get_pairings())
            tournament_pairings_to_pdf(self.tournament, self.get_folder())
            upload_latest_pairings(self.tournament, self.get_folder())

    def load_next_round(self) -> None:
        sender = cast(Widget_Tournament_Round | Widget_Tournament_Round_Team, self.sender())
        self.tournament.add_results(sender.get_results())
        tournament_results_to_pdf(self.tournament, self.get_folder())
        tournament_standings_to_pdf(self.tournament, self.get_folder())
        upload_latest_standings(self.tournament, self.get_folder())
        upload_latest_results(self.tournament, self.get_folder())
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
        if not bool(self.tournament.get_pairings()):
            return
        self.removeWidget(self.widgets_round.pop())
        self.tournament.set_pairings([])
        self.tournament.load_pairings()
        self.add_new_round()
        self.make_side_menu.emit()

    def reload_global(self) -> None:
        if not bool(self.tournament.get_pairings()):
            self.add_new_round()
        else:
            self.reload_local()
        self.update_rounds()

    def update_rounds(self) -> None:
        if self.associate is None:
            DB_TOURNAMENT.update_list("", [self.tournament])
        for widget_info in self.widgets_info:
            widget_info.refresh()
        self.make_side_menu.emit()
        self.update_window_tournament_actions()

    def add_new_round(self) -> None:
        self.tournament.load_pairings()
        if bool(self.tournament.get_pairings()):
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
