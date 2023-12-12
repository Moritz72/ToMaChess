from __future__ import annotations
from typing import Sequence, Any, cast
from json import dumps
from copy import deepcopy
from .object import Object
from .player import Player
from .team import Team
from .pairing import Pairing
from .result import Result
from .result_team import Result_Team
from .category_range import Category_Range
from .standings_table import Standings_Table
from .parameter import Parameter
from .parameter_armageddon import Parameter_Armageddon
from .parameter_tiebreak import Parameter_Tiebreak
from .variable import Variable
from .variable_category_ranges import Variable_Category_Ranges
from .variable_pairings import Variable_Pairings
from .variable_results import Variable_Results
from .variable_results_team import Variable_Results_Team
from .variable_knockout_standings import Variable_Knockout_Standings
from .functions_util import shorten_float
from .functions_tournament_util import get_standings_with_tiebreaks, get_team_result, is_valid_seating

Participant = Player | Team
Tournament_Data = tuple[str, str, int, str, str, str, str, str]
Tournament_Data_Loaded = tuple[str, str, int, dict[str, Any], dict[str, Any], list[str], str, str]

PARAMETERS = {
    Parameter_Armageddon,
    Parameter_Tiebreak
}
VARIABLES = {
    Variable_Category_Ranges,
    Variable_Pairings,
    Variable_Results,
    Variable_Results_Team,
    Variable_Knockout_Standings
}


