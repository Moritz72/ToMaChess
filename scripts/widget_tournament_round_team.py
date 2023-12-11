from typing import Sequence, Callable, cast
from functools import partial
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal
from .pairing import Pairing
from .result import Result
from .result_team import Result_Team
from .tournament import Participant
from .widget_tournament_round import Widget_Tournament_Round
from .gui_functions import get_scroll_area_widgets_and_layouts


def header(uuid: str | None, uuid_to_participant_dict: dict[str, Participant]) -> str:
    return "" if uuid is None else uuid_to_participant_dict[uuid].get_name()


def get_dict(uuid: str | None, uuid_to_individual_dicts: dict[str, dict[str, Participant]]) -> dict[str, Participant]:
    return dict() if uuid is None else uuid_to_individual_dicts[uuid]


def get_pairing_individual(pairing: Pairing, uuid_to_individual_dicts: dict[str, dict[str, Participant]]) -> Pairing:
    members_1: list[str | None] = list(get_dict(cast(str | None, pairing[0]), uuid_to_individual_dicts))
    members_2: list[str | None] = list(get_dict(cast(str | None, pairing[1]), uuid_to_individual_dicts))
    return Pairing(members_1 + [None], members_2 + [None])


class Widget_Tournament_Round_Team(QWidget):
    confirmed_results = Signal()
    confirmed_pairings = Signal()

    def __init__(
            self, data: list[Pairing] | list[Result], uuid_to_participant_dict: dict[str, Participant],
            uuid_to_individual_dicts: dict[str, dict[str, Participant]], team_results: list[Result_Team] | None = None,
            drop_outs: list[str] | None = None, possible_scores: list[tuple[str, str]] | None = None,
            is_valid_pairings: Callable[[Pairing, Sequence[Pairing]], bool] | None = None, boards: int | None = None
    ):
        super().__init__()
        self.confirmed_results_counter: int = 0
        self.confirmed_pairings_counter: int = 0
        self.round_widgets: list[Widget_Tournament_Round] = []

        if team_results is not None:
            results = cast(list[Result], data)

            for ((uuid_1, _), (uuid_2, _)), team_result in zip(results, team_results):
                individual_dict = get_dict(uuid_1, uuid_to_individual_dicts)
                individual_dict |= get_dict(uuid_2, uuid_to_individual_dicts)
                headers = (header(uuid_1, uuid_to_participant_dict), header(uuid_2, uuid_to_participant_dict))
                self.round_widgets.append(Widget_Tournament_Round(team_result, individual_dict, headers=headers))
        else:
            pairings = cast(list[Pairing], data)
            assert(drop_outs is not None and possible_scores is not None)
            assert(is_valid_pairings is not None and boards is not None)

            for pairing in pairings:
                p_1, p_2 = cast(str | None, pairing[0]), cast(str | None, pairing[1])
                individual_pairings = [get_pairing_individual(pairing, uuid_to_individual_dicts) for _ in range(boards)]
                individual_dict = get_dict(p_1, uuid_to_individual_dicts) | get_dict(p_2, uuid_to_individual_dicts)
                is_valid = partial(is_valid_pairings, pairing)
                headers = (header(p_1, uuid_to_participant_dict), header(p_2, uuid_to_participant_dict))
                round_widget = Widget_Tournament_Round(
                    individual_pairings, individual_dict, [], possible_scores, is_valid, headers=headers
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
