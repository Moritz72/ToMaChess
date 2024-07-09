from __future__ import annotations
from copy import deepcopy
from json import dumps
from random import shuffle
from typing import Any, Sequence, cast
from ..common.bracket_tree import Bracket_Tree
from ..common.category_range import Category_Range
from ..common.cross_table import Cross_Table
from ..common.pairing import Pairing
from ..common.pairing_item import Pairing_Item
from ..common.result import Result
from ..common.result_team import Result_Team
from ..common.standings_table import Standings_Table
from ..common.type_declarations import Participant, Tournament_Data
from ..parameters.parameter import Parameter
from ..parameters.parameter_tiebreak import Parameter_Tiebreak
from ..registries.parameter_registry import PARAMETER_REGISTRY
from ..registries.variable_registry import VARIABLE_REGISTRY
from ..utils.functions_tournament_util import get_standings_with_tiebreaks, get_team_result, is_valid_lineup
from ..variables.variable import Variable
from ..variables.variable_category_ranges import Variable_Category_Ranges
from ..variables.variable_pairings import Variable_Pairings
from ..variables.variable_results import Variable_Results
from ..variables.variable_results_team import Variable_Results_Team
from ...common.functions_util import has_duplicates
from ...common.object import Object
from ...team.team import Team


class Tournament(Object):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(name, uuid, uuid_associate)
        self.participants: list[Participant] = participants
        self.shallow_participant_count: int = shallow_participant_count or 0
        self.parameters: dict[str, Any] = parameters or dict()
        self.variables: dict[str, Any] = variables or dict()
        self.order: list[str] | None = order
        self.mode: str = ""
        self.parameters_display: dict[str, tuple[str, ...] | str | None] = dict()
        self.variables = {
            "round": 1,
            "pairings": Variable_Pairings([]),
            "results": Variable_Results([]),
            "results_team": Variable_Results_Team([]),
            "drop_outs": [],
            "byes": [],
            "forbidden_pairings": [],
            "category_ranges": Variable_Category_Ranges([])
        } | self.variables

    def copy(self) -> Tournament:
        return deepcopy(self)

    def get_participants(self, drop_outs: bool = True, byes: bool = True) -> list[Participant]:
        return [
            participant for participant in self.participants
            if (drop_outs or participant.get_uuid() not in self.get_drop_outs())
            and (byes or participant.get_uuid() not in self.get_byes())
        ]

    def get_shallow_participant_count(self) -> int:
        return self.shallow_participant_count

    def get_participant_count(self, drop_outs: bool = True, byes: bool = True) -> int:
        if bool(self.get_participants()):
            return len(self.get_participants(drop_outs, byes))
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

    def get_pairings(self) -> Variable_Pairings:
        return cast(Variable_Pairings, self.get_variable("pairings"))

    def get_results(self) -> Variable_Results:
        return cast(Variable_Results, self.get_variable("results"))

    def get_drop_outs(self) -> list[str]:
        return cast(list[str], self.get_variable("drop_outs"))

    def get_byes(self) -> list[str]:
        return cast(list[str], self.get_variable("byes"))

    def get_forbidden_pairings(self) -> list[tuple[str, str]]:
        return [(uuids[0], uuids[1]) for uuids in cast(list[list[str]], self.get_variable("forbidden_pairings"))]

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
                parameters[parameter] = {"class": value.get_class(), "dict": value.get_dict()}
        for variable, value in variables.items():
            if isinstance(value, Variable):
                variables[variable] = {"class": value.get_class(), "dict": value.get_dict()}
        return self.get_mode(), self.get_name(), self.get_participant_count(), dumps(parameters), dumps(variables),\
            dumps([participant.get_uuid() for participant in self.get_participants()] or self.order), \
            self.get_uuid(), self.get_uuid_associate()

    def get_score_dict(self) -> dict[str, float]:
        return {'1': 1, '½': .5, '0': 0, '+': 1, '-': 0, 'b': 0}

    def get_score_dict_game(self) -> dict[str, float]:
        if not self.is_team_tournament():
            return NotImplemented
        return {'1': 1, '½': .5, '0': 0, '+': 1, '-': 0}

    @staticmethod
    def get_possible_scores() -> list[tuple[str, str]]:
        return [('1', '0'), ('½', '½'), ('0', '1'), ('+', '-'), ('-', '+'), ('-', '-')]

    def get_participant_uuids(self, drop_outs: bool = True, byes: bool = True) -> list[str]:
        return [participant.get_uuid() for participant in self.get_participants(drop_outs, byes)]

    def get_uuid_to_participant_dict(self, drop_outs: bool = True, byes: bool = True) -> dict[str, Participant]:
        return {participant.get_uuid(): participant for participant in self.get_participants(drop_outs, byes)}

    def get_uuid_to_name_dict(self, drop_outs: bool = True, byes: bool = True) -> dict[str, str]:
        return {
            participant.get_uuid(): participant.get_name() for participant in self.get_participants(drop_outs, byes)
        }

    def get_individuals(self, drop_outs: bool = True, byes: bool = True) -> list[Participant]:
        if not self.is_team_tournament():
            return NotImplemented
        participants = cast(list[Team], self.get_participants(drop_outs, byes))
        return [member for team in participants for member in team.get_members()]

    def get_uuid_to_name_dict_individual(self, drop_outs: bool = True, byes: bool = True) -> dict[str, str]:
        if not self.is_team_tournament():
            return NotImplemented
        return {
            participant.get_uuid(): participant.get_name() for participant in self.get_individuals(drop_outs, byes)
        }

    def get_uuid_to_individual_dicts(
            self, drop_outs: bool = True, byes: bool = True
    ) -> dict[str, dict[str, Participant]]:
        if not self.is_team_tournament():
            return NotImplemented
        participants = cast(list[Team], self.get_participants(drop_outs, byes))
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
            for (item_1, score_1), (item_2, score_2) in roun:
                if item_1 in scores:
                    scores[item_1] += score_dict[score_1]
                if item_2 in scores:
                    scores[item_2] += score_dict[score_2]
        return scores

    def get_standings(self, category_range: Category_Range | None = None) -> Standings_Table:
        return get_standings_with_tiebreaks(self, category_range)

    def get_cross_table(self, i: int) -> Cross_Table:
        assert(i < self.get_cross_tables())
        participants = self.get_standings().participants
        uuids = [participant.get_uuid() for participant in participants]
        table = [[None if i == j else "" for j in range(len(uuids))] for i in range(len(uuids))]

        for roun in self.get_results():
            for (item_1, score_1), (item_2, score_2) in roun:
                if item_1 in uuids and item_2 in uuids:
                    index_1, index_2 = uuids.index(item_1), uuids.index(item_2)
                    entry_1, entry_2 = table[index_1][index_2], table[index_2][index_1]
                    assert(entry_1 is not None and entry_2 is not None)
                    table[index_1][index_2] = entry_1 + score_1
                    table[index_2][index_1] = entry_2 + score_2
        return Cross_Table(("Crosstable",), table, [participant.get_name() for participant in participants])

    def get_cross_tables(self) -> int:
        return 1

    def get_bracket_tree(self, i: int) -> Bracket_Tree:
        return NotImplemented

    def get_bracket_trees(self) -> int:
        return 0

    def get_details(self) -> dict[tuple[str, ...] | str, str]:
        details: dict[tuple[str, ...] | str, str] = {
            "Name": self.get_name(), "Participants": str(self.get_participant_count()), "Mode": self.get_mode()
        }
        parameters_display = self.get_parameters_display()
        for key, value in self.get_parameters().items():
            display = parameters_display[key]
            if display is None:
                continue
            match value:
                case list():
                    details[display] = str(value[0])
                case Parameter():
                    details[display] = value.display_status()
                case _:
                    details[display] = str(value)
        return details

    def set_participants(self, participants: Sequence[Participant], from_order: bool = False) -> None:
        self.participants = list(participants)
        if from_order and bool(self.participants) and self.order is not None:
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

    def set_pairings(self, pairings: Variable_Pairings | list[Pairing]) -> None:
        if isinstance(pairings, list):
            self.set_variable("pairings", Variable_Pairings([]))
            self.get_pairings().extend(pairings)
        else:
            self.set_variable("pairings", pairings)

    def set_drop_outs(self, uuids: list[str]) -> None:
        self.set_variable("drop_outs", uuids)

    def set_byes(self, uuids: list[str]) -> None:
        self.set_variable("byes", uuids)

    def set_forbidden_pairings(self, forbidden_pairings: list[tuple[str, str]]):
        self.set_variable("forbidden_pairings", forbidden_pairings)

    def set_category_ranges(self, category_ranges: Sequence[Category_Range]) -> None:
        self.get_category_ranges().clear()
        self.get_category_ranges().extend(category_ranges)

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
        return all(item_1 != item_2 for item_1, item_2 in pairings if (item_1, item_2) != ("", ""))

    def is_valid_pairings_match(self, pairing: Pairing, pairings_team: Sequence[Pairing]) -> bool:
        if not self.is_team_tournament():
            return NotImplemented
        participant_dict = cast(dict[str, Team], self.get_uuid_to_participant_dict())
        for i, item in enumerate(pairing):
            assert(not isinstance(item, list))
            if item.is_bye():
                continue
            member_uuids = list(participant_dict[item].get_uuid_to_member_dict())
            if not is_valid_lineup(pairings_team, member_uuids, i, self.get_enforce_lineups()):
                return False
        return True

    def is_team_tournament(self) -> bool:
        return self.get_mode().endswith(" (Team)")

    def is_done(self) -> bool:
        return False

    def is_undo_last_round_allowed(self) -> bool:
        return self.get_round() > 1

    def is_drop_out_allowed(self) -> bool:
        return True

    def is_drop_in_allowed(self) -> bool:
        return True

    def is_add_byes_allowed(self) -> bool:
        return not self.is_done()

    def is_seeding_allowed(self) -> bool:
        return True

    def is_forbidden_pairings_allowed(self) -> bool:
        return False

    def initialize(self) -> None:
        participants = self.get_participants()
        self.load_parameters_and_variables()
        self.set_participants(participants, from_order=True)
        if bool(participants):
            self.shallow_participant_count = len(participants)

    def load_parameters_and_variables(self) -> None:
        for parameter, value in self.get_parameters().items():
            if isinstance(value, dict) and set(value) == {"class", "dict"}:
                self.set_parameter(parameter, PARAMETER_REGISTRY[value["class"]](**value["dict"]))
        for variable, value in self.get_variables().items():
            if isinstance(value, dict) and set(value) == {"class", "dict"}:
                self.set_variable(variable, VARIABLE_REGISTRY[value["class"]](**value["dict"]))

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
                (cast(Pairing_Item, pairing[0]), get_team_result(result, self.get_score_dict())[0]),
                (cast(Pairing_Item, pairing[1]), get_team_result(result, self.get_score_dict())[1])
            ) for pairing, result in zip(pairings, results_team)]
        else:
            results_player = cast(list[Result], results)
        self.get_results().append(results_player)
        self.set_byes([])
        self.set_pairings([])
        self.set_round(self.get_round() + 1)

    def remove_results(self) -> None:
        self.set_round(self.get_round() - 1)
        self.set_pairings([])
        self.get_results().pop()
        if self.is_team_tournament():
            self.get_results_team().pop()

    def seed_participants(self, seeds: list[int] | None = None) -> None:
        if seeds is None:
            participants = self.get_participants()
            shuffle(participants)
            self.set_participants(participants)
            return
        participants = self.get_participants()
        assert(not has_duplicates(seeds) and len(seeds) == len(participants))
        self.set_participants([participants[i] for i in seeds])

    def drop_out_participants(self, uuids: Sequence[str]) -> None:
        if self.get_participant_count(drop_outs=False) <= len(uuids) + 1:
            return
        self.get_drop_outs().extend(list(uuids))
        self.set_byes(list(set(self.get_byes()).difference(set(uuids))))

    def drop_in_participants(self, participants: Sequence[Participant]) -> None:
        uuids = self.get_participant_uuids()
        drop_ins = [participant for participant in participants if participant.get_uuid() not in uuids]
        drop_outs = list(set(self.get_drop_outs()).difference({participant.get_uuid() for participant in participants}))
        for participant in drop_ins:
            participant.apply_uuid_associate(self.get_uuid())
        self.set_participants(self.get_participants() + drop_ins)
        self.set_drop_outs(drop_outs)

    def add_byes(self, uuids: Sequence[str]) -> None:
        self.set_byes(list(uuids))

    def load_pairings(self) -> None:
        return
