from typing import cast
from typing import Any, Sequence
from .variable import Variable
from ..common.bracket_tree import Bracket_Tree
from ..common.result import Result
from ..common.result_team import Result_Team
from ..common.type_declarations import Tournament_Data
from ..registries.variable_registry import VARIABLE_REGISTRY
from ..tournaments.tournament_knockout import Tournament_Knockout
from ..utils.functions_tournament_get import get_tournament_type, json_loads_entry

BEATEN_BY_DUMMY = -1
MODES = {
    "Knockout": get_tournament_type("Knockout"),
    "Knockout (Team)": get_tournament_type("Knockout (Team)")
}


@VARIABLE_REGISTRY.register("Variable_Knockout_Brackets")
class Variable_Knockout_Brackets(list[Tournament_Knockout], Variable):
    def __init__(self, entries: list[Tournament_Data], indices: list[int]) -> None:
        entries_load = [json_loads_entry(entry) for entry in entries]
        tournaments = cast(list[Tournament_Knockout], [
            MODES[entry[0]]([], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7])
            for entry in entries_load
        ])
        for tournament in tournaments:
            tournament.initialize()
        super().__init__(tournaments)
        self.indices: list[int] = indices

    def get_class(self) -> str:
        return "Variable_Knockout_Brackets"

    def get_dict(self) -> dict[str, Any]:
        return {"entries": [tournament.get_data() for tournament in self], "indices": self.indices}

    def get_indices(self) -> list[int]:
        return self.indices

    def get_bracket_uuids(self, index: int) -> list[str]:
        return self[index].get_standings_dict().get_uuids()

    def get_current_bracket(self) -> Tournament_Knockout:
        return self[self.indices[-1]]

    def get_next_bracket_index(self) -> int:
        return max(range(len(self)), key=lambda x: (len(self.get_bracket_uuids(x)), x))

    def get_uuid_to_standings_table_entry_dict(self) -> dict[str, list[float]]:
        standings_table_entry_dict = {}
        for i, bracket in enumerate(self):
            for uuid, standing in bracket.get_standings_dict().items():
                if standing.beaten_by_seed == BEATEN_BY_DUMMY:
                    continue
                standings_table_entry_dict[uuid] = [i + 1, standing.level, *standing.score]
        return standings_table_entry_dict

    def get_bracket_tree(self, i: int) -> Bracket_Tree:
        bracket_tree = self[i].get_bracket_tree(0)
        bracket_tree.name += (' ', f"{i + 1}")
        return bracket_tree

    def set_beaten_by_dummy(self) -> None:
        for bracket in self[1:]:
            for uuid, standing in bracket.get_standings_dict().items():
                standing.beaten_by_seed = BEATEN_BY_DUMMY

    def is_done(self) -> bool:
        return all(tournament.is_done() for tournament in self)

    def add_results(self, results: Sequence[Result] | Sequence[Result_Team]) -> None:
        index = self.indices[-1]
        bracket = self[index]
        standings_dict = bracket.get_standings_dict()
        level = standings_dict.get_current_level()

        bracket.add_results(results)
        if standings_dict.get_current_level() == level:
            self.indices.append(index)
            return

        uuids = [
            uuid for uuid in standings_dict.get_uuids_in_level(level)
            if standings_dict[uuid].beaten_by_seed not in (None, 0, BEATEN_BY_DUMMY)
        ]
        if index + 1 < len(self):
            standings_dict_next = self[index + 1].get_standings_dict()
            level_next = standings_dict_next.get_current_level()
            for uuid in uuids:
                standings_dict_next[uuid].beaten_by_seed = None
                standings_dict_next[uuid].level = level_next
        self.indices.append(self.get_next_bracket_index())

    def remove_results(self) -> None:
        self[self.indices.pop()].set_pairings([])
        index = self.indices[-1]
        bracket = self[index]
        bracket.remove_results()

        if index + 1 >= len(self):
            return
        bracket_below = self[index + 1]
        if bracket == bracket_below:
            return
        standings_dict = bracket_below.get_standings_dict()
        for uuid in bracket.get_standings_dict().get_uuids_in_level():
            standings_dict[uuid].beaten_by_seed = BEATEN_BY_DUMMY
            standings_dict[uuid].level = 0