class Tournament(Object):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(name, uuid, uuid_associate)
        self.participants: list[Participant] = []
        self.parameters: dict[str, Any] = parameters or dict()
        self.variables: dict[str, Any] = variables or dict()
        self.parameters = self.parameters
        self.variables = {"round": 1, "pairings": None, "results": Variable_Results([]),
                          "results_team": Variable_Results_Team([]), "drop_outs": [],
                          "category_ranges": Variable_Category_Ranges([])} | self.variables
        self.order: list[str] | None = order
        self.mode: str = ""
        self.parameters_display: dict[str, tuple[str, ...] | str | None] = dict()
        self.load_parameters_and_variables()
        self.set_participants(participants, order=True)
        self.shallow_participant_count: int = shallow_participant_count or len(self.participants)

    def copy(self) -> Tournament:
        return deepcopy(self)

    def get_participants(self, drop_outs: bool = True) -> list[Participant]:
        if drop_outs:
            return self.participants
        return [participant for participant in self.participants if participant.get_uuid() not in self.get_drop_outs()]

    def get_shallow_participant_count(self) -> int:
        return self.shallow_participant_count

    def get_participant_count(self, drop_outs: bool = True) -> int:
        if bool(self.get_participants()):
            return len(self.get_participants(drop_outs))
        return self.get_shallow_participant_count()

    def get_parameters(self) -> dict[str, Any]:
        return self.parameters

    def get_changeable_parameters(self, initial: bool = False) -> dict[str, Any]:
        return {key: value for key, value in self.get_parameters().items()}

    def get_parameter(self, key: str) -> Any:
        return self.parameters[key]

    def get_variables(self) -> dict[str, Any]:
        return self.variables

    def get_variable(self, key: str) -> Any:
        return self.variables[key]

    def get_order(self) -> list[str] | None:
        return self.order

    def get_mode(self) -> str:
        return self.mode

    def get_parameters_display(self) -> dict[str, tuple[str, ...] | str | None]:
        return self.parameters_display

    def get_tiebreaks(self) -> tuple[Parameter_Tiebreak, ...]:
        return tuple()

    def get_boards(self) -> int:
        if not self.is_team_tournament():
            return NotImplemented
        return cast(int, self.get_parameter("boards"))

    def get_enforce_lineups(self) -> bool:
        if not self.is_team_tournament():
            return NotImplemented
        return cast(bool, self.get_parameter("enforce_lineups"))

    def get_round(self) -> int:
        return cast(int, self.get_variable("round"))

    def get_pairings(self) -> Variable_Pairings | None:
        return cast(Variable_Pairings | None, self.get_variable("pairings"))

    def get_results(self) -> Variable_Results:
        return cast(Variable_Results, self.get_variable("results"))

    def get_drop_outs(self) -> list[str]:
        return cast(list[str], self.get_variable("drop_outs"))

    def get_category_ranges(self) -> Variable_Category_Ranges:
        return cast(Variable_Category_Ranges, self.get_variable("category_ranges"))

    def get_results_team(self) -> Variable_Results_Team:
        if not self.is_team_tournament():
            return NotImplemented
        return cast(Variable_Results_Team, self.get_variable("results_team"))

    def get_data(self) -> Tournament_Data:
        parameters = self.get_parameters().copy()
        variables = self.get_variables().copy()
        for parameter, value in parameters.items():
            if isinstance(value, Parameter):
                parameters[parameter] = {"class": value.__class__.__name__, "dict": value.get_dict()}
        for variable, value in variables.items():
            if isinstance(value, Variable):
                variables[variable] = {"class": value.__class__.__name__, "dict": value.get_dict()}
        return self.get_mode(), self.get_name(), self.get_participant_count(), dumps(parameters), dumps(variables),\
            dumps([participant.get_uuid() for participant in self.get_participants()] or self.order), \
            self.get_uuid(), self.get_uuid_associate()

    def get_score_dict(self) -> dict[str, float]:
        return {'1': 1, '½': .5, '0': 0, '+': 1, '-': 0}

    def get_score_dict_game(self) -> dict[str, float]:
        if not self.is_team_tournament():
            return NotImplemented
        return {'1': 1, '½': .5, '0': 0, '+': 1, '-': 0}

    @staticmethod
    def get_possible_scores() -> list[tuple[str, str]]:
        return [('1', '0'), ('½', '½'), ('0', '1'), ('+', '-'), ('-', '+'), ('-', '-')]

    def get_participant_uuids(self, drop_outs: bool = True) -> list[str]:
        return [participant.get_uuid() for participant in self.get_participants(drop_outs)]

    def get_uuid_to_participant_dict(self, drop_outs: bool = True) -> dict[str, Participant]:
        return {participant.get_uuid(): participant for participant in self.get_participants(drop_outs)}

    def get_uuid_to_individual_dicts(self, drop_outs: bool = True) -> dict[str, dict[str, Participant]]:
        if not self.is_team_tournament():
            return NotImplemented
        participants = cast(list[Team], self.get_participants(drop_outs))
        return {
            participant.get_uuid(): cast(dict[str, Participant], participant.get_uuid_to_member_dict())
            for participant in participants
        }

    def get_round_name(self, r: int) -> tuple[str, ...]:
        return "Round", f" {r}"

    def get_simple_scores(self) -> dict[str, float]:
        score_dict = self.get_score_dict()
        scores = {participant.get_uuid(): 0. for participant in self.get_participants()}
        for roun in self.get_results():
            for (uuid_1, score_1), (uuid_2, score_2) in roun:
                if uuid_1 is not None:
                    scores[uuid_1] += score_dict[score_1]
                if uuid_2 is not None:
                    scores[uuid_2] += score_dict[score_2]
        return {uuid: shorten_float(score) for uuid, score in scores.items()}

    def get_standings(self, category_range: Category_Range | None = None) -> Standings_Table:
        return get_standings_with_tiebreaks(self, category_range)

    def get_info(self) -> dict[tuple[str, ...] | str, str]:
        info: dict[tuple[str, ...] | str, str] = {
            "Name": self.get_name(), "Participants": str(self.get_participant_count()), "Mode": self.get_mode()
        }
        parameters_display = self.get_parameters_display()
        for key, value in self.get_parameters().items():
            display = parameters_display[key]
            if display is None:
                continue
            match value:
                case list():
                    info[display] = str(value[0])
                case Parameter():
                    info[display] = value.display_status()
                case _:
                    info[display] = str(value)
        return info

    def set_participants(self, participants: Sequence[Participant], order: bool = False) -> None:
        self.participants = list(participants)
        if order and bool(self.participants) and self.order is not None:
            uuid_to_participant_dict = self.get_uuid_to_participant_dict()
            self.participants = [uuid_to_participant_dict[uuid] for uuid in self.order]

    def set_shallow_participant_count(self, shallow_participant_count: int) -> None:
        self.shallow_participant_count = shallow_participant_count

    def set_parameter(self, key: str, value: Any) -> None:
        self.parameters[key] = value

    def set_variable(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def set_round(self, roun: int) -> None:
        self.variables["round"] = roun

    def set_pairings(self, pairings: Variable_Pairings | list[Pairing] | None) -> None:
        if isinstance(pairings, list):
            pairings = Variable_Pairings(pairings)
        self.set_variable("pairings", pairings)

    def set_drop_outs(self, uuids: list[str]) -> None:
        self.set_variable("drop_outs", uuids)

    def set_category_ranges(self, category_ranges: Sequence[tuple[str, Any, Any]]) -> None:
        self.set_variable("category_ranges", Variable_Category_Ranges(category_ranges))

    def set_parameters_validate(self, keys: Sequence[str], values: Sequence[Any]) -> bool:
        temps = [self.get_parameter(key) for key in keys]
        for key, value in zip(keys, values):
            self.set_parameter(key, value)
        if not self.is_valid_parameters():
            for key, temp in zip(keys, temps):
                self.set_parameter(key, temp)
            return False
        return True

    def is_valid_parameters(self) -> bool:
        return (not self.is_team_tournament()) or self.get_boards() > 0

    def is_valid(self) -> bool:
        return self.is_valid_parameters() and bool(self.get_name()) and self.get_participant_count(drop_outs=False) > 1

    def is_valid_pairings(self, pairings: Sequence[Pairing]) -> bool:
        assert(all(pairing.is_fixed() for pairing in pairings))
        return all(uuid_1 != uuid_2 for uuid_1, uuid_2 in pairings if (uuid_1, uuid_2) != (None, None))

    def is_valid_pairings_match(self, pairing: Pairing, pairings_team: Sequence[Pairing]) -> bool:
        if not self.is_team_tournament():
            return NotImplemented
        assert(pairing.is_fixed())
        participant_dict = cast(dict[str, Team], self.get_uuid_to_participant_dict())
        for i, uuid in enumerate(pairing):
            if uuid is None:
                continue
            member_uuids = list(participant_dict[cast(str, uuid)].get_uuid_to_member_dict())
            if not is_valid_seating(pairings_team, member_uuids, i, self.get_enforce_lineups()):
                return False
        return True

    def is_team_tournament(self) -> bool:
        return self.get_mode().endswith(" (Team)")

    def load_parameters_and_variables(self) -> None:
        for parameter, value in self.get_parameters().items():
            if isinstance(value, dict) and set(value) == {"class", "dict"}:
                self.set_parameter(parameter, globals()[value["class"]](**value["dict"]))
        for variable, value in self.get_variables().items():
            if isinstance(value, dict) and set(value) == {"class", "dict"}:
                self.set_variable(variable, globals()[value["class"]](**value["dict"]))

    def clear_pairings(self) -> None:
        self.set_pairings(None)

    def apply_uuid_associate(self, uuid_associate: str) -> None:
        super().apply_uuid_associate(uuid_associate)
        for participant in self.get_participants():
            participant.apply_uuid_associate(uuid_associate)

    def possess_participants(self) -> None:
        for participant in self.get_participants():
            participant.apply_uuid_associate(self.get_uuid())

    def add_results(self, results: Sequence[Result] | Sequence[Result_Team]) -> None:
        if self.is_team_tournament():
            pairings = cast(list[Pairing], self.get_pairings())
            results_team = cast(list[Result_Team], results)
            self.get_results_team().append(results_team)
            results_player = [Result(
                (cast(str | None, pairing[0]), get_team_result(result, self.get_score_dict())[0]),
                (cast(str | None, pairing[1]), get_team_result(result, self.get_score_dict())[1])
            ) for pairing, result in zip(pairings, results_team)]
        else:
            results_player = cast(list[Result], results)
        self.get_results().append(results_player)
        self.set_pairings(None)
        self.set_round(self.get_round() + 1)

    def remove_results(self) -> None:
        self.set_round(self.get_round() - 1)
        self.set_pairings(None)
        self.get_results().pop()
        if self.is_team_tournament():
            self.get_results_team().pop()

    def seat_participants(self) -> None:
        return

    def drop_out_participants(self, uuids: Sequence[str] | None = None) -> bool:
        uuids = uuids or []
        if self.get_participant_count(drop_outs=False) <= len(uuids) + 1:
            return False
        self.get_drop_outs().extend(list(uuids))
        return True

    def drop_in_participants(self, participants: Sequence[Participant] | None = None) -> bool:
        participants = participants or []
        uuids = self.get_participant_uuids()
        self.get_participants().extend(
            [participant for participant in participants if participant.get_uuid() not in uuids]
        )
        self.possess_participants()
        self.seat_participants()
        drop_outs = list(set(self.get_drop_outs()).difference({participant.get_uuid() for participant in participants}))
        self.set_drop_outs(drop_outs)
        return True

    def is_done(self) -> bool:
        return False

    def load_pairings(self) -> None:
        return
