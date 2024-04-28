from functools import partial
from typing import Callable, Sequence, cast
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget
from .widget_tournament_round import Widget_Tournament_Round
from ..common.gui_functions import get_scroll_area_widgets_and_layouts
from ...tournament.common.pairing import Pairing
from ...tournament.common.pairing_item import Pairing_Item
from ...tournament.common.result import Result
from ...tournament.common.result_team import Result_Team
from ...tournament.tournaments.tournament import Participant


def get_dict(item: Pairing_Item, individual_dicts: dict[str, dict[str, Participant]]) -> dict[str, Participant]:
    return dict() if item.is_bye() else individual_dicts[item]


def get_pairing_individual(pairing: Pairing, individual_dicts: dict[str, dict[str, Participant]]) -> Pairing:
    members_1 = list(get_dict(cast(Pairing_Item, pairing[0]), individual_dicts))
    members_2 = list(get_dict(cast(Pairing_Item, pairing[1]), individual_dicts))
    return Pairing(members_1 + [""], members_2 + [""])


class Widget_Tournament_Round_Team(QWidget):
    confirmed_results = Signal()
    confirmed_pairings = Signal()

    def __init__(
            self, data: list[Pairing] | list[Result], name_dict: dict[str, str],
            individual_dicts: dict[str, dict[str, Participant]], team_results: list[Result_Team] | None = None,
            drop_outs: list[str] | None = None, possible_scores: list[tuple[str, str]] | None = None,
            is_valid_pairings: Callable[[Pairing, Sequence[Pairing]], bool] | None = None, boards: int | None = None
    ):
        super().__init__()
        self.confirmed_results_counter: int = 0
        self.confirmed_pairings_counter: int = 0
        self.round_widgets: list[Widget_Tournament_Round] = []
        name_dict_individual = {
            uuid: str(participant) for individual_dict in individual_dicts.values()
            for uuid, participant in individual_dict.items()
        } | {"bye": "bye", "": ""}

        if team_results is not None:
            results = cast(list[Result], data)

            for ((item_1, _), (item_2, _)), team_result in zip(results, team_results):
                headers = (name_dict[item_1], name_dict[item_2])
                self.round_widgets.append(Widget_Tournament_Round(team_result, name_dict_individual, headers=headers))
        else:
            pairings = cast(list[Pairing], data)
            assert(drop_outs is not None and possible_scores is not None)
            assert(is_valid_pairings is not None and boards is not None)

            for pairing in pairings:
                p_1, p_2 = cast(Pairing_Item, pairing[0]), cast(Pairing_Item, pairing[1])
                individual_pairings = [get_pairing_individual(pairing, individual_dicts) for _ in range(boards)]
                is_valid = partial(is_valid_pairings, pairing)
                headers = (name_dict[p_1], name_dict[p_2])
                round_widget = Widget_Tournament_Round(
                    individual_pairings, name_dict_individual, [], possible_scores, is_valid, headers=headers
                )
                round_widget.confirmed_results.connect(self.confirm_result)
                round_widget.confirmed_pairings.connect(self.confirm_pairing)
                self.round_widgets.append(round_widget)

        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        _, widget_inner, _ = get_scroll_area_widgets_and_layouts(self.layout_main, self.round_widgets)
        widget_inner.setFixedHeight(sum(round_widget.maximumHeight() for round_widget in self.round_widgets))

    def confirm_result(self) -> None:
        self.confirmed_results_counter += 1
        if self.confirmed_results_counter == len(self.round_widgets):
            self.confirmed_results.emit()

    def confirm_pairing(self) -> None:
        self.confirmed_pairings_counter += 1
        if self.confirmed_pairings_counter == len(self.round_widgets):
            self.confirmed_pairings.emit()

    def get_pairings(self) -> list[list[Pairing]]:
        return [round_widget.get_pairings() for round_widget in self.round_widgets]

    def get_results(self) -> list[Result_Team]:
        return [Result_Team(round_widget.get_results()) for round_widget in self.round_widgets]
